"""Rutas de evaluación."""

from __future__ import annotations

from api_gateway.framework import Router

router = Router(prefix="/v1")


@router.get("/eval/report")
def eval_report(version: str | None = None) -> dict[str, str | None]:
    return {"version": version or "latest", "status": "placeholder"}
