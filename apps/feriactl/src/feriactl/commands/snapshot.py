"""Comandos para snapshots."""

from __future__ import annotations

from feriactl.commands.base import CommandResult


def create(label: str | None = None) -> CommandResult:
    suffix = f" with label {label}" if label else ""
    return CommandResult(stdout=f"Snapshot placeholder created{suffix}")
