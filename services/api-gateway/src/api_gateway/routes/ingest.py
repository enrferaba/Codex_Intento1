"""Endpoint de ingesta."""

from __future__ import annotations

from api_gateway.framework import Router

router = Router(prefix="/v1")


@router.post("/ingest")
def ingest(payload: dict[str, str] | None = None) -> dict[str, str]:
    return {"job_id": "ingest-placeholder"}
