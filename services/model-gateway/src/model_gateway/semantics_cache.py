"""Cache semántica simple."""

from __future__ import annotations

_cache: dict[str, str] = {}


def get(key: str) -> str | None:
    return _cache.get(key)


def set(key: str, value: str) -> None:
    _cache[key] = value
