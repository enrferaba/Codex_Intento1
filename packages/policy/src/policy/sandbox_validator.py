"""Validador de sandbox."""

from __future__ import annotations

from typing import Iterable

ALLOWED = {"python", "pip", "pytest", "ruff", "mypy", "bandit"}


def validate(commands: Iterable[str]) -> bool:
    return all(cmd.split()[0] in ALLOWED for cmd in commands)
