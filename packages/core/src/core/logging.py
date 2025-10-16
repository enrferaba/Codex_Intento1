"""Configuración básica de logging."""

from __future__ import annotations

import logging


def setup(level: str = "INFO") -> None:
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
