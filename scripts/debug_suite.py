"""Genera un informe de depuración integral y, opcionalmente, ejecuta pruebas."""

from __future__ import annotations

import argparse
import json
import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from importlib import import_module
from types import ModuleType
from typing import Any, Protocol, Sequence

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

def _extend_sys_path() -> None:
    for path in EXTRA_PATHS:
        if path.exists():
            entry = str(path)
            if entry not in sys.path:
                sys.path.append(entry)

logger = logging.getLogger(__name__)

MAX_CAPTURE_CHARS = 4000


class _Snapshot(Protocol):
    def to_dict(self) -> dict[str, Any]:
        ...


_MODULE_CACHE: dict[str, ModuleType] = {}


def _load(name: str) -> ModuleType:
    if name not in _MODULE_CACHE:
        _extend_sys_path()
        _MODULE_CACHE[name] = import_module(name)
    return _MODULE_CACHE[name]


def collect_snapshot() -> _Snapshot:
    module = _load("core.debug")
    return module.collect_snapshot()


def format_snapshot(snapshot: _Snapshot) -> str:
    module = _load("core.debug")
    return module.format_snapshot(snapshot)


def setup_logging() -> None:
    module = _load("core.logging")
    module.setup()

DEFAULT_FULL_COMMANDS: list[list[str]] = [
    [sys.executable, "-m", "feriactl.main", "debug", "report", "--json"],
    [
        sys.executable,
        str(ROOT / "scripts" / "dev_debug.py"),
        sys.executable,
        "-m",
        "feriactl.main",
        "debug",
        "report",
    ],
]


def _truncate(text: str, limit: int = MAX_CAPTURE_CHARS) -> str:
    clean = text.strip()
    if len(clean) <= limit:
        return clean
    truncated = clean[:limit]
    suffix = f"… <{len(clean) - limit} chars más>"
    return f"{truncated}{suffix}"


def _build_pythonpath() -> str:
    entries: list[str] = [str(ROOT)]
    for path in EXTRA_PATHS:
        if path.exists():
            entries.append(str(path))
    existing = os.environ.get("PYTHONPATH")
    if existing:
        entries.append(existing)
    # Elimina duplicados preservando el orden.
    seen: list[str] = []
    for entry in entries:
        if entry and entry not in seen:
            seen.append(entry)
    return os.pathsep.join(seen)


def _build_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = _build_pythonpath()
    return env


def parse_command(value: str) -> list[str]:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("El comando no puede estar vacío")
    return shlex.split(cleaned)


def execute_commands(commands: Sequence[Sequence[str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for command in commands:
        if not command:
            continue
        logger.debug("Ejecutando comando de depuración: %s", command)
        start = perf_counter()
        error: str | None = None
        try:
            completed = subprocess.run(
                list(command),
                capture_output=True,
                text=True,
                check=False,
                env=_build_subprocess_env(),
            )
            exit_code = completed.returncode
            stdout = _truncate(completed.stdout)
            stderr = _truncate(completed.stderr)
        except OSError as exc:
            exit_code = None
            stdout = ""
            stderr = ""
            error = str(exc)
            logger.exception("No se pudo ejecutar el comando %s", command)
        duration_ms = round((perf_counter() - start) * 1000, 2)
        status = "ok" if (error is None and exit_code == 0) else "error"
        results.append(
            {
                "command": [str(part) for part in command],
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "duration_ms": duration_ms,
                "status": status,
                "error": error,
            }
        )
    return results


def _format_command_results(results: Sequence[dict[str, Any]]) -> str:
    if not results:
        return ""
    lines: list[str] = ["# Resultados de comandos"]
    for result in results:
        command_line = " ".join(result.get("command", []))
        status = result.get("status", "desconocido")
        exit_code = result.get("exit_code")
        duration = result.get("duration_ms", 0)
        lines.append(f"$ {command_line}")
        lines.append(f"estado: {status} · exit_code: {exit_code} · duración: {duration} ms")
        if result.get("error"):
            lines.append(f"error: {result['error']}")
        if result.get("stdout"):
            lines.append("stdout:")
            lines.append(result["stdout"])
        if result.get("stderr"):
            lines.append("stderr:")
            lines.append(result["stderr"])
        lines.append("")
    return "\n".join(lines).rstrip()


def run_pytest(pytest_args: list[str]) -> int:
    command = [sys.executable, "-m", "pytest", *pytest_args]
    return subprocess.run(command, check=False).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crea un informe de depuración FERIA")
    parser.add_argument("--json", action="store_true", help="Imprime el informe como JSON bruto")
    parser.add_argument("--run-tests", action="store_true", help="Ejecuta pytest tras generar el informe")
    parser.add_argument("--pytest-args", nargs=argparse.REMAINDER, default=[], help="Argumentos extra para pytest")
    parser.add_argument("--output", type=Path, help="Ruta donde guardar el informe generado")
    parser.add_argument(
        "--append",
        action="store_true",
        help="Añade el resultado al archivo en lugar de sobrescribirlo",
    )
    parser.add_argument(
        "--command",
        action="append",
        dest="commands",
        default=[],
        help="Comando adicional a ejecutar y capturar (usa comillas si contiene espacios)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Ejecuta los comandos de depuración predefinidos y pytest",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _extend_sys_path()
    from core.debug import collect_snapshot, format_snapshot
    from core.logging import setup as setup_logging

    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging()
    snapshot = collect_snapshot()

    commands_to_run: list[Sequence[str]] = []
    if getattr(args, "full", False):
        commands_to_run.extend(DEFAULT_FULL_COMMANDS)
        args.run_tests = True

    for value in getattr(args, "commands", []) or []:
        try:
            commands_to_run.append(parse_command(value))
        except ValueError as exc:
            parser.error(str(exc))

    command_results = execute_commands(commands_to_run) if commands_to_run else []

    if args.json:
        payload: dict[str, Any] = snapshot.to_dict()
        if command_results:
            payload["command_results"] = command_results
        rendered = json.dumps(payload, indent=2, sort_keys=True)
    else:
        sections = [format_snapshot(snapshot)]
        command_section = _format_command_results(command_results)
        if command_section:
            sections.append(command_section)
        rendered = "\n\n".join(filter(None, sections))

    print(rendered)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if args.append else "w"
        with args.output.open(mode, encoding="utf-8") as handler:
            if args.append and handler.tell() != 0:
                handler.write("\n")
            handler.write(rendered)
            handler.write("\n")

    exit_code = 0
    if any(result.get("status") != "ok" for result in command_results):
        exit_code = 1
        print("Al menos un comando finalizó con errores", file=sys.stderr)

    if not args.run_tests:
        return exit_code

    tests_exit_code = run_pytest(args.pytest_args)
    if tests_exit_code != 0:
        print("pytest finalizó con errores", file=sys.stderr)
        exit_code = tests_exit_code
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
