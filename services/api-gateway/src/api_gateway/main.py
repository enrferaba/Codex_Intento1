"""Aplicación HTTP simplificada."""

from __future__ import annotations

from api_gateway import routes
from api_gateway.framework import App

app = App(title="FERIA Precision Codex API")
app.include_router(routes.health.router)
app.include_router(routes.query.router)
app.include_router(routes.admin.router)
