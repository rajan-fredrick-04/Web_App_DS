import requests
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from googleapiclient.discovery import build
from spotipy.oauth2 import SpotifyOAuth  
import isodate

# Load environment variables
load_dotenv()

# Spotify API setup
client_id = "dbdbfd0bf6e84619b52f6016f427a2b6"
client_secret = "efbb6ddbec774d5483c8ce6ec916d8bb"
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# YouTube API key
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

apikey='AIzaSyCyXV-yIVrkJn7fz6HmSfgluitwg01cosQ'
# Function to get YouTube videos by keyword
def youtube_search(api_key, query, max_results=5, initial_results=30):
    # Build the YouTube service
    print("Building YouTube service...")
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Call the search.list method to perform a search, retrieving a larger set of initial results
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        type='video',
        maxResults=initial_results
    ).execute()

    # Collect the search results
    results = []
    video_ids = []

    for item in search_response.get('items', []):
        video_id = item['id'].get('videoId')
        if video_id:
            video_ids.append(video_id)

    if video_ids:
        # Get video details including duration
        video_response = youtube.videos().list(
            id=','.join(video_ids),
            part='contentDetails'
        ).execute()

        for i, video in enumerate(video_response.get('items', [])):
            duration = video['contentDetails']['duration']
            duration_seconds = isodate.parse_duration(duration).total_seconds()

            # Only consider videos longer than 100 seconds
            if duration_seconds > 100:
                title = search_response['items'][i]['snippet']['title']
                thumbnails = search_response['items'][i]['snippet'].get('thumbnails', {})
                video_id = video_ids[i]  # Extract just the video ID

                # Select the best available thumbnail
                if 'maxres' in thumbnails:
                    thumbnail_url = thumbnails['maxres']['url']
                elif 'standard' in thumbnails:
                    thumbnail_url = thumbnails['standard']['url']
                elif 'high' in thumbnails:
                    thumbnail_url = thumbnails['high']['url']
                elif 'medium' in thumbnails:
                    thumbnail_url = thumbnails['medium']['url']
                else:
                    thumbnail_url = thumbnails.get('default', {}).get('url', '')

                # Append the title, thumbnail URL, and video ID (not full link)
                results.append({
                    'title': title,
                    'thumbnail': thumbnail_url,
                    'video_id': video_id  # Store the video ID alone
                })
                print(f"Appended result - Title: {title}, Thumbnail: {thumbnail_url}, Video ID: {video_id}")

                # Stop once we have enough results
                if len(results) >= max_results:
                    break

    # Final results
    return results


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
