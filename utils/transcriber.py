import os
import logging
import whisper
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_audio(audio_file_path, output_dir="transcripts"):
    """
    Transcribe audio file to text using Whisper.
    
    Args:
        audio_file_path (str): Path to the audio file
        output_dir (str): Directory to save the transcription
    
    Returns:
        str: Path to the transcription file
        str: The transcribed text
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Get base filename without extension
        base_name = os.path.basename(audio_file_path)
        file_name_without_ext = os.path.splitext(base_name)[0]
        transcript_file = os.path.join(output_dir, f"{file_name_without_ext}.txt")
        
        # Check if transcript already exists
        if os.path.exists(transcript_file):
            logger.info(f"Transcript already exists: {transcript_file}")
            with open(transcript_file, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            return transcript_file, transcript_text
            
        # Start time
        start_time = time.time()
        logger.info(f"Loading Whisper model...")
        
        # Load the Whisper model (using 'base' for a balance of accuracy and speed)
        model = whisper.load_model("base")
        
        logger.info(f"Transcribing audio file: {audio_file_path}")
        
        # Transcribe the audio
        result = model.transcribe(audio_file_path)
        transcript_text = result["text"]
        
        # Save the transcript to a file
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript_text)
            
        elapsed_time = time.time() - start_time
        logger.info(f"Transcription completed in {elapsed_time:.2f} seconds. Saved to: {transcript_file}")
        
        return transcript_file, transcript_text
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise 