"""Eval endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["eval"])


@router.get("/eval/report")
def eval_report(version: str | None = None) -> dict[str, str | None]:
    return {"version": version or "latest", "status": "placeholder"}
