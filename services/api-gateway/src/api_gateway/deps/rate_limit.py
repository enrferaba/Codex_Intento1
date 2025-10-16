"""Rate limiting simple."""

from __future__ import annotations

from time import time

WINDOW = 1.0
LIMIT = 5
_state = {"count": 0, "window_start": time()}


def check_rate_limit() -> None:
    now = time()
    if now - _state["window_start"] > WINDOW:
        _state["window_start"] = now
        _state["count"] = 0
    _state["count"] += 1
    if _state["count"] > LIMIT:
        raise RuntimeError("Rate limit exceeded")
