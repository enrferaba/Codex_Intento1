"""Motor de razonamiento (placeholder)."""

from __future__ import annotations


def score_confidence(evidence_count: int) -> float:
    return min(1.0, 0.2 * evidence_count)
