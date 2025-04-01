# YouTube Video Transcriber

A Python application that processes YouTube videos by:
1. Downloading them as MP3 files
2. Transcribing the audio
3. Summarizing the content

## Setup

1. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip3 install crewai pytube openai langchain langchain-openai python-dotenv whisper pydub ffmpeg-python
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