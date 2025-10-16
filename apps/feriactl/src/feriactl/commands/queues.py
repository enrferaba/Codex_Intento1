"""Comandos para gestionar colas."""

from __future__ import annotations

from feriactl.commands.base import CommandResult


def list(stats: bool = False) -> CommandResult:  # noqa: A003 - compatibilidad con nombre del comando
    suffix = " con estadísticas" if stats else ""
    return CommandResult(stdout=f"Queues placeholder{suffix}")
