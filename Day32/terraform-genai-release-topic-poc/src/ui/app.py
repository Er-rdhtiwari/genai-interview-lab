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

# Small CSS to make the UI a bit more "app-like"
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    .greeting-card {
        padding: 1.5rem 1.75rem;
        border-radius: 0.9rem;
        background: linear-gradient(135deg, #ffecec, #fff7e6);
        border: 1px solid #ffd6b3;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        margin-top: 1rem;
    }
    .greeting-main-text {
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .meta-badges {
        margin-top: 0.75rem;
        font-size: 0.9rem;
    }
    .pill {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }
    .pill-provider {
        background-color: #e3f2fd;
        color: #0d47a1;
    }
    .pill-cache-hit {
        background-color: #e8f5e9;
        color: #1b5e20;
    }
    .pill-cache-miss {
        background-color: #fff3e0;
        color: #e65100;
    }
    .pill-birthday-yes {
        background-color: #fce4ec;
        color: #880e4f;
    }
    .pill-birthday-no {
        background-color: #eceff1;
        color: #37474f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Small helper to call the FastAPI greeting endpoint
# -------------------------------------------------------------------


def call_greeting_api(
    name: str,
    dob: dt.date,
    provider: Optional[str],
) -> Dict[str, Any]:
    """
    Calls the FastAPI backend /api/v1/greeting/generate endpoint.

    Assumes the backend accepts JSON with fields: name, date_of_birth, provider
    (provider optional) and returns JSON with fields:
    greeting_message, provider, model, is_birthday_month, cached.
    """
    url = f"{API_BASE_URL.rstrip('/')}/api/v1/greeting/generate"

    payload = {
        "name": name,
        "date_of_birth": dob.isoformat(),  # YYYY-MM-DD
    }
    if provider:
        payload["provider"] = provider  # "openai" | "oss"

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

st.markdown('<div class="main-title">🎉 Day32 – GenAI Greeting (d32-release)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">FastAPI · Redis · OpenAI / OSS model on EKS · Streamlit UI on app nodes</div>',
    unsafe_allow_html=True,
)

greeting_tab, debug_tab = st.tabs(["🎂 Greeting", "🛠 Debug / Raw Info"])

# -------------------------------------------------------------------
# 🎂 Greeting Tab
# -------------------------------------------------------------------

with greeting_tab:
    st.subheader("Tell me about you")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your name", key="name_input", placeholder="Radhe Shyam")
    with col2:
        # Default to 25 years ago as a neutral value
        today = dt.date.today()
        default_dob = today.replace(year=max(today.year - 25, 1900))
        dob = st.date_input(
            "Date of birth",
            key="dob_input",
            value=default_dob,
            max_value=today,
        )

    st.markdown("---")
    st.markdown("#### Choose model provider")

    provider_label = st.radio(
        "Which LLM should generate the greeting?",
        options=["OpenAI (default)", "OSS model (EKS)", "Use backend mock (if enabled)"],
        index=0,
        horizontal=True,
    )

    provider_map = {
        "OpenAI (default)": "openai",
        "OSS model (EKS)": "oss",
        # When mock is selected, we omit provider so FastAPI accepts the payload.
        "Use backend mock (if enabled)": None,
    }
    provider_value = provider_map[provider_label]

    st.markdown("")
    generate_col, _ = st.columns([1, 3])
    with generate_col:
        generate_clicked = st.button("Generate greeting ✨", type="primary", use_container_width=True)

    if generate_clicked:
        if not name.strip():
            st.warning("Please enter your name before generating a greeting.")
        else:
            try:
                with st.spinner("Talking to the GenAI backend…"):
                    result = call_greeting_api(name=name.strip(), dob=dob, provider=provider_value)
            except httpx.HTTPError as http_exc:
                st.error(f"Error calling API: {http_exc}")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
            else:

                greeting_text = (
                    result.get("greeting_message")
                    or result.get("greeting")
                    or "No greeting returned."
                )
                used_provider = result.get("provider") or (provider_value or "unknown")
                from_cache = bool(result.get("cached", False))
                is_birthday_month = bool(result.get("is_birthday_month", False))
                model_used = result.get("model")

                # 🎈 Extra fun if it's birthday month
                if is_birthday_month:
                    st.balloons()
                    st.success("🎂 Birthday vibes detected! You’re in your birthday month 🎉")

                # Main greeting card
                st.markdown(
                    f"""
                    <div class="greeting-card">
                      <div class="greeting-main-text">
                        {"🎂" if is_birthday_month else "✨"} {greeting_text}
                      </div>
                      <div class="meta-badges">
                        <span class="pill pill-provider">
                          Provider: {used_provider}
                        </span>
                        <span class="pill {'pill-cache-hit' if from_cache else 'pill-cache-miss'}">
                          Cache: {"hit (Redis)" if from_cache else "miss (fresh LLM call)"}
                        </span>
                        {"<span class='pill pill-provider'>Model: " + model_used + "</span>" if model_used else ""}
                        <span class="pill {'pill-birthday-yes' if is_birthday_month else 'pill-birthday-no'}">
                          Birthday month: {"Yes 🎂" if is_birthday_month else "No 📅"}
                        </span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Extra contextual line below card
                if is_birthday_month:
                    st.info(
                        "Pro tip: Even if today is not the exact date, "
                        "your birthday *month* still gets extra love from the GenAI model 💖"
                    )
                else:
                    st.info(
                        "It’s not your birthday month right now, "
                        "but the model still cooked up something special for you ✨"
                    )

# -------------------------------------------------------------------
# 🛠 Debug / Raw Info Tab
# -------------------------------------------------------------------

with debug_tab:
    st.subheader("Backend & Environment Debug")

    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**API base URL**")
        st.code(API_BASE_URL, language="bash")
    with col_b:
        st.write("**Today**")
        st.code(dt.date.today().isoformat(), language="bash")

    st.markdown("")
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
        - The optional `provider` field (`openai` / `oss`) tells the backend which LLM path to use;
          if `USE_MOCK_LLM=true` the backend will still return mock responses.
        """
    )
