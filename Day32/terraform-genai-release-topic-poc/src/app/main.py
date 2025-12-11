# src/app/main.py
from fastapi import FastAPI, Query

from config.settings import get_settings
from core.llm_client import LLMClient
from core.models import (
    GreetingRequest,
    GreetingResponse,
    HealthResponse,
    ModelProvider,
    ReleaseNoteRequest,
    ReleaseNoteResponse,
)
from core.services import GreetingService, RedisCache, ReleaseNotesService

# Initialize shared components (simple "poor man's DI container")
settings = get_settings()
llm_client = LLMClient(settings)
redis_cache = RedisCache(settings=settings)

release_notes_service = ReleaseNotesService(
    settings=settings,
    llm_client=llm_client,
    cache=redis_cache,
)

greeting_service = GreetingService(
    settings=settings,
    llm_client=llm_client,
    cache=redis_cache,
)

app = FastAPI(
    title="Day32 GenAI Release Notes API (d32-release)",
    version="0.1.0",
    description=(
        "FastAPI backend for the Day32 GenAI Release Notes PoC.\n"
        "- Generates release notes + test scenarios using an LLM.\n"
        "- Provides greeting generation (birthday-aware) via LLM.\n"
        "- Uses Redis for caching responses.\n"
    ),
)


# ------------------------
# Health Endpoint
# ------------------------


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Basic health endpoint.

    - Used by Kubernetes readiness/liveness probes.
    - Useful for manual checks via browser or curl.
    """
    return HealthResponse(
        status="ok",
        service="release-notes-api",
        env=settings.app_env,
        llm_default_provider=settings.llm_default_provider,
        use_mock_llm=settings.use_mock_llm,
    )


# ------------------------
# Release Notes Endpoint
# ------------------------


@app.post(
    "/api/v1/release-notes/generate",
    response_model=ReleaseNoteResponse,
    summary="Generate release notes + test scenarios from a change description.",
)
def generate_release_notes(
    body: ReleaseNoteRequest,
    provider: ModelProvider | None = Query(
        default=None,
        description=(
            "Optional provider override: 'openai' or 'oss'. "
            "If omitted, the default from settings is used."
        ),
    ),
) -> ReleaseNoteResponse:
    """
    Generate a release note and 2–3 test scenarios.

    Flow:
    1. Build a cache key from the request body.
    2. Try Redis cache first.
    3. If cache miss, build an LLM prompt and call LLMClient:
        - 'openai' -> OpenAI Completion API,
        - 'oss'    -> hosted OSS model via model_service,
        - mock     -> if USE_MOCK_LLM=true or providers are unavailable.
    4. Parse text into ReleaseNoteResponse, store in cache, and return.
    """
    return release_notes_service.generate_release_notes(
        request=body,
        provider=provider,
    )


# ------------------------
# Greeting Endpoint
# ------------------------


@app.post(
    "/api/v1/greeting/generate",
    response_model=GreetingResponse,
    summary="Generate a greeting message (birthday-aware) via LLM.",
)
def generate_greeting(
    body: GreetingRequest,
) -> GreetingResponse:
    """
    Generate a greeting for a person using LLM (OpenAI or OSS).

    - Always uses Redis cache to avoid recomputation.
    - If the person's birth month equals the current month:
        -> Produces a 'birthday-month' style greeting.
    - Otherwise:
        -> Produces a normal greeting that can mention the birth month.

    The provider used:
    - body.provider if given (openai/oss),
    - otherwise settings.llm_default_provider.
    """
    return greeting_service.generate_greeting(request=body)
