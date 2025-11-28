# llm/client.py
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "10"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    # Fail fast so you don't get confusing runtime errors later
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

# Authenticated client
client = OpenAI(api_key=OPENAI_API_KEY)

class LLMTimeoutError(Exception):
    pass

def generate_answer(prompt: str, temperature: float = 0.2) -> str:
    """
    Call the LLM API with the given prompt.
    In PoC: this can just return a mock string.
    Later: integrate with real OpenAI / provider SDK.
    """
    logger.info("Calling LLM", extra={"model": LLM_MODEL})

    try:
        # Pseudo-code for actual LLM call:
        #
        response = client.chat.completions.create(
            model=LLM_MODEL,
            input=prompt,
            temperature=temperature,
            timeout=LLM_TIMEOUT_SECONDS,
        )
        return response.output_text

        # For Day 1: return a dummy response
        # return "This is a mock answer based on the provided context."
    except TimeoutError as e:
        logger.error("LLM timeout", extra={"model": LLM_MODEL})
        raise LLMTimeoutError("LLM call timed out") from e
    except Exception:
        logger.exception("Unexpected error in LLM call")
        raise
