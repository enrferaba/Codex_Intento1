"""Comandos relacionados con la depuración de la plataforma."""

from __future__ import annotations

import json

from core.debug import collect_snapshot, format_snapshot
from feriactl.commands.base import CommandResult


def report(as_json: bool = False) -> CommandResult:
    snapshot = collect_snapshot()

    if as_json:
        payload = snapshot.to_dict()
        return CommandResult(stdout=json.dumps(payload, indent=2, sort_keys=True))

    rendered = format_snapshot(snapshot)
    return CommandResult(stdout=rendered, exit_code=0)
