from __future__ import annotations

from api_gateway.framework import TestClient


def test_health_returns_components(client: TestClient) -> None:
    response = client.get("/v1/health")
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert payload["version"]
    assert any(component["name"] == "document-store" for component in payload["components"])
