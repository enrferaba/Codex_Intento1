"""Utilidad mínima de tablas."""

from __future__ import annotations

from typing import Iterable, Sequence


def render(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    widths = [len(h) for h in headers]
    data = []
    for row in rows:
        widths[:] = [max(w, len(cell)) for w, cell in zip(widths, row)]
        data.append(row)
    sep = " | "
    header_line = sep.join(h.ljust(widths[i]) for i, h in enumerate(headers))
    divider = "-+-".join("-" * w for w in widths)
    body = [sep.join(cell.ljust(widths[i]) for i, cell in enumerate(row)) for row in data]
    return "\n".join([header_line, divider, *body])
