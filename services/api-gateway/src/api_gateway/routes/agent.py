"""Agent run endpoint."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["agent"])


@router.post("/agent/run")
def agent_run(payload: dict[str, object]) -> dict[str, str]:
    return {"run_id": "run-placeholder", "status": "queued"}
