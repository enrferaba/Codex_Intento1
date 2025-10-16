"""Cliente HTTP para Prometheus (placeholder)."""

from __future__ import annotations

import httpx


class PrometheusClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=5.0)

    def query(self, expr: str) -> dict:
        response = self._client.get("/api/v1/query", params={"query": expr})
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()
