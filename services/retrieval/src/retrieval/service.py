"""Servicio de retrieval mínimo."""

from __future__ import annotations

from typing import Callable, TypeVar

Handler = Callable[[], tuple[int, dict[str, str]]]
T_Handler = TypeVar("T_Handler", bound=Handler)


class App:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], Handler] = {}

    def route(self, method: str, path: str) -> Callable[[T_Handler], T_Handler]:
        def decorator(func: T_Handler) -> T_Handler:
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
