#!/usr/bin/env python3
"""
Example Usage Script

This script demonstrates how to use both the Spotify and Apple Music playlist indexers
and analyze the results.
"""

import json
from pathlib import Path
from spotify_playlist_indexer import SpotifyPlaylistIndexer
from apple_music_playlist_indexer import AppleMusicPlaylistIndexer

def index_spotify_playlist():
    """Example of indexing a Spotify playlist."""
    
    print("🎵 SPOTIFY PLAYLIST INDEXING EXAMPLE")
    print("=" * 50)
    
    # Your Spotify API credentials
    CLIENT_ID = "YOUR_CLIENT_ID_HERE"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
    
    # Example playlists (replace with your own)
    playlists = [
        "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",  # Today's Top Hits
        "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd",  # RapCaviar
        "https://open.spotify.com/playlist/37i9dQZF1DXcF6B6QPhFDv",  # Rock Classics
    ]
    
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print("❌ Please set your Spotify API credentials first!")
        return
    
    try:
        indexer = SpotifyPlaylistIndexer(CLIENT_ID, CLIENT_SECRET)
        
        for playlist_url in playlists:
            print(f"\n🎵 Indexing: {playlist_url}")
            result = indexer.index_playlist(playlist_url)
            
            if result:
                print(f"✅ Success! Data saved to: {result}")
            else:
                print(f"❌ Failed to index playlist")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def index_apple_music_playlist():
    """Example of indexing an Apple Music playlist."""
    
    print("\n🍎 APPLE MUSIC PLAYLIST INDEXING EXAMPLE")
    print("=" * 50)
    
    # Your Apple Music API developer token
    DEVELOPER_TOKEN = "YOUR_DEVELOPER_TOKEN_HERE"
    
    # Example playlists (replace with your own)
    playlists = [
        "https://music.apple.com/us/playlist/encapsulative/pl.u-BNA6rRRCemXeve6",  # Your example playlist
        "https://music.apple.com/us/playlist/todays-hits/pl.f4d106fed2bd41149aaacabb233eb5eb",  # Today's Hits
    ]
    
    if DEVELOPER_TOKEN == "YOUR_DEVELOPER_TOKEN_HERE":
        print("❌ Please set your Apple Music API developer token first!")
        return
    
    try:
        indexer = AppleMusicPlaylistIndexer(DEVELOPER_TOKEN)
        
        for playlist_url in playlists:
            print(f"\n🍎 Indexing: {playlist_url}")
            result = indexer.index_playlist(playlist_url)
            
            if result:
                print(f"✅ Success! Data saved to: {result}")
            else:
                print(f"❌ Failed to index playlist")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def compare_platforms():
    """Compare data from both platforms."""
    
    print("\n📊 PLATFORM COMPARISON")
    print("=" * 50)
    
    data_dir = Path('playlist_data')
    
    if not data_dir.exists():
        print("❌ No playlist data found. Run the indexers first!")
        return
    
    spotify_files = list(data_dir.glob('spotify_playlist_*.json'))
    apple_files = list(data_dir.glob('playlist_pl.*.json'))
    
    print(f"📊 Found {len(spotify_files)} Spotify playlists")
    print(f"📊 Found {len(apple_files)} Apple Music playlists")
    
    # Compare features
    print("\n📋 FEATURE COMPARISON:")
    print("Feature                    | Spotify | Apple Music")
    print("---------------------------|---------|------------")
    print("Audio Features            | ✅      | ❌         ")
    print("Popularity Scores         | ✅      | ❌         ")
    print("ISRC Codes               | ❌      | ✅         ")
    print("Genre Information        | ❌      | ✅         ")
    print("Preview URLs             | ✅      | ✅         ")
    print("High-res Artwork         | ✅      | ✅         ")
    print("Setup Complexity         | Easy    | Complex    ")
    print("API Cost                 | Free    | $99/year   ")
    
    # Show sample data structures
    if spotify_files:
        print(f"\n🎵 SPOTIFY SAMPLE DATA:")
        with open(spotify_files[0], 'r') as f:
            spotify_data = json.load(f)
            playlist_name = spotify_data['playlist_metadata']['name']
            track_count = spotify_data['summary']['total_tracks']
            print(f"   Playlist: {playlist_name}")
            print(f"   Tracks: {track_count}")
            
            # Show first track structure
            if spotify_data['tracks']:
                track = spotify_data['tracks'][0]
                print(f"   Sample track keys: {list(track.keys())[:8]}...")
    
    if apple_files:
        print(f"\n🍎 APPLE MUSIC SAMPLE DATA:")
        with open(apple_files[0], 'r') as f:
            apple_data = json.load(f)
            playlist_name = apple_data['playlist_metadata']['name']
            track_count = apple_data['summary']['total_tracks']
            print(f"   Playlist: {playlist_name}")
            print(f"   Tracks: {track_count}")
            
            # Show first track structure
            if apple_data['tracks']:
                track = apple_data['tracks'][0]
                print(f"   Sample track keys: {list(track.keys())[:8]}...")

def quick_analysis():
    """Quick analysis of indexed playlists."""
    
    print("\n🔍 QUICK ANALYSIS")
    print("=" * 50)
    
    data_dir = Path('playlist_data')
    json_files = list(data_dir.glob('*.json'))
    
    for json_file in json_files:
        print(f"\n📂 Analyzing: {json_file.name}")
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        metadata = data['playlist_metadata']
        summary = data['summary']
        
        print(f"   📋 Name: {metadata['name']}")
        print(f"   📊 Tracks: {summary['total_tracks']}")
        print(f"   ⏱️  Duration: {summary.get('total_duration_hours', 0):.1f} hours")
        print(f"   🎤 Artists: {summary.get('unique_primary_artists', summary.get('unique_artists', 0))}")
        print(f"   💿 Albums: {summary.get('unique_albums', 0)}")
        
        # Platform-specific info
        if 'average_popularity' in summary:
            print(f"   ⭐ Avg Popularity: {summary['average_popularity']:.1f}")
        if 'genres' in summary:
            print(f"   🎵 Genres: {len(summary['genres'])}")

def main():
    """Main function demonstrating all functionality."""
    
    print("🎵 MUSIC PLAYLIST INDEXER - EXAMPLE USAGE")
    print("=" * 60)
    
    print("\n👋 Welcome! This script demonstrates how to use both indexers.")
    print("Before running, make sure you have:")
    print("1. 🎵 Spotify API credentials (free)")
    print("2. 🍎 Apple Music API token (requires $99/year developer account)")
    print("3. 📦 Installed requirements: pip install -r requirements.txt")
    
    print("\n🔧 What this script does:")
    print("- Index playlists from both platforms")
    print("- Compare features and data structures")
    print("- Perform quick analysis")
    print("- Show you what's possible!")
    
    # Uncomment the functions you want to test:
    
    # index_spotify_playlist()        # Index Spotify playlists
    # index_apple_music_playlist()    # Index Apple Music playlists
    compare_platforms()               # Compare features
    quick_analysis()                  # Quick analysis of existing data
    
    print("\n🎯 Next steps:")
    print("1. Edit the credentials in this script")
    print("2. Uncomment the indexing functions you want to use")
    print("3. Run: python example_usage.py")
    print("4. Analyze results with: python analyze_playlist.py")
    
    print("\n✨ Happy music analyzing! 🎵")

if __name__ == "__main__":
    main() 