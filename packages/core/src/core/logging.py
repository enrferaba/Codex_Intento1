"""Configuración centralizada de logging para FERIA Precision Codex."""

from __future__ import annotations

import logging
import os
from typing import Final

_DEFAULT_FORMAT: Final = "%(asctime)s %(levelname)s %(name)s - %(message)s"


def setup(*, level: str | None = None, force: bool = False) -> None:
    """Configura el logging del proyecto.

    Si no se proporciona ``level`` se calcula a partir de las variables de
    entorno ``FERIA_LOG_LEVEL`` y ``FERIA_DEBUG``. Esto permite activar el modo
    debug sin cambiar código, algo especialmente útil cuando se trabaja con el
    agente o los servicios en sandbox.
    """

    resolved_level = _resolve_level(level)
    logging.basicConfig(level=resolved_level, format=_DEFAULT_FORMAT, force=force)


def _resolve_level(explicit_level: str | None) -> int:
    if explicit_level:
        return _safe_level(explicit_level)

    env_level = os.getenv("FERIA_LOG_LEVEL")
    if env_level:
        return _safe_level(env_level)

    debug_flag = os.getenv("FERIA_DEBUG", "").lower()
    if debug_flag in {"1", "true", "yes", "on"}:
        return logging.DEBUG

    return logging.INFO


def _safe_level(value: str) -> int:
    try:
        return logging._nameToLevel[value.upper()]  # type: ignore[attr-defined]
    except KeyError:  # pragma: no cover - defensa ante valores desconocidos
        return logging.INFO
