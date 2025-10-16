"""Exporters placeholder."""

from __future__ import annotations

from typing import Mapping


def format_prometheus(metric: str, value: float, labels: Mapping[str, str] | None = None) -> str:
    if labels:
        label_str = ",".join(f"{k}=\"{v}\"" for k, v in labels.items())
        return f"{metric}{{{label_str}}} {value}"
    return f"{metric} {value}"
