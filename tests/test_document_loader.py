from autodev_rag.config import DOCS_DIR
from autodev_rag.document_loader import load_documents


def test_load_documents_from_data_docs() -> None:
    documents = load_documents(DOCS_DIR)

    assert len(documents) >= 8
    for document in documents:
        assert document.doc_id
        assert document.title
        assert document.text
        assert document.metadata["doc_id"] == document.doc_id

