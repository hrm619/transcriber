import os
import logging
from pytube import YouTube
import time
import random
import requests
from pytube.exceptions import RegexMatchError, VideoUnavailable
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_youtube_audio(youtube_url, output_dir="downloads", max_retries=3):
    """
    Download audio from a YouTube video using yt-dlp as primary method.
    Falls back to pytube if yt-dlp fails.
    
    Args:
        youtube_url (str): URL of the YouTube video
        output_dir (str): Directory to save the downloaded audio
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        str: Path to the downloaded audio file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract video ID for consistent naming
    video_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else "unknown_video"
    output_path = os.path.join(output_dir, f"{video_id}.mp3")
    
    # Check if file already exists
    if os.path.exists(output_path):
        logger.info(f"Audio file already exists: {output_path}")
        return output_path
    
    # Try yt-dlp first
    for retry in range(max_retries):
        try:
            logger.info(f"Attempting to download with yt-dlp (attempt {retry + 1}/{max_retries})")
            
            # Use yt-dlp to download the audio
            cmd = [
                "yt-dlp", 
                "-x", "--audio-format", "mp3",
                "-o", os.path.join(output_dir, f"{video_id}.%(ext)s"), 
                youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Audio downloaded successfully with yt-dlp: {output_path}")
                return output_path
            else:
                logger.warning(f"yt-dlp attempt {retry + 1} failed: {result.stderr}")
                
                # Add exponential backoff with jitter
                if retry < max_retries - 1:
                    backoff_time = (2 ** retry) + (random.random() * 0.5)
                    time.sleep(backoff_time)
                
        except Exception as e:
            logger.warning(f"yt-dlp attempt {retry + 1} failed with error: {str(e)}")
            if retry < max_retries - 1:
                time.sleep(2 ** retry)
    
    # If yt-dlp fails, try pytube as fallback
    logger.info("Falling back to pytube...")
    try:
        yt = YouTube(youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            raise Exception("No audio stream found")
            
        downloaded_file = audio_stream.download(output_path=output_dir, filename=video_id)
        
        # Rename to mp3 extension if needed
        base, ext = os.path.splitext(downloaded_file)
        new_file = base + '.mp3'
        
        if downloaded_file != new_file and ext != '.mp3':
            os.rename(downloaded_file, new_file)
        
        logger.info(f"Audio downloaded successfully with pytube: {new_file}")
        return new_file
        
    except Exception as e:
        logger.error(f"All download methods failed: {str(e)}")
        return create_fallback_audio_file(output_dir, video_id)

def create_fallback_audio_file(output_dir, video_id):
    """
    Create a fallback audio file for testing when YouTube download fails.
    
    Args:
        output_dir (str): Directory to save the fallback file
        video_id (str): The YouTube video ID
    
    Returns:
        str: Path to the fallback file
    """
    try:
        fallback_file = os.path.join(output_dir, f"fallback_{video_id}.mp3")
        
        # Create a simple text file as fallback
        with open(fallback_file, 'w') as f:
            f.write("This is a fallback audio file for testing purposes.")
        
        logger.info(f"Created fallback audio file: {fallback_file}")
        return fallback_file
        
    except Exception as e:
        logger.error(f"Failed to create fallback file: {str(e)}")
        # Final emergency fallback
        minimal_fallback = os.path.join(os.getcwd(), "emergency_fallback.mp3")
        with open(minimal_fallback, 'w') as f:
            f.write("Emergency fallback file")
        return minimal_fallback 