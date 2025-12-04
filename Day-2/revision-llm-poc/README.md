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

## Architecture Overview

At a high level, the system is a small layered backend service:

1. **Client (curl/Postman/frontend)**  
   - Sends HTTP `POST` requests to the API with JSON payloads like  
     `{ "topic": "virtual environments", "detail_level": "short" }`.

2. **FastAPI App (app layer)**  
   - Exposes `/api/v1/explain`.  
   - Validates and parses JSON into Pydantic models.  
   - Delegates work to the core service layer and returns JSON responses.

3. **Core Domain Layer (services + models)**  
   - `ExplanationService` takes a typed request model and builds a prompt.  
   - Contains the core logic for how we talk to the LLM and interpret responses.  
   - Knows nothing about HTTP or OpenAI SDK details.

4. **LLM Client Layer (llm_client + providers)**  
   - `LLMClient` chooses an underlying provider based on configuration.  
   - `OpenAILLMProvider` calls the real OpenAI API when `OPENAI_API_KEY` is present.  
   - `MockLLMProvider` returns a deterministic string in local/dev when no keys are set.

5. **Configuration Layer (settings)**  
   - `Settings` reads environment variables using `BaseSettings`.  
   - Provides API keys, model names, environment (`APP_ENV`), etc.  
   - Ensures no secrets are hard-coded.

### End-to-End Flow (Request → Response)

```text
[ Client (curl/Postman) ]
            |
      POST /api/v1/explain
            |
      FastAPI app (app.main)
            |
   ExplanationService (core.services)
            |
        LLMClient (core.llm_client)
            |
  OpenAILLMProvider  /  MockLLMProvider
            |
      OpenAI API      /   Deterministic mock

```

### Component Responsibilities

- **FastAPI app (`app.main`)**
  - Owns HTTP concerns: routing, request/response validation, status codes.
  - Very thin: does not contain business logic.

- **Core models (`core.models`)**
  - Pydantic models for request/response payloads.
  - Dataclasses for internal domain entities.

- **Core services (`core.services`)**
  - Orchestrate the use case: build prompts, call `LLMClient`, wrap results.

- **LLM client (`core.llm_client`)**
  - Provides a stable `generate_text(prompt: str) -> str` interface.
  - Hides provider details (OpenAI vs mock), error handling, and retries.

- **Config (`config.settings`)**
  - Central place for all environment-driven config (API keys, model names, log level).
  - Uses `.env` in local/dev; behaves like a typical 12-factor app.

