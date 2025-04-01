def test_imports():
    try:
        import crewai
        import pytube
        import openai
        import langchain
        import langchain_openai
        from dotenv import load_dotenv
        import whisper
        import pydub
        import ffmpeg
        print("All packages imported successfully!")
    except ImportError as e:
        print(f"Error importing packages: {e}")

if __name__ == "__main__":
    test_imports() 