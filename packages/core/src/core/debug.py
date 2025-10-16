"""Herramientas utilitarias para recopilar diagnósticos de depuración."""

from __future__ import annotations

import dataclasses
import json
import logging
import os
import platform
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Iterable


@dataclasses.dataclass(slots=True)
class DebugSnapshot:
    """Instantánea estructurada con los indicadores de depuración relevantes."""

    timestamp: float
    python_version: str
    platform: str
    executable: str
    feria_debug_flag: bool
    feria_log_level: str | None
    effective_log_level: str
    working_directory: str
    git_branch: str | None
    git_commit: str | None
    git_dirty: bool | None
    env: Mapping[str, str]
    loaded_modules: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convierte la instantánea en un diccionario listo para serialización."""

        return dataclasses.asdict(self)


def _gather_git_metadata(cwd: Path | None = None) -> tuple[str | None, str | None, bool | None]:
    """Recopila información básica del repositorio Git si está disponible."""

    if cwd is None:
        cwd = Path.cwd()

    def _run(*args: str) -> str | None:
        try:
            completed = subprocess.run(
                ("git", *args),
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return None
        return completed.stdout.strip()

    commit = _run("rev-parse", "--short", "HEAD")
    branch = _run("rev-parse", "--abbrev-ref", "HEAD")

    porcelain = _run("status", "--porcelain")
    dirty: bool | None
    if porcelain is None:
        dirty = None
    else:
        dirty = bool(porcelain.strip())

    if branch is None and commit is None and dirty is None:
        return (None, None, None)

    return (branch, commit, dirty)


def collect_snapshot(env_keys: Iterable[str] | None = None) -> DebugSnapshot:
    """Recopila los valores que ayudan a depurar ejecuciones FERIA.

    Args:
        env_keys: subconjunto de variables de entorno adicionales a capturar. Si es
            ``None`` se utilizará un conjunto por defecto de claves relevantes.
    """

    if env_keys is None:
        env_keys = (
            "FERIA_DEBUG",
            "FERIA_LOG_LEVEL",
            "FERIA_ENV",
            "FERIA_SETTINGS",
        )

    env_snapshot: dict[str, str] = {}
    for key in env_keys:
        value = os.getenv(key)
        if value is not None:
            env_snapshot[key] = value

    feria_debug_flag = os.getenv("FERIA_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    feria_log_level = os.getenv("FERIA_LOG_LEVEL")
    root_logger = logging.getLogger()
    effective_level = logging.getLevelName(root_logger.getEffectiveLevel())

    branch, commit, dirty = _gather_git_metadata()

    return DebugSnapshot(
        timestamp=time.time(),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        executable=sys.executable,
        feria_debug_flag=feria_debug_flag,
        feria_log_level=feria_log_level,
        effective_log_level=str(effective_level),
        working_directory=str(Path.cwd()),
        git_branch=branch,
        git_commit=commit,
        git_dirty=dirty,
        env=env_snapshot,
        loaded_modules=tuple(sorted(sys.modules)),
    )


def format_snapshot(snapshot: DebugSnapshot, *, indent: int = 2) -> str:
    """Formatea la instantánea como un bloque de texto legible."""

    payload = {
        "timestamp": snapshot.timestamp,
        "python_version": snapshot.python_version,
        "platform": snapshot.platform,
        "executable": snapshot.executable,
        "feria_debug_flag": snapshot.feria_debug_flag,
        "feria_log_level": snapshot.feria_log_level,
        "effective_log_level": snapshot.effective_log_level,
        "working_directory": snapshot.working_directory,
        "git_branch": snapshot.git_branch,
        "git_commit": snapshot.git_commit,
        "git_dirty": snapshot.git_dirty,
        "env": dict(snapshot.env),
        "loaded_modules_count": len(snapshot.loaded_modules),
    }
    return json.dumps(payload, indent=indent, sort_keys=True)


__all__ = [
    "DebugSnapshot",
    "collect_snapshot",
    "format_snapshot",
]
