import os
from crewai import Agent
from langchain_openai import ChatOpenAI

# Set up the LLM
def get_llm(model="gpt-3.5-turbo"):
    """Get the LLM instance."""
    return ChatOpenAI(
        temperature=0.7,
        model=model
    )

# Define our agents
def create_downloader_agent():
    """Create an agent that downloads YouTube videos."""
    return Agent(
        role="YouTube Downloader",
        goal="Download YouTube videos as MP3 files",
        backstory="""You are an expert in downloading content from YouTube.
        Your job is to take YouTube URLs and download them as MP3 files for further processing.""",
        verbose=True,
        llm=get_llm()
    )

def create_transcription_agent():
    """Create an agent that transcribes audio files."""
    return Agent(
        role="Audio Transcriber",
        goal="Accurately transcribe audio to text",
        backstory="""You are an expert in audio transcription.
        You use advanced AI models to convert speech to text with high accuracy.""",
        verbose=True,
        llm=get_llm()
    )

def create_summarization_agent():
    """Create an agent that summarizes text based on prompts."""
    return Agent(
        role="Content Summarizer",
        goal="Create insightful summaries based on specific prompts",
        backstory="""You are an expert in understanding and summarizing content.
        You can take any text and a specific prompt, and create a summary that
        focuses on the aspects mentioned in the prompt.""",
        verbose=True,
        llm=get_llm("gpt-4-turbo")  # Using a more advanced model for summarization
    ) 