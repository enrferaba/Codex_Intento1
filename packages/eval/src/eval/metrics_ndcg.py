"""Cálculo simplificado de nDCG."""

from __future__ import annotations

from math import log2
from typing import Sequence


def ndcg(scores: Sequence[float]) -> float:
    if not scores:
        return 0.0
    ideal = sum(score / log2(idx + 2) for idx, score in enumerate(sorted(scores, reverse=True)))
    actual = sum(score / log2(idx + 2) for idx, score in enumerate(scores))
    return actual / ideal if ideal else 0.0
