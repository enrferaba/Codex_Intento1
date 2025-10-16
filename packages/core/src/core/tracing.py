"""Herramientas de tracing minimalistas."""

from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator


@contextmanager
def span(name: str) -> Iterator[None]:
    start = perf_counter()
    print(f"Span {name} started")
    try:
        yield
    finally:
        duration = perf_counter() - start
        print(f"Span {name} finished in {duration:.3f}s")
