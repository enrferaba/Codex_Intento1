from __future__ import annotations

import json

from feriactl.commands import health
from feriactl.commands.base import CommandResult


class _FakeAPI:
    def __init__(self, *_, **__):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get_json(self, path: str):
        assert path == "/v1/health"
        return {"status": "ok", "version": "0.1.0", "uptime_seconds": 10, "components": []}


def test_health_verbose_prints_json(monkeypatch):
    monkeypatch.setattr(health, "FeriaAPI", _FakeAPI)

    result = health.verbose(pretty=False)

    assert isinstance(result, CommandResult)
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
