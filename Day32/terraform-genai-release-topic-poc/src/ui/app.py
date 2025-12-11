# src/ui/app.py
import streamlit as st

st.set_page_config(page_title="Day32 GenAI Release Notes UI (d32-release)")

st.title("Day32 – GenAI Release Notes Assistant (Skeleton)")
st.write(
    """
    This is the initial Streamlit UI placeholder.

    In later parts, we will:
    - Add a form to enter a title + description,
    - Send a request to the FastAPI Release Notes API,
    - Display generated release notes + test scenarios,
    - Allow choosing between OpenAI and the OSS model service.
    """
)

st.info("Part 3: environment + structure only. Backend integration comes later.")
