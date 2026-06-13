"""Evaluation utilities for the AutoDev RAG pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from autodev_rag.models import EvalCase, EvalResult
from autodev_rag.pipeline import AutoDevRAGPipeline


def load_eval_cases(path: str | Path) -> list[EvalCase]:
    path = Path(path)
    cases: list[EvalCase] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                cases.append(EvalCase.model_validate_json(stripped))
            except ValueError as exc:
                raise ValueError(f"invalid eval case at line {line_number}: {exc}") from exc
    return cases


def evaluate_case(
    pipeline: AutoDevRAGPipeline,
    case: EvalCase,
    output_dir: str | Path = "outputs/eval",
) -> EvalResult:
    trace = pipeline.run(case.query, top_k=6, output_dir=output_dir, write_report=True)
    retrieved_entity_types = {
        str(chunk.metadata.get("entity_type"))
        for chunk in trace.retrieved_chunks
        if chunk.metadata.get("entity_type")
    }
    expected = set(case.expected_entities)
    entity_recall = len(expected & retrieved_entity_types) / len(expected) if expected else 1.0
    cited_docs = {citation.split("#", 1)[0] for citation in trace.expert_output.citations}
    citation_hit = bool(cited_docs & set(case.must_cite_docs))

    return EvalResult(
        case_id=case.id,
        intent_correct=trace.planner_output.intent == case.expected_intent,
        entity_recall=round(entity_recall, 3),
        citation_hit=citation_hit,
        groundedness_score=trace.verifier_output.groundedness_score,
        invalid=trace.verifier_output.final_verdict == "fail",
    )


def evaluate_all(
    pipeline: AutoDevRAGPipeline,
    cases: list[EvalCase],
    output_dir: str | Path = "outputs/eval",
) -> dict[str, Any]:
    results = [evaluate_case(pipeline, case, output_dir=output_dir) for case in cases]
    total = len(results)
    if total == 0:
        return {
            "total": 0,
            "intent_accuracy": 0.0,
            "avg_entity_recall": 0.0,
            "citation_hit_rate": 0.0,
            "avg_groundedness_score": 0.0,
            "invalid_answer_rate": 0.0,
            "results": [],
        }
    return {
        "total": total,
        "intent_accuracy": round(mean(1.0 if result.intent_correct else 0.0 for result in results), 3),
        "avg_entity_recall": round(mean(result.entity_recall for result in results), 3),
        "citation_hit_rate": round(mean(1.0 if result.citation_hit else 0.0 for result in results), 3),
        "avg_groundedness_score": round(mean(result.groundedness_score for result in results), 3),
        "invalid_answer_rate": round(mean(1.0 if result.invalid else 0.0 for result in results), 3),
        "results": [result.model_dump(mode="json") for result in results],
    }


def save_eval_summary(summary: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

