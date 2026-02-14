import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Medical RAG Chatbot"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Groq (Replaced OpenAI)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    # Vector Database (Intel VDMS)
    VDMS_HOST: str = os.getenv("VDMS_HOST", "localhost")
    VDMS_PORT: int = int(os.getenv("VDMS_PORT", 55555))
    VDMS_COLLECTION: str = os.getenv("VDMS_COLLECTION", "medical_knowledge")

    # Models
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # RAG Parameters
    TOP_K: int = 3
    TEMPERATURE: float = 0.0  # Set to 0 for factual medical consistency

settings = Settings()