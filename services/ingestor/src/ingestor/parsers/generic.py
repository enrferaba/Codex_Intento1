"""Parser genérico."""

from __future__ import annotations


def parse(content: str) -> list[str]:
    return content.splitlines()
