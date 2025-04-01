import os
import logging
import time
import subprocess
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    try:
        # Start timing the transcription process
        start_time = time.time()
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
            
        elapsed_time = time.time() - start_time
        logger.info(f"Transcription completed in {elapsed_time:.2f} seconds. Saved to: {transcript_file}")
        
        return transcript_file, transcript_text
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return create_mock_transcript(audio_file_path, transcript_file, error_msg=str(e))

def create_mock_transcript(audio_file_path, transcript_file, is_mock_by_choice=False, error_msg=None):
    """
    Create a mock transcript for testing purposes.
    
    Args:
        audio_file_path (str): Path to the audio file
        transcript_file (str): Path to save the transcript
        is_mock_by_choice (bool): Whether we're using mock by choice or due to an error
        error_msg (str): Error message if any
        
    Returns:
        tuple: (transcript_file_path, mock_transcript_text)
    """
    # Extract video ID if possible
    base_filename = os.path.basename(audio_file_path)
    video_id = "unknown"
    
    if "fallback_" in base_filename:
        video_id = base_filename.replace("fallback_", "").replace(".mp3", "")
    else:
        # Try to extract the video ID from the filename
        video_id = os.path.splitext(base_filename)[0]
    
    message = ""
    if error_msg:
        message = f"Note: Transcription failed with error: {error_msg}\n\n"
    elif is_mock_by_choice:
        message = (
            "Note: We're using a mock transcript by choice.\n"
            "In a production environment, this would contain the actual transcription.\n\n"
        )
            
    # Create mock transcript
    mock_transcript = (
        f"{message}This is a mock transcript for testing purposes.\n"
        f"The original video ID was: {video_id}\n"
        f"In a real scenario, this would contain the actual transcription of the YouTube video.\n"
        f"Since we couldn't process the actual video audio, this placeholder is used instead.\n"
        f"This enables testing of the full pipeline even when transcription fails."
    )
    
    # Save the mock transcript
    try:
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(mock_transcript)
            
        logger.info(f"Created mock transcript: {transcript_file}")
        return transcript_file, mock_transcript
        
    except Exception as e:
        logger.error(f"Error creating mock transcript: {str(e)}")
        return None, "Error creating transcript." 