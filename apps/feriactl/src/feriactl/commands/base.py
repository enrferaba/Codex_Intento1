"""Utilidades comunes para los comandos de ``feriactl``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO


@dataclass(slots=True)
class CommandResult:
    """Representa la salida de un comando de la CLI."""

    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""

    def emit(self, stdout: TextIO, stderr: TextIO) -> None:
        if self.stdout:
            stdout.write(self.stdout)
            if not self.stdout.endswith("\n"):
                stdout.write("\n")
        if self.stderr:
            stderr.write(self.stderr)
            if not self.stderr.endswith("\n"):
                stderr.write("\n")
