"""Endpoint de consulta simplificado."""

from __future__ import annotations

from api_gateway.framework import Router

router = Router(prefix="/v1")


@router.post("/query")
def query(payload: dict[str, str] | None = None) -> dict[str, object]:
    payload = payload or {}
    question = payload.get("query", "")
    return {
        "answer": f"Respuesta placeholder para: {question}",
        "citations": [],
        "confidence": 0.0,
    }
