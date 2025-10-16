"""Esquemas ligeros basados en dataclasses."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class QueryRequest:
    query: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class QueryResponse:
    answer: str
    citations: list[dict[str, str]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
