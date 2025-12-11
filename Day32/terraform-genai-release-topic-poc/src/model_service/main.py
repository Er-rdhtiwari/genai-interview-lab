# src/model_service/main.py
from fastapi import FastAPI

from config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Day32 GenAI Model Service (d32-release)",
    version="0.1.0",
    description=(
        "Model service for the Day32 PoC. "
        "Later, it will wrap a small OSS model and can also route to OpenAI."
    ),
)


@app.get("/health")
def health() -> dict:
    """
    Basic health endpoint for the Model Service.

    In later parts, this service will expose a /generate endpoint that:
    - Calls a local open-source model running in this pod, or
    - Forwards to OpenAI (or other providers),
    based on configuration and/or UI selection.
    """
    return {
        "status": "ok",
        "service": "model-service",
        "env": settings.app_env,
        "llm_default_provider": settings.llm_default_provider,
        "use_mock_llm": settings.use_mock_llm,
        "part": 4,
    }
