"""Judge placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metrics:
    ndcg: float
    p95: float
    ece: float
    cost: float


def is_promotable(candidate: Metrics, control: Metrics) -> bool:
    return candidate.ndcg >= control.ndcg and candidate.p95 <= control.p95
