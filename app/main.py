import os
import logging
import argparse
from dotenv import load_dotenv
from crewai import Crew

from agents import create_downloader_agent, create_transcription_agent, create_summarization_agent
from tasks import create_download_task, create_transcription_task, create_summarization_task

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_youtube_video(youtube_url, prompt_instruction):
    """
    Process a YouTube video by downloading it, transcribing it, and summarizing it.
    
    Args:
        youtube_url (str): URL of the YouTube video
        prompt_instruction (str): Prompt for summarization
    
    Returns:
        str: The summary of the video
    """
    try:
        logger.info(f"Starting to process YouTube video: {youtube_url}")
        logger.info(f"Using summarization prompt: {prompt_instruction}")
        
        # Create agents
        downloader_agent = create_downloader_agent()
        transcription_agent = create_transcription_agent()
        summarization_agent = create_summarization_agent()
        
        # Create download task
        download_task = create_download_task(downloader_agent, youtube_url)
        
        # Create the crew with just the download task initially
        crew = Crew(
            agents=[downloader_agent, transcription_agent, summarization_agent],
            tasks=[download_task],
            verbose=2
        )
        
        # Execute the download task
        result = crew.kickoff()
        audio_file_path = result
        
        logger.info(f"Downloaded audio file: {audio_file_path}")
        
        # Create and execute transcription task
        transcription_task = create_transcription_task(transcription_agent, audio_file_path)
        crew.tasks = [transcription_task]
        transcript_file, transcript_text = crew.kickoff()
        
        logger.info(f"Transcribed to: {transcript_file}")
        
        # Create and execute summarization task
        summarization_task = create_summarization_task(
            summarization_agent, 
            transcript_text, 
            prompt_instruction
        )
        crew.tasks = [summarization_task]
        summary_file, summary = crew.kickoff()
        
        logger.info(f"Generated summary: {summary_file}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error processing YouTube video: {str(e)}")
        raise

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="YouTube Transcriber and Summarizer")
    parser.add_argument("youtube_url", help="URL of the YouTube video to process")
    parser.add_argument("prompt", help="Prompt instruction for summarization")
    
    args = parser.parse_args()
    
    # Process the YouTube video
    summary = process_youtube_video(args.youtube_url, args.prompt)
    
    # Print the summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(summary)
    print("="*50)

if __name__ == "__main__":
    main() 