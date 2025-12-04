# Revision LLM PoC – Python & GenAI Interview Coach API

## Problem Statement

Teams preparing for Python + GenAI interviews need quick, accurate explanations
of key concepts like virtual environments, OOP principles, logging, and LLM design.
Manually searching docs or blogs is slow and inconsistent.

This PoC provides a small HTTP API that takes a **topic** (e.g. "virtual environments")
and returns a **short or detailed explanation**, powered by an LLM in production
or a safe mock in local/dev.

## Use Case

- Internal tool for engineers preparing for **Senior AI Engineer / backend** interviews.
- Can be integrated into a dev portal, chat bot, or internal dashboard.
- Acts as a starting point for more advanced features like quizzes, RAG, or personalization.

## Functional Requirements

- Expose a `POST /api/v1/explain` endpoint that:
  - accepts JSON payload: `{ "topic": "<string>", "detail_level": "short" | "detailed" }`,
  - validates input and returns clear error if invalid,
  - uses a service layer to build a prompt and call an LLM client,
  - responds with JSON: `{ "topic": ..., "explanation": ..., "provider": "mock" | "openai" }`.
- Support both:
  - **real LLM calls** when API keys are configured,
  - **mock responses** when no keys are configured (local/dev mode).

## Non-Functional Requirements

- **Reliability**  
  - Missing or invalid API keys must not crash the service; it should fall back to the mock provider.
  - LLM errors (timeouts, network issues) should be logged and handled gracefully.

- **Security**  
  - All secrets (API keys) must come from environment variables (e.g. `.env`), never hard-coded.
  - Logs must not print API keys or full sensitive payloads.

- **Observability**  
  - Use Python's `logging` with INFO/ERROR logs for requests and provider selection.
  - Log short previews of prompts/responses, not full long texts.

- **Performance & Cost**  
  - Designed for low to moderate traffic as a single FastAPI process.
  - Local/dev runs use mock provider **by default** to avoid LLM token costs.
  - Real LLM calls used only when keys are explicitly configured.

## High-Level Goal

By the end of the implementation, we will have a **fully runnable PoC** that:
- follows clean backend architecture,
- uses a proper `src/` layout,
- has a clear LLM abstraction layer,
- is safe to run without any external keys,
- and is easy to explain in a Senior AI Engineer interview.
