import os
import openai
from dotenv import load_dotenv
from .logger import logger
import time

# Load environment variables
load_dotenv()

def summarize_text(text, prompt_instruction, output_dir="summaries", youtube_url=None, max_text_length=4000):
    """
    Summarize text using OpenAI's API.
    
    Args:
        text (str): Text to summarize
        prompt_instruction (str): Instructions for summarization
        output_dir (str): Directory to save the summary
        youtube_url (str, optional): YouTube URL for file naming
        max_text_length (int): Maximum length of text to process
        
    Returns:
        tuple: (summary_file_path, summary_text)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare file paths
    if youtube_url:
        video_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else "unknown"
        summary_file = os.path.join(output_dir, f"{video_id}_summary.txt")
    else:
        summary_file = os.path.join(output_dir, "summary.txt")
    
    # Check if this is a mock transcript
    if "mock transcript" in text.lower():
        logger.info("Detected mock transcript, creating a mock summary")
        return create_mock_summary(text, summary_file)
    
    try:
        logger.info(f"Summarizing text with prompt: {prompt_instruction[:100]}...")
        
        # Truncate text if too long
        if len(text) > max_text_length:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {max_text_length} chars")
            text = text[:max_text_length] + "..."
        
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
        raise

def create_mock_summary(text, summary_file):
    """Create a mock summary for testing purposes."""
    try:
        # Create mock summary content
        mock_content = """This is a mock summary for testing purposes.
In a real scenario, this would contain an AI-generated summary of the video content.
The summary would focus on the key points and main ideas presented in the video.
This mock summary enables testing of the full pipeline even when summarization fails."""
        
        # Write the mock summary to file
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(mock_content)
        
        logger.info(f"Created mock summary: {summary_file}")
        return summary_file, mock_content
        
    except Exception as e:
        logger.error(f"Error creating mock summary: {str(e)}")
        raise 