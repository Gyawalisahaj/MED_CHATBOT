import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Medical RAG Chatbot"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # Vector Database (Intel VDMS)
    VDMS_HOST: str = os.getenv("VDMS_HOST", "localhost")
    VDMS_PORT: int = int(os.getenv("VDMS_PORT", 55555))
    VDMS_COLLECTION: str = "medical_knowledge"

    # Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "gpt-4-turbo-preview"

    # RAG Parameters
    TOP_K: int = 3
    TEMPERATURE: float = 0.1


settings = Settings()
