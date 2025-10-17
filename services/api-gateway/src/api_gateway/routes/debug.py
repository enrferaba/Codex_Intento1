"""Endpoint para registrar sesiones de depuración."""

from __future__ import annotations

from typing import Iterable

from api_gateway.framework import Router
from api_gateway.services.debug import DebugArtifactPayload, get_debug_recorder

router = Router(prefix="/v1")


@router.post("/debug")
def submit_debug(payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    if not isinstance(payload, dict):
        return 400, {"detail": "Payload JSON requerido"}

    path = str(payload.get("path", "")).strip()
    error_text_raw = payload.get("error_text")
    modes_raw = payload.get("modes", [])
    metadata_raw = payload.get("metadata")
    artifacts_raw = payload.get("artifacts", [])

    if not path:
        return 400, {"detail": "'path' es obligatorio"}
    if not isinstance(modes_raw, list):
        return 400, {"detail": "'modes' debe ser una lista"}
    if not isinstance(artifacts_raw, list):
        return 400, {"detail": "'artifacts' debe ser una lista"}

    artifacts = list(_normalise_artifacts(artifacts_raw))

    record = get_debug_recorder().record(
        path=path,
        error_text=str(error_text_raw) if error_text_raw is not None else None,
        modes=[str(mode) for mode in modes_raw],
        artifacts=artifacts,
        metadata=metadata_raw if isinstance(metadata_raw, dict) else None,
    )

    return 201, {
        "debug_id": record.debug_id,
        "location": record.location,
        "artifact_count": record.artifact_count,
    }


def _normalise_artifacts(raw_artifacts: Iterable[object]) -> Iterable[DebugArtifactPayload]:
    for item in raw_artifacts:
        if not isinstance(item, dict):
            continue
        name_raw = item.get("name")
        content_raw = item.get("content")
        if not isinstance(name_raw, str) or not isinstance(content_raw, str):
            continue
        content_type = item.get("content_type")
        yield DebugArtifactPayload(name=name_raw, content=content_raw, content_type=str(content_type) if isinstance(content_type, str) else None)
