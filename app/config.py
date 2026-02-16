"""
Configuration management for the Multi-Model AI Chat System.
Loads environment variables and provides centralized config access.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Configuration (Free Tier - Flash only)
    GEMINI_MODEL_GENERAL: str = "gemini-2.5-flash"
    GEMINI_MODEL_CODE: str = "gemini-2.5-flash"
    GEMINI_MODEL_MATH: str = "gemini-2.5-flash"
    GEMINI_MODEL_DOCUMENT: str = "gemini-2.5-flash"
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "./vectorstore"
    TOP_K_RETRIEVAL: int = 3
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Upload Configuration
    UPLOAD_DIR: str = "./data"
    MAX_FILE_SIZE_MB: int = 10
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please set it in .env file or environment."
            )
    
    @classmethod
    def get_model_config(cls, model_type: str) -> dict:
        """Get model configuration for a specific type."""
        model_map = {
            "general": cls.GEMINI_MODEL_GENERAL,
            "code": cls.GEMINI_MODEL_CODE,
            "math": cls.GEMINI_MODEL_MATH,
            "document": cls.GEMINI_MODEL_DOCUMENT,
        }
        
        return {
            "model_name": model_map.get(model_type, cls.GEMINI_MODEL_GENERAL),
            "temperature": 0.3 if model_type != "math" else 0.1,
            "max_output_tokens": 2048,
        }


# Create config instance
config = Config()
