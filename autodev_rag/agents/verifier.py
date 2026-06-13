"""Rule-based groundedness verifier."""

from __future__ import annotations

from autodev_rag.models import ExpertOutput, RetrievedChunk, VerificationOutput


class VerificationAgent:
    STRONG_ASSERTIONS = ("必须", "显著", "完全", "保证", "always", "never")

    def verify(
        self,
        query: str,
        expert_output: ExpertOutput,
        retrieved_chunks: list[RetrievedChunk],
    ) -> VerificationOutput:
        retrieved_citations = {chunk.citation for chunk in retrieved_chunks}
        cited = set(expert_output.citations)
        hit_count = len(cited & retrieved_citations)
        citation_coverage = hit_count / len(retrieved_chunks) if retrieved_chunks else 0.0

        unsupported_claims: list[str] = []
        if not expert_output.citations:
            unsupported_claims.append("Answer has no citations.")
        if len(expert_output.citations) < 2 and any(
            token in expert_output.answer for token in self.STRONG_ASSERTIONS
        ):
            unsupported_claims.append("Strong assertion appears with insufficient citations.")
        if retrieved_chunks and not expert_output.related_entities:
            unsupported_claims.append("No engineering entity IDs were extracted from evidence.")

        citation_component = min(len(expert_output.citations) / max(len(retrieved_chunks), 1), 1.0)
        entity_component = min(len(expert_output.related_entities) / 4, 1.0)
        penalty = min(len(unsupported_claims) * 0.25, 0.75)
        groundedness_score = max(0.0, min(1.0, 0.55 * citation_component + 0.35 * entity_component + 0.10 - penalty))

        if groundedness_score >= 0.8:
            verdict = "pass"
        elif groundedness_score >= 0.5:
            verdict = "pass_with_minor_risk"
        else:
            verdict = "fail"

        return VerificationOutput(
            groundedness_score=round(groundedness_score, 3),
            citation_coverage=round(citation_coverage, 3),
            unsupported_claims=unsupported_claims,
            final_verdict=verdict,
        )

