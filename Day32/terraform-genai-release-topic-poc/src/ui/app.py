import os
import datetime as dt
from typing import Any, Dict, Optional

import httpx
import streamlit as st

# -------------------------------------------------------------------
# Basic config
# -------------------------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Day32 – GenAI Greeting PoC",
    page_icon="🎉",
    layout="centered",
)

# -------------------------------------------------------------------
# Small helper to call the FastAPI greeting endpoint
# -------------------------------------------------------------------


def call_greeting_api(
    name: str,
    dob: dt.date,
    provider: str,
) -> Dict[str, Any]:
    """
    Calls the FastAPI backend /api/v1/greeting/generate endpoint.

    Assumes the backend:
      - accepts JSON with fields: name, date_of_birth, provider
      - returns JSON with fields: greeting, used_provider, from_cache, is_birthday_month
    """
    url = f"{API_BASE_URL.rstrip('/')}/api/v1/greeting/generate"

    payload = {
        "name": name,
        "date_of_birth": dob.isoformat(),  # YYYY-MM-DD
        "provider": provider,              # "openai" | "oss" | "mock"
    }

    resp = httpx.post(url, json=payload, timeout=30.0)
    resp.raise_for_status()
    return resp.json()


def call_healthcheck() -> Optional[Dict[str, Any]]:
    """
    Optional: call a simple /health endpoint if you have one.
    Safe to ignore errors.
    """
    url = f"{API_BASE_URL.rstrip('/')}/health"
    try:
        resp = httpx.get(url, timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


# -------------------------------------------------------------------
# UI Layout
# -------------------------------------------------------------------

st.title("Day32 – GenAI Greeting (d32-release)")
st.caption(
    "FastAPI + Redis + OpenAI / OSS model on EKS • Streamlit UI on separate app nodes"
)

greeting_tab, debug_tab = st.tabs(["🎉 Greeting", "🛠 Debug / Raw Info"])

# -------------------------------------------------------------------
# 🎉 Greeting Tab
# -------------------------------------------------------------------

with greeting_tab:
    st.subheader("Personalized Greeting")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your name", key="name_input", placeholder="Radhe Shyam")
    with col2:
        # Default to 25 years ago as a neutral value
        default_dob = dt.date.today().replace(year=max(dt.date.today().year - 25, 1900))
        dob = st.date_input(
            "Date of birth",
            key="dob_input",
            value=default_dob,
            max_value=dt.date.today(),
        )

    st.markdown("### Choose model provider")

    provider_label = st.radio(
        "Which LLM should generate the greeting?",
        options=["OpenAI", "OSS model (EKS)", "Mock (no real LLM)"],
        index=0,
        horizontal=False,
        label_visibility="collapsed",
    )

    provider_map = {
        "OpenAI": "openai",
        "OSS model (EKS)": "oss",
        "Mock (no real LLM)": "mock",
    }
    provider_value = provider_map[provider_label]

    if st.button("Generate greeting ✨", type="primary"):
        if not name.strip():
            st.warning("Please enter your name before generating a greeting.")
        else:
            try:
                with st.spinner("Calling FastAPI backend..."):
                    result = call_greeting_api(name=name.strip(), dob=dob, provider=provider_value)
            except httpx.HTTPError as http_exc:
                st.error(f"Error calling API: {http_exc}")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
            else:
                greeting_text = result.get("greeting", "No greeting returned.")
                used_provider = result.get("used_provider", provider_value)
                from_cache = bool(result.get("from_cache", False))
                is_birthday_month = bool(result.get("is_birthday_month", False))

                st.success(greeting_text)

                # Meta info box
                info_lines = []

                info_lines.append(f"**Model provider:** `{used_provider}`")
                if from_cache:
                    info_lines.append("**Cache:** ✅ Served from Redis")
                else:
                    info_lines.append("**Cache:** ❌ Fresh LLM call")

                if is_birthday_month:
                    info_lines.append("**Birthday month:** 🎂 Yes – special birthday-style greeting!")
                else:
                    info_lines.append("**Birthday month:** 📅 No – normal greeting")

                st.markdown("  \n".join(info_lines))

# -------------------------------------------------------------------
# 🛠 Debug / Raw Info Tab
# -------------------------------------------------------------------

with debug_tab:
    st.subheader("Backend & Environment Debug")

    st.write("**API base URL**", f"`{API_BASE_URL}`")

    if st.button("Check backend health"):
        health = call_healthcheck()
        if health is None:
            st.error("Health check failed or /health endpoint is not available.")
        else:
            st.success("Health check OK.")
            st.json(health)

    st.markdown("---")
    st.markdown(
        """
        **Notes**

        - This UI only talks to the FastAPI backend – it does *not* talk directly to Redis or the OSS model.
        - Redis caching and birthday-month logic happen in the backend service layer.
        - The `provider` field (`openai` / `oss` / `mock`) tells the backend which LLM path to use.
        """
    )
