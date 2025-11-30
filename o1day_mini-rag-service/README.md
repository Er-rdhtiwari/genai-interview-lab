## Local setup

1) Create a virtual env and install deps:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) (Optional) Set an OpenAI key if you want real LLM answers:
```
export OPENAI_API_KEY=sk-...
# Optional overrides
export LLM_MODEL=gpt-4.1-mini
export LLM_TIMEOUT_SECONDS=10
```
If no key is set, the service returns a deterministic mock answer but still includes sources.

## Run the API

From the repo root:
```
uvicorn src.app.main:app --reload --port 8000
```

Health check:
```
curl -s http://localhost:8000/health
```

Ask endpoint (defaults to top_k=3):
```
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are common RAG pipeline steps?","top_k":3}'
```

Another example without top_k:
```
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do vector databases help RAG?"}'
```

## Run tests

```
pytest
```
