from __future__ import annotations

import json

import pytest

from feriactl.utils.api import FeriaAPI, FeriaAPIError, TransportResponse


def _transport_from_callable(fn):
    def _inner(method: str, url: str, body: bytes | None, headers, timeout: float) -> TransportResponse:
        return fn(method, url, body, headers, timeout)

    return _inner


def test_get_json_success():
    def handler(method, url, body, headers, timeout):  # noqa: ANN001 - firma definida por pruebas
        return TransportResponse(200, json.dumps({"status": "ok"}).encode("utf-8"), {})

    with FeriaAPI(base_url="http://test", transport=_transport_from_callable(handler)) as api:
        assert api.get_json("/v1/health") == {"status": "ok"}


def test_http_error_raises_custom_exception():
    def handler(method, url, body, headers, timeout):
        return TransportResponse(500, json.dumps({"detail": "boom"}).encode("utf-8"), {})

    with FeriaAPI(base_url="http://test", transport=_transport_from_callable(handler)) as api:
        with pytest.raises(FeriaAPIError) as excinfo:
            api.get_json("/boom")
        assert "500" in str(excinfo.value)
        assert "boom" in str(excinfo.value)


def test_base_url_can_be_configured_via_environment(monkeypatch):
    monkeypatch.setenv("FERIA_API_URL", "http://env")

    captured = {}

    def handler(method, url, body, headers, timeout):
        captured["url"] = url
        return TransportResponse(200, json.dumps({"status": "ok"}).encode("utf-8"), {})

    with FeriaAPI(transport=_transport_from_callable(handler)) as api:
        api.get_json("/v1/health")

    assert captured["url"].startswith("http://env")
    monkeypatch.delenv("FERIA_API_URL")


def test_resolved_base_url_property_returns_effective_url():
    with FeriaAPI(base_url="http://test") as api:
        assert api.resolved_base_url == "http://test"
