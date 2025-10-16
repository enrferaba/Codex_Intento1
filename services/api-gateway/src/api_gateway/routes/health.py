"""Health endpoint providing structured service metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Final

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1", tags=["health"])

_SERVICE_START: Final[datetime] = datetime.now(timezone.utc)
_SERVICE_VERSION: Final[str] = "0.1.0"


class ComponentStatus(BaseModel):
    """Represents the health of a single subsystem."""

    name: str
    status: str
    detail: str | None = None


class HealthPayload(BaseModel):
    """Top level payload for the health endpoint."""

    status: str
    version: str
    uptime_seconds: int
    components: list[ComponentStatus]


@router.get("/health", response_model=HealthPayload)
def health() -> HealthPayload:
    """Return a machine friendly view of the gateway status."""

    uptime = datetime.now(timezone.utc) - _SERVICE_START
    components = [ComponentStatus(name="api-gateway", status="ok")]
    return HealthPayload(
        status="ok",
        version=_SERVICE_VERSION,
        uptime_seconds=max(int(uptime.total_seconds()), 0),
        components=components,
    )
