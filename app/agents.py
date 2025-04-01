import os
import yaml
from crewai import Agent
from langchain_openai import ChatOpenAI

# Load agent configurations
def load_agent_configs(config_path="app/config/agents.yaml"):
    """Load agent configurations from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Set up the LLM
def get_llm(model=None):
    """Get the LLM instance with the specified model or default from env variable."""
    model = model or os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
    return ChatOpenAI(temperature=0.7, model=model)

# Define our agents
def create_agents():
    """Create all agents from configurations."""
    configs = load_agent_configs()
    agents = {}
    
    # Create downloader and transcriber agents with default model
    for key in ['youtube_downloader', 'audio_transcriber']:
        if key in configs:
            agents[key] = Agent(
                config=configs[key],
                llm=get_llm()
            )
    
    # Create summarizer agent with advanced model
    if 'content_summarizer' in configs:
        agents['content_summarizer'] = Agent(
            config=configs['content_summarizer'],
            llm=get_llm("gpt-4-turbo")
        )
    
    return agents 