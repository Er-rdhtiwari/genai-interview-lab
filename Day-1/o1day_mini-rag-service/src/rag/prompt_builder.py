# rag/prompt_builder.py
from typing import List, Dict

def build_prompt(question: str, scored_docs: List[Dict]) -> str:
    """
    Build a prompt string from a user question and a list of scored docs.

    Each item in scored_docs is: {"doc": Document, "score": float}.
    """
    # Build a context block by joining doc snippets
    context_parts = []
    for item in scored_docs:
        doc = item["doc"]
        # Take only the first 300 characters as a "snippet"
        snippet = doc.content[:300]  # slicing
        context_parts.append(
            f"Title: {doc.title}\nSnippet: {snippet}"
        )

    context_block = "\n\n---\n\n".join(context_parts)

    prompt = f"""
You are an assistant that answers questions based on internal company documents.

Context:
{context_block}

User question: {question}
Answer in a concise paragraph and reference the relevant document titles when appropriate.
""".strip()

    return prompt
