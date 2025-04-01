from crewai import Task
from utils.youtube_downloader import download_youtube_audio
from utils.transcriber import transcribe_audio
from utils.summarizer import summarize_text

def create_download_task(agent, youtube_url):
    """Create a task for downloading a YouTube video."""
    return Task(
        description=f"Download the YouTube video at {youtube_url} as an MP3 file.",
        expected_output="Path to the downloaded MP3 file.",
        agent=agent,
        async_execution=False,
        context=[
            f"The YouTube URL to download is: {youtube_url}",
            "Use the download_youtube_audio function to download the audio."
        ],
        function=lambda: download_youtube_audio(youtube_url)
    )

def create_transcription_task(agent, audio_file_path):
    """Create a task for transcribing an audio file."""
    return Task(
        description=f"Transcribe the audio file at {audio_file_path} to text.",
        expected_output="The transcription of the audio file and path to the transcript file.",
        agent=agent,
        async_execution=False,
        context=[
            f"The audio file to transcribe is located at: {audio_file_path}",
            "Use the transcribe_audio function to convert the audio to text."
        ],
        function=lambda: transcribe_audio(audio_file_path)
    )

def create_summarization_task(agent, transcript_text, prompt_instruction):
    """Create a task for summarizing text based on a prompt."""
    return Task(
        description=f"Summarize the transcript based on the following prompt: {prompt_instruction}",
        expected_output="A summary of the transcript that focuses on the aspects mentioned in the prompt.",
        agent=agent,
        async_execution=False,
        context=[
            f"The prompt instruction is: {prompt_instruction}",
            "Use the summarize_text function to create a summary that addresses the prompt."
        ],
        function=lambda: summarize_text(transcript_text, prompt_instruction)
    ) 