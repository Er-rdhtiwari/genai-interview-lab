from rag.retrieval import retrieve_documents


def test_retrieve_documents_returns_sorted_results():
    question = "How does the RAG pipeline retrieve documents?"
    results = retrieve_documents(question, top_k=3)

    assert results, "Expected at least one document to match the query"
    assert len(results) <= 3

    scores = [item["score"] for item in results]
    assert scores == sorted(scores, reverse=True)
    assert all("doc" in item and "score" in item for item in results)


def test_retrieve_returns_expected_doc_for_specific_query():
    results = retrieve_documents("guardrails and content filters", top_k=3)

    assert results, "Expected at least one match"
    top_doc = results[0]["doc"]
    assert top_doc.id == "doc_8"
    assert results[0]["score"] > 0


def test_top_k_limits_results():
    results = retrieve_documents("rag vector database embeddings", top_k=1)
    assert len(results) == 1
    # ensure scores sorted descending
    assert all(results[i]["score"] >= results[i + 1]["score"] for i in range(len(results) - 1))


def test_retrieve_documents_handles_no_overlap():
    results = retrieve_documents("nonexistent keyword", top_k=3)
    assert results == []
