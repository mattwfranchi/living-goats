#!/usr/bin/env python3
"""
Apple Music Playlist Indexer

This script indexes an Apple Music playlist, downloads artwork images,
and saves metadata as JSON using pandas DataFrame.
"""

import requests
import pandas as pd
import json
import os
import time
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppleMusicPlaylistIndexer:
    def __init__(self, developer_token, storefront='us'):
        """
        Initialize the Apple Music API client.
        
        Args:
            developer_token (str): Apple Music API developer token
            storefront (str): Apple Music storefront (default: 'us')
        """
        self.developer_token = developer_token
        self.storefront = storefront
        self.base_url = 'https://api.music.apple.com/v1'
        self.headers = {
            'Authorization': f'Bearer {developer_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Create directories for storing images and data
        self.images_dir = Path('playlist_images')
        self.data_dir = Path('playlist_data')
        self.images_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
    
    def extract_playlist_id(self, playlist_url):
        """
        Extract playlist ID from Apple Music URL.
        
        Args:
            playlist_url (str): Apple Music playlist URL
            
        Returns:
            str: Playlist ID
        """
        # Extract playlist ID from URL like: https://music.apple.com/us/playlist/encapsulative/pl.u-BNA6rRRCemXeve6
        if '/playlist/' in playlist_url:
            return playlist_url.split('/playlist/')[-1].split('/')[-1]
        return None
    
    def get_playlist_details(self, playlist_id):
        """
        Get playlist details from Apple Music API.
        
        Args:
            playlist_id (str): Apple Music playlist ID
            
        Returns:
            dict: Playlist data
        """
        url = f"{self.base_url}/catalog/{self.storefront}/playlists/{playlist_id}"
        params = {
            'include': 'tracks',
            'limit': 300  # Maximum tracks per request
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching playlist details: {e}")
            return None
    
    def download_artwork(self, artwork_url, filename):
        """
        Download artwork image from URL.
        
        Args:
            artwork_url (str): Artwork URL
            filename (str): Local filename to save
            
        Returns:
            str: Local file path or None if failed
        """
        if not artwork_url:
            return None
            
        try:
            # Replace size parameters with high resolution
            if '{w}x{h}' in artwork_url:
                artwork_url = artwork_url.replace('{w}x{h}', '1200x1200')
            
            response = requests.get(artwork_url, timeout=30)
            response.raise_for_status()
            
            file_path = self.images_dir / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded artwork: {filename}")
            return str(file_path)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading artwork {filename}: {e}")
            return None
    
    def process_track(self, track_data, track_index):
        """
        Process individual track data and download artwork.
        
        Args:
            track_data (dict): Track data from API
            track_index (int): Track index in playlist
            
        Returns:
            dict: Processed track metadata
        """
        track_info = {
            'index': track_index,
            'id': track_data.get('id'),
            'type': track_data.get('type'),
            'name': track_data.get('attributes', {}).get('name'),
            'artist_name': track_data.get('attributes', {}).get('artistName'),
            'album_name': track_data.get('attributes', {}).get('albumName'),
            'duration_ms': track_data.get('attributes', {}).get('durationInMillis'),
            'release_date': track_data.get('attributes', {}).get('releaseDate'),
            'genre_names': track_data.get('attributes', {}).get('genreNames', []),
            'track_number': track_data.get('attributes', {}).get('trackNumber'),
            'disc_number': track_data.get('attributes', {}).get('discNumber'),
            'isrc': track_data.get('attributes', {}).get('isrc'),
            'content_rating': track_data.get('attributes', {}).get('contentRating'),
            'preview_url': track_data.get('attributes', {}).get('previews', [{}])[0].get('url'),
            'artwork_url': None,
            'artwork_local_path': None
        }
        
        # Handle artwork
        artwork = track_data.get('attributes', {}).get('artwork')
        if artwork:
            artwork_url = artwork.get('url')
            if artwork_url:
                track_info['artwork_url'] = artwork_url
                
                # Create filename for artwork
                safe_name = f"{track_index:03d}_{track_info['artist_name']}_{track_info['name']}"
                safe_name = "".join(c for c in safe_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')[:100]  # Limit filename length
                artwork_filename = f"{safe_name}.jpg"
                
                # Download artwork
                local_path = self.download_artwork(artwork_url, artwork_filename)
                if local_path:
                    track_info['artwork_local_path'] = local_path
        
        return track_info
    
    def index_playlist(self, playlist_url):
        """
        Index entire playlist and save metadata.
        
        Args:
            playlist_url (str): Apple Music playlist URL
            
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
        playlist_info = playlist_data.get('data', [{}])[0]
        playlist_attributes = playlist_info.get('attributes', {})
        
        playlist_metadata = {
            'id': playlist_info.get('id'),
            'name': playlist_attributes.get('name'),
            'description': playlist_attributes.get('description', {}).get('standard'),
            'curator_name': playlist_attributes.get('curatorName'),
            'last_modified_date': playlist_attributes.get('lastModifiedDate'),
            'track_count': len(playlist_attributes.get('tracks', {}).get('data', [])),
            'url': playlist_url
        }
        
        logger.info(f"Playlist: {playlist_metadata['name']} ({playlist_metadata['track_count']} tracks)")
        
        # Process tracks
        tracks_data = playlist_attributes.get('tracks', {}).get('data', [])
        processed_tracks = []
        
        for index, track in enumerate(tracks_data, 1):
            logger.info(f"Processing track {index}/{len(tracks_data)}: {track.get('attributes', {}).get('name')}")
            
            track_info = self.process_track(track, index)
            processed_tracks.append(track_info)
            
            # Add small delay to be respectful to the API
            time.sleep(0.1)
        
        # Create DataFrame
        df = pd.DataFrame(processed_tracks)
        
        # Prepare final data structure
        final_data = {
            'playlist_metadata': playlist_metadata,
            'tracks': df.to_dict('records'),
            'summary': {
                'total_tracks': len(processed_tracks),
                'total_duration_ms': df['duration_ms'].sum(),
                'unique_artists': df['artist_name'].nunique(),
                'unique_albums': df['album_name'].nunique(),
                'genres': list(set([genre for genres in df['genre_names'] for genre in genres if genres])),
                'indexed_at': pd.Timestamp.now().isoformat()
            }
        }
        
        # Save to JSON
        json_filename = f"playlist_{playlist_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = self.data_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved playlist data to: {json_path}")
        logger.info(f"Downloaded {len([t for t in processed_tracks if t['artwork_local_path']])} artwork images")
        
        return str(json_path)

def main():
    """Main function to run the playlist indexer."""
    
    # Configuration
    DEVELOPER_TOKEN = "YOUR_DEVELOPER_TOKEN_HERE"  # Replace with your actual token
    PLAYLIST_URL = "https://music.apple.com/us/playlist/encapsulative/pl.u-BNA6rRRCemXeve6"
    
    # Check if developer token is provided
    if DEVELOPER_TOKEN == "YOUR_DEVELOPER_TOKEN_HERE":
        print("ERROR: Please set your Apple Music API developer token in the script.")
        print("You can get one from: https://developer.apple.com/documentation/applemusicapi/generating_developer_tokens")
        return
    
    # Create indexer instance
    indexer = AppleMusicPlaylistIndexer(DEVELOPER_TOKEN)
    
    # Index the playlist
    result_path = indexer.index_playlist(PLAYLIST_URL)
    
    if result_path:
        print(f"\n✅ Successfully indexed playlist!")
        print(f"📁 Data saved to: {result_path}")
        print(f"🖼️  Images saved to: {indexer.images_dir}")
        print(f"\nYou can now load the JSON file to analyze the playlist data.")
    else:
        print("\n❌ Failed to index playlist. Check the logs for details.")

if __name__ == "__main__":
    main() 