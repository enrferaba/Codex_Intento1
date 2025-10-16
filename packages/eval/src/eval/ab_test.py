"""Evaluación A/B básica."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VariantResult:
    name: str
    ndcg: float
    p95: float
    ece: float
    cost: float


def is_winner(candidate: VariantResult, control: VariantResult) -> bool:
    return (
        candidate.ndcg >= control.ndcg - 0.01
        and candidate.p95 <= control.p95 + 0.2
        and candidate.ece <= control.ece + 0.02
        and candidate.cost <= control.cost * 1.1
    )
