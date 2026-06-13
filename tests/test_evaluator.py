from pathlib import Path

from autodev_rag.chunker import chunk_documents
from autodev_rag.config import DOCS_DIR, EVAL_CASES_PATH
from autodev_rag.document_loader import load_documents
from autodev_rag.evaluator import evaluate_all, load_eval_cases
from autodev_rag.pipeline import AutoDevRAGPipeline
from autodev_rag.vector_store import LocalVectorStore


def test_load_eval_cases() -> None:
    cases = load_eval_cases(EVAL_CASES_PATH)

    assert len(cases) == 20


def test_evaluate_all_returns_metrics(tmp_path: Path) -> None:
    documents = load_documents(DOCS_DIR)
    chunks = chunk_documents(documents)
    store = LocalVectorStore()
    store.build(chunks)
    pipeline = AutoDevRAGPipeline(vector_store=store)
    cases = load_eval_cases(EVAL_CASES_PATH)

    summary = evaluate_all(pipeline, cases, output_dir=tmp_path)

    for metric in [
        "intent_accuracy",
        "avg_entity_recall",
        "citation_hit_rate",
        "avg_groundedness_score",
        "invalid_answer_rate",
    ]:
        assert metric in summary
        assert 0 <= summary[metric] <= 1
    assert summary["total"] == 20
    assert summary["intent_accuracy"] >= 0.8
    assert summary["avg_entity_recall"] >= 0.6
    assert summary["citation_hit_rate"] >= 0.6
