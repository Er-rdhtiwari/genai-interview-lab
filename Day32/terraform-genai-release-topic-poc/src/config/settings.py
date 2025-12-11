# src/config/settings.py
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Central application configuration.

    Notes:
    - Reads from environment variables (12-factor style).
    - .env is used ONLY in local/dev for convenience.
    - In EKS, env vars and Secrets Manager / K8s secrets take over.
    """

    # --- LLM / Provider keys ---
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    olama_api_key: Optional[str] = Field(default=None, env="OLAMA_API_KEY")
    hf_token: Optional[str] = Field(default=None, env="HF_TOKEN")
    grok_model: Optional[str] = Field(default=None, env="GROK_MODEL")

    # --- App runtime ---
    app_env: str = Field(default="local", env="APP_ENV")
    port: int = Field(default=8000, env="PORT")

    # --- Database (RDS / local Postgres) ---
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_user: str = Field(default="genai", env="DB_USER")
    db_password: str = Field(default="genai", env="DB_PASSWORD")
    db_name: str = Field(default="genai", env="DB_NAME")

    # --- Redis ---
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL (ElastiCache in AWS).",
    )

    # --- LLM routing ---
    llm_default_provider: str = Field(
        default="openai",
        env="LLM_DEFAULT_PROVIDER",
        description="Default provider: 'openai' or 'oss'.",
    )
    use_mock_llm: bool = Field(
        default=True,
        env="USE_MOCK_LLM",
        description="If true, force mock responses (no real API calls).",
    )

    # --- Service URLs (used by UI / cross-service calls) ---
    release_api_base_url: str = Field(
        default="http://localhost:8000",
        env="RELEASE_API_BASE_URL",
        description="Base URL for the Release Notes API.",
    )
    model_service_base_url: str = Field(
        default="http://localhost:8001",
        env="MODEL_SERVICE_BASE_URL",
        description="Base URL for the Model Service.",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Return a singleton Settings instance.
    This ensures we don't re-parse env variables for every request.
    """
    return Settings()
