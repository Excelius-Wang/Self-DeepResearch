import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo-preview")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
