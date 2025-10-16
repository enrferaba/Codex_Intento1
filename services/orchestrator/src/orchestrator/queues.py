"""Gestión de colas con métricas de profundidad y antigüedad."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Any, Deque, Dict, Iterable, List


@dataclass
class QueueItem:
    payload: Any
    enqueued_at: float


@dataclass(frozen=True)
class QueueSnapshot:
    name: str
    depth: int
    total_enqueued: int
    total_dequeued: int
    oldest_age: float | None


class QueueManager:
    """Administra múltiples colas priorizadas."""

    def __init__(self, names: Iterable[str]) -> None:
        names_list = list(dict.fromkeys(names))
        if not names_list:
            raise ValueError("At least one queue must be declared")
        self._queues: Dict[str, Deque[QueueItem]] = {name: deque() for name in names_list}
        self._stats: Dict[str, Dict[str, int]] = {
            name: {"enqueued": 0, "dequeued": 0} for name in names_list
        }
        self._lock = Lock()

    def enqueue(self, queue: str, payload: Any, *, now: float | None = None) -> None:
        now_monotonic = monotonic() if now is None else now
        with self._lock:
            self._ensure_queue(queue)
            self._queues[queue].append(QueueItem(payload=payload, enqueued_at=now_monotonic))
            self._stats[queue]["enqueued"] += 1

    def dequeue(self, queue: str) -> Any | None:
        with self._lock:
            self._ensure_queue(queue)
            if not self._queues[queue]:
                return None
            item = self._queues[queue].popleft()
            self._stats[queue]["dequeued"] += 1
            return item.payload

    def depth(self, queue: str) -> int:
        with self._lock:
            self._ensure_queue(queue)
            return len(self._queues[queue])

    def stats(self) -> List[QueueSnapshot]:
        with self._lock:
            snapshots: List[QueueSnapshot] = []
            now = monotonic()
            for name, queue in self._queues.items():
                oldest_age: float | None = None
                if queue:
                    oldest_age = max(0.0, now - queue[0].enqueued_at)
                stats = self._stats[name]
                snapshots.append(
                    QueueSnapshot(
                        name=name,
                        depth=len(queue),
                        total_enqueued=stats["enqueued"],
                        total_dequeued=stats["dequeued"],
                        oldest_age=oldest_age,
                    )
                )
            return snapshots

    def clear(self) -> None:
        with self._lock:
            for queue in self._queues.values():
                queue.clear()
            for stats in self._stats.values():
                stats["enqueued"] = 0
                stats["dequeued"] = 0

    def _ensure_queue(self, queue: str) -> None:
        if queue not in self._queues:
            raise KeyError(f"Unknown queue '{queue}'")


__all__ = ["QueueManager", "QueueSnapshot"]
