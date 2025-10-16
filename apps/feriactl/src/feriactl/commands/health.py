"""Comandos relacionados con el estado general del sistema."""

from __future__ import annotations

import json

import typer

from feriactl.utils.api import FeriaAPI, FeriaAPIError

app = typer.Typer(help="Salud del sistema")


@app.command()
def verbose(
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        "-b",
        help="URL base de la API (prioriza FERIA_API_URL).",
    ),
    pretty: bool = typer.Option(True, help="Formatea la salida JSON."),
) -> None:
    """Imprime el payload completo del endpoint de salud."""

    try:
        with FeriaAPI(base_url=base_url) as api:
            payload = api.get_json("/v1/health")
    except FeriaAPIError as exc:  # pragma: no cover - CLI maneja error
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    if pretty:
        typer.echo(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        typer.echo(json.dumps(payload))
