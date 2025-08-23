#!/usr/bin/env python3
"""
Streamlined playlist downloader for Spotify and SoundCloud.
Simplified version focused on core functionality.
"""

import os
import sys
import json
import time
import random
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp


def get_config_dir() -> Path:
    """Get the configuration directory for playback-tui."""
    config_dir = Path.home() / ".config" / "playback-tui"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_default_config_path(filename: str) -> str:
    """Get the default path for a config file."""
    return str(get_config_dir() / filename)


class PlaylistDownloader:
    """Handles downloading playlists from Spotify and SoundCloud."""
    
    def __init__(self, spotify_credentials: Dict[str, str]):
        """Initialize the downloader with Spotify credentials."""
        self.spotify_credentials = spotify_credentials
        self._setup_spotify_client()
        
        # User agents for rotation to avoid rate limiting
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]
        self.current_ua_index = 0
    
    def _setup_spotify_client(self):
        """Setup Spotify client with credentials."""
        try:
            # Set environment variables for Spotify
            os.environ['SPOTIPY_CLIENT_ID'] = self.spotify_credentials.get('SPOTIFY_CLIENT_ID', '')
            if os.environ['SPOTIPY_CLIENT_ID'] == "":
                raise Exception("No Spotify credentials found")
            os.environ['SPOTIPY_CLIENT_SECRET'] = self.spotify_credentials.get('SPOTIFY_CLIENT_SECRET', '')
            if os.environ['SPOTIPY_CLIENT_ID'] == "":
                raise Exception("No Spotify credentials found")
            
            self.spotify = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials()
            )
        except Exception as e:
            print(f"Failed to setup Spotify client: {e}")
            print(f"Passed Spotify credentials: {self.spotify_credentials}")
            self.spotify = None
    
    def _get_next_user_agent(self) -> str:
        """Get the next user agent in rotation."""
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return ua
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename to remove problematic characters."""
        # Remove or replace problematic characters
        filename = filename.replace("/", "_").replace("\\", "_")
        filename = "".join(c if c.isalnum() or c in "- " else "_" for c in filename)
        # Remove multiple consecutive underscores
        while "__" in filename:
            filename = filename.replace("__", "_")
        return filename.strip("_")
    
    def get_spotify_tracks(self, playlist_url: str) -> List[Dict]:
        """Get tracks from a Spotify playlist."""
        if not self.spotify:
            raise Exception("Spotify client not initialized")
        
        # Extract playlist ID from URL
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        
        print("Fetching Spotify playlist tracks...")
        results = self.spotify.playlist_tracks(playlist_id)
        tracks = results["items"]
        
        # Handle pagination
        while results["next"]:
            results = self.spotify.next(results)
            tracks.extend(results["items"])
        
        print(f"Found {len(tracks)} tracks in playlist")
        return tracks
    
    def _download_with_yt_dlp(self, search_term: str, output_path: str) -> bool:
        """Download a single track using yt-dlp."""
        # Set FFmpeg location in environment
        import shutil
        ffmpeg_path = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
        ffprobe_path = shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'
        
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": f"{output_path}.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "http_headers": {"User-Agent": self._get_next_user_agent()},
            "ffmpeg_location": ffmpeg_path,
        }
        
        # Also add to PATH as backup
        import os
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = f"/opt/homebrew/bin:{old_path}"
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch:{search_term}"])
                return True
        except Exception as e:
            print(f"Failed to download {search_term}: {e}")
            return False
        finally:
            # Restore original PATH
            os.environ['PATH'] = old_path
    
    def download_spotify_playlist(self, playlist_url: str, output_dir: str, 
                                 progress_callback=None) -> Dict[str, int]:
        """Download all tracks from a Spotify playlist."""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get tracks
        tracks = self.get_spotify_tracks(playlist_url)
        
        successful = 0
        failed = 0
        skipped = 0
        
        for i, item in enumerate(tracks):
            track = item.get("track")
            if not track:
                skipped += 1
                continue
            
            track_name = track["name"]
            artists = [artist["name"] for artist in track["artists"]]
            artist = artists[0]  # Use primary artist
            
            # Create safe filename
            safe_filename = self._clean_filename(f"{artist} - {track_name}")
            output_path = os.path.join(output_dir, safe_filename)
            
            # Check if file already exists
            if os.path.exists(f"{output_path}.mp3"):
                skipped += 1
                if progress_callback:
                    progress_callback(i + 1, len(tracks), f"Skipped: {artist} - {track_name}")
                continue
            
            if progress_callback:
                progress_callback(i + 1, len(tracks), f"Downloading: {artist} - {track_name}")
            
            # Try to download
            search_term = f"{artist} - {track_name}"
            success = self._download_with_yt_dlp(search_term, output_path)
            
            if success and os.path.exists(f"{output_path}.mp3"):
                successful += 1
                print(f"✓ Downloaded: {artist} - {track_name}")
            else:
                failed += 1
                print(f"✗ Failed: {artist} - {track_name}")
                # Log failed downloads
                with open(os.path.join(output_dir, "failed_downloads.txt"), "a") as f:
                    f.write(f"{artist} - {track_name}\n")
            
            # Small delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
        
        return {
            "total": len(tracks),
            "successful": successful,
            "failed": failed,
            "skipped": skipped
        }
    
    def download_soundcloud_likes(self, soundcloud_url: str, output_dir: str,
                                 progress_callback=None) -> Dict[str, int]:
        """Download SoundCloud likes."""
        # Import required modules
        import shutil
        import os
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        if progress_callback:
            progress_callback(0, 0, "Starting SoundCloud download...")
        
        # Set FFmpeg location
        ffmpeg_path = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
        
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "quiet": False,
            "ignoreerrors": True,
            "http_headers": {"User-Agent": self._get_next_user_agent()},
            "sleep_interval": 1,
            "max_sleep_interval": 3,
            "ffmpeg_location": ffmpeg_path,
        }
        
        # Add to PATH as backup
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = f"/opt/homebrew/bin:{old_path}"
        
        successful = 0
        
        def progress_hook(d):
            nonlocal successful
            if d['status'] == 'finished':
                successful += 1
                filename = d.get('filename', 'Unknown')
                track_title = os.path.basename(filename)
                if progress_callback:
                    progress_callback(successful, 0, f"Downloaded: {track_title}")
        
        ydl_opts['progress_hooks'] = [progress_hook]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([soundcloud_url])
        except Exception as e:
            print(f"SoundCloud download error: {e}")
        finally:
            # Restore original PATH
            os.environ['PATH'] = old_path
        
        return {
            "total": successful,
            "successful": successful,
            "failed": 0,
            "skipped": 0
        }


def download_playlist(playlist_name: str, settings_file: Optional[str] = None, 
                     spotify_env_file: Optional[str] = None,
                     progress_callback=None) -> bool:
    """
    Download a playlist by name using settings files.
    
    Args:
        playlist_name: Name of the playlist from settings
        settings_file: Path to playlist settings JSON file
        spotify_env_file: Path to Spotify credentials JSON file
        progress_callback: Optional callback function for progress updates
    
    Returns:
        True if download was successful, False otherwise
    """
    try:
        # Use default config paths if not provided
        settings_file = settings_file or get_default_config_path("playlist_settings.json")
        spotify_env_file = spotify_env_file or get_default_config_path("spotify_env.json")
        
        # Load playlist settings
        with open(settings_file, 'r') as f:
            playlists = json.load(f)
        
        if playlist_name not in playlists:
            print(f"Playlist '{playlist_name}' not found in settings")
            return False
        
        playlist_config = playlists[playlist_name]
        playlist_url = playlist_config["url"]
        output_dir = os.path.expanduser(playlist_config["directory"])
        
        # Load Spotify credentials
        with open(spotify_env_file, 'r') as f:
            spotify_credentials = json.load(f)
        
        # Initialize downloader
        downloader = PlaylistDownloader(spotify_credentials)
        
        print(f"Starting download for playlist: {playlist_name}")
        print(f"URL: {playlist_url}")
        print(f"Output directory: {output_dir}")
        
        # Download based on platform
        if "soundcloud.com" in playlist_url:
            results = downloader.download_soundcloud_likes(playlist_url, output_dir, progress_callback)
        else:  # Assume Spotify
            results = downloader.download_spotify_playlist(playlist_url, output_dir, progress_callback)
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"Download Complete for: {playlist_name}")
        print(f"Total tracks: {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped: {results['skipped']}")
        print(f"{'='*50}")
        
        return True
        
    except Exception as e:
        print(f"Error downloading playlist: {e}")
        return False


if __name__ == "__main__":
    # Command line usage
    if len(sys.argv) != 2:
        print("Usage: python downloader.py <playlist_name>")
        sys.exit(1)
    
    playlist_name = sys.argv[1]
    success = download_playlist(playlist_name)
    sys.exit(0 if success else 1)
