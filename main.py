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
import pytesseract
from PIL import Image
import edge_tts
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import json

# Reddit API credentials
REDDIT_CLIENT_ID = 'pt-JR8zhqvg1H_mKZRlQPQ'  # Replace with your Reddit Client ID
REDDIT_CLIENT_SECRET = '53p50OUUOZ9TL83x_eK5kuSvQloG-w'  # Replace with your Reddit Client Secret
REDDIT_USER_AGENT = 'python:MyYouTubeAutomation:v1.0 (by u/Nice-Preparation-804)'  # Replace with your User Agent

# YouTube API credentials
YOUTUBE_CLIENT_SECRET_FILE = '/home/zay/python-projects11/yt=automater/sercet-token.json'  # Path to your YouTube API credentials file
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

LOG_FILE = 'processed_memes.log'

if not os.path.exists('tts'):
    os.makedirs('tts')

def load_processed_memes():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed_memes(processed_memes):
    with open(LOG_FILE, 'w') as f:
        json.dump(list(processed_memes), f)


async def generate_tts(text, output_file='output.mp3'):
    output_path = os.path.join('tts', output_file)
    communicate = edge_tts.Communicate(text, voice='en-US-AriaNeural', rate='+30%', pitch='+10Hz')
    await communicate.save(output_path)
    print(f"Saved TTS file to: {output_path}")

def scrape_reddit_memes(subreddit_name, limit=60):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    subreddit = reddit.subreddit(subreddit_name)
    memes = []
    last_post = None
    requests_made = 0
    processed_memes = load_processed_memes()

    for i in range(0, limit, 30):
        batch = []
        if last_post:
            submissions = subreddit.hot(limit=30, params={'after': last_post})
        else:
            submissions = subreddit.hot(limit=30)
        
        for submission in submissions:
            if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')):
                if submission.url not in processed_memes:
                    batch.append({
                        'title': submission.title,
                        'url': submission.url,
                        'file_extension': submission.url.split('.')[-1],
                        'id': submission.id
                    })
                    processed_memes.add(submission.url)
            last_post = submission.name
        
        memes.extend(batch)
        print(f"Fetched {len(batch)} memes.")

        requests_made += 1
        if requests_made % 10 == 0:
            print("Pausing for 28 seconds to stay within Reddit's rate limit...")
            time.sleep(28)
        
        if len(batch) == 30:
            time.sleep(28)

    save_processed_memes(processed_memes)
    return memes

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

def compile_memes(memes, output_file='meme_compilation.mp4', duration_per_meme=3, resolution=(1920, 1080)):
    clips = []
    for meme in memes:
        try:
            if meme['file_extension'] in ['jpg', 'jpeg', 'png']:
                clip = ImageClip(meme['file_path']).with_duration(duration_per_meme).resized(resolution)
                clips.append(clip)
            elif meme['file_extension'] in ['gif', 'mp4']:
                if meme['file_extension'] == 'gif':
                    try:
                        clip = VideoFileClip(meme['file_path'], codec='gif').resized(resolution)
                    except OSError:
                        print(f"Skipping corrupt GIF: {meme['file_path']}")
                        continue
                else:
                    clip = VideoFileClip(meme['file_path']).resized(resolution)
                clips.append(clip)
        except Exception as e:
            print(f"Error processing meme {meme['title']}: {e}")
            continue

    if not clips:
        print("No valid clips found to compile.")
        return

    final_clip = concatenate_videoclips(clips, method="compose")
    background_music = AudioFileClip("background_music.mp3")
    final_clip = final_clip.with_audio(background_music)
    final_clip.write_videofile(output_file, fps=24)

def upload_to_youtube(video_file, title, description, tags, category_id='22'):
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

def process_tts_for_memes(memes):
    with ThreadPoolExecutor() as executor:
        futures = []
        for meme in memes:
            print(f"Reading title: {meme['title']}")
            futures.append(executor.submit(asyncio.run, generate_tts(meme['title'], f"audio_{meme['title']}.mp3")))
        
        for future in futures:
            future.result()

def main():
    subreddit_name = 'memes'
    memes = scrape_reddit_memes(subreddit_name, limit=60)
    process_tts_for_memes(memes)
    memes = download_memes(memes)
    video_file = 'meme_compilation.mp4'
    compile_memes(memes, video_file, duration_per_meme=3)
    title = 'Top 60 Memes of the Week | Reddit Meme Compilation'
    description = 'Check out these hilarious memes from Reddit!'
    tags = ['memes', 'Reddit', 'meme compilation', 'AskReddit']
    upload_to_youtube(video_file, title, description, tags)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print(f"Process completed in {time.time() - start_time} seconds")
