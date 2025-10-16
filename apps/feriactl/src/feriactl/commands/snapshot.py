"""Comando snapshot."""

from __future__ import annotations

import typer

app = typer.Typer(help="Gestiona snapshots")


@app.command()
def create(label: str = "manual") -> None:
    typer.echo(f"Snapshot placeholder created with label {label}")
