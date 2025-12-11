# src/core/services.py
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional, Tuple

import redis

from config.settings import Settings
from core.llm_client import LLMClient
from core.models import (
    GreetingRequest,
    GreetingResponse,
    LLMGenerationResult,
    ModelProvider,
    ReleaseNoteRequest,
    ReleaseNoteResponse,
)


logger = logging.getLogger(__name__)


# ------------------------
# Redis Cache Helper
# ------------------------


@dataclass
class RedisCache:
    """
    Thin wrapper over Redis for JSON-encoded values.

    Notes:
    - Redis is NOT optional in this PoC: all services try to use it.
    - If Redis is unavailable, we log a warning and continue without caching
      (to keep the app usable).
    """

    settings: Settings

    def __post_init__(self) -> None:
        self._client = redis.Redis.from_url(
            self.settings.redis_url,
            decode_responses=True,
        )
        logger.info("RedisCache initialized with URL: %s", self.settings.redis_url)

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            raw = self._client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:  # pragma: no cover - network/infra
            logger.warning("Redis GET failed for key=%s: %s", key, exc)
            return None

    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
        try:
            serialized = json.dumps(value)
            self._client.set(key, serialized, ex=ttl_seconds)
        except Exception as exc:  # pragma: no cover - network/infra
            logger.warning("Redis SET failed for key=%s: %s", key, exc)


def _hash_dict(data: Dict[str, Any]) -> str:
    """
    Stable hash for dict contents, used for Redis keys.

    - Sorts keys to ensure same dict -> same hash.
    - Converts values to strings where needed.
    """
    payload = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

# ------------------------
# Release Notes Service
# ------------------------


class ReleaseNotesService:
    """
    Business logic for generating release notes + test scenarios.

    Responsibilities:
    - Build an LLM prompt from ReleaseNoteRequest.
    - ALWAYS check Redis for a cached result before calling LLM.
    - Call LLMClient (OpenAI or OSS model via model_service).
    - Parse LLM text into ReleaseNoteResponse.
    - Store the result in Redis with a TTL.

    This service is framework-agnostic and can be used from FastAPI,
    CLI, or tests.
    """

    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient,
        cache: RedisCache,
        cache_ttl_seconds: int = 3600,
    ) -> None:
        self._settings = settings
        self._llm_client = llm_client
        self._cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds

    # Public API
    # ----------

    def generate_release_notes(
        self,
        request: ReleaseNoteRequest,
        provider: Optional[ModelProvider] = None,
    ) -> ReleaseNoteResponse:
        """
        Main entrypoint:
        1) Compute cache key from request.
        2) If cached, return cached response (with cached=True).
        3) Otherwise, call LLMClient, parse text, cache and return.
        """
        cache_key = self._build_cache_key(request)
        cached = self._cache.get_json(cache_key)

        if cached is not None:
            logger.info("ReleaseNotesService cache HIT. key=%s", cache_key)
            cached["cached"] = True  # ensure the flag is set
            return ReleaseNoteResponse(**cached)

        logger.info("ReleaseNotesService cache MISS. key=%s", cache_key)

        prompt = self._build_prompt(request)
        llm_result = self._llm_client.generate_text(prompt, provider=provider)

        release_note, scenarios = self._parse_release_note_text(llm_result)

        response = ReleaseNoteResponse(
            release_note=release_note,
            test_scenarios=scenarios,
            provider=llm_result.provider,
            model=llm_result.model,
            cached=False,
        )

        # Store in Redis cache (best-effort)
        self._cache.set_json(cache_key, response.dict(), self._cache_ttl_seconds)

        return response

    # Internal helpers
    # ----------------

    def _build_cache_key(self, request: ReleaseNoteRequest) -> str:
        payload = request.dict()
        digest = _hash_dict(payload)
        return f"d32-release:release-notes:{digest}"

    def _build_prompt(self, request: ReleaseNoteRequest) -> str:
        """
        Build a compact but clear prompt for the LLM.

        We ask for:
        - A single, user-facing release note paragraph.
        - 2–3 concise test scenarios as bullet points.
        """
        risk = request.risk_level or "unspecified"
        impact = request.impact_area or "general"

        return (
            "You are an assistant that writes clear, concise release notes and test scenarios.\n\n"
            f"Title: {request.title}\n"
            f"Risk level: {risk}\n"
            f"Impact area: {impact}\n"
            f"Change description:\n{request.description}\n\n"
            "Please produce:\n"
            "1) A short release note (2–4 sentences) suitable for end users.\n"
            "2) 2–3 bullet-point test scenarios.\n\n"
            "Return the answer as plain text, where the first paragraph is the release note "
            "and the following lines (starting with '-') are the test scenarios.\n"
        )

    def _parse_release_note_text(
        self,
        llm_result: LLMGenerationResult,
    ) -> Tuple[str, list]:
        """
        Parse LLM text into:
        - release_note (string)
        - test_scenarios (list of strings)

        The parsing is robust:
        - If text has multiple lines, treat the first non-empty paragraph as the
          release note and bullet-like lines as scenarios.
        - If parsing fails, use generic fallback scenarios.
        """
        text = (llm_result.text or "").strip()
        if not text:
            return "No content generated.", [
                "Verify the main feature works as intended.",
                "Check error handling and edge cases.",
                "Ensure no regressions in related areas.",
            ]

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Release note: first non-empty line or paragraph
        release_note = lines[0]

        # The rest: anything starting with '-', '*', or containing 'Test'
        scenarios = []
        for line in lines[1:]:
            if line.startswith(("-", "*")):
                # Strip the bullet marker
                scenarios.append(line.lstrip("-* ").strip())
            elif "test" in line.lower():
                scenarios.append(line)

        if not scenarios:
            scenarios = [
                "Verify the main feature works as described in the release note.",
                "Test edge cases and error conditions for this change.",
                "Validate there are no regressions in related features.",
            ]

        return release_note, scenarios
# ------------------------
# Greeting Service
# ------------------------


class GreetingService:
    """
    Business logic for birthday and normal greetings.

    Requirements (non-optional for this PoC):
    - Always use Redis cache for greeting responses.
    - Always use an LLM (OpenAI or OSS via LLMClient) to generate the greeting
      text, never a purely static string.
    - If the person's birth month equals the current month:
        -> Generate a "birthday month" style greeting.
      Otherwise:
        -> Generate a friendly non-birthday greeting that still references
           their birth month.

    The choice of provider:
    - Can be overridden per-request via GreetingRequest.provider.
    - Otherwise defaults to settings.llm_default_provider.
    """

    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient,
        cache: RedisCache,
        cache_ttl_seconds: int = 3600,
    ) -> None:
        self._settings = settings
        self._llm_client = llm_client
        self._cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds

    # Public API
    # ----------

    def generate_greeting(
        self,
        request: GreetingRequest,
    ) -> GreetingResponse:
        """
        Main entrypoint:
        1) Compute cache key (name + dob + provider + birthday-month flag).
        2) If cached, return it.
        3) Otherwise, build an LLM prompt (birthday or normal),
           call LLMClient, cache, and return.
        """
        is_birthday_month = self._is_birthday_month(request.date_of_birth)
        provider_enum = request.provider
        provider_str = (
            provider_enum.value
            if provider_enum is not None
            else (self._settings.llm_default_provider or "openai").lower()
        )

        cache_key = self._build_cache_key(
            name=request.name,
            dob=request.date_of_birth,
            provider=provider_str,
            is_birthday_month=is_birthday_month,
        )

        cached = self._cache.get_json(cache_key)
        if cached is not None:
            logger.info("GreetingService cache HIT. key=%s", cache_key)
            return GreetingResponse(**cached)

        logger.info("GreetingService cache MISS. key=%s", cache_key)

        prompt = self._build_prompt(
            name=request.name,
            dob=request.date_of_birth,
            is_birthday_month=is_birthday_month,
        )

        # Choose provider for LLMClient (use enum when possible)
        provider_for_llm: Optional[ModelProvider] = None
        if provider_enum is not None:
            provider_for_llm = provider_enum
        elif provider_str == ModelProvider.OPENAI.value:
            provider_for_llm = ModelProvider.OPENAI
        elif provider_str == ModelProvider.OSS.value:
            provider_for_llm = ModelProvider.OSS

        llm_result = self._llm_client.generate_text(
            prompt,
            provider=provider_for_llm,
        )

        response = GreetingResponse(
            greeting_message=llm_result.text,
            is_birthday_month=is_birthday_month,
            provider=llm_result.provider,
            model=llm_result.model,
        )

        # Store in Redis cache (best-effort)
        self._cache.set_json(cache_key, response.dict(), self._cache_ttl_seconds)

        return response

    # Internal helpers
    # ----------------

    def _is_birthday_month(self, dob: date) -> bool:
        """
        Returns True if the person's birth month equals the current month
        (according to the system date).
        """
        today = date.today()
        return dob.month == today.month

    def _build_cache_key(
        self,
        name: str,
        dob: date,
        provider: str,
        is_birthday_month: bool,
    ) -> str:
        payload = {
            "name": name.strip().lower(),
            "dob": dob.isoformat(),
            "provider": provider,
            "is_birthday_month": is_birthday_month,
        }
        digest = _hash_dict(payload)
        return f"d32-release:greeting:{digest}"

    def _build_prompt(
        self,
        name: str,
        dob: date,
        is_birthday_month: bool,
    ) -> str:
        """
        Build an LLM prompt for either:
        - birthday-month greeting, or
        - normal greeting.
        """
        dob_str = dob.strftime("%d %B %Y")
        month_name = dob.strftime("%B")

        if is_birthday_month:
            return (
                "You are a friendly assistant.\n\n"
                f"Generate a warm, cheerful birthday-month greeting for a person.\n\n"
                f"Name: {name}\n"
                f"Date of birth: {dob_str}\n\n"
                "Requirements:\n"
                "- Mention that this is their birthday month.\n"
                "- Keep it short (2–4 sentences).\n"
                "- Sound natural and kind, without over-the-top emojis.\n"
            )

        return (
            "You are a friendly assistant.\n\n"
            "Generate a short, positive greeting for a person.\n"
            "It is not their birthday month, but you can optionally mention "
            "when their birthday month is.\n\n"
            f"Name: {name}\n"
            f"Date of birth: {dob_str}\n\n"
            "Requirements:\n"
            f"- Keep it short (2–4 sentences).\n"
            f"- You may gently mention that their birthday month is {month_name}.\n"
            "- Sound polite and encouraging.\n"
        )
