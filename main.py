import praw
import requests
import os
import re
from moviepy import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import edge_tts
import asyncio
import time
import json

# Reddit API credentials
REDDIT_CLIENT_ID = '???'  # Replace with your Reddit Client ID
REDDIT_CLIENT_SECRET = '???'  # Replace with your Reddit Client Secret
REDDIT_USER_AGENT = 'python:YTautomater:v1.0 (by u/Username)'  # Put your username 

# YouTube API credentials
YOUTUBE_CLIENT_SECRET_FILE = 'sercet-token.json'  # Put it in the same dir
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

LOG_FILE = 'processed_memes.log'

def load_processed_memes():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed_memes(processed_memes):
    with open(LOG_FILE, 'w') as f:
        json.dump(list(processed_memes), f)

async def generate_tts(text, output_file='output.mp3'):
    communicate = edge_tts.Communicate(text, voice='en-US-AriaNeural', rate='+30%', pitch='+10Hz')
    await communicate.save(output_file)

def scrape_reddit_memes(subreddit_name, limit=70, sort_methods=['hot', 'new', 'top', 'controversial']):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    subreddit = reddit.subreddit(subreddit_name)
    memes = []
    processed_memes = load_processed_memes()

    for sort_method in sort_methods:
        print(f"Fetching memes from '{sort_method}' feed...")
        last_post = None
        requests_made = 0

        while len(memes) < limit:
            batch = []
            try:
                if last_post:
                    submissions = getattr(subreddit, sort_method)(limit=100, params={'after': last_post})
                else:
                    submissions = getattr(subreddit, sort_method)(limit=100)
                
                for submission in submissions:
                    # Skip text-only posts and ensure URL ends with a valid media extension
                    if (not submission.is_self and 
                        submission.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')) and 
                        submission.id not in processed_memes):
                        meme = {
                            'title': submission.title,
                            'url': submission.url,
                            'file_extension': submission.url.split('.')[-1].lower(),
                            'id': submission.id
                        }
                        batch.append(meme)
                        processed_memes.add(submission.id)
                        if len(batch) + len(memes) >= limit:
                            break
                    last_post = submission.name
                
                memes.extend(batch)
                print(f"Fetched {len(batch)} memes from '{sort_method}'. Total memes so far: {len(memes)}")

                if len(batch) == 0:
                    print(f"No more memes found in '{sort_method}' feed.")
                    break

                requests_made += 1
                if requests_made % 500 == 0:  # Pause after 500 requests
                    print("Pausing for 60 seconds to stay within Reddit's rate limit...")
                    time.sleep(60)
            except Exception as e:
                print(f"Error fetching memes from '{sort_method}': {e}")
                break

        if len(memes) >= limit:
            break

    save_processed_memes(processed_memes)
    return memes[:limit]

def sanitize_filename(title):
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
    # Limit the filename length to avoid issues
    return sanitized[:50]  # Adjust the length as needed

def download_memes(memes, folder='memes'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for meme in memes:
        try:
            response = requests.get(meme['url'])
            # Sanitize the title to create a valid filename
            sanitized_title = sanitize_filename(meme['title'])
            file_path = f"{folder}/{sanitized_title}.{meme['file_extension']}"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            meme['file_path'] = file_path
        except Exception as e:
            print(f"Error downloading meme {meme['title']}: {e}")
            continue
    return memes

def compile_memes(memes, output_file='meme_compilation.mp4', duration_per_meme=3, resolution=(1920, 1080)):
    clips = []
    for meme in memes:
        try:
            if meme['file_extension'] in ['jpg', 'jpeg', 'png']:
                clip = ImageClip(meme['file_path']).with_duration(duration_per_meme).resized(resolution)
                tts_audio = AudioFileClip(f"audio_{meme['id']}.mp3")
                clip = clip.with_audio(tts_audio)
                clips.append(clip)
            elif meme['file_extension'] in ['gif', 'mp4']:
                clip = VideoFileClip(meme['file_path']).resized(resolution)
                tts_audio = AudioFileClip(f"audio_{meme['id']}.mp3")
                clip = clip.with_audio(CompositeAudioClip([clip.audio, tts_audio]) if clip.audio else tts_audio)
                clips.append(clip)
        except Exception as e:
            print(f"Error processing meme {meme['title']}: {e}")
            continue

    if not clips:
        print("No valid clips found to compile.")
        return

    final_clip = concatenate_videoclips(clips, method="compose")
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
    for meme in memes:
        print(f"Generating TTS for: {meme['title']}")
        asyncio.run(generate_tts(meme['title'], f"audio_{meme['id']}.mp3"))

def main():
    subreddit_name = 'dankmemes' 
    sort_methods = ['hot', 'new', 'top', 'controversial']  
    memes = scrape_reddit_memes(subreddit_name, limit=70, sort_methods=sort_methods)
    memes = download_memes(memes)
    process_tts_for_memes(memes)
    video_file = 'meme_compilation.mp4'
    compile_memes(memes, video_file, duration_per_meme=3)
    title = 'Top 60 Memes of the Week | Reddit Meme Compilation'
    description = 'Check out these hilarious memes from Reddit!'
    tags = [
        'memes', 'Reddit', 'meme compilation', 'funny', 'dankmemes',
        'dankmemesdaily', 'dankmemesonly', 'dankmemescomp', 'dankmemes4life',
        'epicmemes', 'goodmemes', 'funnymemes', 'spicymemes', 'viralmemes',
        'bestmemes', 'hilariousmemes', 'memesfordays', 'memesdaily',
        'memestagram', 'memecompilation', 'memelord', 'relatablememes',
        'funniestmemes', 'randommemes', 'memeworld', 'memesarelife',
        'internetmemes', 'memeculture', 'viralcontent', 'funnyvideos',
        'trendingmemes', 'memezone', 'dankmemecompilation', 'comedyclips',
        'laughchallenge', 'memefan', 'memecollection', 'memefest', 'sillymemes',
        'memehype', 'jokes', 'humorclips', 'classicmemes', 'memecomp',
        'foryou', 'foryoupage', 'memeentertainment', 'lolmemes', 'laughoutloud'
    ]


    upload_to_youtube(video_file, title, description, tags)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print(f"Process completed in {time.time() - start_time} seconds")
