"""Genera un informe de depuración integral y, opcionalmente, ejecuta pruebas."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXTRA_PATHS = [
    ROOT / "apps/feriactl/src",
    ROOT / "packages/core/src",
    ROOT / "packages/agent/src",
    ROOT / "packages/policy/src",
    ROOT / "packages/eval/src",
    ROOT / "packages/observability/src",
    ROOT / "packages/metrics-client/src",
    ROOT / "packages/sdk/src",
    ROOT / "services/api-gateway/src",
    ROOT / "services/model-gateway/src",
    ROOT / "services/orchestrator/src",
    ROOT / "services/retrieval/src",
]

for path in EXTRA_PATHS:
    if path.exists():
        entry = str(path)
        if entry not in sys.path:
            sys.path.append(entry)

from core.debug import collect_snapshot, format_snapshot
from core.logging import setup as setup_logging


def run_pytest(pytest_args: list[str]) -> int:
    command = [sys.executable, "-m", "pytest", *pytest_args]
    return subprocess.run(command, check=False).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crea un informe de depuración FERIA")
    parser.add_argument("--json", action="store_true", help="Imprime el informe como JSON bruto")
    parser.add_argument("--run-tests", action="store_true", help="Ejecuta pytest tras generar el informe")
    parser.add_argument("--pytest-args", nargs=argparse.REMAINDER, default=[], help="Argumentos extra para pytest")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging()
    snapshot = collect_snapshot()

    if args.json:
        payload: dict[str, Any] = snapshot.to_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_snapshot(snapshot))

    if not args.run_tests:
        return 0

    exit_code = run_pytest(args.pytest_args)
    if exit_code != 0:
        print("pytest finalizó con errores", file=sys.stderr)
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
