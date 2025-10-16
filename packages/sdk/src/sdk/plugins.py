"""Gestor de plugins (placeholder)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Tool(Protocol):
    name: str

    def run(self, **kwargs) -> dict:
        ...


@dataclass
class Plugin:
    name: str
    tool: Tool

    def execute(self, **kwargs) -> dict:
        return self.tool.run(**kwargs)
