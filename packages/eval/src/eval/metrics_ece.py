"""ECE simplificada."""

from __future__ import annotations

from typing import Sequence, Tuple

# Cada entrada: (peso, confianza_media, exactitud_media)
Bin = Tuple[float, float, float]


def ece(bins: Sequence[Bin]) -> float:
    if not bins:
        return 0.0
    total = sum(weight for weight, _, _ in bins)
    if total <= 0:
        return 0.0
    error = sum(weight * abs(confidence - accuracy) for weight, confidence, accuracy in bins)
    return error / total
