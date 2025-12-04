import importlib

import llm.client as llm_client
import app.qa_service as qa_service


def test_answer_question_returns_mock_and_sources(monkeypatch):
    # Force mock mode to avoid real API calls
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(llm_client, "client", None)

    # Reload to ensure the qa_service module picks up the mocked client
    importlib.reload(llm_client)
    importlib.reload(qa_service)

    result = qa_service.answer_question("What is RAG?", top_k=2)

    assert "answer" in result
    assert "sources" in result
    assert result["answer"] == "This is a mock answer based on the provided context."
    assert 1 <= len(result["sources"]) <= 2
    assert all("doc_id" in s and "title" in s and "score" in s for s in result["sources"])
import pytest

from app.qa_service import answer_question


def test_answer_question_returns_sources(monkeypatch):
    monkeypatch.setattr("app.qa_service.generate_answer", lambda prompt: "mocked answer")

    result = answer_question("Explain vector databases", top_k=2)

    assert result["answer"] == "mocked answer"
    assert result["sources"]
    assert len(result["sources"]) <= 2
    assert all("doc_id" in s and "title" in s and "score" in s for s in result["sources"])


def test_answer_question_handles_no_results(monkeypatch):
    # Force retrieval to return nothing
    monkeypatch.setattr("app.qa_service.retrieve_documents", lambda question, top_k=3: [])

    result = answer_question("gibberish that matches nothing", top_k=3)

    assert "couldn't find" in result["answer"].lower()
    assert result["sources"] == []
