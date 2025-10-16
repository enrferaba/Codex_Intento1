"""Dynamic batching."""

from __future__ import annotations

from typing import Iterable


def batch(requests: Iterable[str], max_batch: int = 4) -> list[list[str]]:
    batch: list[list[str]] = []
    current: list[str] = []
    for item in requests:
        current.append(item)
        if len(current) >= max_batch:
            batch.append(current)
            current = []
    if current:
        batch.append(current)
    return batch
