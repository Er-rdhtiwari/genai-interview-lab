# app/qa_service.py
from typing import Dict
import logging

from rag.retrieval import retrieve_documents
from rag.prompt_builder import build_prompt
from llm.client import generate_answer

logger = logging.getLogger(__name__)

def answer_question(question: str, top_k: int = 3) -> Dict:
    """
    Orchestrates retrieval -> prompt building -> LLM call.
    Returns a dict ready for JSON response.
    """
    logger.info("Answering question", extra={"question_len": len(question), "top_k": top_k})

    # 1. Retrieve docs
    scored_docs = retrieve_documents(question, top_k=top_k)

    if not scored_docs:
        # No relevant docs – respond gracefully
        logger.info("No documents matched the query")
        return {
            "answer": "I couldn't find any relevant internal document for this question.",
            "sources": [],
        }

    # 2. Build prompt
    prompt = build_prompt(question, scored_docs)

    # 3. Call LLM
    answer = generate_answer(prompt)

    # 4. Build API response
    sources = [
        {
            "doc_id": item["doc"].id,
            "title": item["doc"].title,
            "score": item["score"],
        }
        for item in scored_docs
    ]

    return {
        "answer": answer,
        "sources": sources,
    }
