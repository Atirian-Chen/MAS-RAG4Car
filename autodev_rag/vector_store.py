"""Offline TF-IDF vector store with metadata filtering."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from autodev_rag.models import Chunk, RetrievedChunk


class LocalVectorStore:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            lowercase=True,
            max_features=20000,
        )
        self.chunks: list[Chunk] = []
        self.matrix: Any = None

    def build(self, chunks: list[Chunk]) -> None:
        if not chunks:
            raise ValueError("cannot build vector store with no chunks")
        self.chunks = chunks
        texts = [self._index_text(chunk) for chunk in chunks]
        self.matrix = self.vectorizer.fit_transform(texts)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        if self.matrix is None or not self.chunks:
            raise ValueError("vector store is not built")
        if top_k <= 0:
            return []

        candidate_indices = self._filter_indices(filters or {})
        if not candidate_indices:
            candidate_indices = list(range(len(self.chunks)))

        query_vector = self.vectorizer.transform([query])
        candidate_matrix = self.matrix[candidate_indices]
        similarities = cosine_similarity(query_vector, candidate_matrix).ravel()
        ranked_pairs = sorted(
            zip(candidate_indices, similarities, strict=True),
            key=lambda pair: pair[1],
            reverse=True,
        )

        if not ranked_pairs or ranked_pairs[0][1] <= 0:
            ranked_pairs = self._global_rank(query)

        results: list[RetrievedChunk] = []
        for index, score in ranked_pairs[:top_k]:
            chunk = self.chunks[index]
            results.append(
                RetrievedChunk(
                    doc_id=chunk.doc_id,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=float(max(score, 0.0)),
                    metadata=chunk.metadata,
                )
            )
        return results

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, path: str | Path) -> "LocalVectorStore":
        path = Path(path)
        with path.open("rb") as file:
            store = pickle.load(file)
        if not isinstance(store, cls):
            raise TypeError(f"pickle did not contain {cls.__name__}")
        return store

    def _index_text(self, chunk: Chunk) -> str:
        metadata_bits = [
            str(chunk.metadata.get("entity_type", "")),
            str(chunk.metadata.get("function", "")),
            str(chunk.metadata.get("title", "")),
        ]
        return "\n".join(metadata_bits + [chunk.text])

    def _filter_indices(self, filters: dict[str, Any]) -> list[int]:
        if not filters:
            return list(range(len(self.chunks)))

        matched: list[int] = []
        for index, chunk in enumerate(self.chunks):
            if self._matches_filters(chunk.metadata, filters):
                matched.append(index)
        return matched

    def _matches_filters(self, metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if expected in (None, "", []):
                continue
            actual = metadata.get(key)
            if isinstance(expected, (list, tuple, set)):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        return True

    def _global_rank(self, query: str) -> list[tuple[int, float]]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.matrix).ravel()
        return sorted(
            enumerate(similarities),
            key=lambda pair: pair[1],
            reverse=True,
        )

