import requests
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from googleapiclient.discovery import build
from spotipy.oauth2 import SpotifyOAuth  
import isodate



client_id = "dbdbfd0bf6e84619b52f6016f427a2b6"
client_secret = "efbb6ddbec774d5483c8ce6ec916d8bb"
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# YouTube API key
# Quotable API Base URL
QUOTABLE_BASE_URL = 'https://api.api-ninjas.com/v1/quotes'

# Function to get Spotify songs by genre
def get_songs_by_genre(genre):
    results = sp.search(q='genre:' + genre, type='track', limit=5)
    tracks = results['tracks']['items']
    
    track_info = [{'id': track['id'], 'name': track['name']} for track in tracks]
    
    return track_info

# Function to get quotes by tag
def get_quotes_by_tag(tag):
    params = {'category': tag, 'limit': 5}  # Note the change to 'category'
    headers = {'X-Api-Key': 'YOUR_API_KEY'}  # Replace with your actual API key
    response = requests.get(QUOTABLE_BASE_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        quotes = response.json()  # Directly get the list of quotes
        return quotes
    else:
        print(f"Error: {response.status_code}")
        return []
    
res=get_songs_by_genre("happy")
print(res)