import os
import sys
import json
import requests
import base64
import argparse
from urllib.parse import urlencode

def get_credentials():
    client_id = input("Enter Spotify Client ID: ")
    client_secret = input("Enter Spotify Client Secret: ")
    return client_id, client_secret

def get_access_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(auth_url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Error obtaining token")
        sys.exit(1)

def find_remix(track_name, artist, token):
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": f"remix {track_name} {artist}", "type": "track", "limit": 1}
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        tracks = response.json()["tracks"]["items"]
        if tracks:
            return tracks[0]["id"]
    return None

def get_playlist_tracks(playlist_id, token):
    playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(playlist_url, headers=headers)
    if response.status_code == 200:
        return [item["track"] for item in response.json()["items"]]
    return []

def create_new_playlist(user_id, name, token):
    create_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps({"name": name, "public": False})
    response = requests.post(create_url, headers=headers, data=data)
    if response.status_code == 201:
        return response.json()["id"]
    return None

def add_tracks_to_playlist(playlist_id, track_ids, token):
    add_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps({"uris": [f"spotify:track:{tid}" for tid in track_ids]})
    requests.post(add_url, headers=headers, data=data)

def main():
    parser = argparse.ArgumentParser(description="Spotify Playlist Remixer")
    parser.add_argument("playlist_id", help="Spotify Playlist ID")
    parser.add_argument("user_id", help="Spotify User ID")
    args = parser.parse_args()

    client_id, client_secret = get_credentials()
    token = get_access_token(client_id, client_secret)
    tracks = get_playlist_tracks(args.playlist_id, token)
    remix_ids = []
    for track in tracks:
        remix_id = find_remix(track["name"], track["artists"][0]["name"], token)
        if remix_id:
            remix_ids.append(remix_id)
    new_playlist_id = create_new_playlist(args.user_id, "Remixed Playlist", token)
    if new_playlist_id:
        add_tracks_to_playlist(new_playlist_id, remix_ids, token)
        print(f"New playlist created: {new_playlist_id}")

if __name__ == "__main__":
    main()
