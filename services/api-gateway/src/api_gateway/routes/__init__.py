"""Colección de rutas para la API."""

from . import admin, agent, eval, health, ingest, query  # noqa: F401

__all__ = [
    "admin",
    "agent",
    "eval",
    "health",
    "ingest",
    "query",
]
