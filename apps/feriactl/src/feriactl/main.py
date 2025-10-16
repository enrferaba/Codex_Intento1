"""Punto de entrada de feriactl."""

from __future__ import annotations

import typer

from feriactl.commands import health, ingest, queues, scale, snapshot, status

app = typer.Typer(help="Administra FERIA Precision Codex")
app.add_typer(status.app, name="status")
app.add_typer(health.app, name="health")
app.add_typer(scale.app, name="scale")
app.add_typer(queues.app, name="queues")
app.add_typer(ingest.app, name="ingest")
app.add_typer(snapshot.app, name="snapshot")


if __name__ == "__main__":
    app()
