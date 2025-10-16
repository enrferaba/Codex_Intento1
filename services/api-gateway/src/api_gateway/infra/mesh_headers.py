"""Gestión de headers para service mesh."""

from __future__ import annotations

from typing import Mapping


def inject(headers: Mapping[str, str]) -> Mapping[str, str]:
    enriched = dict(headers)
    enriched.setdefault("x-feria-run-id", "placeholder")
    return enriched
