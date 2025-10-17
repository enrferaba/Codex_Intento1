"""Servicio de retrieval mínimo."""

from __future__ import annotations

from typing import Callable


RouteHandler = Callable[[], tuple[int, dict[str, str]]]


class App:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], RouteHandler] = {}

    def route(self, method: str, path: str) -> Callable[[RouteHandler], RouteHandler]:
        def decorator(func: RouteHandler) -> RouteHandler:
            self._routes[(method, path)] = func
            return func

        return decorator

    def handle(self, method: str, path: str) -> tuple[int, dict[str, str]]:
        handler = self._routes[(method, path)]
        status, payload = handler()
        return status, payload


app = App()


@app.route("GET", "/health")
def health() -> tuple[int, dict[str, str]]:
    return 200, {"status": "ok"}
