"""Endpoint para ejecutar el agente."""

from __future__ import annotations

from api_gateway.framework import Router

router = Router(prefix="/v1")


@router.post("/agent/run")
def agent_run(payload: dict[str, object] | None = None) -> dict[str, str]:
    return {"run_id": "run-placeholder", "status": "queued"}
