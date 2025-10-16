"""Valida reglas de ruteo."""

from __future__ import annotations

from typing import Mapping


def validate_rule(rule: Mapping[str, float]) -> bool:
    min_score = rule.get("min_score", float("-inf"))
    max_score = rule.get("max_score", float("inf"))
    return min_score <= max_score
