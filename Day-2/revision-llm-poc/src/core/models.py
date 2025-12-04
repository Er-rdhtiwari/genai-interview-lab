from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

class ExplainRequest(BaseModel):
    """
    Request payload for the explanation endpoint.

    The client sends a topic and an optional detail_level indicating how
    verbose the explanation should be.
    """

    topic: str = Field(
        ..., 
        description="Python/GenAI topic to explain.")
    detail_level: Literal["short", "detailed"] = Field(
        "short",
        description="Controls how verbose the explanation should be.",
    )


class ExplainResponse(BaseModel):
    """
    Response payload from the explanation endpoint.

    It contains the topic, generated explanation text, and the provider name.
    """

    topic: str
    explanation: str
    provider: str

@dataclass
class ExplanationContext:
    topic: str
    detail_level: str 