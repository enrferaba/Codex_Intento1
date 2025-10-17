"""Colección de rutas para la API."""

from . import admin, debug, health, ingest, query  # noqa: F401

__all__ = [
    "admin",
    "debug",
    "health",
    "ingest",
    "query",
]
