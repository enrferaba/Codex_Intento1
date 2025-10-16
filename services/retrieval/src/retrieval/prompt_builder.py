"""Prompt builder placeholder."""

from __future__ import annotations

from typing import Sequence


def build(question: str, chunks: Sequence[str]) -> str:
    context = "\n".join(chunks)
    return f"Pregunta: {question}\nContexto:\n{context}"
