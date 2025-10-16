"""Guardrails básicos."""

from __future__ import annotations


def check_output(text: str) -> bool:
    return "http" not in text
