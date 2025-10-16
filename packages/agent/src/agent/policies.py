"""Valida comandos permitidos."""

from __future__ import annotations

ALLOWED_COMMANDS = {"python", "pip", "pytest", "ruff", "mypy", "bandit"}


def is_allowed(command: str) -> bool:
    return command.split()[0] in ALLOWED_COMMANDS
