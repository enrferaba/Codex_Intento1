"""Comandos de ingesta placeholder."""

from __future__ import annotations

from feriactl.commands.base import CommandResult


def run(repo: str) -> CommandResult:
    return CommandResult(stdout=f"Ingest placeholder for {repo}")
