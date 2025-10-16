from api_gateway.framework import TestClient
from api_gateway.main import app


def test_health_endpoint_returns_structured_payload():
    client = TestClient(app)

    response = client.get("/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "0.1.0"
    assert isinstance(payload["uptime_seconds"], int)
    assert payload["uptime_seconds"] >= 0
    assert payload["components"], "se esperaba al menos un componente reportado"
    first_component = payload["components"][0]
    assert first_component["name"] == "api-gateway"
    assert first_component["status"] == "ok"
