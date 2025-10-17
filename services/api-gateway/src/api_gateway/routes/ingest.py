"""Endpoint de ingesta de documentos."""

from __future__ import annotations

from typing import Iterable

from api_gateway.framework import Router
from api_gateway.services.documents import get_document_store

router = Router(prefix="/v1")


@router.post("/ingest")
def ingest(payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    if not isinstance(payload, dict):
        return 400, {"detail": "Payload JSON requerido"}

    repository = str(payload.get("repository", "")).strip()
    modes_raw = payload.get("modes", [])
    documents_raw = payload.get("documents")

    if not repository:
        return 400, {"detail": "'repository' es obligatorio"}
    if not isinstance(documents_raw, list) or not documents_raw:
        return 400, {"detail": "'documents' debe ser una lista no vacía"}
    if not isinstance(modes_raw, list):
        return 400, {"detail": "'modes' debe ser una lista"}

    documents = list(_normalise_documents(documents_raw))
    if not documents:
        return 400, {"detail": "No hay documentos válidos"}

    job_id, document_count = get_document_store().add_documents(
        repository=repository,
        modes=[str(mode) for mode in modes_raw],
        documents=documents,
    )
    return 201, {"job_id": job_id, "document_count": document_count, "accepted_modes": [str(mode) for mode in modes_raw]}


def _normalise_documents(raw_documents: Iterable[object]) -> Iterable[tuple[str, str]]:
    for item in raw_documents:
        if not isinstance(item, dict):
            continue
        path_raw = item.get("path")
        text_raw = item.get("text")
        if not isinstance(path_raw, str) or not isinstance(text_raw, str):
            continue
        path = path_raw.strip()
        text = text_raw.strip()
        if not path or not text:
            continue
        yield path, text
