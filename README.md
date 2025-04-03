# YouTube Video Transcriber

A Python application that processes YouTube videos by:
1. Downloading them as MP3 files
2. Transcribing the audio
3. Summarizing the content

## Setup

1. Create a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
uv pip sync requirements.txt
```

3. Create a `.env` file with your configuration:
```bash
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-3.5-turbo
LOG_LEVEL=INFO
```

## Requirements
- Python 3.x
- FFmpeg
- OpenAI API key
- uv (install with `curl -LsSf https://astral.sh/uv/install.sh | sh` on macOS/Linux or `irm https://astral.sh/uv/install.ps1 | iex` on Windows)

## Usage

Run the transcriber with a YouTube URL and a prompt for summarization:

```bash
python transcribe.py https://www.youtube.com/watch?v=dQw4w9WgXcQ "Summarize the key points of this video"
```

You can also use the mock mode for testing:

```bash
python transcribe.py https://www.youtube.com/watch?v=dQw4w9WgXcQ "Summarize the key points" --mock
```

## Implementation

This application uses LangGraph to create a workflow with three main nodes:
1. YouTube Downloader - Downloads the video as audio
2. Audio Transcriber - Transcribes the audio to text
3. Content Summarizer - Summarizes the text based on the prompt 