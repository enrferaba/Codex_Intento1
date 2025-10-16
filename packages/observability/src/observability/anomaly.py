"""Detección de anomalías simple."""

from __future__ import annotations

from statistics import mean
from typing import Iterable


def ewma(values: Iterable[float], alpha: float = 0.3) -> float:
    iterator = iter(values)
    try:
        current = next(iterator)
    except StopIteration:
        return 0.0
    for value in iterator:
        current = alpha * value + (1 - alpha) * current
    return current


def z_score(value: float, history: Iterable[float]) -> float:
    data = list(history)
    if not data:
        return 0.0
    avg = mean(data)
    variance = mean((x - avg) ** 2 for x in data)
    std = variance ** 0.5
    if std == 0:
        return 0.0
    return (value - avg) / std
