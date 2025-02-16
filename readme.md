# Reddit Meme Compilation to YouTube

This tool allows you to automatically scrape memes from Reddit, compile them into a video, and upload the video to YouTube. It’s perfect for creating meme compilations with minimal effort!

---

## 🛠️ Installation

### Step 1: Install Python
Make sure you have **Python 3.x** installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Step 2: Download the Script
1. Download the script files from the repository.
2. Place the files in a folder on your computer.

### Step 3: Install Required Libraries
Open a terminal or command prompt in the folder where the script is located and run the following command to install the required libraries:

```bash
pip install praw requests moviepy google-api-python-client google-auth-oauthlib google-auth

# 🔑 Setting Up API Credentials
# Reddit API

    Go to Reddit's Developer Portal and create a new application.
    Copy the Client ID, Client Secret, and set a User Agent (e.g., YourAppName (by u/YourRedditUsername)).
    Open the script (main.py) and replace the following placeholders with your Reddit API credentials:

REDDIT_CLIENT_ID = 'your_client_id'
REDDIT_CLIENT_SECRET = 'your_client_secret'
REDDIT_USER_AGENT = 'your_user_agent'

# YouTube API

    Go to the Google Cloud Console.
    Create a new project and enable the YouTube Data API v3.
    Download the credentials.json file and place it in the same folder as the script.
    Rename the file to secret_token.json.

# 🚀 How to Use

    Open the script (main.py) in a text editor.
    Customize the following settings (optional):
        Subreddit Name: Change subreddit_name to the subreddit you want to scrape (default is memes).
        Video Title, Description, and Tags: Modify these in the main() function.
        Background Music: Replace background_music.mp3 with your own music file (optional).
    Run the script:

python main.py

 # The script will:

    Scrape memes from the specified subreddit.
    Download the memes to a folder named memes.
    Compile the memes into a video (meme_compilation.mp4).
    Upload the video to YouTube.

# ⚙️ Configuration Options

    Video Duration per Meme: Adjust the duration_per_meme parameter in the compile_memes function to control how long each meme stays on screen.
    Video Resolution: Change the resolution parameter in the compile_memes function to set the video resolution (default is 1920x1080).
    Privacy Settings: Modify the privacyStatus in the upload_to_youtube function to set the video privacy (public, private, or unlisted).

# ❓ Frequently Asked Questions

Q: Where are the downloaded memes stored?

A: The memes are saved in a folder named memes in the same directory as the script.

Q: Can I change the background music?

A: Yes! Replace the background_music.mp3 file with your own music file.

Q: How do I change the subreddit?

A: Modify the subreddit_name variable in the main() function to the subreddit you want to scrape.
# 📜 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as you see fit.
# 🙏 Acknowledgments

    PRAW for Reddit API access.
    MoviePy for video editing.
    Google API Client Library for YouTube API access.

Enjoy creating your meme compilations! If you have any questions or issues, feel free to open an issue on the repository.


This should work perfectly as a GitHub README file. Let me know if you'd like any changes! 😊

You said:
stop missign parts keep thinking ur writing ur message in a file
ChatGPT said:

Got it! Here's the full Markdown for your README with all parts included as requested:

# Reddit Meme Compilation to YouTube

This tool allows you to automatically scrape memes from Reddit, compile them into a video, and upload the video to YouTube. It’s perfect for creating meme compilations with minimal effort!

---

# 🛠️ Installation

### Step 1: Install Python
Make sure you have **Python 3.x** installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Step 2: Download the Script
1. Download the script files from the repository.
2. Place the files in a folder on your computer.

### Step 3: Install Required Libraries
Open a terminal or command prompt in the folder where the script is located and run the following command to install the required libraries:

```bash
pip install praw requests moviepy google-api-python-client google-auth-oauthlib google-auth

# 🔑 Setting Up API Credentials
Reddit API

    Go to Reddit's Developer Portal and create a new application.
    Copy the Client ID, Client Secret, and set a User Agent (e.g., YourAppName (by u/YourRedditUsername)).
    Open the script (main.py) and replace the following placeholders with your Reddit API credentials:

REDDIT_CLIENT_ID = 'your_client_id'
REDDIT_CLIENT_SECRET = 'your_client_secret'
REDDIT_USER_AGENT = 'your_user_agent'

# YouTube API

    Go to the Google Cloud Console.
    Create a new project and enable the YouTube Data API v3.
    Download the credentials.json file and place it in the same folder as the script.
    Rename the file to secret_token.json.

# 🚀 How to Use

    Open the script (main.py) in a text editor.
    Customize the following settings (optional):
        Subreddit Name: Change subreddit_name to the subreddit you want to scrape (default is memes).
        Video Title, Description, and Tags: Modify these in the main() function.
        Background Music: Replace background_music.mp3 with your own music file (optional).
    Run the script:

python main.py

The script will:

    Scrape memes from the specified subreddit.
    Download the memes to a folder named memes.
    Compile the memes into a video (meme_compilation.mp4).
    Upload the video to YouTube.

# ⚙️ Configuration Options

    Video Duration per Meme: Adjust the duration_per_meme parameter in the compile_memes function to control how long each meme stays on screen.
    Video Resolution: Change the resolution parameter in the compile_memes function to set the video resolution (default is 1920x1080).
    Privacy Settings: Modify the privacyStatus in the upload_to_youtube function to set the video privacy (public, private, or unlisted).

❓ Frequently Asked Questions

Q: Where are the downloaded memes stored?

A: The memes are saved in a folder named memes in the same directory as the script.

Q: Can I change the background music?

A: Yes! Replace the background_music.mp3 file with your own music file.

Q: How do I change the subreddit?

A: Modify the subreddit_name variable in the main() function to the subreddit you want to scrape.
📜 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as you see fit.
🙏 Acknowledgments

    PRAW for Reddit API access.
    MoviePy for video editing.
    Google API Client Library for YouTube API access.

Enjoy creating your meme compilations! If you have any questions or issues, feel free to open an issue on the repository.
