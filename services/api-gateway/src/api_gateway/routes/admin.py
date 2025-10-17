"""Rutas administrativas del gateway."""

from __future__ import annotations

from api_gateway.framework import Router

router = Router(prefix="/v1/admin")


@router.post("/kill-switch")
def kill_switch(payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    if not isinstance(payload, dict) or "enabled" not in payload:
        return 400, {"detail": "Se requiere el campo 'enabled'"}
    enabled_value = payload["enabled"]
    if isinstance(enabled_value, bool):
        enabled = enabled_value
    elif isinstance(enabled_value, str):
        enabled = enabled_value.lower() in {"1", "true", "yes", "on"}
    else:
        return 400, {"detail": "'enabled' debe ser booleano"}
    return 200, {"enabled": enabled}
