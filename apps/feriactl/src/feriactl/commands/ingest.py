"""Comandos de ingesta que interactúan con la API."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from feriactl.commands.base import CommandResult
from feriactl.utils.api import FeriaAPI, FeriaAPIError

_SUPPORTED_SUFFIXES = {".md", ".py", ".txt"}
_MAX_DOCUMENTS = 50
_MAX_FILE_BYTES = 40_000


def run(repo: str) -> CommandResult:
    repo_path = Path(repo)
    if not repo_path.exists():
        return CommandResult(exit_code=1, stderr=f"La ruta {repo_path} no existe")
    documents = list(_collect_documents(repo_path))
    if not documents:
        return CommandResult(exit_code=1, stderr="No se encontraron documentos ingeribles")

    payload = {
        "repository": repo_path.name,
        "modes": ["python"],
        "documents": [{"path": path, "text": text} for path, text in documents],
    }

    try:
        with FeriaAPI() as api:
            response = api.post_json("/v1/ingest", payload)
    except FeriaAPIError as exc:
        return CommandResult(exit_code=1, stderr=str(exc))

    job_id = response.get("job_id", "desconocido")
    count = response.get("document_count", 0)
    return CommandResult(stdout=f"Ingesta {job_id} aceptada ({count} documentos)")


def _collect_documents(repo_path: Path) -> Iterable[tuple[str, str]]:
    collected = 0
    for path in sorted(repo_path.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in _SUPPORTED_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if len(content.encode("utf-8")) > _MAX_FILE_BYTES:
            content = content[: _MAX_FILE_BYTES // 2]
        relative = path.relative_to(repo_path)
        yield (str(relative), content)
        collected += 1
        if collected >= _MAX_DOCUMENTS:
            break
