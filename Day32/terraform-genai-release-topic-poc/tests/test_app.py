# tests/test_app.py
from datetime import date

from fastapi.testclient import TestClient

from app.main import app
import core.llm_client as llm_client_module


client = TestClient(app)


def test_health_endpoint():
    """Health endpoint should return basic service info and status 'ok'."""
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "release-notes-api"
    assert "env" in body
    assert "llm_default_provider" in body
    assert "use_mock_llm" in body


def test_generate_release_notes_mock_mode():
    """
    Release notes endpoint should return a structured response even in mock mode.

    We rely on USE_MOCK_LLM=true (from .env.example), so the LLM text will be
    deterministic mock content, but the endpoint should still be 200 and shape
    should match ReleaseNoteResponse.
    """
    payload = {
        "title": "Improve login error messages",
        "description": (
            "We clarified error messages when users enter the wrong password "
            "or when their account is locked."
        ),
        "risk_level": "low",
        "impact_area": "authentication",
    }

    response = client.post("/api/v1/release-notes/generate", json=payload)
    assert response.status_code == 200

    body = response.json()
    # Basic shape checks
    assert "release_note" in body
    assert "test_scenarios" in body
    assert "provider" in body
    assert "model" in body
    assert "cached" in body

    # In mock mode, provider should contain 'mock'
    assert "mock" in body["provider"]


def test_generate_greeting_birthday_month_flag():
    """
    Greeting endpoint should correctly set is_birthday_month
    when DOB month matches the current system month.

    We construct a DOB with today's day + month so we know the flag must be True.
    """
    today = date.today()
    dob = date(year=today.year - 20, month=today.month, day=today.day)
    dob_str = dob.isoformat()

    payload = {
        "name": "Test User",
        "date_of_birth": dob_str,
        # provider is optional; it will use default from settings if omitted.
    }

    response = client.post("/api/v1/greeting/generate", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert "greeting_message" in body
    assert "is_birthday_month" in body
    assert "provider" in body
    assert "model" in body

    # Since we used a DOB with the current month, flag must be True
    assert body["is_birthday_month"] is True


def test_release_notes_oss_provider(monkeypatch):
    """
    OSS provider path should call the model service client (mocked) and return its model name.
    """
    from app import main as api_main

    # Disable mock mode so the OSS path is exercised
    monkeypatch.setattr(api_main.settings, "use_mock_llm", False, raising=False)
    monkeypatch.setattr(api_main.llm_client._settings, "use_mock_llm", False, raising=False)
    monkeypatch.setattr(api_main.redis_cache, "get_json", lambda key: None, raising=False)
    monkeypatch.setattr(api_main.redis_cache, "set_json", lambda key, value, ttl: None, raising=False)

    def fake_post(url, json, timeout):
        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "text": "Release note generated line\n- scenario A\n- scenario B",
                    "model": "oss-test-model",
                }

        return Resp()

    monkeypatch.setattr(llm_client_module.httpx, "post", fake_post)

    payload = {
        "title": "Improve login error messages",
        "description": "Clarified login errors for wrong password vs locked account.",
        "risk_level": "low",
        "impact_area": "authentication",
    }

    response = client.post(
        "/api/v1/release-notes/generate",
        params={"provider": "oss"},
        json=payload,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "oss"
    assert body["model"] == "oss-test-model"
    assert body["cached"] is False
