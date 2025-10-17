"""Aplicación HTTP principal del API Gateway."""

from __future__ import annotations

import os

from api_gateway import routes
from api_gateway.framework import App


def _create_app() -> App:
    app = App(title="FERIA Precision Codex API")
    app.include_router(routes.health.router)
    app.include_router(routes.query.router)
    app.include_router(routes.ingest.router)
    app.include_router(routes.debug.router)
    app.include_router(routes.admin.router)
    return app


app = _create_app()


def run() -> None:  # pragma: no cover - ejecución manual
    host = os.getenv("FERIA_API_HOST", "0.0.0.0")
    port = int(os.getenv("FERIA_API_PORT", "8000"))
    app.serve(host=host, port=port)


if __name__ == "__main__":  # pragma: no cover - ejecución directa
    run()
