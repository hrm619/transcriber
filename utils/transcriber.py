import os
import time
import subprocess
import openai
from dotenv import load_dotenv
from .logger import logger

# Load environment variables
load_dotenv()

def transcribe_audio(audio_file_path, output_dir="transcripts", youtube_url=None):
    """
    Transcribe audio file to text using OpenAI's API.
    
    Args:
        audio_file_path (str): Path to the audio file
        output_dir (str): Directory to save the transcription
        youtube_url (str, optional): YouTube URL for file naming
    
    Returns:
        tuple: (transcript_file_path, transcribed_text)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
        
    # Prepare file paths
    base_name = os.path.basename(audio_file_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    
    # Use video_id in filename if youtube_url is provided
    if youtube_url:
        video_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else file_name_without_ext
        transcript_file = os.path.join(output_dir, f"{video_id}.txt")
    else:
        transcript_file = os.path.join(output_dir, f"{file_name_without_ext}.txt")
    
    # Check if transcript already exists
    if os.path.exists(transcript_file):
        logger.info(f"Transcript already exists: {transcript_file}")
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        return transcript_file, transcript_text
    
    # Check if this is a fallback file and create mock transcript if it is
    if "fallback_" in file_name_without_ext:
        logger.info(f"Detected fallback file: {audio_file_path}, using mock transcription.")
        return create_mock_transcript(audio_file_path, transcript_file)
    
    # Start timing the transcription
    start_time = time.time()
    
    try:
        logger.info(f"Transcribing audio file with OpenAI API: {audio_file_path}")
        
        # Check if file exists
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Open the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Call OpenAI API
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        # Extract the transcript text
        transcript_text = transcript.text
        
        # Save the transcript to a file
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript_text)
            
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        logger.info(f"Transcription completed in {elapsed_time:.2f} seconds. Saved to: {transcript_file}")
        
        return transcript_file, transcript_text
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise

def create_mock_transcript(audio_file_path, transcript_file):
    """Create a mock transcript for testing purposes."""
    try:
        # Extract video ID from the audio file path
        video_id = os.path.splitext(os.path.basename(audio_file_path))[0].replace("fallback_", "")
        
        # Create mock transcript content
        mock_content = f"""This is a mock transcript for testing purposes.
The original video ID was: {video_id}
In a real scenario, this would contain the actual transcription of the YouTube video.
Since we couldn't download or process the actual video, this placeholder is used instead.
This enables testing of the full pipeline even when YouTube downloads fail."""
        
        # Write the mock transcript to file
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(mock_content)
        
        logger.info(f"Created mock transcript: {transcript_file}")
        return transcript_file, mock_content
        
    except Exception as e:
        logger.error(f"Error creating mock transcript: {str(e)}")
        raise 