"""Orquestador de ingesta."""

from __future__ import annotations


def enqueue(repo: str) -> str:
    return f"job-{repo}"
