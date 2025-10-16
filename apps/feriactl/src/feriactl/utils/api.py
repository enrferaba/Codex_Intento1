"""Cliente HTTP robusto para la API de FERIA Precision Codex."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0


class FeriaAPIError(RuntimeError):
    """Error de alto nivel al interactuar con la API."""


@dataclass(slots=True)
class FeriaAPI:
    """Pequeño wrapper sobre :class:`httpx.Client` con manejo de errores."""

    base_url: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    transport: httpx.BaseTransport | None = None

    def __post_init__(self) -> None:
        url = self.base_url or os.getenv("FERIA_API_URL", "http://localhost:8000")
        self._client = httpx.Client(base_url=url, timeout=self.timeout, transport=self.transport)

    def __enter__(self) -> "FeriaAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()

    def close(self) -> None:
        self._client.close()

    # Public helpers -----------------------------------------------------
    def get_json(self, path: str) -> dict[str, Any]:
        return self._request_json("GET", path)

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request_json("POST", path, json=payload)

    # Internal helpers ---------------------------------------------------
    def _request_json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self._request(method, path, **kwargs)
        return response.json()

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:  # pragma: no cover - handled in tests
            detail = self._safe_json_error(exc.response)
            message = f"Error {exc.response.status_code} al llamar a {path}: {detail}"
            raise FeriaAPIError(message) from exc
        except httpx.RequestError as exc:  # pragma: no cover - handled in tests
            raise FeriaAPIError(f"No se pudo conectar con la API: {exc}") from exc
        return response

    @staticmethod
    def _safe_json_error(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:  # pragma: no cover - respuesta no JSON
            return response.text
        if isinstance(payload, dict) and "detail" in payload:
            return str(payload["detail"])
        return str(payload)
