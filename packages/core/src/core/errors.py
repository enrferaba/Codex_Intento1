"""Errores compartidos."""

from __future__ import annotations


class FeriaError(Exception):
    """Error base del sistema."""


class NotFound(FeriaError):
    """Recurso no encontrado."""


class ValidationError(FeriaError):
    """Entrada inválida."""
