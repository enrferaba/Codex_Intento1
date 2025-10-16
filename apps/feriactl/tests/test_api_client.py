import httpx
import pytest

from feriactl.utils.api import FeriaAPI, FeriaAPIError


def test_get_json_success(monkeypatch):
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"status": "ok"}))

    with FeriaAPI(base_url="http://test", transport=transport) as api:
        assert api.get_json("/v1/health") == {"status": "ok"}


def test_http_error_raises_custom_exception():
    transport = httpx.MockTransport(lambda request: httpx.Response(500, json={"detail": "boom"}))

    with FeriaAPI(base_url="http://test", transport=transport) as api:
        with pytest.raises(FeriaAPIError) as excinfo:
            api.get_json("/boom")
        assert "500" in str(excinfo.value)
        assert "boom" in str(excinfo.value)


def test_base_url_can_be_configured_via_environment(monkeypatch):
    monkeypatch.setenv("FERIA_API_URL", "http://env")

    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(handler)
    with FeriaAPI(transport=transport) as api:
        api.get_json("/v1/health")

    assert captured["url"].startswith("http://env")
    monkeypatch.delenv("FERIA_API_URL")
