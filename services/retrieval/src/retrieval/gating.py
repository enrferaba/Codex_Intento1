"""Gating placeholder."""

from __future__ import annotations


def should_query(question: str) -> bool:
    return len(question) > 0
