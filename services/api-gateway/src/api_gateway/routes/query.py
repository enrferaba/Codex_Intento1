"""Endpoint de consulta con búsqueda determinista."""

from __future__ import annotations

from api_gateway.framework import Router
from api_gateway.services.documents import DocumentMatch, get_document_store

router = Router(prefix="/v1")


@router.post("/query")
def query(payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    if not isinstance(payload, dict):
        return 400, {"detail": "Payload JSON requerido"}

    query_raw = str(payload.get("query", "")).strip()
    if not query_raw:
        return 400, {"detail": "'query' es obligatoria"}

    limit_value = payload.get("limit", 3)
    try:
        limit = int(limit_value)
    except (ValueError, TypeError):
        return 400, {"detail": "'limit' debe ser entero"}
    if limit <= 0:
        return 400, {"detail": "'limit' debe ser mayor que cero"}

    matches = get_document_store().search(query_raw, limit=limit)
    if not matches:
        return 200, {
            "answer": "No se encontraron documentos relevantes.",
            "citations": [],
            "confidence": 0.0,
            "documents": [],
        }

    total_score = sum(match.score for match in matches)
    confidence = matches[0].score / total_score if total_score > 0 else 0.0

    return 200, {
        "answer": _build_answer(query_raw, matches[0]),
        "citations": [match.path for match in matches],
        "confidence": round(confidence, 3),
        "documents": [
            {"path": match.path, "snippet": match.snippet, "score": round(match.score, 6)} for match in matches
        ],
    }


def _build_answer(question: str, top_match: DocumentMatch) -> str:
    return top_match.snippet or f"No se encontraron coincidencias exactas para: {question}"
