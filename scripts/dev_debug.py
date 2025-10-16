"""Ejecutor auxiliar para lanzar comandos FERIA con logging DEBUG."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import Sequence


def run(command: Sequence[str]) -> int:
    env = os.environ.copy()
    env["FERIA_DEBUG"] = "1"
    process = subprocess.run(command, env=env, check=False)
    return process.returncode


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta comandos con FERIA_DEBUG=1")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Comando a ejecutar")
    args = parser.parse_args(argv)

    if not args.command:
        parser.error("Debes proporcionar un comando a ejecutar")
    return run(args.command)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
