#!/usr/bin/env python3
"""
Check if all required dependencies are installed.
"""
import sys
import subprocess
import shutil

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    if shutil.which("ffmpeg") is None:
        print("ERROR: FFmpeg is not installed. Please install it first.")
        print("macOS: brew install ffmpeg")
        print("Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("Windows: download from https://ffmpeg.org/download.html")
        return False
    return True

def check_python_dependencies():
    """Check if all Python dependencies are installed."""
    required_packages = [
        "crewai",
        "pytube",
        "openai",
        "langchain",
        "langchain-openai",
        "python-dotenv",
        "whisper",
        "pydub",
        "ffmpeg-python"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("ERROR: The following Python packages are missing:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install them with:")
        print(f"uv pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists."""
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" not in content or "your_openai_api_key_here" in content:
                print("WARNING: OpenAI API key may not be properly set in .env file.")
                print("Please edit the .env file and set your OpenAI API key.")
                return False
    except FileNotFoundError:
        print("WARNING: .env file not found.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return False
    
    return True

def main():
    """Run all checks."""
    ffmpeg_ok = check_ffmpeg()
    deps_ok = check_python_dependencies()
    env_ok = check_env_file()
    
    if ffmpeg_ok and deps_ok and env_ok:
        print("All dependencies are installed and configured correctly!")
        return 0
    else:
        print("\nPlease fix the issues above before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 