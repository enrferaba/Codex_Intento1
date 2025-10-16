"""Tipos comunes."""

from __future__ import annotations

from typing import TypedDict


class Citation(TypedDict):
    path: str
    start_line: int
    end_line: int
    score: float
