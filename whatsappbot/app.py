# File: app.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from googleapiclient.discovery import build
import youtube_dl
import os

app = Flask(__name__)

# YouTube Data API setup
YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Twilio credentials
TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()
    
    if incoming_msg:
        try:
            search_response = youtube.search().list(
                q=incoming_msg,
                part='snippet',
                maxResults=5,
                type='video'
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                video_title = item['snippet']['title']
                video_id = item['id']['videoId']
                videos.append((video_title, video_id))
            
            response_text = "Select a song to download by entering the number:\n"
            for idx, (title, vid) in enumerate(videos):
                response_text += f"{idx + 1}. {title}\n"
            response_text += "\nReply with the number of the song you want to download."
            msg.body(response_text)
        
        except Exception as e:
            msg.body(f"An error occurred: {e}")
    else:
        msg.body("Please enter a song name or artist name.")

    return str(resp)

@app.route('/download', methods=['POST'])
def download():
    incoming_msg = request.values.get('Body', '').strip()
    video_index = int(incoming_msg) - 1
    
    if 0 <= video_index < len(videos):
        video_title, video_id = videos[video_index]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{video_title}.mp3',
                'quiet': True
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            msg = MessagingResponse().message()
            msg.body(f"Download complete. Here is your link: {os.path.abspath(video_title)}.mp3")
        
        except Exception as e:
            msg = MessagingResponse().message()
            msg.body(f"An error occurred while downloading: {e}")

    return str(msg)

if __name__ == '__main__':
    app.run(debug=True)
