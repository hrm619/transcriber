import os
import logging
import argparse
from typing import TypedDict, Annotated, List, Dict, Any
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

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

# Define our state
class AgentState(TypedDict):
    youtube_url: str
    prompt_instruction: str
    audio_file_path: str
    transcript_text: str
    transcript_file: str
    summary: str
    current_step: str
    error: str

# Define our nodes (these replace Agents in CrewAI)
def youtube_downloader(state: AgentState) -> AgentState:
    """Download a YouTube video as audio."""
    logger.info(f"Downloading YouTube video: {state['youtube_url']}")
    
    try:
        audio_file_path = download_youtube_audio(state["youtube_url"])
        logger.info(f"Downloaded audio file: {audio_file_path}")
        
        return {
            **state,
            "audio_file_path": audio_file_path,
            "current_step": "transcription"
        }
    except Exception as e:
        error_msg = f"Error downloading YouTube video: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "error": error_msg,
            "current_step": "end"
        }

def audio_transcriber(state: AgentState) -> AgentState:
    """Transcribe an audio file to text."""
    logger.info(f"Transcribing audio file: {state['audio_file_path']}")
    
    try:
        transcript_file, transcript_text = transcribe_audio(
            state["audio_file_path"], 
            youtube_url=state["youtube_url"]
        )
        logger.info(f"Transcribed to: {transcript_file}")
        
        return {
            **state,
            "transcript_file": transcript_file,
            "transcript_text": transcript_text,
            "current_step": "summarization"
        }
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "error": error_msg,
            "current_step": "end"
        }

def content_summarizer(state: AgentState) -> AgentState:
    """Summarize text based on a prompt."""
    logger.info(f"Summarizing transcript with prompt: {state['prompt_instruction']}")
    
    try:
        summary_file, summary = summarize_text(
            state["transcript_text"], 
            state["prompt_instruction"],
            youtube_url=state["youtube_url"]
        )
        logger.info(f"Generated summary: {summary_file}")
        
        return {
            **state,
            "summary": summary,
            "current_step": "end"
        }
    except Exception as e:
        error_msg = f"Error summarizing transcript: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "error": error_msg,
            "current_step": "end"
        }

# Define our route logic
def router(state: AgentState) -> str:
    """Route to the next step in the pipeline based on the current step."""
    # If there's an error, we should end the process
    if "error" in state and state["error"]:
        return "end"
    return state["current_step"]

# Create the LangGraph workflow
def create_youtube_processing_graph():
    """Create a graph for processing YouTube videos."""
    # Create the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add our nodes
    workflow.add_node("download", youtube_downloader)
    workflow.add_node("transcription", audio_transcriber)
    workflow.add_node("summarization", content_summarizer)
    
    # Add our edges
    workflow.add_conditional_edges(
        "download",
        router,
        {
            "transcription": "transcription",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "transcription",
        router,
        {
            "summarization": "summarization",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "summarization",
        router,
        {
            "end": END
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("download")
    
    return workflow.compile()

def handle_mock_data(args):
    """Use mock data if the --mock flag is provided."""
    if args.mock:
        logger.info("Using mock data for demonstration")
        # Return a mock state with data
        return {
            "youtube_url": args.youtube_url,
            "prompt_instruction": args.prompt,
            "audio_file_path": "mock_audio.mp3",
            "transcript_text": "This is a mock transcript of a YouTube video about technology and innovation.",
            "transcript_file": "mock_transcript.txt",
            "summary": "This is a mock summary of the video. The main points discussed include technology, innovation, and the future of AI.",
            "current_step": "end",
            "error": ""
        }
    return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="YouTube Transcriber and Summarizer")
    parser.add_argument("youtube_url", help="URL of the YouTube video to process")
    parser.add_argument("prompt", help="Prompt instruction for summarization")
    parser.add_argument("--mock", action="store_true", help="Use mock data for demonstration")
    
    args = parser.parse_args()
    
    # Check if we should use mock data
    mock_result = handle_mock_data(args)
    if mock_result:
        print("\n" + "="*50)
        print("SUMMARY (MOCK DATA)")
        print("="*50)
        print(mock_result["summary"])
        print("="*50)
        return
    
    # Create and run the LangGraph
    graph = create_youtube_processing_graph()
    
    # Define the initial state
    initial_state = {
        "youtube_url": args.youtube_url,
        "prompt_instruction": args.prompt,
        "audio_file_path": "",
        "transcript_text": "",
        "transcript_file": "",
        "summary": "",
        "current_step": "download",  # Start with download step
        "error": ""
    }
    
    # Execute the graph
    result = graph.invoke(initial_state)
    
    # Print the summary or error
    print("\n" + "="*50)
    if result.get("error"):
        print("ERROR")
        print("="*50)
        print(result["error"])
    else:
        print("SUMMARY")
        print("="*50)
        print(result.get("summary", "No summary generated"))
    print("="*50)

if __name__ == "__main__":
    main() 