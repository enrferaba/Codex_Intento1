"""Token bucket simple."""

from __future__ import annotations

from time import time

RATE = 30
BURST = 60
_tokens = BURST
_last_refill = time()


def allow() -> bool:
    global _tokens, _last_refill
    now = time()
    elapsed = now - _last_refill
    refill = int(elapsed * RATE)
    if refill:
        _tokens = min(BURST, _tokens + refill)
        _last_refill = now
    if _tokens <= 0:
        return False
    _tokens -= 1
    return True
