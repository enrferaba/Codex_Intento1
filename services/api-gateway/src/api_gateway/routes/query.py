"""Query endpoint placeholder."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["query"])


@router.post("/query")
def query(payload: dict[str, str]) -> dict[str, object]:
    question = payload.get("query", "")
    return {
        "answer": f"Respuesta placeholder para: {question}",
        "citations": [],
        "confidence": 0.0,
    }
