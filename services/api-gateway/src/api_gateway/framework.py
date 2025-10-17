"""Framework HTTP minimalista con servidor WSGI incorporado."""

from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Callable, Dict, Iterable, List, Tuple
from wsgiref.simple_server import make_server


@dataclass(slots=True)
class Route:
    method: str
    path: str
    handler: Callable[[Dict[str, Any] | None], Tuple[int, Any]]


class Router:
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix.rstrip("/")
        self._routes: List[Route] = []

    def get(self, path: str) -> Callable[[Callable[[Dict[str, Any] | None], Tuple[int, Any]]], Callable[[Dict[str, Any] | None], Tuple[int, Any]]]:
        return self._register("GET", path)

    def post(self, path: str) -> Callable[[Callable[[Dict[str, Any] | None], Tuple[int, Any]]], Callable[[Dict[str, Any] | None], Tuple[int, Any]]]:
        return self._register("POST", path)

    def _register(self, method: str, path: str) -> Callable[[Callable[[Dict[str, Any] | None], Tuple[int, Any]]], Callable[[Dict[str, Any] | None], Tuple[int, Any]]]:
        full_path = f"{self.prefix}{path}" if self.prefix else path

        def decorator(func: Callable[[Dict[str, Any] | None], Tuple[int, Any]]) -> Callable[[Dict[str, Any] | None], Tuple[int, Any]]:
            self._routes.append(Route(method=method, path=full_path, handler=func))
            return func

        return decorator

    @property
    def routes(self) -> Iterable[Route]:
        return tuple(self._routes)


class App:
    def __init__(self, title: str = "") -> None:
        self.title = title
        self._routes: List[Route] = []

    def include_router(self, router: Router) -> None:
        self._routes.extend(router.routes)

    def handle(self, method: str, path: str, json_body: Dict[str, Any] | None = None) -> Tuple[int, Any]:
        for route in self._routes:
            if route.method == method and route.path == path:
                return route.handler(json_body)
        raise LookupError(f"Ruta no encontrada: {method} {path}")

    def wsgi_app(self, environ, start_response):  # pragma: no cover - validado en tests de integración
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "") or "/"
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            length = 0
        body_bytes = environ["wsgi.input"].read(length) if length > 0 else b""
        json_body = None
        if body_bytes:
            try:
                json_body = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                json_body = None
        try:
            status_code, payload = self.handle(method, path, json_body if isinstance(json_body, dict) else None)
        except LookupError:
            response_body = json.dumps({"detail": "Not Found"}).encode("utf-8")
            start_response(f"{HTTPStatus.NOT_FOUND.value} {HTTPStatus.NOT_FOUND.phrase}", [("Content-Type", "application/json"), ("Content-Length", str(len(response_body)))])
            return [response_body]
        except Exception as exc:  # pragma: no cover - errores inesperados
            response_body = json.dumps({"detail": str(exc)}).encode("utf-8")
            start_response(f"{HTTPStatus.INTERNAL_SERVER_ERROR.value} {HTTPStatus.INTERNAL_SERVER_ERROR.phrase}", [("Content-Type", "application/json"), ("Content-Length", str(len(response_body)))])
            return [response_body]

        status = HTTPStatus(status_code)
        response_body = json.dumps(payload).encode("utf-8") if payload is not None else b""
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response_body))),
        ]
        start_response(f"{status.value} {status.phrase}", headers)
        return [response_body]

    def serve(self, host: str = "0.0.0.0", port: int = 8000) -> None:  # pragma: no cover - se usa en ejecución manual
        with make_server(host, port, self.wsgi_app) as server:
            print(f"🚀 FERIA API escuchando en http://{host}:{port}")
            server.serve_forever()


class Response:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Any:
        return self._payload


class TestClient:
    """Cliente de pruebas basado en el manejador interno."""

    __test__ = False  # evita que pytest lo detecte como caso de prueba

    def __init__(self, app: App) -> None:
        self._app = app

    def get(self, path: str) -> Response:
        status_code, payload = self._app.handle("GET", path)
        return Response(status_code, payload)

    def post(self, path: str, json: Dict[str, Any] | None = None) -> Response:
        status_code, payload = self._app.handle("POST", path, json)
        return Response(status_code, payload)
