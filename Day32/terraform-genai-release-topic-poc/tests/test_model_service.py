# tests/test_model_service.py
from fastapi.testclient import TestClient

from model_service.main import app


client = TestClient(app)


def test_model_service_generate_mock_mode():
    """Model service /api/v1/generate should return text + model fields."""
    resp = client.post("/api/v1/generate", json={"prompt": "Summarize change"})
    assert resp.status_code == 200
    data = resp.json()
    assert "text" in data
    assert "model" in data
    assert data["model"].startswith("oss")
