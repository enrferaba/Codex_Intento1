"""Hooks de observabilidad."""

from __future__ import annotations

from time import time
from typing import Iterator

from contextlib import contextmanager


@contextmanager
def track_latency(route: str) -> Iterator[None]:
    start = time()
    try:
        yield
    finally:
        duration = time() - start
        print(f"Route {route} took {duration:.3f}s")
