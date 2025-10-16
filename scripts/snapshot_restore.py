"""Restaura snapshots (placeholder)."""

from __future__ import annotations

import argparse
from pathlib import Path


def restore_snapshot(snapshot_id: str) -> Path:
    path = Path("storage/snapshots") / snapshot_id
    if not path.exists():
        raise FileNotFoundError(f"Snapshot {snapshot_id} no encontrado")
    print(f"Restaurando snapshot desde {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Restaurar snapshot")
    parser.add_argument("id")
    args = parser.parse_args()
    restore_snapshot(args.id)


if __name__ == "__main__":
    main()
