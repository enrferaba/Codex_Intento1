"""Comandos de estado para feriactl."""

from __future__ import annotations

from typing import Iterable

import typer

from feriactl.utils.api import FeriaAPI, FeriaAPIError
from feriactl.utils.tabulate import render

app = typer.Typer(help="Consultar estado")


def _component_rows(components: Iterable[dict[str, object]]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for component in components:
        name = str(component.get("name", "desconocido"))
        status = str(component.get("status", "desconocido"))
        detail_raw = component.get("detail", "")
        detail = "" if detail_raw is None else str(detail_raw)
        rows.append((name, status, detail))
    return rows


@app.command()
def show(
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        "-b",
        help="URL base de la API (prioriza FERIA_API_URL).",
    ),
) -> None:
    """Muestra el estado resumido de los componentes reportados por la API."""

    try:
        with FeriaAPI(base_url=base_url) as api:
            payload = api.get_json("/v1/health")
    except FeriaAPIError as exc:  # pragma: no cover - CLI maneja error
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    components = payload.get("components", []) if isinstance(payload, dict) else []
    if not components:
        typer.echo("La API no devolvió componentes de salud.")
        return

    table = render(["Componente", "Estado", "Detalle"], _component_rows(components))
    typer.echo(table)
    typer.echo("")
    typer.echo(
        f"Versión: {payload.get('version', 'desconocida')} · Uptime: {payload.get('uptime_seconds', '?')} s"
    )
