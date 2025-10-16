"""Circuit breaker."""

from __future__ import annotations

from time import time

THRESHOLD = 3
OPEN_WINDOW = 30
_failures = 0
_opened_at: float | None = None


def record_failure() -> None:
    global _failures, _opened_at
    _failures += 1
    if _failures >= THRESHOLD:
        _opened_at = time()


def allow_request() -> bool:
    global _failures, _opened_at
    if _opened_at is None:
        return True
    if time() - _opened_at > OPEN_WINDOW:
        _failures = 0
        _opened_at = None
        return True
    return False
