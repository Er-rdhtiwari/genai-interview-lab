from __future__ import annotations

"""
Streamlit UI for the Revision LLM PoC.

This is a thin UI layer that talks to the FastAPI backend:

- It does NOT call LLMs directly.
- It sends HTTP requests to /api/v1/explain on the backend.
- BACKEND_URL controls which backend to talk to.

Local dev:
    BACKEND_URL defaults to http://localhost:8000

Kubernetes / Docker:
    Set BACKEND_URL to the internal service URL,
    e.g. http://revision-llm-api:8000
"""

import os

import httpx
import streamlit as st

# Backend base URL:
# - Local dev: default http://localhost:8000
# - In Kubernetes: e.g. http://revision-llm-api:8000
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def call_backend(topic: str, detail_level: str) -> dict | None:
    """
    Call the FastAPI backend /api/v1/explain endpoint.

    Returns parsed JSON dict on success, or None on failure.
    """
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{BACKEND_URL}/api/v1/explain",
                json={"topic": topic, "detail_level": detail_level},
            )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Error calling backend: {exc}")
        return None


def main() -> None:
    """Render the Streamlit app."""
    st.set_page_config(page_title="Python & GenAI Interview Coach", layout="centered")

    st.title("🧠 Python & GenAI Interview Coach")
    st.caption(
        "Revision LLM PoC – FastAPI + LLMClient (mock / OpenAI / Ollama) with a simple Streamlit UI."
    )

    # Sidebar: show backend info
    with st.sidebar:
        st.header("Backend Settings")
        st.write("Current backend URL:")
        st.code(BACKEND_URL, language="bash")
        st.caption(
            "Override with BACKEND_URL env var (e.g., inside Docker or Kubernetes)."
        )

    st.subheader("Ask for an explanation")

    topic = st.text_input(
        "Topic",
        placeholder="e.g. Python virtual environments, OOP composition vs inheritance",
    )

    detail_level = st.radio(
        "Detail level",
        options=["short", "detailed"],
        index=0,
        horizontal=True,
    )

    # Main action button
    generate_clicked = st.button(
        "Generate Explanation",
        type="primary",
        disabled=not topic.strip(),
    )

    if generate_clicked:
        with st.spinner("Talking to your interview coach..."):
            data = call_backend(topic.strip(), detail_level)

        if data:
            provider = data.get("provider", "unknown")
            st.success(f"Provider: {provider}")

            st.markdown("### Explanation")
            st.write(data.get("explanation", ""))

            with st.expander("Raw response JSON"):
                st.json(data)


if __name__ == "__main__":
    main()
