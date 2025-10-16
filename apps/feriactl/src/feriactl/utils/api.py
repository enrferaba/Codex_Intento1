"""Cliente HTTP sin dependencias externas para la API de FERIA."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict, Optional, Protocol


class TransportError(RuntimeError):
    """Error bajo nivel al ejecutar una petición HTTP."""


@dataclass(slots=True)
class TransportResponse:
    """Respuesta devuelta por el transporte HTTP configurable."""

    status_code: int
    body: bytes
    headers: Dict[str, str]

    def json(self) -> object:
        return json.loads(self.body.decode("utf-8"))


class Transport(Protocol):
    """Contrato mínimo que debe implementar un transporte HTTP."""

    def __call__(
        self,
        method: str,
        url: str,
        body: bytes | None,
        headers: Dict[str, str],
        timeout: float,
    ) -> TransportResponse:
        """Ejecuta una petición y devuelve la respuesta cruda."""


DEFAULT_TIMEOUT = 10.0


class FeriaAPIError(RuntimeError):
    """Error de alto nivel al interactuar con la API."""


@dataclass(slots=True)
class FeriaAPI:
    """Pequeño cliente HTTP configurable."""

    base_url: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    transport: Optional[Transport] = None
    _base_url: str = field(init=False)
    _transport: Transport = field(init=False)

    def __post_init__(self) -> None:
        self._base_url = self.base_url or os.getenv("FERIA_API_URL", "http://localhost:8000")
        self._transport = self.transport or _default_transport

    @property
    def resolved_base_url(self) -> str:
        return self._base_url

    # Context manager -------------------------------------------------
    def __enter__(self) -> "FeriaAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        return None

    # Public helpers --------------------------------------------------
    def get_json(self, path: str) -> Dict[str, object]:
        return self._request_json("GET", path)

    def post_json(self, path: str, payload: Dict[str, object]) -> Dict[str, object]:
        return self._request_json("POST", path, payload)

    # Internal helpers ------------------------------------------------
    def _request_json(self, method: str, path: str, payload: Dict[str, object] | None = None) -> Dict[str, object]:
        logger = logging.getLogger(__name__)
        start = perf_counter()
        response = self._request(method, path, payload)
        elapsed_ms = (perf_counter() - start) * 1000
        logger.debug(
            "Petición %s %s completada en %.2f ms", method, _join_url(self._base_url, path), elapsed_ms
        )
        try:
            data = response.json()
        except ValueError as exc:  # pragma: no cover - no debería ocurrir en tests
            raise FeriaAPIError("La API devolvió una respuesta no JSON") from exc
        if not isinstance(data, dict):  # pragma: no cover - protección extra
            raise FeriaAPIError("La API devolvió un JSON inesperado")
        return data

    def _request(self, method: str, path: str, payload: Dict[str, object] | None) -> TransportResponse:
        url = _join_url(self._base_url, path)
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers: Dict[str, str] = {}
        if body is not None:
            headers["Content-Type"] = "application/json"
        logger = logging.getLogger(__name__)
        url = _join_url(self._base_url, path)
        logger.debug("Llamando a %s %s", method, url)
        try:
            response = self._transport(method, url, body, headers, self.timeout)
        except TransportError as exc:
            logger.error("Error de transporte contra %s: %s", url, exc)
            raise FeriaAPIError(f"No se pudo conectar con la API: {exc}") from exc
        if not 200 <= response.status_code < 300:
            detail = _safe_json_error(response)
            logger.warning("Respuesta no satisfactoria %s %s: %s", method, url, detail)
            raise FeriaAPIError(f"Error {response.status_code} al llamar a {path}: {detail}")
        return response


def _join_url(base: str, path: str) -> str:
    if not base.endswith("/"):
        base = base + "/"
    return base + path.lstrip("/")


def _safe_json_error(response: TransportResponse) -> str:
    try:
        data = response.json()
    except Exception:  # pragma: no cover - respuesta no JSON
        return response.body.decode("utf-8", errors="replace")
    if isinstance(data, dict) and "detail" in data:
        return str(data["detail"])
    return str(data)


def _default_transport(
    method: str,
    url: str,
    body: bytes | None,
    headers: Dict[str, str],
    timeout: float,
) -> TransportResponse:
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body_bytes = response.read()
            headers_dict = {k.lower(): v for k, v in response.headers.items()}
            return TransportResponse(status_code=response.status, body=body_bytes, headers=headers_dict)
    except urllib.error.HTTPError as exc:
        return TransportResponse(status_code=exc.code, body=exc.read(), headers=dict(exc.headers.items()))
    except urllib.error.URLError as exc:  # pragma: no cover - entorno sin red
        raise TransportError(str(exc)) from exc
