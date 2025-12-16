from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class OllamaClient:
    base_url: str
    timeout_sec: int
    client: httpx.AsyncClient

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}{path}"

    async def get_version(self) -> dict[str, Any]:
        # GET /api/version is documented :contentReference[oaicite:2]{index=2}
        r = await self.client.get(self._url("/api/version"))
        r.raise_for_status()
        return r.json()

    async def list_models(self) -> dict[str, Any]:
        # GET /api/tags is documented :contentReference[oaicite:3]{index=3}
        r = await self.client.get(self._url("/api/tags"))
        r.raise_for_status()
        return r.json()

    async def chat(self, model: str, messages: list[dict[str, str]]) -> dict[str, Any]:
        # POST /api/chat is documented :contentReference[oaicite:4]{index=4}
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,  # disable streaming :contentReference[oaicite:5]{index=5}
        }
        r = await self.client.post(self._url("/api/chat"), json=payload)
        r.raise_for_status()
        return r.json()
