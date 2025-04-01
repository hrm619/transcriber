#!/usr/bin/env python3
import sys
from transcribe import main

def run_transcriber():
    # Get inputs from user
    print("\n=== YouTube Video Transcriber ===")
    url = input("\nEnter YouTube URL: ").strip()
    prompt = input("Enter your prompt for summarization: ").strip()
    
    # Set up arguments for main()
    sys.argv = [
        "transcribe.py",
        url,
        prompt
    ]
    
    print("\nProcessing... This may take a few minutes.")
    print("The video will be downloaded, transcribed, and summarized.")
    print("Results will be saved in the downloads/, transcripts/, and summaries/ folders.")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    run_transcriber() 