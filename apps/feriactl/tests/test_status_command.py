from __future__ import annotations

from feriactl.commands.base import CommandResult
from feriactl.commands import status
from feriactl.utils.api import FeriaAPIError


class _FakeAPI:
    def __init__(self, *_, **__):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get_json(self, path: str):
        assert path == "/v1/health"
        return {
            "status": "ok",
            "version": "0.1.0",
            "uptime_seconds": 5,
            "components": [
                {"name": "api-gateway", "status": "ok", "detail": "operativo"},
                {"name": "retrieval", "status": "degraded", "detail": "nDCG bajo"},
            ],
        }


def test_status_show_renders_table(monkeypatch):
    monkeypatch.setattr(status, "FeriaAPI", _FakeAPI)
    result = status.show()

    assert isinstance(result, CommandResult)
    assert result.exit_code == 0
    assert "api-gateway" in result.stdout
    assert "retrieval" in result.stdout
    assert "Versión: 0.1.0" in result.stdout


def test_status_show_handles_api_error(monkeypatch):
    class _ErrorAPI(_FakeAPI):
        def get_json(self, path: str):  # type: ignore[override]
            raise FeriaAPIError("fallo")

    monkeypatch.setattr(status, "FeriaAPI", _ErrorAPI)

    result = status.show()

    assert result.exit_code == 1
    assert "fallo" in result.stderr
