"""Comando scale placeholder."""

from __future__ import annotations

import typer

app = typer.Typer(help="Escalar workers")


@app.command()
def set(agent: int = typer.Option(2), indexing: int = typer.Option(4)) -> None:
    typer.echo(f"Scaling agent={agent}, indexing={indexing} (placeholder)")
