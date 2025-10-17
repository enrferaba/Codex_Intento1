"""Almacén de documentos ingeridos y utilidades de búsqueda."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Iterable, Sequence
from uuid import uuid4


@dataclass(slots=True)
class DocumentMatch:
    path: str
    snippet: str
    score: float
    repository: str


class DocumentStore:
    """Persistencia JSON extremadamente simple para pruebas de integración."""

    def __init__(self, base_path: Path, *, max_document_chars: int = 20_000) -> None:
        self._base_path = base_path
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._index_path = self._base_path / "index.json"
        self._lock = Lock()
        self._max_document_chars = max_document_chars
        if not self._index_path.exists():
            self._write({"documents": [], "jobs": []})

    # API pública -----------------------------------------------------
    def add_documents(
        self,
        *,
        repository: str,
        modes: Sequence[str],
        documents: Iterable[tuple[str, str]],
    ) -> tuple[str, int]:
        job_id = uuid4().hex
        stored_docs: list[dict[str, object]] = []
        for path, text in documents:
            stored_docs.append(
                {
                    "document_id": uuid4().hex,
                    "job_id": job_id,
                    "repository": repository,
                    "path": path,
                    "text": _trim(text, self._max_document_chars),
                }
            )
        with self._lock:
            payload = self._read()
            payload["documents"].extend(stored_docs)
            payload["jobs"].append(
                {
                    "job_id": job_id,
                    "repository": repository,
                    "document_count": len(stored_docs),
                    "modes": list(modes),
                }
            )
            self._write(payload)
        return job_id, len(stored_docs)

    def search(self, query: str, *, limit: int = 3) -> list[DocumentMatch]:
        query = query.strip()
        if not query:
            return []
        tokens = _tokenize(query)
        if not tokens:
            return []
        payload = self._read()
        matches: list[DocumentMatch] = []
        for doc in payload["documents"]:
            text: str = doc["text"]
            score = _score(text, tokens)
            if score <= 0:
                continue
            snippet = _build_snippet(text, tokens)
            matches.append(
                DocumentMatch(
                    path=str(doc["path"]),
                    snippet=snippet,
                    score=score,
                    repository=str(doc["repository"]),
                )
            )
        matches.sort(key=lambda item: item.score, reverse=True)
        return matches[: max(limit, 1)]

    def stats(self) -> dict[str, int]:
        payload = self._read()
        repositories = {doc["repository"] for doc in payload["documents"]}
        return {
            "documents": len(payload["documents"]),
            "jobs": len(payload["jobs"]),
            "repositories": len(repositories),
        }

    # Persistencia ----------------------------------------------------
    def _read(self) -> dict[str, list]:
        with self._index_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, payload: dict[str, list]) -> None:
        with self._index_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[\w-]+", text.lower()) if token]


def _score(text: str, tokens: Sequence[str]) -> float:
    lowered = text.lower()
    counts = Counter(_tokenize(lowered))
    total = sum(counts.values()) or 1
    score = 0.0
    for token in tokens:
        score += counts.get(token, 0) / total
    return score


def _build_snippet(text: str, tokens: Sequence[str], *, window: int = 240) -> str:
    lowered = text.lower()
    best_index = None
    for token in tokens:
        index = lowered.find(token)
        if index != -1:
            best_index = index if best_index is None else min(best_index, index)
    if best_index is None:
        return text[:window].strip()
    start = max(best_index - window // 3, 0)
    end = min(start + window, len(text))
    return text[start:end].strip()


def _trim(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


@lru_cache(maxsize=1)
def get_document_store() -> DocumentStore:
    base_dir = Path(os.getenv("FERIA_STORAGE_PATH", "/app/storage")) / "ingest"
    return DocumentStore(base_dir)


def reset_document_state_for_tests() -> None:
    get_document_store.cache_clear()
