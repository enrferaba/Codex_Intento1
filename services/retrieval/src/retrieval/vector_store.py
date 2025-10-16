"""Vector store wrapper."""

from __future__ import annotations


def search(query: str, top_k: int = 5) -> list[str]:
    return [f"chunk-{i}" for i in range(top_k)]
