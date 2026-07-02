"""
Configuration management using Pydantic Settings.
Loads environment variables from .env files.
"""
from pathlib import Path
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

_CURRENT_FILE = Path(__file__).resolve()

# 🎯 FIX: Split these back into two separate lines
_BACKEND_DIR = _CURRENT_FILE.parent.parent.parent
_ROOT_DIR = _BACKEND_DIR.parent

class Settings(BaseSettings):
    """
    Medical RAG Chatbot Configuration.
    All settings load from environment variables (.env file).
    """
    
    # ==================== PROJECT SETTINGS ====================
    PROJECT_NAME: str = "Medical RAG Chatbot"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # ==================== GROQ API ====================
    GROQ_API_KEY: str = ""  # Required: https://console.groq.com/
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # ==================== VECTOR DATABASE ====================
    VECTOR_STORE_PATH: str = str(_BACKEND_DIR / "vector_store" / "faiss_index")
    
    # ==================== EMBEDDING MODEL ====================
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"  # Can be 'cpu' or 'cuda'
    
    # ==================== RAG PARAMETERS ====================
    TOP_K: int = 7           # Number of documents to retrieve
    TEMPERATURE: float = 0.0  # Model temperature (0 = deterministic, 1 = creative)
    MAX_RETRIES: int = 3
    
    # ==================== DATABASE ====================
    DATABASE_URL: str = f"sqlite:///{_BACKEND_DIR / 'medical_chatbot.db'}"
    
    # ==================== CACHE ====================
    CACHE_TTL: int = 3600  # Cache time-to-live in seconds
    ENABLE_CACHE: bool = True
    
    # ==================== FRONTEND ====================
    FRONTEND_URL: str = "http://localhost:8501"
    CORS_ORIGINS: list = ["*"]
    
    # ==================== PDF INGESTION ====================
    PDF_FOLDER: str = str(_ROOT_DIR / "Document")
    PDF_EXTENSIONS: list = [".pdf"]
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 120
    
    # Pydantic V2 config
    model_config = SettingsConfigDict(
        # env_prefix="MEDICAL_CHATBOT_",
        env_file=os.path.join(_BACKEND_DIR, ".env"),
        env_file_encoding='utf-8',
        extra="allow",
        case_sensitive=False
    )


# Create global settings instance
settings = Settings()
