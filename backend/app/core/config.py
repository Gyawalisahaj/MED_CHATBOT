import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Medical RAG Chatbot"
    ENVIRONMENT: str = "development"

    # Groq API
    GROQ_API_KEY: str  # No default = Required. Pydantic will check the env file for this.
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # Vector Database (Intel VDMS)
    VDMS_HOST: str = "localhost"
    VDMS_PORT: int = 55555
    VDMS_COLLECTION: str = "../Document/Harrisons.pdf"

    # Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # RAG Parameters
    TOP_K: int = 7
    TEMPERATURE: float = 0.0

    # Pydantic Settings magic: This replaces manual load_dotenv()
    model_config = SettingsConfigDict(
        env_file=".local.env",      # Point directly to your custom filename
        env_file_encoding='utf-8',
        extra='ignore'              # Prevents crashing if extra vars are in your .env
    )

settings = Settings()