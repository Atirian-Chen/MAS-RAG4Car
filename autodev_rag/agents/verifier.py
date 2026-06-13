"""Rule-based groundedness verifier."""

from __future__ import annotations

import re

from autodev_rag.models import ExpertOutput, RetrievedChunk, VerificationOutput


ENTITY_PATTERN = re.compile(
    r"\b(?:REQ-[A-Z]+-\d+|TC-[A-Z]+(?:-[A-Z]+)+-\d+|RISK-[A-Z]+-\d+|BUG-[A-Z]+-\d+|SIG-[A-Z]+-\d+)\b"
)


class VerificationAgent:
    STRONG_ASSERTIONS = ("必须", "显著", "完全", "保证", "always", "never")
    QUERY_TERMS = (
        "AEB",
        "LKA",
        "BMS",
        "雨天",
        "低速",
        "高温",
        "弯道",
        "误触发",
        "风险",
        "测试",
        "验证",
        "需求",
        "缺陷",
        "根因",
        "制动",
        "车道",
        "电池",
        "温度",
        "扭矩",
        "信号",
    )

    def verify(
        self,
        query: str,
        expert_output: ExpertOutput,
        retrieved_chunks: list[RetrievedChunk],
    ) -> VerificationOutput:
        retrieved_by_citation = {chunk.citation: chunk for chunk in retrieved_chunks}
        retrieved_citations = set(retrieved_by_citation)
        cited = set(expert_output.citations)
        hit_count = len(cited & retrieved_citations)
        citation_coverage = hit_count / len(retrieved_chunks) if retrieved_chunks else 0.0
        valid_cited_chunks = [retrieved_by_citation[citation] for citation in expert_output.citations if citation in retrieved_by_citation]

        unsupported_claims: list[str] = []
        if not expert_output.citations:
            unsupported_claims.append("Answer has no citations.")
        invalid_citations = sorted(cited - retrieved_citations)
        if invalid_citations:
            unsupported_claims.append(f"Answer cites chunks that were not retrieved: {', '.join(invalid_citations)}.")
        if len(expert_output.citations) < 2 and any(
            token in expert_output.answer for token in self.STRONG_ASSERTIONS
        ):
            unsupported_claims.append("Strong assertion appears with insufficient citations.")
        if retrieved_chunks and not expert_output.related_entities:
            unsupported_claims.append("No engineering entity IDs were extracted from evidence.")
        if len(valid_cited_chunks) == len(retrieved_chunks) and len(retrieved_chunks) > 3:
            unsupported_claims.append("Answer cites every retrieved chunk; evidence selection may be insufficiently discriminative.")

        cited_entities = self._extract_entities("\n".join(chunk.text for chunk in valid_cited_chunks))
        answer_entities = set(expert_output.related_entities) | self._extract_entities(expert_output.answer)
        unsupported_entities = sorted(answer_entities - cited_entities)
        if answer_entities and unsupported_entities:
            unsupported_claims.append(f"Related entities are not present in cited evidence: {', '.join(unsupported_entities)}.")

        query_terms = self._query_terms(query)
        cited_text = "\n".join(chunk.text for chunk in valid_cited_chunks)
        query_term_hits = {term for term in query_terms if term in cited_text}
        if query_terms and not query_term_hits and valid_cited_chunks:
            unsupported_claims.append("Cited evidence has weak lexical overlap with the query focus.")

        citation_validity_component = hit_count / len(expert_output.citations) if expert_output.citations else 0.0
        citation_focus_component = min(hit_count / 3, 1.0)
        entity_support_component = (
            len(answer_entities & cited_entities) / len(answer_entities)
            if answer_entities
            else (0.4 if valid_cited_chunks else 0.0)
        )
        query_support_component = 1.0 if not query_terms or query_term_hits else 0.0
        penalty = min(len(unsupported_claims) * 0.25, 0.75)
        groundedness_score = max(
            0.0,
            min(
                1.0,
                0.35 * citation_validity_component
                + 0.25 * citation_focus_component
                + 0.25 * entity_support_component
                + 0.15 * query_support_component
                - penalty,
            ),
        )

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

    def _extract_entities(self, text: str) -> set[str]:
        return set(ENTITY_PATTERN.findall(text))

    def _query_terms(self, query: str) -> set[str]:
        terms = {term for term in self.QUERY_TERMS if term in query}
        terms.update(ENTITY_PATTERN.findall(query))
        return terms
