"""Comandos relacionados con la depuración de la plataforma."""

from __future__ import annotations

import json

from core.debug import collect_snapshot
from feriactl.commands.base import CommandResult
from feriactl.utils.api import FeriaAPI, FeriaAPIError


def report(as_json: bool = False) -> CommandResult:
    snapshot = collect_snapshot()
    payload = {
        "path": snapshot.working_directory,
        "error_text": None,
        "modes": ["python", "tests"],
        "artifacts": [
            {
                "name": "snapshot.json",
                "content": json.dumps(snapshot.to_dict(), indent=2, sort_keys=True),
                "content_type": "application/json",
            }
        ],
        "metadata": {"python_version": snapshot.python_version, "platform": snapshot.platform},
    }

    try:
        with FeriaAPI() as api:
            response = api.post_json("/v1/debug", payload)
    except FeriaAPIError as exc:
        return CommandResult(exit_code=1, stderr=str(exc))

    if as_json:
        return CommandResult(stdout=json.dumps(response, indent=2, ensure_ascii=False))

    return CommandResult(
        stdout=(
            "Sesión de depuración registrada\n"
            f"ID: {response.get('debug_id')}\n"
            f"Ubicación: {response.get('location')}"
        )
    )
