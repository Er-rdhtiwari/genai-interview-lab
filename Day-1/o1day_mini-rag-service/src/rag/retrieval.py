# rag/retrieval.py
import re
from typing import List, Dict

from .models import Document

from typing import List

# Assuming you have something like:
# @dataclass
# class Document:
#     doc_id: str
#     title: str
#     content: str
#     tags: List[str]

DOCUMENTS: List[Document] = [
    Document(
        doc_id="doc_1",
        title="RAG Design Overview",
        content=(
            "RAG stands for Retrieval-Augmented Generation. It retrieves documents "
            "from an external knowledge base (like a vector database) and passes "
            "the retrieved context along with the user query to the LLM. This helps "
            "reduce hallucinations and keeps responses grounded in up-to-date data."
        ),
        tags=["rag", "architecture"],
    ),
    Document(
        doc_id="doc_2",
        title="RAG Pipeline Steps",
        content=(
            "A typical RAG pipeline includes: (1) Ingestion and chunking of raw documents, "
            "(2) Embedding each chunk into a vector space, (3) Storing vectors in a "
            "vector database, (4) Retrieving top-k relevant chunks using similarity search, "
            "(5) Passing retrieved chunks plus the user query as context to the LLM."
        ),
        tags=["rag", "pipeline", "embeddings"],
    ),
    Document(
        doc_id="doc_3",
        title="Vector Database Basics",
        content=(
            "Vector databases such as Chroma, FAISS, Pinecone, and Weaviate are used "
            "to store high-dimensional embeddings. They support fast similarity search "
            "operations like k-NN or cosine similarity lookups, enabling efficient retrieval "
            "of semantically similar documents."
        ),
        tags=["vector-db", "faiss", "chroma"],
    ),
    Document(
        doc_id="doc_4",
        title="Chunking Strategies for RAG",
        content=(
            "Chunking determines how you split large documents into smaller pieces. "
            "Common strategies include fixed-size character windows, paragraph-based splits, "
            "and markdown-aware splitters. The goal is to balance context completeness with "
            "retrieval precision so that each chunk is self-contained but not too large."
        ),
        tags=["rag", "chunking", "preprocessing"],
    ),
    Document(
        doc_id="doc_5",
        title="Prompt Engineering for RAG",
        content=(
            "In RAG, prompts should explicitly instruct the model to use the provided "
            "context and avoid inventing details. A good pattern is: 'Use only the "
            "context below to answer. If the answer is not in the context, say you do "
            "not know.' System and developer messages often encode these rules."
        ),
        tags=["prompt-engineering", "rag", "best-practices"],
    ),
    Document(
        doc_id="doc_6",
        title="Evaluating RAG Systems",
        content=(
            "RAG evaluation typically focuses on three layers: retrieval quality "
            "(recall/precision of relevant chunks), generation quality (faithfulness, "
            "helpfulness, coherence), and end-to-end task metrics (e.g., exact match, "
            "F1, or custom business KPIs). Human evaluation is often combined with "
            "automatic metrics."
        ),
        tags=["rag", "evaluation", "metrics"],
    ),
    Document(
        doc_id="doc_7",
        title="Caching Strategies for LLM Apps",
        content=(
            "LLM-powered systems can use caching at multiple levels: prompt+response "
            "caching to avoid repeated calls for identical queries, embedding caching "
            "to avoid recomputing vectors for the same text, and HTTP-level caching "
            "for static assets. Effective caching can dramatically reduce latency and cost."
        ),
        tags=["llm", "caching", "performance"],
    ),
    Document(
        doc_id="doc_8",
        title="LLM Safety and Guardrails",
        content=(
            "Guardrails in LLM systems include content filters, input validation, "
            "output validation, and policy enforcement. They help prevent the model "
            "from returning harmful, disallowed, or non-compliant responses, especially "
            "in regulated domains like finance and healthcare."
        ),
        tags=["safety", "guardrails", "policy"],
    ),
    Document(
        doc_id="doc_9",
        title="Observability for LLM Applications",
        content=(
            "Observability involves collecting logs, metrics, and traces for the entire "
            "LLM pipeline: request latency, token usage, error rates, and user feedback. "
            "Structured logging and correlation IDs help debug production incidents and "
            "analyze model behavior at scale."
        ),
        tags=["observability", "logging", "monitoring"],
    ),
    Document(
        doc_id="doc_10",
        title="Python Logging Patterns for LLM Services",
        content=(
            "Python's logging module can be used to add structured logs around LLM calls. "
            "Include fields like request_id, user_id (if allowed), model_name, latency, "
            "and token counts. This makes it easier to trace issues, measure performance, "
            "and build dashboards in tools like Grafana or Kibana."
        ),
        tags=["python", "logging", "llm"],
    ),
]


def tokenize(text: str) -> List[str]:
    """
    Very simple tokenizer: lowercase + split on non-alphabetic characters.
    """
    # Lowercase and split on non-letters
    return [t for t in re.split(r"[^a-zA-Z]+", text.lower()) if t]


def retrieve_documents(question: str, top_k: int = 3) -> List[Dict]:
    """
    Retrieve top_k documents based on simple keyword overlap.
    Returns a list of dicts: {doc, score}.
    """
    query_tokens = set(tokenize(question))

    scored_docs = []

    for doc in DOCUMENTS:
        # Tokenize title + content
        doc_tokens = set(tokenize(doc.title + " " + doc.content))
        # Overlap is our naive "relevance score"
        overlap = query_tokens.intersection(doc_tokens)
        score = len(overlap)  # int score

        if score > 0:
            scored_docs.append({"doc": doc, "score": float(score)})

    # Sort by score descending and slice top_k
    scored_docs.sort(key=lambda d: d["score"], reverse=True)
    return scored_docs[:top_k]
