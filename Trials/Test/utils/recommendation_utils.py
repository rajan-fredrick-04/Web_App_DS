import requests
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Spotify API setup
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# YouTube API key
#YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_KEY ='AIzaSyCyXV-yIVrkJn7fz6HmSfgluitwg01cosQ'
# Quotable API Base URL
QUOTABLE_BASE_URL = 'https://api.api-ninjas.com/v1/quotes'

# Emotion-based keyword mapping for recommendations
emotion_keywords = {
    'happy': 'comedy sketches',
    'sad': 'motivational videos',
    'angry': 'relaxing meditation',
    'neutral': 'inspiring talks'
}

emotion_genres_music = {
    'happy': 'pop',
    'sad': 'acoustic',
    'angry': 'classical',
    'neutral': 'chill'
}

emotion_tags_quotes = {
    'happy': 'happiness',
    'sad': 'motivational',
    'angry': 'calm',
    'neutral': 'life'
}

# Function to get YouTube videos by keyword
def get_videos_by_keyword(keyword):
    # Build the YouTube service object
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    # Execute the search request
    request = youtube.search().list(
        part='snippet',
        q=keyword,
        type='video',
        maxResults=5
    )
    response = request.execute()
    
    # Return the list of video items
    return response['items']

# Function to get Spotify songs by genre
def get_songs_by_genre(genre):
    results = sp.search(q='genre:' + genre, type='track', limit=5)
    tracks = results['tracks']['items']
    return tracks

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
