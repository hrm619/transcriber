import yaml
from crewai import Task
from utils.youtube_downloader import download_youtube_audio
from utils.transcriber import transcribe_audio
from utils.summarizer import summarize_text

# Load task configurations
def load_task_configs(config_path="app/config/tasks.yaml"):
    """Load task configurations from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_tasks(agents):
    """Create all tasks for the processing pipeline."""
    configs = load_task_configs()
    
    # Map of task types to their function handlers
    task_handlers = {
        'download_task': download_youtube_audio,
        'transcription_task': transcribe_audio,
        'summarization_task': summarize_text
    }
    
    # Empty dictionary to store task objects (will be populated later)
    return {
        'download_task': None,
        'transcription_task': None, 
        'summarization_task': None
    }

def configure_download_task(task_dict, agent, youtube_url):
    """Configure the download task with runtime parameters."""
    configs = load_task_configs()
    task_dict['download_task'] = Task(
        config=configs['download_task'],
        agent=agent,
        context={'youtube_url': youtube_url},
        function=lambda: download_youtube_audio(youtube_url)
    )
    
def configure_transcription_task(task_dict, agent, audio_file_path):
    """Configure the transcription task with runtime parameters."""
    configs = load_task_configs()
    task_dict['transcription_task'] = Task(
        config=configs['transcription_task'],
        agent=agent,
        context={'audio_file_path': audio_file_path},
        function=lambda: transcribe_audio(audio_file_path)
    )
    
def configure_summarization_task(task_dict, agent, transcript_text, prompt_instruction):
    """Configure the summarization task with runtime parameters."""
    configs = load_task_configs()
    task_dict['summarization_task'] = Task(
        config=configs['summarization_task'],
        agent=agent,
        context={'prompt_instruction': prompt_instruction},
        function=lambda: summarize_text(transcript_text, prompt_instruction)
    ) 