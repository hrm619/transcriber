#!/usr/bin/env python3
"""
Batch YouTube Transcription and Summarization

This script processes multiple YouTube URLs using the same prompt instruction,
leveraging the functionality from transcribe.py.
"""

import os
import logging
import pandas as pd
import time
import random
from dotenv import load_dotenv
from typing import List, Dict, Any
from openai import OpenAIError, RateLimitError

# Import core utility functions directly
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

def retry_with_backoff(func, max_retries=3, initial_delay=1, max_delay=60):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Result of the function call
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except (RateLimitError, OpenAIError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                # Add jitter to prevent thundering herd
                jitter = random.uniform(0, 0.1 * delay)
                wait_time = delay + jitter
                logger.warning(f"OpenAI API rate limit hit. Retrying in {wait_time:.2f} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                delay = min(delay * 2, max_delay)  # Exponential backoff with max delay
            else:
                logger.error(f"Max retries ({max_retries}) reached. Last error: {str(last_exception)}")
                raise last_exception
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise e

def process_youtube_urls(urls: List[str], prompt: str, use_mock: bool = False, wait_min: int = 3, wait_max: int = 10) -> List[Dict[str, Any]]:
    """
    Process multiple YouTube URLs with the same prompt instruction.
    
    Args:
        urls: List of YouTube URLs to process
        prompt: Prompt instruction for summarization
        use_mock: Whether to use mock data for demonstration
        wait_min: Minimum wait time in seconds between YouTube downloads
        wait_max: Maximum wait time in seconds between YouTube downloads
        
    Returns:
        List of result dictionaries containing processed data
    """
    results = []
    
    # Process each URL
    for i, url in enumerate(urls):
        logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
        
        # Add a random wait time between requests to avoid rate limiting
        if i > 0:
            wait_time = random.randint(wait_min, wait_max)
            logger.info(f"Waiting {wait_time} seconds before processing next URL...")
            time.sleep(wait_time)
        
        if use_mock:
            # Mock result
            result = {
                "youtube_url": url,
                "prompt_instruction": prompt,
                "audio_file_path": f"mock_audio_{i}.mp3",
                "transcript_text": f"This is a mock transcript for video {i}",
                "transcript_file": f"mock_transcript_{i}.txt",
                "summary": f"Mock summary for video {i} based on prompt: {prompt[:30]}...",
                "current_step": "end",
                "error": ""
            }
        else:
            # Define initial result state
            result = {
                "youtube_url": url,
                "prompt_instruction": prompt,
                "audio_file_path": "",
                "transcript_text": "",
                "transcript_file": "",
                "summary": "",
                "current_step": "download",
                "error": ""
            }
            
            # Execute step 1: Download
            try:
                logger.info(f"Downloading YouTube video: {url}")
                audio_file_path = download_youtube_audio(url)
                logger.info(f"Downloaded audio file: {audio_file_path}")
                result["audio_file_path"] = audio_file_path
                result["current_step"] = "transcription"
                
                # Execute step 2: Transcription with retry logic
                logger.info(f"Transcribing audio file: {audio_file_path}")
                def transcribe_with_retry():
                    return transcribe_audio(audio_file_path)
                
                transcript_file, transcript_text = retry_with_backoff(
                    transcribe_with_retry,
                    max_retries=3,
                    initial_delay=5,
                    max_delay=60
                )
                
                logger.info(f"Transcribed to: {transcript_file}")
                result["transcript_file"] = transcript_file
                result["transcript_text"] = transcript_text
                result["current_step"] = "summarization"
                
                # Execute step 3: Summarization
                logger.info(f"Summarizing transcript with prompt: {prompt}")
                summary_file, summary = summarize_text(transcript_text, prompt)
                logger.info(f"Generated summary: {summary_file}")
                result["summary"] = summary
                result["current_step"] = "end"
                
            except Exception as e:
                error_msg = f"Processing failed at step {result['current_step']}: {str(e)}"
                logger.error(error_msg)
                result["error"] = error_msg
                result["current_step"] = "end"
        
        # Add result to list
        results.append(result)
        logger.info(f"Completed processing URL: {url}")
        
    return results

def display_results(results: List[Dict[str, Any]]) -> None:
    """Display processing results in a simple text format."""
    print(f"\nProcessed {len(results)} YouTube videos")
    print("=" * 80)
    
    for i, result in enumerate(results):
        url = result["youtube_url"]
        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else "unknown"
        
        print(f"\nVideo {i+1}: {video_id}")
        print(f"URL: {url}")
        
        if result["error"]:
            print(f"ERROR: {result['error']}")
        else:
            print(f"Audio: {os.path.basename(result['audio_file_path'])}")
            print(f"Transcript: {os.path.basename(result['transcript_file'])}")
            print("\nSummary:")
            print("-" * 40)
            print(result["summary"])
            print("-" * 40)
        
        print("=" * 80)

def save_results_to_csv(results: List[Dict[str, Any]], output_file: str = "batch_processing_results.csv") -> None:
    """Save basic processing results to a CSV file."""
    df_results = []

    for result in results:
        # Create a simplified result for the DataFrame
        df_result = {
            "URL": result["youtube_url"],
            "Success": len(result["error"]) == 0,
            "Audio File": os.path.basename(result["audio_file_path"]) if result["audio_file_path"] else "",
            "Transcript File": os.path.basename(result["transcript_file"]) if result["transcript_file"] else "",
            "Summary Length": len(result["summary"]) if result["summary"] else 0,
            "Error": result["error"][:100] + "..." if len(result["error"]) > 100 else result["error"]
        }
        df_results.append(df_result)

    # Create and save DataFrame
    df = pd.DataFrame(df_results)
    df.to_csv(output_file, index=False)
    logger.info(f"Results saved to {output_file}")

def save_detailed_summaries(results: List[Dict[str, Any]], output_file: str = "batch_processing_summaries.txt") -> None:
    """Save detailed summaries to a text file."""
    with open(output_file, "w", encoding="utf-8") as f:
        for i, result in enumerate(results):
            f.write(f"\n{'=' * 50}\n")
            f.write(f"Video {i+1}: {result['youtube_url']}\n")
            f.write(f"{'=' * 50}\n\n")
            
            if result["error"]:
                f.write(f"ERROR: {result['error']}\n")
            else:
                f.write(f"SUMMARY:\n{result['summary']}\n")
    
    logger.info(f"Detailed summaries saved to {output_file}")

def main():
    """Main function to run the batch processing."""
    # List of YouTube URLs to process
    youtube_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Replace with your URLs
        "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    ]

    # Prompt instruction to apply to all videos
    prompt_instruction = "Summarize the key points and main ideas presented in this video. Include any important facts, arguments, or conclusions."

    # Process all URLs (set use_mock=True to test without downloading videos)
    results = process_youtube_urls(youtube_urls, prompt_instruction, use_mock=False)

    # Display the results
    display_results(results)

    # Save results to files
    save_results_to_csv(results)
    save_detailed_summaries(results)

if __name__ == "__main__":
    main() 