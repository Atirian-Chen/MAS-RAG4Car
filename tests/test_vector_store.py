from autodev_rag.chunker import chunk_documents
from autodev_rag.config import DOCS_DIR
from autodev_rag.document_loader import load_documents
from autodev_rag.vector_store import LocalVectorStore


def _store() -> LocalVectorStore:
    documents = load_documents(DOCS_DIR)
    chunks = chunk_documents(documents)
    store = LocalVectorStore()
    store.build(chunks)
    return store


def test_vector_store_build_and_search() -> None:
    store = _store()

    results = store.search("AEB 雨天误触发", top_k=5)

    assert results
    assert results == sorted(results, key=lambda item: item.score, reverse=True)


def test_vector_store_filter_prefers_aeb() -> None:
    store = _store()

    results = store.search("AEB 低速跟车", top_k=5, filters={"function": "AEB"})

    assert results
    assert all(result.metadata.get("function") == "AEB" for result in results)


def test_vector_store_filter_fallback_when_no_match() -> None:
    store = _store()

    results = store.search("AEB", top_k=3, filters={"function": "NO_SUCH_FUNCTION"})

    assert results

