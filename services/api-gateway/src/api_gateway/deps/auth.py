"""Dependencia de autenticación placeholder."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status


def verify_token(token: str | None = None) -> str:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    return token


def get_current_token(token: str = Depends(verify_token)) -> str:
    return token
