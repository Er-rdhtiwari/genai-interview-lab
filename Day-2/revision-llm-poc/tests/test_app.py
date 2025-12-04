from __future__ import annotations

"""
Tests for the FastAPI application.

Run from project root (with venv active and dev extras installed):

    pytest
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
def test_explain_happy_path() -> None:
    """
    Basic happy-path test that verifies:
    - endpoint responds with HTTP 200,
    - response JSON has expected fields and types,
    - provider is one of the known providers.
    """
    payload = {
        "topic": "Python virtual environments",
        "detail_level": "short",
    }

    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 200

    data = response.json()

    # Check basic shape
    assert data["topic"] == payload["topic"]
    assert isinstance(data["explanation"], str)
    assert data["explanation"]  # non-empty string

    # Provider should be one of our known labels
    assert data["provider"] in {"mock", "openai", "ollama"}

def test_explain_validation_error_on_invalid_detail_level() -> None:
    """
    When an invalid detail_level is provided, FastAPI/Pydantic should
    reject the request with a 422 Unprocessable Entity error.
    """
    payload = {
        "topic": "Some topic",
        "detail_level": "medium",  # invalid, not 'short' or 'detailed'
    }

    response = client.post("/api/v1/explain", json=payload)

    # FastAPI uses 422 for validation errors
    assert response.status_code == 422

    data = response.json()
    assert data["detail"]  # FastAPI error structure with validation details
