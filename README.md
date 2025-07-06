# Music Playlist Indexer

This repository contains Python scripts that index music playlists from streaming platforms, download artwork images for each track, and save all metadata as JSON files generated from pandas DataFrames.

## 🎵 Available Platforms

### **Spotify** (Recommended - Easier Setup)
- ✅ **Free** - No paid developer program required
- ✅ **Simple setup** - Just need Client ID + Client Secret
- ✅ **Rich audio features** - Includes danceability, energy, valence, tempo, etc.
- ✅ **Better rate limits** - More generous API access

### **Apple Music**
- ⚠️ **Requires $99/year** Apple Developer Program
- ⚠️ **Complex setup** - JWT token generation required
- ✅ **High-quality metadata** - Official Apple Music catalog data
- ✅ **High-resolution artwork** - Up to 1200x1200 pixels

## 🚀 Quick Start (Spotify)

1. **Get Spotify API credentials** (Free!):
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app (any name/description)
   - Copy your Client ID and Client Secret

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure and run**:
   ```bash
   # Edit spotify_playlist_indexer.py
   # Replace YOUR_CLIENT_ID_HERE and YOUR_CLIENT_SECRET_HERE
   # Replace PLAYLIST_URL with your desired playlist
   
   python spotify_playlist_indexer.py
   ```

## 📋 Features

### Common Features (Both Platforms)
- 📋 Complete playlist metadata
- 🎵 Detailed track information (name, artist, album, duration, etc.)
- 🖼️ High-resolution artwork download
- 📊 Pandas DataFrame integration
- 💾 Structured JSON output
- 📈 Summary statistics

### Spotify Exclusive Features
- 🎛️ **Audio features** - Danceability, energy, valence, tempo, acousticness, etc.
- 📊 **Popularity scores** - Track popularity metrics
- 🔍 **Enhanced metadata** - More detailed track and album information
- ⚡ **Faster processing** - Better rate limits

### Apple Music Exclusive Features
- 🎤 **ISRC codes** - International Standard Recording Codes
- 📱 **Preview URLs** - 30-second track previews
- 🏷️ **Content ratings** - Explicit content flags
- 📅 **Precise release dates** - More accurate release information

## 📂 Output Structure

Both scripts generate similar JSON structures:

```json
{
  "playlist_metadata": {
    "id": "playlist_id",
    "name": "Playlist Name",
    "description": "Playlist description",
    "owner": "owner_name",
    "track_count": 150,
    "url": "original_playlist_url"
  },
  "tracks": [
    {
      "index": 1,
      "id": "track_id",
      "name": "Track Name",
      "artist_name": "Artist Name",
      "album_name": "Album Name",
      "duration_ms": 240000,
      "release_date": "2023-01-01",
      "popularity": 75,
      "explicit": false,
      "preview_url": "https://...",
      "artwork_url": "https://...",
      "artwork_local_path": "playlist_images/001_Artist_Track.jpg",
      "audio_features": {  // Spotify only
        "danceability": 0.8,
        "energy": 0.9,
        "valence": 0.7,
        "tempo": 128.0
      }
    }
  ],
  "summary": {
    "total_tracks": 150,
    "total_duration_ms": 36000000,
    "total_duration_hours": 10.0,
    "unique_artists": 89,
    "unique_albums": 120,
    "average_popularity": 65.5,
    "indexed_at": "2024-01-15T14:30:00.000Z"
  }
}
```

## 🔧 Setup Instructions

### Spotify Setup (Recommended)

1. **Create Spotify App**:
   - Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click "Create an App"
   - Fill in app name and description (anything works)
   - Copy the Client ID and Client Secret

2. **Configure Script**:
   - Open `spotify_playlist_indexer.py`
   - Replace `YOUR_CLIENT_ID_HERE` with your Client ID
   - Replace `YOUR_CLIENT_SECRET_HERE` with your Client Secret
   - Replace `PLAYLIST_URL` with your desired Spotify playlist URL

3. **Run**:
   ```bash
   python spotify_playlist_indexer.py
   ```

### Apple Music Setup

1. **Join Apple Developer Program** ($99/year):
   - Visit [developer.apple.com](https://developer.apple.com)
   - Sign up for the Apple Developer Program

2. **Generate Developer Token**:
   - Follow [Apple's guide](https://developer.apple.com/documentation/applemusicapi/generating_developer_tokens)
   - Create a MusicKit identifier
   - Generate a private key
   - Create a JWT token

3. **Configure Script**:
   - Open `apple_music_playlist_indexer.py`
   - Replace `YOUR_DEVELOPER_TOKEN_HERE` with your JWT token
   - Replace `PLAYLIST_URL` with your Apple Music playlist URL

4. **Run**:
   ```bash
   python apple_music_playlist_indexer.py
   ```

## 📊 Analysis Tools

Use the included analysis script to explore your data:

```bash
python analyze_playlist.py
```

This will generate:
- 📈 Track duration distribution
- 🎤 Top artists charts
- 📅 Release year timeline
- 🎵 Audio features analysis (Spotify only)
- 📊 Summary statistics

## 🎯 Use Cases

- **Music Research** - Analyze playlist compositions and trends
- **DJ Tools** - Get BPM, key, and energy data for mixing
- **Playlist Backup** - Create local copies of your favorite playlists
- **Music Discovery** - Find patterns in your listening habits
- **Data Science** - Music recommendation algorithms
- **Artwork Collection** - Download high-quality album artwork

## 🛠️ Customization

Both scripts are highly customizable:
- Change output formats (CSV, Excel, etc.)
- Add custom metadata fields
- Modify artwork resolution
- Implement different storage backends
- Add visualization features

## 📝 Notes

- **Rate Limiting**: Both scripts include respectful delays between requests
- **Error Handling**: Graceful handling of missing tracks or network issues
- **File Naming**: Automatic sanitization of filenames for cross-platform compatibility
- **Pagination**: Handles playlists of any size automatically
- **Logging**: Detailed logging for debugging and monitoring

## 🔗 API Documentation

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Apple Music API](https://developer.apple.com/documentation/applemusicapi/)

## 📄 License

This project is for educational and personal use. Please respect the terms of service of both Spotify and Apple Music APIs.

## 🤝 Contributing

Feel free to contribute improvements, bug fixes, or additional platform support!