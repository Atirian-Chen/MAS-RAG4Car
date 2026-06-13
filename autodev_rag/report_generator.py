"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path

from autodev_rag.models import ExpertOutput, PlannerOutput, RetrievedChunk, VerificationOutput


class ReportGenerator:
    @staticmethod
    def generate(
        query: str,
        planner_output: PlannerOutput,
        retrieved_chunks: list[RetrievedChunk],
        expert_output: ExpertOutput,
        verifier_output: VerificationOutput,
        output_path: str | Path,
    ) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = ReportGenerator._render(
            query,
            planner_output,
            retrieved_chunks,
            expert_output,
            verifier_output,
        )
        output_path.write_text(content, encoding="utf-8")
        return output_path

    @staticmethod
    def _render(
        query: str,
        planner_output: PlannerOutput,
        retrieved_chunks: list[RetrievedChunk],
        expert_output: ExpertOutput,
        verifier_output: VerificationOutput,
    ) -> str:
        evidence_rows = []
        for rank, chunk in enumerate(retrieved_chunks, start=1):
            preview = " ".join(chunk.text.split())
            if len(preview) > 140:
                preview = f"{preview[:137]}..."
            evidence_rows.append(
                "| {rank} | {citation} | {score:.3f} | {entity_type} | {function} | {preview} |".format(
                    rank=rank,
                    citation=chunk.citation,
                    score=chunk.score,
                    entity_type=chunk.metadata.get("entity_type", ""),
                    function=chunk.metadata.get("function") or "",
                    preview=preview.replace("|", "\\|"),
                )
            )

        citations = ", ".join(expert_output.citations) if expert_output.citations else "None"
        unsupported = "\n".join(f"- {item}" for item in verifier_output.unsupported_claims) or "- None"
        assumptions = "\n".join(f"- {item}" for item in expert_output.assumptions) or "- None"
        missing = "\n".join(f"- {item}" for item in expert_output.missing_info) or "- None"
        entities = "\n".join(f"- {item}" for item in expert_output.related_entities) or "- None"

        return f"""# AutoDev Multi-Agent RAG Report

## 1. User Query

{query}

## 2. Planner Result

- Intent: {planner_output.intent}
- Target Function: {planner_output.target_function or "None"}
- Needed Entities: {", ".join(planner_output.needed_entities)}
- Retrieval Filters: `{planner_output.retrieval_filters}`

## 3. Retrieved Evidence

| Rank | Citation | Score | Entity Type | Function | Evidence Preview |
| --- | --- | ---: | --- | --- | --- |
{chr(10).join(evidence_rows) if evidence_rows else "| - | - | - | - | - | - |"}

## 4. Domain Expert Analysis

{expert_output.answer}

## 5. Related Engineering Entities

{entities}

## 6. Assumptions and Missing Information

### Assumptions

{assumptions}

### Missing Information

{missing}

## 7. Verification Result

- Groundedness Score: {verifier_output.groundedness_score:.3f}
- Citation Coverage: {verifier_output.citation_coverage:.3f}
- Unsupported Claims:
{unsupported}
- Final Verdict: {verifier_output.final_verdict}

## 8. Traceability Notes

This report is grounded on the retrieved citations: {citations}.
"""

