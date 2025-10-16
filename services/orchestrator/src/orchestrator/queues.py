"""Colas placeholder."""

from __future__ import annotations

from collections import deque

FAST = deque()
BATCH = deque()


def depth(queue: str) -> int:
    if queue == "fast":
        return len(FAST)
    if queue == "batch":
        return len(BATCH)
    raise ValueError("Queue desconocida")
