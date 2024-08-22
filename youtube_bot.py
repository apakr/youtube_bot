import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import yt_dlp
import logging

# These are permissions the bot will need.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def authenticate_youtube_api():
    creds = None
    # If we have saved credentials, load them.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If not, log in and save the credentials.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def get_recent_videos(youtube, channel_id, num_videos):
    try:
        # Fetch the upload playlist ID of the channel
        request = youtube.channels().list(part='contentDetails', id=channel_id)
        response = request.execute()
        
        # Debugging: Print the response
        print(response)
        
        if 'items' not in response or len(response['items']) == 0:
            print("Error: No items found in the response. Please check the channel ID.")
            return None

        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Fetch the most recent video IDs from the uploads playlist
        request = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=num_videos)
        response = request.execute()
        
        if 'items' not in response or len(response['items']) == 0:
            print("Error: No videos found in the uploads playlist.")
            return None

        video_ids = [item['snippet']['resourceId']['videoId'] for item in response['items']]
        
        return video_ids
    except Exception as e:
        logging.error(f"An error occurred while fetching recent videos: {e}")
        return None

def download_video(video_id, download_path):
    try:
        # Ensure video_id is a string
        video_id = str(video_id)
        
        # Construct the URL and print it for debugging
        url = f'https://www.youtube.com/watch?v={video_id}'
        print(f"Downloading video from URL: {url}")
        
        # Use yt-dlp to download the video in the highest quality
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best', # Caution: if you have limited disc space or slow internet be careful downloading these videos because it will be at maximum quality (multiple GBs per video)
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Video downloaded successfully: {url}")
    except yt_dlp.utils.DownloadError as e:
        print(f"DownloadError: {e}")
    except yt_dlp.utils.ExtractorError as e:
        print(f"ExtractorError: {e}")
    except yt_dlp.utils.PostProcessingError as e:
        print(f"PostProcessingError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def download_specific_video(video_id, download_path):
    try:
        # Construct the URL and print it for debugging
        url = f'https://www.youtube.com/watch?v={video_id}'
        print(f"Downloading video from URL: {url}")
        
        # Use yt-dlp to download the video in the highest quality
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Video downloaded successfully: {url}")
    except yt_dlp.utils.DownloadError as e:
        print(f"DownloadError: {e}")
    except yt_dlp.utils.ExtractorError as e:
        print(f"ExtractorError: {e}")
    except yt_dlp.utils.PostProcessingError as e:
        print(f"PostProcessingError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# List of channels and the number of recent videos to download from each channel
channels = {
    'Solar Sands': {'channel_id': 'UCR6LasBpceuYUhuLToKBzvQ', 'num_videos': 1},
    # 'Stuff Made Here': {'channel_id': 'UCj1VqrHhDte54oLgPG4xpuQ', 'num_videos': 1}
    # Add more channels as you wish
}


if __name__ == '__main__':
    youtube = authenticate_youtube_api()
    
    # Replace with the path where you want to save the videos
    download_path = r'C:\Users\allen\Desktop\downloaded_yt_vids'
 
    # Download a specific video from a specific channel
    specific_channel_id = 'channel ID'  # Replace with the channel ID
    specific_video_id = 'video ID'  # Replace with the video ID
    
    # Download the specific video
    # download_specific_video(specific_video_id, download_path)

    for channel_name, channel_info in channels.items():
        channel_id = channel_info['channel_id']
        num_videos = channel_info['num_videos']

        print(f"Processing {channel_name} (ID: {channel_id}) for {num_videos} videos.")
    
        # Fetch the recent video IDs from the channel
        recent_video_ids = get_recent_videos(youtube, channel_id, num_videos)
        if recent_video_ids:
           # Download each recent video
            for video_id in recent_video_ids:
                download_video(video_id, download_path)
        else:
            print(f"No videos found or an error occurred for channel {channel_name} (ID: {channel_id})")
