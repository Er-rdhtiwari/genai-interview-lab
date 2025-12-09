from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Verify the health endpoint returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_release_note_endpoint_happy_path() -> None:
    """
    Verify that the release note endpoint returns a valid response
    in either mock or real provider mode.
    """
    payload = {
        "change_summary": (
            "Switched dev RDS instance from db.t3.micro to db.t3.small "
            "to handle higher load."
        ),
        "tone": "neutral",
    }

    response = client.post("/api/v1/release-note", json=payload)
    assert response.status_code == 200

    body = response.json()

    # Basic shape checks
    assert "release_note" in body
    assert "provider" in body

    assert isinstance(body["release_note"], str)
    assert len(body["release_note"]) > 0

    # We allow either provider for flexibility:
    # - "mock" if no OPENAI_API_KEY is configured
    # - "openai" if a valid key is present
    assert body["provider"] in ("mock", "openai")


def test_release_note_validation_error_for_short_summary() -> None:
    """
    If the change_summary is too short, FastAPI/Pydantic should reject it
    with a 422 validation error.
    """
    payload = {
        "change_summary": "Hi",  # shorter than min_length=5
        "tone": "neutral",
    }

    response = client.post("/api/v1/release-note", json=payload)
    assert response.status_code == 422
