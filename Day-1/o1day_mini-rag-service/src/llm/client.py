# llm/client.py
import os
import logging
from dotenv import load_dotenv
from openai import APITimeoutError, OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "10"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Lazy client: stays None when no key is configured so tests/local dev can mock
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class LLMTimeoutError(Exception):
    """Raised when the LLM call times out."""
    pass

def _mock_answer(prompt: str) -> str:
    # Deterministic string so tests can assert on it
    return "This is a mock answer based on the provided context."

def generate_answer(prompt: str, temperature: float = 0.2) -> str:
    """
    Call the LLM API with the given prompt.
    If no OPENAI_API_KEY is configured, return a deterministic mock response.
    """
    if not client:
        logger.info("No OPENAI_API_KEY set; returning mock answer")
        return _mock_answer(prompt)

    logger.info("Calling LLM", extra={"model": LLM_MODEL})

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            timeout=LLM_TIMEOUT_SECONDS,
        )
        return response.choices[0].message.content
    except APITimeoutError as e:
        logger.error("LLM timeout", extra={"model": LLM_MODEL})
        raise LLMTimeoutError("LLM call timed out") from e
    except Exception:
        logger.exception("Unexpected error in LLM call")
        raise
