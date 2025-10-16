"""Cliente de métricas placeholder."""

from __future__ import annotations

from typing import Mapping


class MetricsClient:
    def __init__(self) -> None:
        self._values: dict[str, float] = {}

    def observe(self, name: str, value: float, labels: Mapping[str, str] | None = None) -> None:
        key = name if not labels else f"{name}:{tuple(sorted(labels.items()))}"
        self._values[key] = value

    def snapshot(self) -> dict[str, float]:
        return dict(self._values)
