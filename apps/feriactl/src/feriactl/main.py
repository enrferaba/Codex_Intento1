"""CLI sencilla basada en ``argparse`` para feriactl."""

from __future__ import annotations

import argparse
import sys
from typing import Callable

from feriactl.commands import health, ingest, queues, scale, snapshot, status
from feriactl.commands.base import CommandResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="feriactl", description="Administra FERIA Precision Codex")
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="Comandos de estado")
    status_sub = status_parser.add_subparsers(dest="status_command")
    status_show = status_sub.add_parser("show", help="Mostrar resumen de componentes")
    status_show.add_argument("--base-url", dest="base_url", default=None)
    status_show.set_defaults(func=_wrap_command(lambda args: status.show(base_url=args.base_url)))

    health_parser = subparsers.add_parser("health", help="Comandos de salud")
    health_sub = health_parser.add_subparsers(dest="health_command")
    health_verbose = health_sub.add_parser("verbose", help="Devuelve el JSON crudo de salud")
    health_verbose.add_argument("--base-url", dest="base_url", default=None)
    health_verbose.add_argument("--pretty", dest="pretty", type=_bool_flag, default=True)
    health_verbose.set_defaults(
        func=_wrap_command(lambda args: health.verbose(base_url=args.base_url, pretty=args.pretty))
    )

    ingest_parser = subparsers.add_parser("ingest", help="Gestiona ingestas")
    ingest_parser.add_argument("repo")
    ingest_parser.set_defaults(func=_wrap_command(lambda args: ingest.run(args.repo)))

    scale_parser = subparsers.add_parser("scale", help="Escala workers")
    scale_parser.add_argument("--agent", type=int, default=2)
    scale_parser.add_argument("--indexing", type=int, default=4)
    scale_parser.set_defaults(func=_wrap_command(lambda args: scale.set(agent=args.agent, indexing=args.indexing)))

    queues_parser = subparsers.add_parser("queues", help="Gestiona colas")
    queues_parser.add_argument("--stats", action="store_true", default=False)
    queues_parser.set_defaults(func=_wrap_command(lambda args: queues.list(stats=args.stats)))

    snapshot_parser = subparsers.add_parser("snapshot", help="Snapshots del sistema")
    snapshot_sub = snapshot_parser.add_subparsers(dest="snapshot_command")
    snapshot_create = snapshot_sub.add_parser("create", help="Crea un snapshot")
    snapshot_create.add_argument("--label", default=None)
    snapshot_create.set_defaults(func=_wrap_command(lambda args: snapshot.create(label=args.label)))

    return parser


def _wrap_command(fn: Callable[[argparse.Namespace], CommandResult]) -> Callable[[argparse.Namespace], int]:
    def _inner(args: argparse.Namespace) -> int:
        result = fn(args)
        result.emit(sys.stdout, sys.stderr)
        return result.exit_code

    return _inner


def _bool_flag(value: str) -> bool:
    value_lower = value.lower()
    if value_lower in {"true", "1", "yes", "y"}:
        return True
    if value_lower in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Valor booleano inválido: {value}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0
    return func(args)


if __name__ == "__main__":  # pragma: no cover - ejecución directa
    raise SystemExit(main())
