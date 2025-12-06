# Refrence: 
  - https://chatgpt.com/share/6934718c-b488-800f-8cba-e64b8bd5cec9

---

# Revision LLM PoC – Python & GenAI Interview Coach

A small, **production-flavoured** PoC that exposes a **Python & GenAI “interview explainer”**:

- **FastAPI** backend: `/api/v1/explain`
- **LLMClient** abstraction:
  - `Ollama` (local Llama 3.2) via HTTP
  - `OpenAI` (if key present)
  - `Mock` (deterministic output, good for tests)
- **Streamlit UI** for interactive usage
- **Docker + docker-compose** setup with:
  - `ollama` container (Llama 3.2 pulled at build time)
  - `revision-llm-api` container (FastAPI)
  - `revision-llm-ui` container (Streamlit)

Designed as a realistic base for **AWS/EKS + Terraform + Helm** in the next phase.

---

## High-Level Architecture

- **Streamlit UI** (user-facing)  
- **FastAPI app** (`/api/v1/explain`, `/health`)  
- **Core services** (`ExplanationService`)  
- **LLMClient** chooses provider (Ollama / OpenAI / Mock) based on env  
- **Config layer** (`Settings(BaseSettings)`) reads `.env` / K8s env vars  

```text
[ Browser ]
    │
    ▼
[ Streamlit UI ]  (src/ui/revision_ui.py)
    │  HTTP (BACKEND_URL)
    ▼
[ FastAPI API ]   (src/app/main.py → /api/v1/explain)
    │
    ▼
[ ExplanationService ]  (src/core/services.py)
    │
    ▼
[ LLMClient ]           (src/core/llm_client.py)
    ├── LocalOllamaProvider → http://ollama:11434/api/generate
    ├── OpenAIProvider     → api.openai.com (if OPENAI_API_KEY)
    └── MockLLMProvider    → deterministic string
````

---

## How This Uses 

This PoC was built intentionally to practise **Python + OOP + environments**:

* **Python Core & Environment** 

  * Virtualenv-friendly project (`pyproject.toml`)
  * `Settings(BaseSettings)` config pattern (12-factor)
  * Logging via `logging` module (`config/logging.py`)
* **OOP in Python** 

  * `LLMClient` as a **facade** / abstraction
  * Separate provider classes (Ollama/OpenAI/Mock)
  * Clear separation of concerns (models, services, app, config)
  * Dataclasses + Pydantic models in `core/models.py`

---

## Tech Stack

* **Language**: Python 3.10+ / 3.11
* **Backend**: FastAPI + Uvicorn
* **UI**: Streamlit
* **Config**: Pydantic Settings (`BaseSettings`)
* **HTTP client**: httpx
* **LLM Providers**:

  * Local: [Ollama](https://ollama.com/)
  * Cloud: OpenAI (optional, via `OPENAI_API_KEY`)
  * Mock: built-in fallback
* **Containerization**: Docker, docker-compose
* **(Planned)** IaC: Terraform + Helm (for AWS EKS/ECR)

---

## Repository Layout

```text
revision-llm-poc/
  pyproject.toml
  .env.example
  .dockerignore
  Dockerfile.api        # FastAPI backend image
  Dockerfile.ui         # Streamlit UI image
  Dockerfile.ollama     # Ollama image with pre-pulled model
  docker-compose.yaml   # Ollama + API + UI stack
  README.md

  src/
    app/
      __init__.py
      main.py           # FastAPI app, routes, health endpoint
    core/
      __init__.py
      models.py         # Pydantic request/response + dataclasses
      services.py       # ExplanationService / core logic
      llm_client.py     # LLMClient + provider implementations
    config/
      __init__.py
      settings.py       # Settings(BaseSettings), env variables
      logging.py        # Logging configuration
    ui/
      __init__.py
      revision_ui.py    # Streamlit UI → calls FastAPI

  tests/
    __init__.py
    test_app.py         # Minimal pytest test for /api/v1/explain

  infra/                # (planned)
    terraform/          # will hold AWS/EKS/ECR Terraform code
    helm/               # will hold Helm chart for this app
```

---

## Configuration & Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

**LLM & provider-related envs:**

```env
# Core env
APP_ENV=local
LOG_LEVEL=INFO

# Provider switching
USE_OLLAMA=true
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2

# Optional cloud providers (not required if only using Ollama)
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx
GOOGLE_API_KEY=AIzxxx
OLAMA_API_KEY=olama
HF_TOKEN=hf_xxx
GROK_MODEL=xai-xxx
```

Notes:

* If `USE_OLLAMA=true` and `OLLAMA_BASE_URL` is reachable, `LLMClient` uses Ollama.
* If Ollama is disabled but `OPENAI_API_KEY` is set, it can use OpenAI.
* If nothing is configured, it falls back to `MockLLMProvider` for safe demos/tests.

---

## Local Development (without Docker)

### 1. Create & activate a virtualenv

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
```

### 2. Install the project

```bash
pip install -U pip
pip install .
```

### 3. Prepare `.env`

```bash
cp .env.example .env
# edit .env to set APP_ENV, USE_OLLAMA, OPENAI_API_KEY, etc.
```

For **pure local mock mode**, you can set:

```env
USE_OLLAMA=false
OPENAI_API_KEY=
```

### 4. Run FastAPI backend

```bash
uvicorn app.main:app --reload
```

* API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health: [http://localhost:8000/health](http://localhost:8000/health)

### 5. Run Streamlit UI

In another terminal (same venv):

```bash
streamlit run src/ui/revision_ui.py
```

* UI: [http://localhost:8501](http://localhost:8501)
* UI uses `BACKEND_URL` env var (default `http://localhost:8000`).

---

## Docker & docker-compose Stack (Ollama + API + UI)

This is the main “production-like” local setup.

### 1. Build & run the full stack

From project root:

```bash
docker compose up --build
```

This will:

* Build and run:

  * `revision-ollama` (Ollama with `llama3.2` pre-pulled)
  * `revision-llm-api` (FastAPI backend)
  * `revision-llm-ui` (Streamlit UI)
* Wire them together via an internal Docker network:

  * API → Ollama: `http://ollama:11434`
  * UI → API: `http://api:8000` (via `BACKEND_URL` env)

### 2. Ports

* **UI**: [http://localhost:8501](http://localhost:8501)
* **API**: [http://localhost:8000](http://localhost:8000)
* **Ollama HTTP**: [http://localhost:11434](http://localhost:11434) (if you want to inspect manually)

### 3. First-call behaviour

* The **first request** after container start may take **20–30 seconds**:

  * the model is loaded into memory,
  * KV cache is allocated,
  * Ollama warms up.
* Subsequent calls are much faster.

If the **UI shows `Error calling backend: timed out`**, it usually means:

* Ollama is still loading and the **Streamlit httpx timeout was too small**.
* In `src/ui/revision_ui.py`, the timeout is set to something like:

  ```python
  with httpx.Client(timeout=40.0) as client:
      ...
  ```

You can adjust this based on your hardware.

### 4. Stop the stack

```bash
docker compose down
```

---

## Example API Calls

### 1. Explain a topic (curl)

```bash
curl -X POST "http://localhost:8000/api/v1/explain" \
  -H "Content-Type: application/json" \
  -d '{"topic":"what is RAG?","detail_level":"detailed"}'
```

Expected response shape:

```json
{
  "topic": "what is RAG?",
  "explanation": "....",
  "provider": "ollama"
}
```

(or `"provider": "mock"` if using the mock provider)

### 2. Health check

```bash
curl http://localhost:8000/health
```

---

## Running Tests

Assuming you have `pytest` installed (via `pyproject.toml` dev deps or manually):

```bash
pytest
```

`tests/test_app.py` contains a minimal happy-path test for `/api/v1/explain` using FastAPI’s `TestClient`.

---

## Troubleshooting

### UI: “Error calling backend: timed out”

* Cause: Ollama took longer than the UI’s HTTP timeout.
* Fix:

  * Increase `timeout` in `call_backend()` in `src/ui/revision_ui.py`.
  * Or reduce `num_predict` / output length in the Ollama provider to speed up responses.

---

### API: “Ollama call failed, falling back to mock”

* This means `LLMClient` could not reach Ollama at `OLLAMA_BASE_URL`.
* Check:

  * Is the `ollama` container running?
  * Is `OLLAMA_BASE_URL` set to `http://ollama:11434` (inside Docker) or `http://host.docker.internal:11434` (if using host Ollama)?
  * Is `USE_OLLAMA=true` in `.env` / container env?

The fallback-to-mock behaviour is **intentional** so the API still responds.

---

### High CPU / RAM usage

* Llama 3.2 3B Instruct is ~1.9 GB model; the container needs:

  * At least **4–8 GB** of RAM for comfortable operation.
* If your machine struggles:

  * Use a smaller model,
  * Or lower `num_predict` in Ollama options.

---

## Roadmap – AWS & Infrastructure as Code (Planned)

The next steps (not yet committed, but planned) are:

* **Terraform**:

  * VPC + subnets
  * EKS cluster + managed node group
  * ECR repositories for `api`, `ui`, and `ollama` images
* **Helm**:

  * A chart to deploy:

    * `ollama` Deployment/Service
    * `revision-llm-api` Deployment/Service
    * `revision-llm-ui` Deployment/Service (LoadBalancer or Ingress)
  * ConfigMap/Secret for all env vars (`USE_OLLAMA`, `OLLAMA_BASE_URL`, `OPENAI_API_KEY`, etc.)
* **Cleanup**:

  * `terraform destroy` scripts/checklist to safely tear down EKS, VPC, ECR to avoid costs.

Once those pieces are added under `infra/`, the README will be extended with:

* `infra/terraform/envs/dev` usage (`terraform init && terraform apply`)
* `infra/helm/revision-llm-poc` usage (if not driven fully by Terraform’s Helm provider)
* AWS-specific notes (EKS LB URL, Route 53 DNS, etc.)

---

## Quick Summary

* Use **venv + uvicorn + Streamlit** for simple local dev.
* Use **docker-compose** to run **Ollama + API + UI** together, exactly like a small production stack.
* All configuration is via **env vars** (`Settings(BaseSettings)`), ready for K8s/Terraform/Helm.
* This PoC doubles as:

  * A **learning project** for Python/OOP/LLMs,
  * A **realistic skeleton** you can deploy to AWS later.

```

---

If you want, next we can:

- Add a tiny **“Infra (coming soon)”** section to the README once we create `infra/terraform` and `infra/helm`, or  
- Jump straight into **Part 15 – IaC Blueprint** and start actually creating those folders + minimal `main.tf` and Helm `Chart.yaml`.
::contentReference[oaicite:0]{index=0}
```
