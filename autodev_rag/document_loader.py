"""Markdown document loading utilities."""

from __future__ import annotations

from pathlib import Path

from autodev_rag.models import Document


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def load_documents(docs_dir: str | Path) -> list[Document]:
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        raise FileNotFoundError(f"docs directory not found: {docs_path}")

    documents: list[Document] = []
    for path in sorted(docs_path.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        doc_id = path.stem
        title = _extract_title(text, doc_id)
        metadata = {
            "source_path": str(path),
            "doc_id": doc_id,
            "title": title,
        }
        documents.append(
            Document(
                doc_id=doc_id,
                title=title,
                path=str(path),
                text=text,
                metadata=metadata,
            )
        )
    return documents

