"""Comandos de escalado."""

from __future__ import annotations

from feriactl.commands.base import CommandResult


def set(agent: int = 2, indexing: int = 4) -> CommandResult:
    return CommandResult(stdout=f"Scaling agent={agent}, indexing={indexing} (placeholder)")
