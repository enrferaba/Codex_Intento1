"""Comando queues."""

from __future__ import annotations

import typer

app = typer.Typer(help="Gestiona colas")


@app.command()
def list(stats: bool = typer.Option(False, help="Mostrar estadísticas")) -> None:
    suffix = " con stats" if stats else ""
    typer.echo(f"Queues placeholder{suffix}")
