"""
Application settings loaded from environment variables.
Uses pydantic-settings for validation and .env file support.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Central configuration for the Echoes of Vietnam backend."""

    # --- AI Providers ---
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    USE_MOCK_EMBEDDINGS: bool = True  # Set False when real API key is available

    # --- Musical Defaults ---
    DEFAULT_SCALE: str = "C_major_pentatonic"
    DEFAULT_TEMPO: int = 72
    DEFAULT_PROGRESSION: str = "knockin_verse"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # --- Paths ---
    OUTPUT_DIR: str = "output"
    DATA_DIR: str = "data"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton settings instance
settings = Settings()
