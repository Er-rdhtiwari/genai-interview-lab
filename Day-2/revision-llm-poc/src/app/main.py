from __future__ import annotations

"""
FastAPI entrypoint for the explanation service.

Run locally (from project root):

    uvicorn app.main:app --reload

Make sure you have installed the package into your virtualenv:

    pip install .

and that your .env is set up:

    cp .env.example .env
    # edit .env if you want to enable OpenAI or Ollama
"""

import logging

from fastapi import Depends, FastAPI

from config.logging import setup_logging
from config.settings import Settings, get_settings
from core.llm_client import LLMClient
from core.models import ExplainRequest, ExplainResponse
from core.services import ExplanationService


# Initialize settings and logging once at import time.
_settings: Settings = get_settings()
setup_logging(_settings)

app = FastAPI(
    title="Revision LLM PoC",
    version="0.1.0",
    description=(
        "Tiny LLM-backed explanation API for Python & GenAI topics. "
        "Supports mock, OpenAI, and local Ollama providers."
    ),
)


def get_explanation_service() -> ExplanationService:
    """
    FastAPI dependency that provides an ExplanationService instance.

    We build it from environment-based settings so configuration is centralized
    and consistent with the rest of the app.
    """
    llm_client = LLMClient(settings=_settings)
    return ExplanationService(llm_client=llm_client)


@app.post(
    "/api/v1/explain",
    response_model=ExplainResponse,
    summary="Generate an explanation for a Python/GenAI topic.",
)
def explain_topic(
    request: ExplainRequest,
    service: ExplanationService = Depends(get_explanation_service),
) -> ExplainResponse:
    """
    Accept a topic and optional detail_level, return an LLM-generated explanation.

    This endpoint is intentionally simple but follows a realistic layering:
    - FastAPI handles HTTP and validation via Pydantic models.
    - ExplanationService contains business logic (prompt building + orchestration).
    - LLMClient abstracts the underlying LLM provider (mock/OpenAI/Ollama).
    """
    logging.getLogger(__name__).info(
        "HTTP request received for /api/v1/explain topic=%s detail_level=%s",
        request.topic,
        request.detail_level,
    )
    return service.generate_explanation(request)
