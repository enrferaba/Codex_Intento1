"""Carga sencilla de configuración."""

from __future__ import annotations

from pathlib import Path

import tomllib


def load(path: str) -> dict[str, object]:
    with Path(path).open("rb") as fh:
        return tomllib.load(fh)
