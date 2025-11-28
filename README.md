Love this idea — one **“GenAI Interview Lab”** repo where you add a tiny but realistic project every day. Let’s design it like a small, clean monorepo.

Below is a **practical, industry-style layout** that:

* Lets you add **one new project per day** under `src/dayXX_*`
* Uses **one main virtualenv** and **one .env**
* Centralizes **LLM client, logging, config** in `src/common/`
* Keeps things **secure & maintainable**

---

## 1. High-level repo idea

* **Root** = one Git repo: `genai-interview-lab/`
* **Common utilities** shared by all days in `src/common/`
  (config, logging, LLM client, helpers)
* **Each day’s project** is a separate Python package under `src/`
  e.g. `day01_mini_rag`, `day02_streaming_api`, etc.
* **Tests** live in top-level `tests/`, grouped per day.
* **One `.env` + one main `.venv`** at root.

---

## 2. Proposed repository tree

Here’s a concrete tree you can copy:

```text
genai-interview-lab/
├── README.md
├── pyproject.toml          # or requirements.txt + setup.cfg
├── .gitignore
├── .env                    # local only (ignored by git)
├── .env.example            # template without secrets
├── docs/
│   ├── day-plan.md         # high-level 30-day plan, notes
│   └── prompts/
│       └── daily_project_prompt.md  # the prompt you reuse every day
├── scripts/
│   ├── dev_shell.sh        # activate env, export PYTHONPATH, etc.
│   ├── run_day01.sh        # helper to run day01 app
│   └── run_tests.sh
├── src/
│   ├── __init__.py
│   ├── common/             # reusable building blocks for all days
│   │   ├── __init__.py
│   │   ├── config.py       # .env loading, Settings class
│   │   ├── logging.py      # logging setup
│   │   ├── llm_client.py   # shared LLM wrapper (OpenAI, etc.)
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── text.py     # small helpers: tokenize, truncate, etc.
│   ├── day01_mini_rag/     # Day 1 project package
│   │   ├── __init__.py
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   └── main.py     # FastAPI/Flask entrypoint
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── retrieval.py
│   │   │   └── prompt_builder.py
│   │   └── models/
│   │       ├── __init__.py
│   │       └── document.py
│   ├── day02_xxx_topic/    # placeholder for tomorrow's project
│   │   ├── __init__.py
│   │   └── ...             # structure similar to day01, but simpler/adjusted
│   └── day03_.../
│       └── ...
└── tests/
    ├── __init__.py
    ├── test_common/
    │   └── test_llm_client.py
    ├── day01/
    │   ├── test_retrieval.py
    │   └── test_prompt_builder.py
    ├── day02/
    │   └── ...
    └── day03/
        └── ...
```

You’ll grow it like:

* `src/day04_prompt_router/`
* `src/day05_langgraph_flow/`
* etc.

Each project stays **small, isolated, readable**, but still shares common tools.

---

## 3. What each top-level part does

### 3.1 Root files

* **`README.md`**

  * High-level description of the entire lab.
  * How to set up env, run any day’s project.
* **`pyproject.toml` / `requirements.txt`**

  * All libraries used across days.
  * Start minimal, add when needed.
* **`.gitignore`**

  * Very important for your security goal:

    ```gitignore
    .venv/
    envs/
    .env
    __pycache__/
    .pytest_cache/
    .DS_Store
    *.pyc
    .vscode/
    ```
* **`.env`**

  * Only on your machine.
  * Contains all secrets: `OPENAI_API_KEY`, DB URLs, etc.
* **`.env.example`**

  * Same keys, but with dummy values.
  * Safe to commit, helpful for future-you.

### 3.2 `docs/`

* `day-plan.md`
  → your 30-day outline, high-level checklist.
* `prompts/daily_project_prompt.md`
  → **save the prompt you used for the Day 1 project** here and reuse it daily.

Example content:

```markdown
# Daily Small Project Prompt (Reusable)

[Paste the exact prompt you used for Day 1 here]
```

Each day: open this file, copy prompt, adjust “Today’s topics” section only.

### 3.3 `scripts/`

Just helpers so you don’t keep re-typing:

* `dev_shell.sh`

  ```bash
  #!/usr/bin/env bash
  source .venv/bin/activate
  export PYTHONPATH=src
  echo "Dev shell ready. Python: $(python --version)"
  ```
* `run_day01.sh`

  ```bash
  #!/usr/bin/env bash
  source .venv/bin/activate
  export PYTHONPATH=src
  uvicorn day01_mini_rag.app.main:app --reload
  ```
* `run_tests.sh`

  ```bash
  #!/usr/bin/env bash
  source .venv/bin/activate
  export PYTHONPATH=src
  pytest -q
  ```

You can add similar scripts for later days if needed (or pass module manually).

---

## 4. `src/common/` – Shared building blocks

This is the **heart** of your repo – you use it in almost every daily project.

### 4.1 `common/config.py`

* Loads `.env` (once) with `python-dotenv`
* Exposes a simple `Settings` object:

```python
# src/common/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENV: str = os.getenv("ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4.1-mini")

settings = Settings()
```

All your daily projects can do:

```python
from common.config import settings

print(settings.DEFAULT_LLM_MODEL)
```

> ✅ Single `.env` for all projects.
> ✅ No need to create `.env` per day.

### 4.2 `common/logging.py`

Central logging setup:

```python
# src/common/logging.py
import logging
from .config import settings

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
```

In each day’s `main.py` you just call:

```python
from common.logging import setup_logging

setup_logging()
```

### 4.3 `common/llm_client.py`

Shared wrapper around OpenAI / other LLMs:

```python
# src/common/llm_client.py
import logging
from .config import settings

logger = logging.getLogger(__name__)

class LLMTimeoutError(Exception):
    pass

def generate_text(prompt: str, temperature: float = 0.2) -> str:
    """
    Shared LLM call.
    For some days, keep it mocked.
    For others, plug in real OpenAI/other client.
    """
    logger.info("LLM call", extra={"model": settings.DEFAULT_LLM_MODEL})
    # In some days, use real call; in others, stub it for tests.
    return "Mock answer for now."
```

Daily projects just import this:

```python
from common.llm_client import generate_text
```

> This avoids copy-pasting LLM code *every day*.

---

## 5. Daily project layout under `src/`

Each day gets its own small, self-contained package.

### Example: `src/day01_mini_rag/`

```text
src/day01_mini_rag/
├── __init__.py
├── app/
│   ├── __init__.py
│   └── main.py           # FastAPI / CLI entry
├── rag/
│   ├── __init__.py
│   ├── retrieval.py
│   └── prompt_builder.py
└── models/
    ├── __init__.py
    └── document.py
```

* Day 2 might be `day02_two_pointers_api/` with:

  * `app/main.py`
  * `core/logic.py`
  * `core/models.py`

You don’t need the same structure every day, but:

* Keeping `app/`, `core/` or `rag/`, `models/` makes the repo feel consistent.
* It will feel like working in a **real microservice monorepo**.

---

## 6. Tests structure

Top-level `tests/` with **per-day subfolders**:

```text
tests/
├── __init__.py
├── test_common/
│   └── test_llm_client.py
├── day01/
│   ├── test_retrieval.py
│   └── test_prompt_builder.py
├── day02/
│   └── test_xxx.py
└── day03/
    └── ...
```

* Keeps tests close to each project but still following typical `src/` + `tests/` pattern.
* Easy to run:

  * `pytest`
  * `pytest tests/day01`

---

## 7. Environment & credentials strategy (based on your constraints)

You said:

1. ❌ Don’t want a new env every day.
2. ❌ Don’t want new `.env` every day.
3. ✅ Want security.

Here’s a **simple, robust** strategy.

### 7.1 One main virtualenv at root

At repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or `uv sync` / `pip install -e .`
```

Use this for **most days**.

If someday you have a project with heavy or weird deps (e.g., PyTorch + CUDA), then:

* Create a separate env inside `envs/`:

```text
envs/
  heavy_gpu_env/
```

But **only if really needed**. Most GenAI PoCs will share ~80% libs.

### 7.2 One `.env` at root

`.env` example:

```env
ENV=dev
LOG_LEVEL=INFO

# Shared for all days
OPENAI_API_KEY=sk-...
DEFAULT_LLM_MODEL=gpt-4.1-mini

# Optional: per-day if needed
DAY03_POSTGRES_URL=postgresql://user:pass@localhost:5432/day03
DAY05_MONGO_URI=mongodb://...
```

* You add new keys to **the same** `.env` as new days need them.
* You **never** commit `.env` (it’s in `.gitignore`).
* Each project reads environment via `common.config.settings`.

---

## 8. How you add a new day’s project (workflow)

### Step-by-step (from tomorrow)

1. **Create project skeleton**

   ```bash
   cd genai-interview-lab
   mkdir -p src/day02_xxx_topic/{app,core,models}
   touch src/day02_xxx_topic/__init__.py
   touch src/day02_xxx_topic/app/__init__.py
   touch src/day02_xxx_topic/app/main.py
   ```

2. **Reuse the same daily prompt**

   * Open `docs/prompts/daily_project_prompt.md`.
   * Copy the prompt.
   * Update just:

     * “Today’s topics”
     * Maybe example use-cases.
   * Paste into ChatGPT → get:

     * Problem statement
     * Mini HLD/LLD
     * Skeleton functions

3. **Implement with shared common utils**

   * Use:

     * `from common.config import settings`
     * `from common.logging import setup_logging`
     * `from common.llm_client import generate_text`
   * This ensures all days **feel consistent** and closer to real industry projects.

4. **Add basic tests**

   * Create `tests/day02/test_something.py`.
   * Write 1–3 unit tests for core logic.

5. **Run**

   * `./scripts/dev_shell.sh`
   * `python -m day02_xxx_topic.app.main`
     or
   * `uvicorn day02_xxx_topic.app.main:app --reload` (if API)

6. **Commit**

   * Commit only:

     * `src/day02_xxx_topic/`
     * `tests/day02/`
     * Updated `requirements.txt` or `pyproject.toml`
     * Maybe updated `docs/day-plan.md`, `.env.example` (not `.env`!)

---

If you want, next I can:

* Write **exact contents** for:

  * `common/config.py`
  * `common/logging.py`
  * `common/llm_client.py`
* And then **fully wire `day01_mini_rag`** into this repo structure, so you have a copy–paste-ready starting point.
