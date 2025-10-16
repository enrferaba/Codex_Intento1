"""Comandos relacionados con el estado del sistema."""

from __future__ import annotations

from typing import Iterable, Sequence, Type

from feriactl.commands.base import CommandResult
from feriactl.utils.api import FeriaAPI, FeriaAPIError
from feriactl.utils.tabulate import render


def show(base_url: str | None = None, api_factory: Type[FeriaAPI] | None = None) -> CommandResult:
    """Obtiene el estado desde la API y devuelve una tabla amigable."""

    factory = api_factory or FeriaAPI
    try:
        with factory(base_url=base_url) as api:
            payload = api.get_json("/v1/health")
    except FeriaAPIError as exc:
        return CommandResult(exit_code=1, stderr=str(exc))

    components = _normalise_components(payload.get("components")) if isinstance(payload, dict) else []
    if not components:
        return CommandResult(stdout="La API no devolvió componentes de salud.")

    table = render(["Componente", "Estado", "Detalle"], components)
    footer = (
        f"Versión: {payload.get('version', 'desconocida')} · Uptime: {payload.get('uptime_seconds', '?')} s"
        if isinstance(payload, dict)
        else ""
    )
    stdout_lines = [table, "", footer] if footer else [table]
    return CommandResult(stdout="\n".join(stdout_lines).rstrip())


def _normalise_components(raw_components: object) -> list[Sequence[str]]:
    rows: list[Sequence[str]] = []
    if not isinstance(raw_components, Iterable):
        return rows
    for item in raw_components:
        if isinstance(item, dict):
            name = str(item.get("name", "desconocido"))
            status = str(item.get("status", "desconocido"))
            detail_raw = item.get("detail", "")
            detail = "" if detail_raw is None else str(detail_raw)
            rows.append((name, status, detail))
    return rows
