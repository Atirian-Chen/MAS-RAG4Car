"""End-to-end AutoDev RAG pipeline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from autodev_rag.agents.domain_expert import DomainExpertAgent
from autodev_rag.agents.planner import PlannerAgent
from autodev_rag.agents.verifier import VerificationAgent
from autodev_rag.models import PipelineTrace
from autodev_rag.report_generator import ReportGenerator
from autodev_rag.vector_store import LocalVectorStore


class AutoDevRAGPipeline:
    def __init__(
        self,
        vector_store: LocalVectorStore,
        planner_agent: PlannerAgent | None = None,
        expert_agent: DomainExpertAgent | None = None,
        verifier_agent: VerificationAgent | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.planner_agent = planner_agent or PlannerAgent()
        self.expert_agent = expert_agent or DomainExpertAgent()
        self.verifier_agent = verifier_agent or VerificationAgent()

    def run(
        self,
        query: str,
        top_k: int = 5,
        output_dir: str | Path = "outputs",
        write_report: bool = True,
    ) -> PipelineTrace:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        planner_output = self.planner_agent.plan(query)
        retrieved_chunks = self.vector_store.search(
            query,
            top_k=top_k,
            filters=planner_output.retrieval_filters,
        )
        expert_output = self.expert_agent.answer(query, planner_output, retrieved_chunks)
        verifier_output = self.verifier_agent.verify(query, expert_output, retrieved_chunks)

        safe_name = hashlib.sha1(query.encode("utf-8")).hexdigest()[:12]
        report_path = output_dir / f"report_{safe_name}.md"
        trace_path = output_dir / f"trace_{safe_name}.json"

        if write_report:
            ReportGenerator.generate(
                query=query,
                planner_output=planner_output,
                retrieved_chunks=retrieved_chunks,
                expert_output=expert_output,
                verifier_output=verifier_output,
                output_path=report_path,
            )

        trace = PipelineTrace(
            query=query,
            planner_output=planner_output,
            retrieved_chunks=retrieved_chunks,
            expert_output=expert_output,
            verifier_output=verifier_output,
            final_report_path=str(report_path),
        )
        trace_path.write_text(
            json.dumps(trace.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return trace

