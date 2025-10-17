"""Almacenamiento de sesiones de depuración en disco."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Iterable, Sequence
from uuid import uuid4


@dataclass(slots=True)
class DebugRecord:
    """Metadatos almacenados para una sesión de depuración."""

    debug_id: str
    location: str
    artifact_count: int


@dataclass(slots=True)
class DebugArtifactPayload:
    name: str
    content: str
    content_type: str | None = None


class DebugRecorder:
    """Persistencia en disco de eventos de depuración."""

    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def record(
        self,
        *,
        path: str,
        error_text: str | None,
        modes: Sequence[str],
        artifacts: Iterable[DebugArtifactPayload],
        metadata: dict[str, object] | None,
    ) -> DebugRecord:
        timestamp = datetime.now(timezone.utc)
        debug_id = uuid4().hex
        folder_name = f"{timestamp.strftime('%Y%m%dT%H%M%S')}_{debug_id}"
        target_dir = self._base_path / folder_name

        record_payload = {
            "debug_id": debug_id,
            "path": path,
            "error_text": error_text,
            "modes": list(modes),
            "metadata": metadata or {},
            "created_at": timestamp.isoformat(),
        }

        artifact_count = 0
        with self._lock:
            target_dir.mkdir(parents=True, exist_ok=False)
            (target_dir / "summary.json").write_text(
                json.dumps(record_payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            artifacts_dir = target_dir / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            index_entries: list[dict[str, str | int | None]] = []
            for artifact in artifacts:
                artifact_count += 1
                safe_name = _safe_filename(artifact.name, artifact_count)
                artifact_path = artifacts_dir / safe_name
                artifact_path.write_text(artifact.content, encoding="utf-8")
                index_entries.append(
                    {
                        "name": artifact.name,
                        "content_type": artifact.content_type,
                        "file": artifact_path.name,
                        "size_bytes": artifact_path.stat().st_size,
                    }
                )
            (target_dir / "artifacts.json").write_text(
                json.dumps(index_entries, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            index_path = self._base_path / "index.jsonl"
            with index_path.open("a", encoding="utf-8") as index_file:
                index_file.write(json.dumps({**record_payload, "artifact_count": artifact_count}) + "\n")

        return DebugRecord(debug_id=debug_id, location=str(target_dir), artifact_count=artifact_count)

    def stats(self) -> dict[str, int]:
        index_path = self._base_path / "index.jsonl"
        if not index_path.exists():
            return {"events": 0, "artifacts": 0}
        events = 0
        artifacts = 0
        with index_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                events += 1
                try:
                    payload = json.loads(line)
                    artifacts += int(payload.get("artifact_count", 0))
                except json.JSONDecodeError:
                    continue
        return {"events": events, "artifacts": artifacts}


_filename_re = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_filename(name: str, position: int) -> str:
    if not name:
        name = f"artifact-{position}"
    stem = _filename_re.sub("-", name).strip("-.") or f"artifact-{position}"
    return f"{stem}.txt"


@lru_cache(maxsize=1)
def get_debug_recorder() -> DebugRecorder:
    base_dir = Path(os.getenv("FERIA_STORAGE_PATH", "/app/storage")) / "debug"
    return DebugRecorder(base_dir)


def reset_debug_state_for_tests() -> None:
    get_debug_recorder.cache_clear()
