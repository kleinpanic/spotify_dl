import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import re

# Spotify API credentials
SPOTIFY_CLIENT_ID = 'e81422ea946d487ab3fb639c53e90543'
SPOTIFY_CLIENT_SECRET = 'e3346e44c4f842928e74892905dc78fe'

# Set up Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

def get_playlist_id(url):
    match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Spotify playlist URL")

def get_playlist_details(playlist_id):
    playlist = sp.playlist(playlist_id)
    tracks = playlist['tracks']['items']
    playlist_name = playlist['name']
    user_name = playlist['owner']['display_name']
    total_tracks = len(tracks)
    total_size = total_tracks * 5  # Approximation: each track is roughly 5 MB
    return playlist_name, user_name, total_tracks, total_size, tracks

def download_song_from_youtube(query, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch:{query}"])

def main():
    url = input("Enter the Spotify playlist URL: ")
    try:
        playlist_id = get_playlist_id(url)
    except ValueError as e:
        print(e)
        return

    playlist_name, user_name, total_tracks, total_size, tracks = get_playlist_details(playlist_id)
    size_units = "MB" if total_size < 1024 else "GB"
    total_size = total_size if total_size < 1024 else total_size / 1024

    print(f"Found playlist '{playlist_name}' by user '{user_name}'. It is {total_size:.2f} {size_units} in size.")
    confirm = input("Confirm? (y/n): ").lower()

    if confirm != 'y':
        print("Request cancelled.")
        return

    music_dir = os.path.expanduser("~/Music")
    playlist_dir = os.path.join(music_dir, playlist_name)

    if not os.path.exists(playlist_dir):
        os.makedirs(playlist_dir)

    print(f"Downloading '{playlist_name}'")

    for track in tracks:
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        search_query = f"{track_name} {artist_name} audio"
        print(f"Downloading: {track_name} by {artist_name}")
        download_song_from_youtube(search_query, playlist_dir)

if __name__ == "__main__":
    main()
