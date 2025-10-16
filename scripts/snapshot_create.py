"""Crea snapshots firmados (placeholder)."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from core.logging import setup as setup_logging


logger = logging.getLogger(__name__)


def create_snapshot(label: str) -> Path:
    target = Path("storage/snapshots") / f"snapshot-{label}.txt"
    target.write_text("Snapshot placeholder\n")
    logger.debug("Snapshot generado en %s", target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Crear snapshot local")
    parser.add_argument("label", nargs="?", default="manual")
    args = parser.parse_args()
    setup_logging()
    logger.info("Creando snapshot con etiqueta %s", args.label)
    path = create_snapshot(args.label)
    logger.info("Snapshot creado en %s", path)
    print(f"Snapshot creado en {path}")


if __name__ == "__main__":
    main()
