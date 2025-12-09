"""
Run locally:

    uvicorn app.main:app --reload
"""

import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from config.settings import Settings, get_settings
from core.llm_client import LLMClient
from core.models import ReleaseNoteRequest, ReleaseNoteResponse
from core.services import generate_release_note

logger = logging.getLogger(__name__)


def get_llm_client(settings: Settings = Depends(get_settings)) -> LLMClient:
    """
    FastAPI dependency that returns a configured LLMClient instance.
    """
    return LLMClient(settings=settings)


def get_provider_name(settings: Settings = Depends(get_settings)) -> str:
    """
    Derive provider name based on which key is configured.

    This lets the API surface which provider generated the response
    (e.g., 'openai' vs 'mock').
    """
    if settings.openai_api_key:
        return "openai"
    return "mock"


SettingsDep = Annotated[Settings, Depends(get_settings)]
LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]
ProviderDep = Annotated[str, Depends(get_provider_name)]

app = FastAPI(
    title="Terraform + GenAI Release Note Helper",
    version="0.1.0",
    description=(
        "Tiny FastAPI service that turns infra change descriptions into "
        "short release-note sentences using an LLM (or a mock)."
    ),
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """
    Simple health check endpoint.

    Used by load balancers, uptime checks, or quick manual verification.
    """
    return {"status": "ok"}


@app.post(
    "/api/v1/release-note",
    response_model=ReleaseNoteResponse,
    tags=["release-notes"],
)
def create_release_note(
    payload: ReleaseNoteRequest,
    llm_client: LLMClientDep,
    provider_name: ProviderDep,
) -> ReleaseNoteResponse:
    """
    Generate a release note sentence for the given infrastructure change summary.
    """
    try:
        return generate_release_note(
            payload=payload,
            llm_client=llm_client,
            provider_name=provider_name,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate release note: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate release note.",
        ) from exc
