import os
import logging
import argparse
from dotenv import load_dotenv
from crewai import Crew, Process

from app.agents import create_agents
from app.tasks import create_tasks, configure_download_task, configure_transcription_task, configure_summarization_task
from utils.youtube_downloader import download_youtube_audio
from utils.transcriber import transcribe_audio
from utils.summarizer import summarize_text

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_youtube_processing(youtube_url, prompt_instruction):
    """Run the YouTube processing pipeline."""
    # Create agents
    agents_dict = create_agents()
    
    # Create task dictionary
    tasks_dict = create_tasks(agents_dict)
    
    # Configure the first task - downloading
    configure_download_task(
        tasks_dict, 
        agents_dict['youtube_downloader'], 
        youtube_url
    )
    
    # Execute download task
    download_result = tasks_dict['download_task'].execute()
    audio_file_path = download_result
    
    # Configure the second task - transcription
    configure_transcription_task(
        tasks_dict,
        agents_dict['audio_transcriber'],
        audio_file_path
    )
    
    # Execute transcription task
    transcription_result = tasks_dict['transcription_task'].execute()
    transcript_file, transcript_text = transcription_result
    
    # Configure the third task - summarization
    configure_summarization_task(
        tasks_dict,
        agents_dict['content_summarizer'],
        transcript_text,
        prompt_instruction
    )
    
    # Execute summarization task
    summarization_result = tasks_dict['summarization_task'].execute()
    summary_file, summary_text = summarization_result
    
    return summary_text

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="YouTube Transcriber and Summarizer")
    parser.add_argument("youtube_url", help="URL of the YouTube video to process")
    parser.add_argument("prompt", help="Prompt instruction for summarization")
    
    args = parser.parse_args()
    
    # Process the YouTube video
    result = run_youtube_processing(args.youtube_url, args.prompt)
    
    # Print the summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(result)
    print("="*50)

if __name__ == "__main__":
    main() 