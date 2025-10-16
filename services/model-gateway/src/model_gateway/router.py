"""Router placeholder."""

from __future__ import annotations

from typing import Sequence

LANES: Sequence[str] = ("small", "medium", "large")


def route(score: float) -> str:
    if score < 3:
        return LANES[0]
    if score < 6:
        return LANES[1]
    return LANES[2]
