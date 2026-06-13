from pathlib import Path

from autodev_rag.agents import DomainExpertAgent, PlannerAgent, VerificationAgent
from autodev_rag.chunker import chunk_documents
from autodev_rag.config import DOCS_DIR
from autodev_rag.document_loader import load_documents
from autodev_rag.pipeline import AutoDevRAGPipeline
from autodev_rag.vector_store import LocalVectorStore


def test_pipeline_run_generates_report_and_trace(tmp_path: Path) -> None:
    documents = load_documents(DOCS_DIR)
    chunks = chunk_documents(documents)
    store = LocalVectorStore()
    store.build(chunks)
    pipeline = AutoDevRAGPipeline(
        vector_store=store,
        planner_agent=PlannerAgent(),
        expert_agent=DomainExpertAgent(),
        verifier_agent=VerificationAgent(),
    )

    trace = pipeline.run("AEB 在雨天低速场景误触发可能涉及哪些风险？", output_dir=tmp_path)
    trace_dict = trace.model_dump(mode="json")

    assert trace_dict["planner_output"]
    assert trace_dict["retrieved_chunks"]
    assert trace_dict["expert_output"]
    assert trace_dict["verifier_output"]
    assert trace.planner_output.intent == "risk_analysis"
    assert trace.planner_output.target_function == "AEB"
    assert trace.expert_output.citations
    assert len(trace.expert_output.citations) < len(trace.retrieved_chunks)
    assert trace.verifier_output.final_verdict in {"pass", "pass_with_minor_risk"}
    assert Path(trace.final_report_path).exists()
    assert list(tmp_path.glob("trace_*.json"))
