"""FastAPI gateway placeholder."""

from __future__ import annotations

from fastapi import FastAPI

from api_gateway.routes import health, query

app = FastAPI(title="FERIA Precision Codex API")
app.include_router(health.router)
app.include_router(query.router)
