#!/usr/bin/env python3
"""
Wrapper script for the YouTube transcriber and summarizer.
"""
import sys
import os
from app.main import process_youtube_video

def show_usage():
    """Show usage instructions."""
    print("Usage: python transcribe.py <youtube_url> \"<prompt>\"")
    print("Example: python transcribe.py https://www.youtube.com/watch?v=dQw4w9WgXcQ \"Summarize the key points of this video\"")
    sys.exit(1)

if __name__ == "__main__":
    # Check for correct number of arguments
    if len(sys.argv) < 3:
        show_usage()
    
    # Get YouTube URL and prompt
    youtube_url = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    
    # Process the YouTube video
    try:
        summary = process_youtube_video(youtube_url, prompt)
        
        # Print the summary
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(summary)
        print("="*50)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1) 