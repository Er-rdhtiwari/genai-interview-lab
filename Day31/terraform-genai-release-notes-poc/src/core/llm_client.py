import logging
from typing import Optional

from openai import OpenAI

from config.settings import Settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Simple LLM client abstraction.

    - Uses OpenAI Chat Completions if OPENAI_API_KEY is configured.
    - Falls back to a deterministic mock response in all other cases.

    This keeps external API details in one place and makes it easy to:
    - unit test the rest of the app,
    - switch providers later,
    - centralize logging and error handling.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Optional[OpenAI] = None
        self._provider_name: str = "mock"

        if settings.openai_api_key:
            logger.info("Initializing OpenAI client for LLMClient.")
            # New OpenAI SDK style
            self._client = OpenAI(api_key=settings.openai_api_key)
            self._provider_name = "openai"
        else:
            logger.info(
                "No OPENAI_API_KEY found. LLMClient will operate in MOCK mode."
            )

    @property
    def provider_name(self) -> str:
        """Return the provider name used by this client ('openai' or 'mock')."""
        return self._provider_name

    def generate_text(self, prompt: str) -> str:
        """
        Generate a short text completion for the given prompt.

        If OpenAI is not configured or a call fails, returns a deterministic
        MOCK_LLM_RESPONSE string for reliability.
        """
        # If no real client is configured, always return mock response
        if self._client is None:
            logger.info("Using mock LLM response (no provider configured).")
            return f"MOCK_LLM_RESPONSE for: {prompt}"

        try:
            logger.info("Calling OpenAI chat completions for prompt.")
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a concise release-note helper. "
                            "You produce one short sentence suitable for "
                            "a changelog visible to engineers."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=80,
                temperature=0.3,
            )
            text = response.choices[0].message.content or ""
            logger.info("Received LLM response with %d characters.", len(text))
            return text.strip()
        except Exception as exc:  # noqa: BLE001
            # In a real system you might distinguish network errors, rate limits, etc.
            logger.error("OpenAI call failed: %s. Falling back to mock.", exc)
            return f"MOCK_LLM_RESPONSE for: {prompt}"
