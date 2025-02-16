import praw
import requests
import os
from moviepy import *
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys

# Reddit API credentials
REDDIT_CLIENT_ID = '????'  # Replace with your Reddit Client ID
REDDIT_CLIENT_SECRET = '????'  # Replace with your Reddit Client Secret
REDDIT_USER_AGENT = 'youruseragent (by u/yourusername)'  # Replace with your User Agent

# YouTube API credentials
YOUTUBE_CLIENT_SECRET_FILE = 'sercet_token.json'  # download your youtube api key token and put it here in the same dir
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Step 1: Scrape Reddit Meme Posts
def scrape_reddit_memes(subreddit_name, limit=29):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    subreddit = reddit.subreddit(subreddit_name)
    memes = []
    for submission in subreddit.hot(limit=limit):
        if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')):
            memes.append({
                'title': submission.title,
                'url': submission.url,
                'file_extension': submission.url.split('.')[-1]
            })
    return memes

# Step 2: Download Memes
def download_memes(memes, folder='memes'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for meme in memes:
        response = requests.get(meme['url'])
        file_path = f"{folder}/{meme['title']}.{meme['file_extension']}"
        with open(file_path, 'wb') as f:
            f.write(response.content)
        meme['file_path'] = file_path
    return memes

# Step 3: Put all memes into a vid
def compile_memes(memes, output_file='meme_compilation.mp4', duration_per_meme=5, resolution=(1920, 1080)):
    clips = []
    for meme in memes:
        if meme['file_extension'] in ['jpg', 'jpeg', 'png']:
            # For images, create a clip with a fixed duration and resize to the resolution
            clip = ImageClip(meme['file_path']).with_duration(duration_per_meme).resized(resolution)
        elif meme['file_extension'] in ['gif', 'mp4']:
            # For videos, resize to the resolution
            clip = VideoFileClip(meme['file_path']).resized(resolution)
        clips.append(clip)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Add background music
    background_music = AudioFileClip("background_music.mp3")  # Use the one that came with it or use your own one
    final_clip = final_clip.with_audio(background_music)

    # Save the final video
    final_clip.write_videofile(output_file, fps=24)


# Step 4: Upload Video to YouTube
def upload_to_youtube(video_file, title, description, tags, category_id='22'):
    # Authenticate with YouTube API
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', YOUTUBE_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

    # Upload the video
    request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': 'public' 
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    print(f'Video uploaded! Video ID: {response["id"]}')

# Main Function
def main():
    # Step 1: Scrape Reddit Meme Posts
    subreddit_name = 'memes'  # Change to your desired subreddit
    memes = scrape_reddit_memes(subreddit_name, limit=29)

    # Step 2: Download Memes
    memes = download_memes(memes)

    # Step 3: Compile Memes into a Video
    video_file = 'meme_compilation.mp4'
    compile_memes(memes, video_file, duration_per_meme=5) # How many secs does meme stay on for

    # Step 4: Upload to YouTube
    title = 'Top 20 Memes of the Week | Reddit Meme Compilation'
    description = 'Check out these hilarious memes from Reddit!'
    tags = ['memes', 'Reddit', 'meme compilation']
    #os.execv(sys.executable, ['python3', 'upload.py'] + sys.argv[1:])
    upload_to_youtube(video_file, title, description, tags)
    

if __name__ == '__main__':
    main()
