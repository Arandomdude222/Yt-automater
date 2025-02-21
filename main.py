import praw
import requests
import os
import sys
import time
from moviepy import *
from edge_tts import Communicate
import asyncio
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Reddit API credentials
REDDIT_CLIENT_ID = '???' # fill the ???
REDDIT_CLIENT_SECRET = '???'
REDDIT_USER_AGENT = 'python:MyYouTubeAutomation:v1.0 (by u/USERNAME)'# put your username

# YouTube API credentials
YOUTUBE_CLIENT_SECRET_FILE = 'sercet-token.json' # make sure you downloaded your client token file and put it in the same dir
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def scrape_reddit_memes(subreddit_name, limit):
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

def collect_memes():
    all_memes = []
    all_memes.extend(scrape_reddit_memes('memes', 30))
    time.sleep(60)
    all_memes.extend(scrape_reddit_memes('memes', 20))
    time.sleep(60)
    all_memes.extend(scrape_reddit_memes('memes', 20))
    return all_memes

def download_memes(memes, folder='current_memes', used_folder='memes'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(used_folder):
        os.makedirs(used_folder)
    
    new_memes = []
    for meme in memes:
        safe_title = ''.join(c if c.isalnum() or c in " -_" else "_" for c in meme['title'])
        file_path = f"{folder}/{safe_title}.{meme['file_extension']}"
        used_path = f"{used_folder}/{safe_title}.{meme['file_extension']}"
        
        if os.path.exists(used_path):
            continue
        
        response = requests.get(meme['url'])
        with open(file_path, 'wb') as f:
            f.write(response.content)
        meme['file_path'] = file_path
        new_memes.append(meme)
    
    return new_memes

def move_to_used(memes, folder='current_memes', used_folder='memes'):
    for meme in memes:
        os.rename(meme['file_path'], f"{used_folder}/{os.path.basename(meme['file_path'])}")
    
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))

def generate_tts(text, output_file):
    communicate = Communicate(text, voice="en-US-AriaNeural")
    asyncio.run(communicate.save(output_file))

def generate_all_tts(memes, folder='tts'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for meme in memes:
        safe_title = ''.join(c if c.isalnum() or c in " -_" else "_" for c in meme['title'])
        tts_path = f"{folder}/{safe_title}.mp3"
        generate_tts(meme['title'], tts_path)
        meme['tts_path'] = tts_path
    return memes

def compile_memes(memes, output_file='meme_compilation.mp4', duration_per_meme=2, resolution=(1920, 1080)):
    clips = []
    for meme in memes:
        if meme['file_extension'] in ['jpg', 'jpeg', 'png']:
            clip = ImageClip(meme['file_path']).with_duration(duration_per_meme).resize(resolution)
        elif meme['file_extension'] in ['gif', 'mp4']:
            clip = VideoFileClip(meme['file_path']).resize(resolution)
        audio_clip = AudioFileClip(meme['tts_path'])
        clip = clip.set_audio(audio_clip)
        clips.append(clip)
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_file, fps=24)

def main():
    memes = collect_memes()
    memes = download_memes(memes)
    memes = generate_all_tts(memes)
    video_file = 'meme_compilation.mp4'
    compile_memes(memes, video_file, duration_per_meme=2)
    move_to_used(memes)
    os.execv(sys.executable, ['python3', 'noob.py'] + sys.argv[1:])

if __name__ == '__main__':
    main()
