import logging

from .llm_client import LLMClient
from .models import ReleaseNoteRequest, ReleaseNoteResponse

logger = logging.getLogger(__name__)


def build_prompt(payload: ReleaseNoteRequest) -> str:
    """
    Construct a prompt for the LLM based on the incoming payload.

    This keeps prompt-building logic separate and easy to test.
    """
    tone_instruction = (
        "Use a neutral, professional tone."
        if payload.tone.lower() == "neutral"
        else f"Use a {payload.tone.lower()} tone."
    )

    prompt = (
        "You are helping a platform team write concise release notes for "
        "infrastructure changes (Terraform, AWS, Kubernetes, databases).\n\n"
        f"Change description:\n{payload.change_summary}\n\n"
        "Return exactly one sentence suitable for a technical changelog.\n"
        f"{tone_instruction}"
    )
    logger.debug("Built LLM prompt for release note.")
    return prompt


def generate_release_note(
    payload: ReleaseNoteRequest,
    llm_client: LLMClient,
    provider_name: str,
) -> ReleaseNoteResponse:
    """
    Generate a release note sentence using the given LLM client.
    """
    prompt = build_prompt(payload)
    logger.info("Generating release note using provider=%s.", provider_name)

    text = llm_client.generate_text(prompt=prompt)

    # A tiny safety/trimming step
    release_note = text.replace("\n", " ").strip()

    if not release_note.endswith("."):
        release_note += "."

    return ReleaseNoteResponse(
        release_note=release_note,
        provider=provider_name,
    )
