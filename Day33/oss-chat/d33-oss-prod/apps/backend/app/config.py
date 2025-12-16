from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "d33-oss-backend"
    log_level: str = "INFO"
    port: int = 8000

    # Provider
    llm_provider: str = "ollama"  # ollama|mock

    # Ollama
    ollama_base_url: str = "http://d33-oss-model:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_sec: int = 60

    # CORS
    cors_allow_origins: str = "https://d33-oss.rdhcloudlab.com,http://localhost:3000"

    # Readiness behavior
    readiness_check_model: bool = False

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]
