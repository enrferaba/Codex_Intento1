"""Servicio de retrieval mínimo."""

from __future__ import annotations


class App:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], callable] = {}

    def route(self, method: str, path: str):
        def decorator(func):
            self._routes[(method, path)] = func
            return func

        return decorator

    def handle(self, method: str, path: str):
        handler = self._routes[(method, path)]
        status, payload = handler()
        return status, payload


app = App()


@app.route("GET", "/health")
def health() -> tuple[int, dict[str, str]]:
    return 200, {"status": "ok"}
