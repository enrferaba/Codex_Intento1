"""Reranker placeholder."""

from __future__ import annotations

from typing import Sequence


def rerank(items: Sequence[str]) -> Sequence[str]:
    return items[:5]
