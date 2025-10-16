"""Planner placeholder."""

from __future__ import annotations

from typing import Sequence


def plan(task: str) -> Sequence[str]:
    return [f"Review task: {task}", "Select allowed recipe", "Execute in sandbox"]
