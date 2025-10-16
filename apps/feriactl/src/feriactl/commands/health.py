"""Comandos de salud para ``feriactl``."""

from __future__ import annotations

import json
from typing import Type

from feriactl.commands.base import CommandResult
from feriactl.utils.api import FeriaAPI, FeriaAPIError


def verbose(
    base_url: str | None = None,
    pretty: bool = True,
    api_factory: Type[FeriaAPI] | None = None,
) -> CommandResult:
    """Devuelve el payload JSON de ``/v1/health``."""

    factory = api_factory or FeriaAPI
    try:
        with factory(base_url=base_url) as api:
            payload = api.get_json("/v1/health")
    except FeriaAPIError as exc:
        return CommandResult(exit_code=1, stderr=str(exc))

    if pretty:
        text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    else:
        text = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return CommandResult(stdout=text)
