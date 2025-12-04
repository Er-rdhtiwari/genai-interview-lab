from __future__ import annotations

"""
LLM client abstractions.

This module defines:
- BaseLLMProvider: an abstract interface for providers,
- OpenAILLMProvider: concrete provider using OpenAI Chat API,
- LocalOllamaProvider: provider calling a local Ollama server,
- MockLLMProvider: deterministic provider for local/dev,
- LLMClient: facade that chooses a provider based on Settings.

The rest of the app talks only to LLMClient.generate_text(), not directly
to provider-specific SDKs. This is exactly the OOP + abstraction pattern
you want in LLM-heavy backends.
"""

import logging
from abc import ABC, abstractmethod

import httpx
from openai import OpenAI

from config.settings import Settings, get_settings


logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate text from the given prompt."""
        raise NotImplementedError


class MockLLMProvider(BaseLLMProvider):
    """Simple deterministic LLM provider for local/dev use."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def generate_text(self, prompt: str) -> str:
        """
        Return a deterministic response which is safe for local runs and tests.

        This avoids any external network calls and removes token costs.
        """
        self._logger.info("Using MockLLMProvider for prompt.")
        return f"MOCK_LLM_RESPONSE for: {prompt[:80]}"


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI-backed LLM provider implementation."""

    def __init__(self, settings: Settings, logger: logging.Logger | None = None) -> None:
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAILLMProvider.")
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        # OpenAI client from the openai>=1.x SDK
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    def generate_text(self, prompt: str) -> str:
        """
        Call OpenAI Chat Completions API with basic parameters.

        Any error during the call is logged and we fall back to a deterministic
        mock-style response to keep the service reliable.
        """
        self._logger.info("Calling OpenAI model %s", self._model)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.2,
            )
            message = response.choices[0].message
            content = message.content or ""
            if isinstance(content, list):
                # Newer SDKs can return a list of content parts
                text_parts = [part.text for part in content if hasattr(part, "text")]
                return "".join(text_parts)
            return str(content)
        except Exception as exc:  # noqa: BLE001
            self._logger.error("OpenAI call failed, falling back to mock. Error: %s", exc)
            return f"MOCK_LLM_RESPONSE (fallback-openai) for: {prompt[:80]}"


class LocalOllamaProvider(BaseLLMProvider):
    """
    Provider implementation for a local Ollama server.

    Assumes an Ollama HTTP server is running (by default at http://localhost:11434)
    and exposes the /api/generate endpoint.
    """

    def __init__(self, settings: Settings, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._base_url = settings.ollama_base_url
        self._model = settings.ollama_model

    def generate_text(self, prompt: str) -> str:
        """
        Call the local Ollama HTTP API to generate text.

        If the call fails (server not running, network error, etc.), we log the
        error and fall back to a deterministic mock-style response.
        """
        self._logger.info("Calling local Ollama model %s at %s", self._model, self._base_url)
        try:
            with httpx.Client(base_url=self._base_url, timeout=30.0) as client:
                response = client.post(
                    "/api/generate",
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("response") or ""
                return str(text)
        except Exception as exc:  # noqa: BLE001
            self._logger.error("Ollama call failed, falling back to mock. Error: %s", exc)
            return f"MOCK_LLM_RESPONSE (fallback-ollama) for: {prompt[:80]}"


class LLMClient:
    """
    High-level LLM client facade used by the rest of the application.

    It chooses a concrete provider (OpenAI, local Ollama, or mock) based on
    configuration, hiding provider-specific details from the calling code.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        # Allow passing custom settings (useful in tests), otherwise use global.
        self._settings = settings or get_settings()
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._provider: BaseLLMProvider = self._select_provider()

    def _select_provider(self) -> BaseLLMProvider:
        """Select the appropriate provider based on configuration."""
        # Prefer Ollama explicitly if configured
        if getattr(self._settings, "use_ollama", False):
            self._logger.info("Initializing LocalOllamaProvider (USE_OLLAMA=true).")
            return LocalOllamaProvider(settings=self._settings, logger=self._logger)

        # Otherwise prefer OpenAI when key is available
        if self._settings.openai_api_key:
            self._logger.info("Initializing OpenAILLMProvider (OPENAI_API_KEY present).")
            return OpenAILLMProvider(settings=self._settings, logger=self._logger)

        # Fallback: mock provider
        self._logger.warning(
            "No provider configured (no USE_OLLAMA and no OPENAI_API_KEY); "
            "using MockLLMProvider instead."
        )
        return MockLLMProvider(logger=self._logger)

    def generate_text(self, prompt: str) -> str:
        """
        Generate text from the given prompt using the selected provider.

        Callers do not need to know which provider is used underneath.
        """
        return self._provider.generate_text(prompt)

    def provider_name(self) -> str:
        """
        Return a simple string label indicating which provider is currently in use.

        This is useful for logging, metrics, and API responses.
        """
        # Imports above in this file define these classes already.
        if isinstance(self._provider, LocalOllamaProvider):
            return "ollama"
        if isinstance(self._provider, OpenAILLMProvider):
            return "openai"
        if isinstance(self._provider, MockLLMProvider):
            return "mock"
        return "unknown"
