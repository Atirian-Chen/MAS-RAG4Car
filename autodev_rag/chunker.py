"""Paragraph-aware chunking and metadata inference."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from autodev_rag.models import Chunk, Document


FUNCTION_PATTERNS = {
    "AEB": ("AEB", "自动紧急制动", "紧急制动"),
    "LKA": ("LKA", "车道保持"),
    "BMS": ("BMS", "电池管理", "电池"),
}


def infer_entity_type(source_name: str, text: str) -> str:
    lower = source_name.lower()
    if "requirement" in lower:
        return "Requirement"
    if "test" in lower:
        return "TestCase"
    if "risk" in lower:
        return "Risk"
    if "defect" in lower or "bug" in lower:
        return "Defect"
    if "signal" in lower:
        return "Signal"
    if "process" in lower:
        return "Process"
    if re.search(r"\bREQ-[A-Z]+-\d+\b", text):
        return "Requirement"
    if re.search(r"\bTC-[A-Z]+(?:-[A-Z]+)+-\d+\b", text):
        return "TestCase"
    if re.search(r"\bRISK-[A-Z]+-\d+\b", text):
        return "Risk"
    if re.search(r"\bBUG-[A-Z]+-\d+\b", text):
        return "Defect"
    if re.search(r"\bSIG-[A-Z]+-\d+\b", text):
        return "Signal"
    return "General"


def infer_function(text: str, fallback: str | None = None) -> str | None:
    scores: dict[str, int] = {}
    for function, patterns in FUNCTION_PATTERNS.items():
        scores[function] = sum(text.upper().count(pattern.upper()) for pattern in patterns)
    best_function, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        return best_function
    return fallback


def _paragraphs(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n")
    parts = re.split(r"\n\s*\n", normalized)
    return [part.strip() for part in parts if part.strip()]


def _build_text_with_overlap(parts: list[str], overlap: int) -> str:
    text = "\n\n".join(parts).strip()
    if overlap <= 0 or len(text) <= overlap:
        return ""
    return text[-overlap:]


def chunk_documents(
    documents: Iterable[Document],
    chunk_size: int = 700,
    overlap: int = 100,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        source_name = Path(document.path).name
        doc_function = infer_function(f"{document.title}\n{document.text}")
        current_parts: list[str] = []
        current_len = 0
        chunk_index = 0

        def flush() -> None:
            nonlocal current_parts, current_len, chunk_index
            if not current_parts:
                return
            text = "\n\n".join(current_parts).strip()
            entity_type = infer_entity_type(source_name, text)
            function = infer_function(text, doc_function)
            metadata = {
                **document.metadata,
                "domain": "automotive_software",
                "entity_type": entity_type,
                "function": function,
            }
            chunks.append(
                Chunk(
                    doc_id=document.doc_id,
                    chunk_id=f"chunk_{chunk_index:03d}",
                    text=text,
                    metadata=metadata,
                )
            )
            chunk_index += 1
            overlap_text = _build_text_with_overlap(current_parts, overlap)
            current_parts = [overlap_text] if overlap_text else []
            current_len = len(overlap_text)

        for paragraph in _paragraphs(document.text):
            paragraph_len = len(paragraph)
            if current_parts and current_len + paragraph_len + 2 > chunk_size:
                flush()
            current_parts.append(paragraph)
            current_len += paragraph_len + 2
            if paragraph_len > chunk_size:
                flush()
        flush()
    return chunks
