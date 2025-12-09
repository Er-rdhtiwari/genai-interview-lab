from pydantic import BaseModel, Field


class ReleaseNoteRequest(BaseModel):
    """
    Incoming payload describing an infrastructure change.

    The client sends a short, free-text summary of what changed
    (e.g. "Upgraded RDS instance from t3.micro to t3.small in dev").
    """

    change_summary: str = Field(
        ...,
        description="Short free-text description of the infrastructure change.",
        min_length=5,
        max_length=1000,
    )
    tone: str = Field(
        default="neutral",
        description="Optional tone hint such as 'neutral', 'formal', or 'casual'.",
    )


class ReleaseNoteResponse(BaseModel):
    """
    Response containing a generated release note line.

    This is what the API returns to clients after calling the LLM (or mock).
    """

    release_note: str = Field(
        ...,
        description="A concise release-note sentence suitable for a changelog.",
    )
    provider: str = Field(
        ...,
        description="LLM provider used (e.g., 'openai' or 'mock').",
    )
