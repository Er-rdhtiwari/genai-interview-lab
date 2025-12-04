# GenAI Interview Lab

Small collection of day-based GenAI/back-end interview practice projects. Each day lives in its own folder with its own FastAPI app, tests, and `.env.example`. When no API keys are set, services default to safe mock providers.

## Current projects

- **Day-1: Mini RAG QA API** (`Day-1/o1day_mini-rag-service`)  
  FastAPI `/ask` endpoint that retrieves a few in-memory docs, builds a prompt, and calls OpenAI when `OPENAI_API_KEY` is set (falls back to a deterministic mock otherwise). Returns an answer plus source metadata.
  - Run:  
    ```bash
    cd Day-1/o1day_mini-rag-service
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn src.app.main:app --reload --port 8000
    ```
  - Smoke test:  
    ```bash
    curl -X POST http://localhost:8000/ask \
      -H "Content-Type: application/json" \
      -d '{"question":"What are common RAG pipeline steps?","top_k":3}'
    ```
  - Tests: `pytest`

- **Day-2: Revision LLM PoC** (`Day-2/revision-llm-poc`)  
  FastAPI `/api/v1/explain` endpoint that returns short or detailed explanations. Provider selection (mock/OpenAI/Ollama) is controlled by env vars; failures fall back to a deterministic mock.
  - Run:  
    ```bash
    cd Day-2/revision-llm-poc
    python -m venv .venv && source .venv/bin/activate
    pip install -e .
    cp .env.example .env  # set OPENAI_API_KEY or USE_OLLAMA=true if desired
    uvicorn app.main:app --reload --port 8000
    ```
  - Smoke test:  
    ```bash
    curl -X POST http://localhost:8000/api/v1/explain \
      -H "Content-Type: application/json" \
      -d '{"topic":"Python virtual environments","detail_level":"short"}'
    ```
  - Tests: `pytest`

## Repo layout

```text
README.md
Notes/                     # prompts, notebooks, scratch notes
Day-1/o1day_mini-rag-service/  # Mini RAG QA API
Day-2/revision-llm-poc/        # Explanation API with mock/OpenAI/Ollama providers
src/common/                # Early shared helpers (env/logging), not yet wired into day apps
scripts/                   # Helper stubs from initial setup
```

## Environment and security

- Each project has its own `.env.example`; copy it to `.env` and fill in keys locally (`OPENAI_API_KEY`, `USE_OLLAMA`, `OPENAI_MODEL`, etc.).  
- `.env` files are gitignored—keep secrets local.  
- Default behavior uses mock providers when no keys are configured, so you can run everything offline.

## Working on new days

Add a new folder under `Day-N/` with its own `src/`, tests, and `.env.example`. Reuse patterns from Day-1 and Day-2 (FastAPI app layer, service layer, provider abstraction, mock fallback). If you want to centralize shared pieces, wire them through `src/common/`.
