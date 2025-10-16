"""Ruta de salud minimalista."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import logging
from typing import Final

from core.logging import setup as setup_logging
from api_gateway.framework import Router

router = Router(prefix="/v1")

_SERVICE_START: Final[datetime] = datetime.now(timezone.utc)
_SERVICE_VERSION: Final[str] = "0.1.0"


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ComponentStatus:
    name: str
    status: str
    detail: str | None = None


@dataclass(slots=True)
class HealthPayload:
    status: str
    version: str
    uptime_seconds: int
    components: list[ComponentStatus]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "version": self.version,
            "uptime_seconds": self.uptime_seconds,
            "components": [asdict(component) for component in self.components],
        }


@router.get("/health")
def health() -> dict[str, object]:
    setup_logging()
    uptime = datetime.now(timezone.utc) - _SERVICE_START
    payload = HealthPayload(
        status="ok",
        version=_SERVICE_VERSION,
        uptime_seconds=max(int(uptime.total_seconds()), 0),
        components=[ComponentStatus(name="api-gateway", status="ok")],
    )
    logger.debug("Generando respuesta de salud: %s", payload)
    return payload.to_dict()
