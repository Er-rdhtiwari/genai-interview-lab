# tests/test_llm_integration.py
"""
Optional integration tests for live OpenAI and OSS endpoints.

These are skipped by default to avoid external calls. Enable by setting:
    RUN_LLM_INTEGRATION=1
and ensure the relevant endpoints/keys are configured:
    OPENAI_API_KEY, optional OPENAI_MODEL
    MODEL_SERVICE_BASE_URL (or OSS_MODEL_URL)
"""

import os

import pytest

from config.settings import Settings
from core.llm_client import LLMClient
from core.models import ModelProvider


def _integration_enabled() -> bool:
    return os.getenv("RUN_LLM_INTEGRATION") == "1"


@pytest.mark.integration
def test_openai_live_integration():
    """Call OpenAI via LLMClient when RUN_LLM_INTEGRATION=1 and key is set."""
    if not _integration_enabled():
        pytest.skip("RUN_LLM_INTEGRATION!=1")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    settings = Settings(
        use_mock_llm=False,
        openai_api_key=api_key,
        openai_model=model,
    )
    client = LLMClient(settings)

    result = client.generate_text(
        "Generate a short greeting for integration testing.",
        provider=ModelProvider.OPENAI,
    )

    assert "mock" not in result.provider.lower()
    assert result.provider == "openai"
    assert result.text.strip()
    assert result.model == model


@pytest.mark.integration
def test_oss_live_integration():
    """
    Call OSS model-service via LLMClient when RUN_LLM_INTEGRATION=1 and endpoint is set.
    Expects the service to expose POST {MODEL_SERVICE_BASE_URL}/api/v1/generate.
    """
    if not _integration_enabled():
        pytest.skip("RUN_LLM_INTEGRATION!=1")

    base_url = os.getenv("MODEL_SERVICE_BASE_URL") or os.getenv("OSS_MODEL_URL")
    if not base_url:
        pytest.skip("MODEL_SERVICE_BASE_URL/OSS_MODEL_URL not set")

    settings = Settings(
        use_mock_llm=False,
        model_service_base_url=base_url,
        llm_default_provider="oss",
    )
    client = LLMClient(settings)

    result = client.generate_text(
        "Generate a short release note summary for integration testing.",
        provider=ModelProvider.OSS,
    )

    assert result.provider == "oss"
    assert result.text.strip()
