"""Ingest endpoint placeholder."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["ingest"])


@router.post("/ingest")
def ingest(payload: dict[str, str]) -> dict[str, str]:
    return {"job_id": "ingest-placeholder"}
