from __future__ import annotations

"""
Core business logic for the explanation use case.

ExplanationService sits between:
- the API layer (FastAPI endpoint) and
- the LLM client layer (LLMClient).

It:
- converts request models into internal context,
- builds a prompt for the LLM,
- calls LLMClient,
- wraps the result into a response model.
"""

import logging

from core.llm_client import LLMClient
from core.models import ExplainRequest, ExplainResponse, ExplanationContext


logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Service that coordinates between request models, domain logic,
    and the LLM client.

    This class contains the core business logic: how to build prompts and
    interpret responses.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        """
        Initialize the service with a concrete LLMClient instance.

        In production, the LLMClient is built from environment-based settings.
        In tests, we can inject a fake or preconfigured LLMClient.
        """
        self._llm_client = llm_client
        self._logger = logging.getLogger(self.__class__.__name__)

    def generate_explanation(self, request: ExplainRequest) -> ExplainResponse:
        """
        Generate an explanation for the requested topic using the configured LLM.

        Flow:
        - Convert the external request into an internal ExplanationContext.
        - Build a prompt based on the context (topic + detail level).
        - Call the LLM client to get the explanation text.
        - Wrap the result into an ExplainResponse, including provider name.
        """
        # Map external request model to internal context object.
        ctx = ExplanationContext(
            topic=request.topic,
            detail_level=request.detail_level,
        )

        prompt = self._build_prompt(ctx)
        self._logger.info("Generating explanation for topic=%s", ctx.topic)

        explanation_text = self._llm_client.generate_text(prompt)
        provider_name = self._llm_client.provider_name()

        # For observability, only log a short preview.
        self._logger.debug("Explanation provider=%s preview=%s", provider_name, explanation_text[:80])

        return ExplainResponse(
            topic=ctx.topic,
            explanation=explanation_text,
            provider=provider_name,
        )

    @staticmethod
    def _build_prompt(ctx: ExplanationContext) -> str:
        """
        Build an instruction-style prompt to send to the LLM.

        The prompt is deterministic so it is easier to debug and test.
        It uses the detail_level to control verbosity.
        """
        if ctx.detail_level == "short":
            detail_instruction = "Explain in 3–4 concise bullet points."
        else:
            detail_instruction = (
                "Explain step by step with examples, short code snippets, and common pitfalls "
                "for a Senior AI Engineer interview."
            )

        return (
            "You are a senior Python and GenAI mentor.\n\n"
            f"Topic: {ctx.topic}\n\n"
            f"Instruction: {detail_instruction}\n\n"
            "Answer clearly and in plain language."
        )
