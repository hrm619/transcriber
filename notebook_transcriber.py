#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from transcribe import create_youtube_processing_graph, AgentState
from utils.logger import logger

# Load environment variables
load_dotenv()

def transcribe_video(youtube_url: str, prompt: str, use_mock: bool = False) -> dict:
    """
    Transcribe and summarize a YouTube video.
    
    Args:
        youtube_url (str): URL of the YouTube video
        prompt (str): Prompt instruction for summarization
        use_mock (bool): Whether to use mock data for testing
        
    Returns:
        dict: Dictionary containing the results including:
            - audio_file_path: Path to the downloaded audio file
            - transcript_file: Path to the transcript file
            - transcript_text: The transcribed text
            - summary: The generated summary
            - error: Any error message if processing failed
    """
    print("\nProcessing... This may take a few minutes.")
    print("The video will be downloaded, transcribed, and summarized.")
    print("Results will be saved in the downloads/, transcripts/, and summaries/ folders.")
    
    try:
        # Create and run the LangGraph
        graph = create_youtube_processing_graph()
        
        # Define the initial state
        initial_state = {
            "youtube_url": youtube_url,
            "prompt_instruction": prompt,
            "audio_file_path": "",
            "transcript_text": "",
            "transcript_file": "",
            "summary": "",
            "current_step": "download",  # Start with download step
            "error": ""
        }
        
        # Execute the graph
        result = graph.invoke(initial_state)
        
        return result
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "current_step": "end"
        }

# Example usage in a notebook:
"""
# Example cell in a Jupyter notebook:
from notebook_transcriber import transcribe_video

# Process a video
result = transcribe_video(
    youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    prompt="Summarize the key points of this video"
)

# Display results
if result.get("error"):
    print(f"ERROR: {result['error']}")
else:
    print("\n=== TRANSCRIPT ===")
    print(result["transcript_text"])
    print("\n=== SUMMARY ===")
    print(result["summary"])
""" 