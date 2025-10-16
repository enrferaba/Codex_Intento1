"""RBAC básico."""

from __future__ import annotations

from typing import Mapping

ROLE_PERMISSIONS: Mapping[str, set[str]] = {
    "admin": {"query", "admin", "eval"},
    "analyst": {"query", "eval"},
    "user": {"query"},
}


def can(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, set())
