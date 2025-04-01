import os
import logging
from pytube import YouTube

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_youtube_audio(youtube_url, output_dir="downloads"):
    """
    Download audio from a YouTube video.
    
    Args:
        youtube_url (str): URL of the YouTube video
        output_dir (str): Directory to save the downloaded audio
    
    Returns:
        str: Path to the downloaded audio file
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Create YouTube object
        yt = YouTube(youtube_url)
        
        # Get video title for filename (clean it for filesystem compatibility)
        video_title = "".join([c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in yt.title])
        output_file = f"{video_title}.mp3"
        output_path = os.path.join(output_dir, output_file)
        
        # Check if file already exists
        if os.path.exists(output_path):
            logger.info(f"Audio file already exists: {output_path}")
            return output_path
            
        logger.info(f"Downloading audio from: {yt.title}")
        
        # Get audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        # Download audio
        downloaded_file = audio_stream.download(output_path=output_dir)
        
        # Rename the file to have mp3 extension
        base, _ = os.path.splitext(downloaded_file)
        new_file = base + '.mp3'
        
        if downloaded_file != new_file:
            os.rename(downloaded_file, new_file)
            
        logger.info(f"Audio downloaded successfully: {new_file}")
        return new_file
        
    except Exception as e:
        logger.error(f"Error downloading YouTube audio: {str(e)}")
        raise 