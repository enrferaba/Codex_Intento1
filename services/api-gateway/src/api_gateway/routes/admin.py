"""Admin endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/kill-switch")
def kill_switch(enabled: bool) -> dict[str, bool]:
    return {"enabled": enabled}
