import os
import logging
import openai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_text(text, prompt_instruction, output_dir="summaries", youtube_url=None):
    """
    Summarize text based on a specific prompt instruction using OpenAI API directly.
    
    Args:
        text (str): The text to summarize
        prompt_instruction (str): The prompt with specific instructions for summarization
        output_dir (str): Directory to save the summary
        youtube_url (str, optional): YouTube URL for file naming
    
    Returns:
        tuple: (summary_file_path, summarized_text)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
        
    # Generate a filename based on the video URL if provided, otherwise use a generic name
    if youtube_url:
        video_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else "unknown_video"
        summary_file = os.path.join(output_dir, f"{video_id}.txt")
    else:
        summary_file = os.path.join(output_dir, f"summary_{int(time.time())}.txt")
    
    # Check if this is mock data
    if "This is a mock transcript for testing purposes" in text:
        logger.info("Detected mock transcript, creating a mock summary")
        return create_mock_summary(text, prompt_instruction, summary_file)
    
    try:
        logger.info(f"Summarizing text with prompt: {prompt_instruction[:100]}...")
        
        # Check if text is too long, truncate if necessary
        max_text_length = 16000  # Leave room for prompt and system message
        if len(text) > max_text_length:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {max_text_length} chars")
            text = text[:max_text_length] + "... [truncated]"
        
        # Create the system prompt
        system_prompt = "You are an expert in summarizing content and extracting key insights from transcripts."
        
        # Create the user prompt
        user_prompt = f"""
        I need you to summarize the following transcript based on these instructions:
        
        INSTRUCTION: {prompt_instruction}
        
        TRANSCRIPT:
        {text}
        
        Your summary should be comprehensive, well-organized, and directly address all the points in the instruction.
        """
        
        # Call OpenAI API directly
        response = openai.chat.completions.create(
            model=os.getenv('SUMMARY_MODEL', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        # Extract the summary text
        summary = response.choices[0].message.content.strip()
        
        # Save the summary to a file
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        logger.info(f"Summary completed and saved to: {summary_file}")
        
        return summary_file, summary
        
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        # Provide a mock summary in case of error
        if youtube_url:
            video_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else "unknown_video"
            error_file = os.path.join(output_dir, f"error_summary_{video_id}.txt")
        else:
            error_file = os.path.join(output_dir, f"error_summary_{int(time.time())}.txt")
        return create_mock_summary(text, prompt_instruction, error_file)

def create_mock_summary(text, prompt_instruction, summary_file):
    """
    Create a mock summary for testing purposes.
    
    Args:
        text (str): The original text
        prompt_instruction (str): The original prompt instruction
        summary_file (str): Path to save the summary
        
    Returns:
        tuple: (summary_file_path, mock_summary_text)
    """
    # Extract any video ID if present in the text
    video_id = "unknown"
    for line in text.split('\n'):
        if "original video ID was:" in line:
            video_id = line.split(":")[-1].strip()
            break
            
    # Create mock summary
    mock_summary = (
        f"This is a mock summary for testing purposes.\n\n"
        f"For the YouTube video with ID: {video_id}\n\n"
        f"In a real scenario, this would contain an actual AI-generated summary of the content.\n"
        f"Since we're using mock data, this placeholder is provided to demonstrate the complete pipeline workflow."
    )
    
    try:
        # Save the mock summary
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(mock_summary)
            
        logger.info(f"Created mock summary: {summary_file}")
        return summary_file, mock_summary
        
    except Exception as e:
        logger.error(f"Error creating mock summary: {str(e)}")
        return None, "Error creating summary." 