"""Crea snapshots firmados (placeholder)."""

from __future__ import annotations

import argparse
from pathlib import Path


def create_snapshot(label: str) -> Path:
    target = Path("storage/snapshots") / f"snapshot-{label}.txt"
    target.write_text("Snapshot placeholder\n")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Crear snapshot local")
    parser.add_argument("label", nargs="?", default="manual")
    args = parser.parse_args()
    path = create_snapshot(args.label)
    print(f"Snapshot creado en {path}")


if __name__ == "__main__":
    main()
