# src/core/llm_client.py
import logging
from typing import Optional

import httpx

from config.settings import Settings
from core.models import LLMGenerationResult, ModelProvider


logger = logging.getLogger(__name__)


class LLMClient:
    """
    Facade over all LLM backends used in this PoC.

    Responsibilities:
    - Decide WHICH provider to use (OpenAI vs OSS) for a given request.
    - Call the provider in a safe way (catch errors, log, fall back to mock).
    - Return a unified LLMGenerationResult so higher-level services don't care
      about provider-specific details.

    Providers:
    - 'openai' -> OpenAI API (if key is present).
    - 'oss'    -> Hosted model_service (running on the EKS model node group).
    - mock     -> Used when USE_MOCK_LLM=true or provider is unavailable.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._openai_client = None

        # Best-effort OpenAI initialization (chat completions, API v1/v2 compatible)
        if settings.openai_api_key:
            try:
                from openai import OpenAI

                self._openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("LLMClient initialized with OpenAI backend.")
            except Exception as exc:  # pragma: no cover - env specific
                logger.warning("Failed to initialize OpenAI client: %s", exc)
        else:
            logger.info("No OPENAI_API_KEY set; OpenAI backend will be disabled.")

    # ---------------------
    # Public API
    # ---------------------

    def generate_text(
        self,
        prompt: str,
        provider: Optional[ModelProvider] = None,
    ) -> LLMGenerationResult:
        """
        Generate text using the configured LLM backend.

        Selection order:
        1) If USE_MOCK_LLM=true -> always return mock.
        2) Else, determine provider from argument or settings.llm_default_provider.
        3) Dispatch to the appropriate backend (OpenAI or OSS model_service).
        4) On any error, log and fall back to a mock result.

        This method is synchronous and safe to call from normal FastAPI endpoints.
        """
        provider_str = self._resolve_provider(provider)
        explicit_provider = provider is not None

        # Respect global mock flag only when no explicit provider override was chosen.
        if self._settings.use_mock_llm and not explicit_provider:
            logger.info("LLMClient in mock mode. provider=%s", provider_str)
            return self._mock_response(prompt, provider_str, model="mock")

        try:
            if provider_str == ModelProvider.OPENAI.value:
                return self._call_openai(prompt)
            elif provider_str == ModelProvider.OSS.value:
                return self._call_oss_model_service(prompt)
            else:
                logger.warning(
                    "Unknown provider '%s'; falling back to mock.", provider_str
                )
                return self._mock_response(prompt, provider_str, model="mock-unknown")
        except Exception as exc:  # pragma: no cover - network / provider issues
            logger.warning(
                "LLM provider call failed (provider=%s). Falling back to mock. Error: %s",
                provider_str,
                exc,
            )
            return self._mock_response(
                prompt, provider_str, model="mock-fallback-error"
            )

    # ---------------------
    # Internal helpers
    # ---------------------

    def _resolve_provider(
        self,
        provider: Optional[ModelProvider],
    ) -> str:
        """
        Decide which provider string to use.

        - If an explicit provider enum is passed, use that.
        - Otherwise use settings.llm_default_provider.
        """
        if provider is not None:
            return provider.value

        default_provider = (self._settings.llm_default_provider or "openai").lower()
        return default_provider

    def _mock_response(
        self,
        prompt: str,
        provider: str,
        model: Optional[str] = None,
    ) -> LLMGenerationResult:
        """
        Build a deterministic mock response.

        This is used for:
        - Local development without credentials,
        - CI tests,
        - Fallback when real providers fail.
        """
        text = f"[MOCK:{provider}] Response for prompt: {prompt[:200]}"
        return LLMGenerationResult(text=text, provider=f"mock-{provider}", model=model)

    # ---------------------
    # Provider implementations
    # ---------------------

    def _call_openai(self, prompt: str) -> LLMGenerationResult:
        """
        Call OpenAI's chat completion API (works with SDK v1/v2).
        """
        if self._openai_client is None:
            logger.warning("OpenAI backend requested but not initialized; using mock.")
            return self._mock_response(prompt, "openai", model=None)

        model_name = self._settings.openai_model or "gpt-4o-mini"
        response = self._openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise assistant that writes release notes and greetings."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.4,
        )
        text = response.choices[0].message.content.strip()
        return LLMGenerationResult(
            text=text,
            provider="openai",
            model=model_name,
        )

    def _call_oss_model_service(self, prompt: str) -> LLMGenerationResult:
        """
        Call the hosted OSS model service via HTTP.

        The model service is expected to run on the EKS model node group and expose
        an endpoint like:

            POST {MODEL_SERVICE_BASE_URL}/api/v1/generate
            body: {"prompt": "..."}  # can be extended with provider/model later

        For this PoC, we assume the response JSON has at least:
            {"text": "...", "model": "tiny-oss-model"}

        We'll implement that endpoint in the model_service app in a later part.
        """
        base_url = self._settings.model_service_base_url.rstrip("/")
        url = f"{base_url}/api/v1/generate"

        logger.info("Calling OSS model service at %s", url)
        response = httpx.post(
            url,
            json={"prompt": prompt},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        text = data.get("text", "")
        model = data.get("model", "oss-model")

        return LLMGenerationResult(
            text=text,
            provider="oss",
            model=model,
        )
