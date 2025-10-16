"""Calcula Precision@Coverage simple."""

from __future__ import annotations

from typing import Sequence


def precision_at_threshold(confidences: Sequence[float], labels: Sequence[bool], threshold: float) -> tuple[float, float]:
    selected = [label for conf, label in zip(confidences, labels) if conf >= threshold]
    if not confidences:
        return 0.0, 0.0
    coverage = len(selected) / len(confidences)
    if not selected:
        return 1.0, coverage
    precision = sum(1 for label in selected if label) / len(selected)
    return precision, coverage
