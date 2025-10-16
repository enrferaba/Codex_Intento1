"""Esquemas de requests/responses."""

from __future__ import annotations

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[dict[str, str]]
