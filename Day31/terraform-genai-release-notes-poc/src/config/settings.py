from functools import lru_cache
from typing import Optional
import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    This class centralizes all config needed by the app:
    - environment and logging configuration
    - LLM provider API keys
    - optional database connection info (for future use)
    """

    # App-level settings
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_name: str = Field(default="terraform-genai-llm-poc", alias="APP_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    port: int = Field(default=8000, alias="PORT")

    # LLM provider keys (all optional; we can run in mock mode)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    olama_api_key: Optional[str] = Field(default=None, alias="OLAMA_API_KEY")
    hf_token: Optional[str] = Field(default=None, alias="HF_TOKEN")
    grok_model: Optional[str] = Field(default=None, alias="GROK_MODEL")

    # Optional DB configuration (not used directly yet, but ready for RDS)
    db_host: Optional[str] = Field(default=None, alias="DB_HOST")
    db_port: Optional[int] = Field(default=None, alias="DB_PORT")
    db_name: Optional[str] = Field(default=None, alias="DB_NAME")
    db_user: Optional[str] = Field(default=None, alias="DB_USER")
    db_password: Optional[str] = Field(default=None, alias="DB_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",             # load from .env by default
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    This ensures we:
    - read env vars only once,
    - configure logging once,
    - reuse the same Settings object across the app.
    """
    settings = Settings()

    # Configure root logging based on settings.log_level
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    logger.info("Loaded settings for env=%s", settings.app_env)
    return settings
