"""Pydantic data models used across the AutoDev RAG pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


Intent = Literal[
    "requirement_analysis",
    "test_case_generation",
    "risk_analysis",
    "defect_diagnosis",
    "general_qa",
]

Verdict = Literal["pass", "pass_with_minor_risk", "fail"]


class Document(BaseModel):
    doc_id: str
    title: str
    path: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("document text must not be empty")
        return value


class Chunk(BaseModel):
    doc_id: str
    chunk_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def citation(self) -> str:
        return f"{self.doc_id}#{self.chunk_id}"


class RetrievedChunk(BaseModel):
    doc_id: str
    chunk_id: str
    text: str
    score: float = Field(ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def citation(self) -> str:
        return f"{self.doc_id}#{self.chunk_id}"


class PlannerOutput(BaseModel):
    intent: Intent = "general_qa"
    target_function: str | None = None
    needed_entities: list[str] = Field(default_factory=list)
    retrieval_filters: dict[str, Any] = Field(default_factory=dict)
    reasoning_steps: list[str] = Field(default_factory=list)


class ExpertOutput(BaseModel):
    answer: str
    related_entities: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)


class VerificationOutput(BaseModel):
    groundedness_score: float = Field(ge=0.0, le=1.0)
    citation_coverage: float = Field(ge=0.0, le=1.0)
    unsupported_claims: list[str] = Field(default_factory=list)
    final_verdict: Verdict


class PipelineTrace(BaseModel):
    query: str
    planner_output: PlannerOutput
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    expert_output: ExpertOutput
    verifier_output: VerificationOutput
    final_report_path: str


class EvalCase(BaseModel):
    id: str
    query: str
    expected_intent: Intent
    expected_entities: list[str] = Field(default_factory=list)
    must_cite_docs: list[str] = Field(default_factory=list)


class EvalResult(BaseModel):
    case_id: str
    intent_correct: bool
    entity_recall: float = Field(ge=0.0, le=1.0)
    citation_hit: bool
    groundedness_score: float = Field(ge=0.0, le=1.0)
    invalid: bool


def model_to_jsonable(model: BaseModel) -> dict[str, Any]:
    """Return a JSON-friendly dict across Pydantic v2 style models."""
    return model.model_dump(mode="json")


def as_path(value: str | Path) -> Path:
    return value if isinstance(value, Path) else Path(value)

