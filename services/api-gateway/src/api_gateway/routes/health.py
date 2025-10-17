"""Ruta de salud con detalles operativos."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Final

from api_gateway.framework import Router
from api_gateway.services.debug import get_debug_recorder
from api_gateway.services.documents import get_document_store

router = Router(prefix="/v1")

_SERVICE_START: Final[datetime] = datetime.now(timezone.utc)
_SERVICE_VERSION: Final[str] = "0.2.0"


@router.get("/health")
def health(_: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    uptime = datetime.now(timezone.utc) - _SERVICE_START
    store_stats = get_document_store().stats()
    debug_stats = get_debug_recorder().stats()
    payload = {
        "status": "ok",
        "version": _SERVICE_VERSION,
        "uptime_seconds": max(int(uptime.total_seconds()), 0),
        "components": [
            {
                "name": "document-store",
                "status": "ok" if store_stats["documents"] else "empty",
                "detail": f"{store_stats['documents']} docs / {store_stats['repositories']} repos",
            },
            {
                "name": "debug-recorder",
                "status": "ok",
                "detail": f"{debug_stats['events']} eventos",
            },
        ],
    }
    return 200, payload
