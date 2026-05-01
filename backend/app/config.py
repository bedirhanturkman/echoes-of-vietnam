"""
Configuration settings for The Echoing Threshold.
Loads from .env file using pydantic-settings.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AI Model API Keys
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # App Settings
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    DEFAULT_CHARACTER: str = "bob_dylan_1973"
    OUTPUT_DIR: str = "output"

    # Historical Context
    HISTORICAL_PERIOD: int = 1973

    # Feature Flags
    USE_MOCK_EMBEDDINGS: bool = False

    # Musical Defaults
    DEFAULT_SCALE: str = "C_major_pentatonic"
    DEFAULT_TEMPO: int = 72
    DEFAULT_PROGRESSION: str = "knockin_verse"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
