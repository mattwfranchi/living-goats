#!/usr/bin/env python3
"""
Spotify Playlist Indexer

This script indexes a Spotify playlist, downloads artwork images,
and saves metadata as JSON using pandas DataFrame.
"""

import requests
import pandas as pd
import json
import os
import time
import base64
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpotifyPlaylistIndexer:
    def __init__(self, client_id, client_secret):
        """
        Initialize the Spotify API client.
        
        Args:
            client_id (str): Spotify API client ID
            client_secret (str): Spotify API client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = 'https://api.spotify.com/v1'
        self.access_token = None
        
        # Create directories for storing images and data
        self.images_dir = Path('playlist_images')
        self.data_dir = Path('playlist_data')
        self.images_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Get access token
        self.get_access_token()
    
    def get_access_token(self):
        """
        Get access token using Client Credentials flow.
        """
        auth_url = 'https://accounts.spotify.com/api/token'
        
        # Create authorization header
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            logger.info("Successfully obtained Spotify access token")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting access token: {e}")
            raise
    
    def get_headers(self):
        """Get headers with authorization for API requests."""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def extract_playlist_id(self, playlist_url):
        """
        Extract playlist ID from Spotify URL.
        
        Args:
            playlist_url (str): Spotify playlist URL
            
        Returns:
            str: Playlist ID
        """
        # Handle different Spotify URL formats
        # https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
        # https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=...
        
        if 'playlist/' in playlist_url:
            # Extract ID from URL
            playlist_id = playlist_url.split('playlist/')[-1]
            # Remove query parameters if present
            playlist_id = playlist_id.split('?')[0]
            return playlist_id
        
        return None
    
    def get_playlist_details(self, playlist_id):
        """
        Get playlist details from Spotify API.
        
        Args:
            playlist_id (str): Spotify playlist ID
            
        Returns:
            dict: Playlist data
        """
        url = f"{self.base_url}/playlists/{playlist_id}"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching playlist details: {e}")
            return None
    
    def get_playlist_tracks(self, playlist_id):
        """
        Get all tracks from a playlist (handles pagination).
        
        Args:
            playlist_id (str): Spotify playlist ID
            
        Returns:
            list: List of track data
        """
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        all_tracks = []
        
        params = {
            'limit': 100,  # Maximum per request
            'offset': 0
        }
        
        while True:
            try:
                response = requests.get(url, headers=self.get_headers(), params=params)
                response.raise_for_status()
                
                data = response.json()
                tracks = data.get('items', [])
                
                if not tracks:
                    break
                
                all_tracks.extend(tracks)
                
                # Check if there are more tracks
                if data.get('next') is None:
                    break
                
                params['offset'] += 100
                logger.info(f"Retrieved {len(all_tracks)} tracks so far...")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching tracks: {e}")
                break
        
        return all_tracks
    
    def download_artwork(self, artwork_url, filename):
        """
        Download artwork image from URL if it doesn't already exist.
        
        Args:
            artwork_url (str): Artwork URL
            filename (str): Local filename to save
            
        Returns:
            str: Local file path or None if failed
        """
        if not artwork_url:
            return None
        
        file_path = self.images_dir / filename
        
        # Check if file already exists
        if file_path.exists():
            logger.info(f"Artwork already exists, skipping download: {filename}")
            return str(file_path)
            
        try:
            response = requests.get(artwork_url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded artwork: {filename}")
            return str(file_path)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading artwork {filename}: {e}")
            return None
    
    def process_track(self, track_item, track_index):
        """
        Process individual track data and download artwork.
        
        Args:
            track_item (dict): Track item from API (includes track + added info)
            track_index (int): Track index in playlist
            
        Returns:
            dict: Processed track metadata
        """
        track_data = track_item.get('track', {})
        
        # Handle local tracks or None tracks
        if not track_data or track_data.get('type') != 'track':
            return None
        
        # Extract artist names
        artists = track_data.get('artists', [])
        artist_names = [artist.get('name', '') for artist in artists]
        primary_artist = artist_names[0] if artist_names else 'Unknown Artist'
        
        # Extract album info
        album = track_data.get('album', {})
        album_name = album.get('name', 'Unknown Album')
        
        # Get the largest artwork image
        album_images = album.get('images', [])
        artwork_url = album_images[0].get('url') if album_images else None
        
        # Extract other metadata
        track_info = {
            'index': track_index,
            'id': track_data.get('id'),
            'name': track_data.get('name'),
            'artist_name': primary_artist,
            'all_artists': artist_names,
            'album_name': album_name,
            'album_id': album.get('id'),
            'duration_ms': track_data.get('duration_ms'),
            'explicit': track_data.get('explicit', False),
            'popularity': track_data.get('popularity', 0),
            'track_number': track_data.get('track_number'),
            'disc_number': track_data.get('disc_number'),
            'release_date': album.get('release_date'),
            'release_date_precision': album.get('release_date_precision'),
            'album_type': album.get('album_type'),
            'total_tracks': album.get('total_tracks'),
            'external_urls': track_data.get('external_urls', {}),
            'preview_url': track_data.get('preview_url'),
            'spotify_url': track_data.get('external_urls', {}).get('spotify'),
            'added_at': track_item.get('added_at'),
            'added_by': track_item.get('added_by', {}).get('id'),
            'artwork_url': artwork_url,
            'artwork_local_path': None
        }
        
        # Download artwork if available
        if artwork_url:
            # Create safe filename
            safe_name = f"{track_index:03d}_{primary_artist}_{track_info['name']}"
            safe_name = re.sub(r'[^\w\s-]', '', safe_name)  # Remove special chars
            safe_name = re.sub(r'[-\s]+', '_', safe_name)  # Replace spaces/hyphens with underscores
            safe_name = safe_name[:100]  # Limit filename length
            artwork_filename = f"{safe_name}.jpg"
            
            # Download artwork
            local_path = self.download_artwork(artwork_url, artwork_filename)
            if local_path:
                track_info['artwork_local_path'] = local_path
        
        return track_info
    
    def get_audio_features(self, track_ids):
        """
        Get audio features for multiple tracks.
        
        Args:
            track_ids (list): List of track IDs
            
        Returns:
            dict: Dictionary mapping track ID to audio features
        """
        if not track_ids:
            return {}
        
        # Spotify allows up to 100 track IDs per request
        chunk_size = 100
        all_features = {}
        
        for i in range(0, len(track_ids), chunk_size):
            chunk_ids = track_ids[i:i + chunk_size]
            ids_param = ','.join(chunk_ids)
            
            url = f"{self.base_url}/audio-features"
            params = {'ids': ids_param}
            
            try:
                response = requests.get(url, headers=self.get_headers(), params=params)
                response.raise_for_status()
                
                data = response.json()
                features_list = data.get('audio_features', [])
                
                for features in features_list:
                    if features:  # Some tracks might not have audio features
                        all_features[features['id']] = features
                
                logger.info(f"Retrieved audio features for {len(chunk_ids)} tracks")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching audio features: {e}")
        
        return all_features
    
    def convert_to_json_serializable(self, obj):
        """
        Convert numpy/pandas types to JSON-serializable Python types.
        
        Args:
            obj: Object to convert
            
        Returns:
            JSON-serializable object
        """
        if isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict('records') if isinstance(obj, pd.DataFrame) else obj.to_dict()
        elif isinstance(obj, (pd.Int64Dtype, pd.Float64Dtype)):
            return obj.item()
        elif hasattr(obj, 'dtype'):
            # Handle numpy/pandas scalar types
            if pd.isna(obj):
                return None
            elif 'int' in str(obj.dtype):
                return int(obj)
            elif 'float' in str(obj.dtype):
                return float(obj)
            elif 'bool' in str(obj.dtype):
                return bool(obj)
            else:
                return str(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self.convert_to_json_serializable(item) for item in obj]
        else:
            return obj
    
    def index_playlist(self, playlist_url):
        """
        Index entire playlist and save metadata.
        
        Args:
            playlist_url (str): Spotify playlist URL
            
        Returns:
            str: Path to saved JSON file
        """
        logger.info(f"Starting to index playlist: {playlist_url}")
        
        # Extract playlist ID
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            logger.error("Could not extract playlist ID from URL")
            return None
        
        logger.info(f"Extracted playlist ID: {playlist_id}")
        
        # Get playlist details
        playlist_data = self.get_playlist_details(playlist_id)
        if not playlist_data:
            logger.error("Could not fetch playlist data")
            return None
        
        # Extract playlist metadata
        playlist_metadata = {
            'id': playlist_data.get('id'),
            'name': playlist_data.get('name'),
            'description': playlist_data.get('description'),
            'owner': playlist_data.get('owner', {}).get('display_name'),
            'owner_id': playlist_data.get('owner', {}).get('id'),
            'public': playlist_data.get('public'),
            'collaborative': playlist_data.get('collaborative'),
            'follower_count': playlist_data.get('followers', {}).get('total'),
            'track_count': playlist_data.get('tracks', {}).get('total'),
            'url': playlist_url,
            'spotify_url': playlist_data.get('external_urls', {}).get('spotify'),
            'snapshot_id': playlist_data.get('snapshot_id')
        }
        
        logger.info(f"Playlist: {playlist_metadata['name']} ({playlist_metadata['track_count']} tracks)")
        
        # Get all tracks
        tracks_data = self.get_playlist_tracks(playlist_id)
        processed_tracks = []
        
        for index, track_item in enumerate(tracks_data, 1):
            track_name = track_item.get('track', {}).get('name', 'Unknown')
            logger.info(f"Processing track {index}/{len(tracks_data)}: {track_name}")
            
            track_info = self.process_track(track_item, index)
            if track_info:  # Skip None tracks (local files, etc.)
                processed_tracks.append(track_info)
            
            # Small delay to be respectful (reduced since no audio features)
            time.sleep(0.02)
        
        # Audio features disabled for faster processing
        # Uncomment the following lines if you want audio features:
        # track_ids = [track['id'] for track in processed_tracks if track.get('id')]
        # logger.info("Fetching audio features...")
        # audio_features = self.get_audio_features(track_ids)
        # 
        # # Add audio features to track data
        # for track in processed_tracks:
        #     track_id = track.get('id')
        #     if track_id in audio_features:
        #         features = audio_features[track_id]
        #         track['audio_features'] = {
        #             'danceability': features.get('danceability'),
        #             'energy': features.get('energy'),
        #             'key': features.get('key'),
        #             'loudness': features.get('loudness'),
        #             'mode': features.get('mode'),
        #             'speechiness': features.get('speechiness'),
        #             'acousticness': features.get('acousticness'),
        #             'instrumentalness': features.get('instrumentalness'),
        #             'liveness': features.get('liveness'),
        #             'valence': features.get('valence'),
        #             'tempo': features.get('tempo'),
        #             'time_signature': features.get('time_signature')
        #         }
        
        # Create DataFrame
        df = pd.DataFrame(processed_tracks)
        
        # Calculate summary statistics
        total_duration = df['duration_ms'].sum()
        unique_artists = df['artist_name'].nunique()
        unique_albums = df['album_name'].nunique()
        
        # Extract all artists (including collaborations)
        all_artist_names = []
        for artists_list in df['all_artists']:
            all_artist_names.extend(artists_list)
        unique_all_artists = len(set(all_artist_names))
        
        # Prepare final data structure (converting numpy/pandas types to Python types for JSON serialization)
        final_data = {
            'playlist_metadata': playlist_metadata,
            'tracks': self.convert_to_json_serializable(df.to_dict('records')),
            'summary': {
                'total_tracks': len(processed_tracks),
                'total_duration_ms': int(total_duration),
                'total_duration_hours': float(total_duration / (1000 * 60 * 60)),
                'unique_primary_artists': int(unique_artists),
                'unique_all_artists': int(unique_all_artists),
                'unique_albums': int(unique_albums),
                'average_popularity': float(df['popularity'].mean()),
                'explicit_tracks': int(df['explicit'].sum()),
                'tracks_with_preview': int(df['preview_url'].notna().sum()),
                'indexed_at': pd.Timestamp.now().isoformat()
                # Audio features summary disabled - uncomment if you enable audio features above
                # 'audio_features_summary': {
                #     'avg_danceability': float(df['audio_features'].apply(lambda x: x.get('danceability') if x else None).mean()),
                #     'avg_energy': float(df['audio_features'].apply(lambda x: x.get('energy') if x else None).mean()),
                #     'avg_valence': float(df['audio_features'].apply(lambda x: x.get('valence') if x else None).mean()),
                #     'avg_tempo': float(df['audio_features'].apply(lambda x: x.get('tempo') if x else None).mean())
                # } if any(df['audio_features'].notna()) else None
            }
        }
        
        # Save to JSON
        json_filename = f"spotify_playlist_{playlist_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = self.data_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved playlist data to: {json_path}")
        logger.info(f"Downloaded {len([t for t in processed_tracks if t['artwork_local_path']])} artwork images")
        
        return str(json_path)

def load_spotify_keys(keys_file='keys.txt'):
    """
    Load Spotify API keys from a file.
    
    Args:
        keys_file (str): Path to the keys file
        
    Returns:
        tuple: (client_id, client_secret) or (None, None) if failed
    """
    try:
        keys = {}
        with open(keys_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    keys[key.strip()] = value.strip()
        
        client_id = keys.get('SPOTIFY_CLIENT_ID')
        client_secret = keys.get('SPOTIFY_SECRET')
        
        if client_id and client_secret:
            logger.info("Successfully loaded Spotify API credentials from keys.txt")
            return client_id, client_secret
        else:
            logger.error("Missing SPOTIFY_CLIENT_ID or SPOTIFY_SECRET in keys.txt")
            return None, None
            
    except FileNotFoundError:
        logger.error(f"Keys file '{keys_file}' not found")
        return None, None
    except Exception as e:
        logger.error(f"Error reading keys file: {e}")
        return None, None

def main():
    """Main function to run the playlist indexer."""
    
    # Load Spotify API credentials from keys.txt
    CLIENT_ID, CLIENT_SECRET = load_spotify_keys()
    
    # Example playlist URL - replace with your desired playlist
    PLAYLIST_URL = "https://open.spotify.com/playlist/1PhVF0dSacCtdeOmgbDHTt?si=0ee4dc39da894242"  # Example: Today's Top Hits
    
    # Check if credentials were loaded successfully
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Could not load Spotify API credentials from keys.txt")
        print("\nMake sure keys.txt exists with the following format:")
        print("SPOTIFY_CLIENT_ID=your_client_id_here")
        print("SPOTIFY_SECRET=your_client_secret_here")
        print("\nTo get your credentials:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create a new app (any name/description)")
        print("3. Copy the Client ID and Client Secret")
        print("4. Add them to keys.txt")
        return
    
    try:
        # Create indexer instance
        indexer = SpotifyPlaylistIndexer(CLIENT_ID, CLIENT_SECRET)
        
        # Index the playlist
        result_path = indexer.index_playlist(PLAYLIST_URL)
        
        if result_path:
            print(f"\n✅ Successfully indexed playlist!")
            print(f"📁 Data saved to: {result_path}")
            print(f"🖼️  Images saved to: {indexer.images_dir}")
            print(f"\n🎵 The JSON file contains:")
            print(f"   - Complete playlist metadata")
            print(f"   - Track details (audio features disabled)")
            print(f"   - Downloaded artwork images")
            print(f"   - Summary statistics")
            print(f"\nYou can now analyze the playlist data!")
        else:
            print("\n❌ Failed to index playlist. Check the logs for details.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure your Spotify API credentials are correct.")

if __name__ == "__main__":
    main() 