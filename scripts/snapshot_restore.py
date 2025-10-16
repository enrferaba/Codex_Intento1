"""Restaura snapshots (placeholder)."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from core.logging import setup as setup_logging


logger = logging.getLogger(__name__)


def restore_snapshot(snapshot_id: str) -> Path:
    path = Path("storage/snapshots") / snapshot_id
    if not path.exists():
        logger.error("Snapshot %s no encontrado", snapshot_id)
        raise FileNotFoundError(f"Snapshot {snapshot_id} no encontrado")
    logger.info("Restaurando snapshot desde %s", path)
    print(f"Restaurando snapshot desde {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Restaurar snapshot")
    parser.add_argument("id")
    args = parser.parse_args()
    setup_logging()
    logger.debug("Solicitando restauración del snapshot %s", args.id)
    restore_snapshot(args.id)


if __name__ == "__main__":
    main()
