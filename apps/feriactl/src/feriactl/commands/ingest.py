"""Comando ingest."""

from __future__ import annotations

import typer

app = typer.Typer(help="Lanzar ingestas")


@app.command()
def run(repo: str) -> None:
    typer.echo(f"Ingest placeholder for {repo}")
