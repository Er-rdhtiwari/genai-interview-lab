from __future__ import annotations

"""
Application settings module.

Uses pydantic BaseSettings to load configuration from environment variables
following 12-factor app principles.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Generic app settings
    app_env: str = "local"
    port: int = 8000

    # Logging
    log_level: str = "INFO"

    # LLM-related settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4.1-mini"

    # Local Ollama settings
    use_ollama: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    olama_api_key: Optional[str] = None
    hf_token: Optional[str] = None
    grok_model: Optional[str] = None

    class Config:
        # Load variables from .env file in local/dev environments.
        env_file = ".env"
        env_file_encoding = "utf-8"

        # Optional: allow environment variables to override .env
        # (this is the default behavior).
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    lru_cache ensures we create the Settings object only once per process,
    which is typical for config in web applications.
    """
    return Settings()
