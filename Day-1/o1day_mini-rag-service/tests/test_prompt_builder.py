from rag.models import Document
from rag.prompt_builder import build_prompt


def test_build_prompt_includes_question_and_titles():
    doc = Document(
        doc_id="doc_test",
        title="Test Title",
        content="Some content about retrieval augmented generation.",
        tags=["test"],
    )
    scored_docs = [{"doc": doc, "score": 1.0}]

    question = "What is RAG?"
    prompt = build_prompt(question, scored_docs)

    assert "Title: Test Title" in prompt
    assert question in prompt
    assert "User question: What is RAG?" in prompt


def test_build_prompt_includes_snippet_content():
    doc = Document(
        doc_id="doc_test_2",
        title="Sample Title",
        content="Sample content about RAG prompt building and how snippets are included.",
        tags=["sample"],
    )
    scored_docs = [{"doc": doc, "score": 1.0}]

    prompt = build_prompt("What is in the sample document?", scored_docs)

    assert "Sample Title" in prompt
    assert "Sample content" in prompt
    assert "What is in the sample document?" in prompt
