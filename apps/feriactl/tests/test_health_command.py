import json

from typer.testing import CliRunner

from feriactl.main import app


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
    runner = CliRunner()
    monkeypatch.setattr("feriactl.commands.health.FeriaAPI", _FakeAPI)

    result = runner.invoke(app, ["health", "verbose", "--pretty", "False"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip())
    assert payload["status"] == "ok"
