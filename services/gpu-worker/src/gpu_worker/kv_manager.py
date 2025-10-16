"""KV cache manager."""

from __future__ import annotations

_cache: dict[str, str] = {}


def evict() -> None:
    _cache.clear()
