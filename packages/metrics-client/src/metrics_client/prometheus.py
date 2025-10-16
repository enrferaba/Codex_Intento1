"""Cliente mínimo para realizar peticiones a Prometheus."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class PrometheusClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def query(self, expr: str) -> dict:
        url = f"{self._base_url}/api/v1/query?{urllib.parse.urlencode({'query': expr})}"
        request = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(request, timeout=5.0) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.URLError as exc:  # pragma: no cover - entorno sin red
            raise RuntimeError(f"No se pudo contactar con Prometheus: {exc}") from exc
        return json.loads(payload)

    def close(self) -> None:  # pragma: no cover - no se mantiene estado
        return None
