"""Dependencias de autenticación minimalistas."""

from __future__ import annotations


class AuthError(RuntimeError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


HTTP_401_UNAUTHORIZED = 401


def verify_token(token: str | None = None) -> str:
    if not token:
        raise AuthError(status_code=HTTP_401_UNAUTHORIZED, detail="Token requerido")
    return token


def get_current_token(token: str | None = None) -> str:
    return verify_token(token)
