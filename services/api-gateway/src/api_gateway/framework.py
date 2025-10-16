"""Framework HTTP mínimo para pruebas sin dependencias externas."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Tuple


@dataclass(slots=True)
class Route:
    method: str
    path: str
    handler: Callable[..., Any]


class Router:
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix.rstrip("/")
        self._routes: List[Route] = []

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._register("GET", path)

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._register("POST", path)

    def _register(self, method: str, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        full_path = f"{self.prefix}{path}" if self.prefix else path

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
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
                return _invoke(route.handler, json_body)
        raise LookupError(f"Ruta no encontrada: {method} {path}")


def _invoke(handler: Callable[..., Any], json_body: Dict[str, Any] | None) -> Tuple[int, Any]:
    signature = inspect.signature(handler)
    if not signature.parameters:
        result = handler()
    else:
        kwargs = {}
        json_body = json_body or {}
        for name, parameter in signature.parameters.items():
            if name in json_body:
                kwargs[name] = json_body[name]
            elif parameter.default is not inspect._empty:  # pragma: no cover - rutas sin datos
                kwargs[name] = parameter.default
            else:
                kwargs[name] = None
        result = handler(**kwargs)
    if isinstance(result, tuple) and len(result) == 2:
        return int(result[0]), result[1]
    return 200, result


class Response:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Any:
        return self._payload


class TestClient:
    __test__ = False  # evita que pytest lo trate como caso de prueba

    def __init__(self, app: App) -> None:
        self._app = app

    def get(self, path: str) -> Response:
        status_code, payload = self._app.handle("GET", path)
        return Response(status_code, payload)

    def post(self, path: str, json: Dict[str, Any] | None = None) -> Response:
        status_code, payload = self._app.handle("POST", path, json)
        return Response(status_code, payload)
