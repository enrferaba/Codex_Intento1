"""DTO helpers."""

from __future__ import annotations

from api_gateway.domain.schemas import QueryResponse


def make_placeholder_response(question: str) -> QueryResponse:
    return QueryResponse(answer=f"Respuesta placeholder para: {question}", citations=[], confidence=0.0)
