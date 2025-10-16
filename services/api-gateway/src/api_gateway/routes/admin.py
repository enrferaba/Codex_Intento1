"""Rutas administrativas."""

from __future__ import annotations

from api_gateway.framework import Router

router = Router(prefix="/v1/admin")


@router.post("/kill-switch")
def kill_switch(enabled: bool | None = None) -> dict[str, bool | None]:
    return {"enabled": enabled}
