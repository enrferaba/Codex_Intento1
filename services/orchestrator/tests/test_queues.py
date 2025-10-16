import time

import pytest

from orchestrator.queues import QueueManager


@pytest.fixture
def manager() -> QueueManager:
    return QueueManager(["fast", "batch"])


def test_enqueue_and_depth(manager: QueueManager) -> None:
    assert manager.depth("fast") == 0
    manager.enqueue("fast", {"id": 1}, now=time.monotonic())
    assert manager.depth("fast") == 1


def test_dequeue_returns_payload(manager: QueueManager) -> None:
    manager.enqueue("batch", "payload")
    assert manager.dequeue("batch") == "payload"
    assert manager.dequeue("batch") is None


def test_stats_reports_oldest_age(manager: QueueManager) -> None:
    now = time.monotonic()
    manager.enqueue("fast", "first", now=now - 2)
    manager.enqueue("fast", "second", now=now)
    snapshot = {s.name: s for s in manager.stats()}
    assert snapshot["fast"].depth == 2
    assert snapshot["fast"].oldest_age is not None
    assert snapshot["fast"].oldest_age >= 2


def test_clear_resets_counters(manager: QueueManager) -> None:
    manager.enqueue("fast", 1)
    manager.dequeue("fast")
    manager.clear()
    snapshot = {s.name: s for s in manager.stats()}
    assert snapshot["fast"].depth == 0
    assert snapshot["fast"].total_enqueued == 0
    assert snapshot["fast"].total_dequeued == 0
