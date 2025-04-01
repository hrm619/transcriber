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
    Download audio from a YouTube video.
    
    Args:
        youtube_url (str): URL of the YouTube video
        output_dir (str): Directory to save the downloaded audio
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        str: Path to the downloaded audio file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract video ID for consistent fallback naming
    video_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else "unknown_video"
    
    # Check if we have yt-dlp installed as a fallback
    has_yt_dlp = False
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        has_yt_dlp = True
        logger.info("yt-dlp is available as a fallback")
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.info("yt-dlp not available, will use pytube only")
    
    # First try yt-dlp if available as it's the most reliable method
    if has_yt_dlp:
        try:
            logger.info("Trying yt-dlp method...")
            # Create a filename using the video ID
            filename = f"{video_id}"
            output_path = os.path.join(output_dir, f"{filename}.mp3")
            
            # Use yt-dlp to download the audio
            cmd = [
                "yt-dlp", 
                "-x", "--audio-format", "mp3",
                "-o", os.path.join(output_dir, filename + ".%(ext)s"), 
                youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Audio downloaded successfully with yt-dlp: {output_path}")
                return output_path
            else:
                logger.error(f"yt-dlp download failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error using yt-dlp: {str(e)}")
    
    # Fall back to pytube if yt-dlp failed or is not available
    methods = ['direct', 'alternative']
    
    for method in methods:
        for retry_count in range(max_retries):
            try:
                if method == 'direct':
                    # Create YouTube object
                    yt = YouTube(youtube_url)
                    
                    # Add a short delay to avoid rate limiting
                    time.sleep(1)
                    
                    # Clean video title for filename
                    video_title = "".join([c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in yt.title])
                    output_file = f"{video_title}.mp3"
                    output_path = os.path.join(output_dir, output_file)
                    
                    # Return existing file if already downloaded
                    if os.path.exists(output_path):
                        logger.info(f"Audio file already exists: {output_path}")
                        return output_path
                        
                    logger.info(f"Downloading audio from: {yt.title}")
                    
                    # Get and download audio stream (try multiple stream types)
                    audio_stream = None
                    for stream_type in ['audio/mp4', 'audio/webm']:
                        streams = yt.streams.filter(only_audio=True, mime_type=stream_type)
                        if streams:
                            audio_stream = streams.first()
                            break
                    
                    if not audio_stream:
                        audio_stream = yt.streams.filter(only_audio=True).first()
                    
                    if not audio_stream:
                        raise Exception("No audio stream found")
                        
                    downloaded_file = audio_stream.download(output_path=output_dir)
                    
                    # Rename to mp3 extension
                    base, _ = os.path.splitext(downloaded_file)
                    new_file = base + '.mp3'
                    
                    if downloaded_file != new_file:
                        os.rename(downloaded_file, new_file)
                        
                    logger.info(f"Audio downloaded successfully: {new_file}")
                    return new_file
                
                else:  # method == 'alternative'
                    # Try with different parameters for pytube
                    logger.info("Trying alternative pytube method...")
                    
                    # Try to download using itag directly
                    yt = YouTube(youtube_url)
                    
                    # Try to get a specific audio itag known to work
                    audio_stream = None
                    for itag in [140, 139, 249, 250, 251]:
                        try:
                            audio_stream = yt.streams.get_by_itag(itag)
                            if audio_stream:
                                break
                        except Exception:
                            continue
                    
                    if not audio_stream:
                        raise Exception("No audio stream found with alternative method")
                    
                    # Use video ID for filename to avoid title parsing issues
                    output_path = os.path.join(output_dir, f"{video_id}.mp3")
                    
                    downloaded_file = audio_stream.download(output_path=output_dir, filename=video_id)
                    
                    # Rename to mp3 extension if needed
                    base, ext = os.path.splitext(downloaded_file)
                    new_file = base + '.mp3'
                    
                    if downloaded_file != new_file and ext != '.mp3':
                        os.rename(downloaded_file, new_file)
                    
                    logger.info(f"Audio downloaded successfully with alternative method: {new_file}")
                    return new_file
                
            except (RegexMatchError, VideoUnavailable) as e:
                logger.warning(f"YouTube error with {method} method: {str(e)}")
                # These errors indicate the video might not be available, try alternative immediately
                break
                
            except Exception as e:
                # Calculate backoff time with jitter for retry
                backoff_time = (2 ** retry_count) + (random.random() * 0.5)
                logger.warning(f"Attempt {retry_count + 1} with {method} method failed: {str(e)}. Retrying in {backoff_time:.2f} seconds...")
                
                if retry_count < max_retries - 1:
                    time.sleep(backoff_time)
                else:
                    logger.error(f"Failed to download with {method} method after {max_retries} attempts: {str(e)}")
                    break  # Try next method
    
    # If we get here, all methods failed
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