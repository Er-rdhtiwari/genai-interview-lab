from __future__ import annotations

import logging
import time
import uuid
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import Settings
from .logging_json import configure_json_logging
from .ollama_client import OllamaClient

settings = Settings()
configure_json_logging(service_name=settings.app_name, level=settings.log_level)
log = logging.getLogger("app")

app = FastAPI(title=settings.app_name)

# CORS (UI -> API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = "user"
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    # OpenAI-like shape (simple)
    messages: list[ChatMessage] | None = None
    message: str | None = Field(default=None, min_length=1, max_length=8000)
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str
    model: str
    provider: str
    request_id: str
    metrics: dict | None = None


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start = time.time()

    try:
        response: Response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response
    finally:
        duration_ms = int((time.time() - start) * 1000)
        log.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "duration_ms": duration_ms,
            },
        )


@app.on_event("startup")
async def startup():
    timeout = httpx.Timeout(settings.ollama_timeout_sec)
    app.state.http = httpx.AsyncClient(timeout=timeout)
    app.state.ollama = OllamaClient(
        base_url=settings.ollama_base_url,
        timeout_sec=settings.ollama_timeout_sec,
        client=app.state.http,
    )
    log.info(
        "startup_complete",
        extra={
            "request_id": "-",
            "provider": settings.llm_provider,
            "ollama_base_url": settings.ollama_base_url,
            "ollama_model": settings.ollama_model,
        },
    )


@app.on_event("shutdown")
async def shutdown():
    await app.state.http.aclose()


@app.get("/healthz")
async def healthz():
    return {"ok": True, "service": settings.app_name}


@app.get("/readyz")
async def readyz():
    # If mock mode, always ready
    if settings.llm_provider == "mock":
        return {"ok": True, "provider": "mock"}

    # Ollama readiness: check /api/version :contentReference[oaicite:6]{index=6}
    try:
        ver = await app.state.ollama.get_version()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"ollama_not_ready: {type(e).__name__}")

    # Optional: verify model exists via /api/tags :contentReference[oaicite:7]{index=7}
    if settings.readiness_check_model:
        try:
            tags = await app.state.ollama.list_models()
            models = {m.get("name") for m in tags.get("models", []) if isinstance(m, dict)}
            if settings.ollama_model not in models:
                raise HTTPException(status_code=503, detail=f"model_not_pulled: {settings.ollama_model}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"ollama_tags_failed: {type(e).__name__}")

    return {"ok": True, "provider": "ollama", "ollama_version": ver.get("version")}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

    # Build messages
    messages: list[dict[str, str]]
    if req.messages:
        messages = [{"role": m.role, "content": m.content} for m in req.messages][-20:]
    elif req.message:
        messages = [{"role": "user", "content": req.message}]
    else:
        raise HTTPException(status_code=400, detail="Provide either 'messages' or 'message'")

    model = req.model or settings.ollama_model

    # Mock mode (helps local testing)
    if settings.llm_provider == "mock":
        reply = f"[mock] You said: {messages[-1]['content']}"
        return ChatResponse(reply=reply, model=model, provider="mock", request_id=request_id, metrics=None)

    # Ollama mode: POST /api/chat :contentReference[oaicite:8]{index=8}
    try:
        t0 = time.time()
        out = await app.state.ollama.chat(model=model, messages=messages)
        ms = int((time.time() - t0) * 1000)

        reply = (out.get("message") or {}).get("content") or ""
        if not reply:
            raise HTTPException(status_code=502, detail="empty_response_from_ollama")

        metrics = {
            "duration_ms": ms,
            # Ollama exposes timing metrics in responses :contentReference[oaicite:9]{index=9}
            "total_duration": out.get("total_duration"),
            "load_duration": out.get("load_duration"),
            "prompt_eval_count": out.get("prompt_eval_count"),
            "eval_count": out.get("eval_count"),
        }

        log.info(
            "chat_ok",
            extra={
                "request_id": request_id,
                "model": model,
                "provider": "ollama",
                "duration_ms": ms,
            },
        )

        return ChatResponse(reply=reply, model=model, provider="ollama", request_id=request_id, metrics=metrics)

    except HTTPException:
        raise
    except Exception as e:
        log.exception("chat_failed", extra={"request_id": request_id})
        raise HTTPException(status_code=502, detail=f"ollama_error: {type(e).__name__}")
