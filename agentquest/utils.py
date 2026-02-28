import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables if they haven't been loaded already
load_dotenv()

def get_configured_llm() -> LLM | str | None:
    """
    Returns the explicitly configured LLM base on the MODEL environment variable, 
    so standard CrewAI can interface seamlessly with Anthropic, Gemini, Ollama, etc.
    If MODEL is not set, it returns None, falling back to CrewAI's default (OpenAI).
    """
    model_name = os.environ.get("MODEL")
    if not model_name:
        return None
        
    return LLM(model=model_name)
