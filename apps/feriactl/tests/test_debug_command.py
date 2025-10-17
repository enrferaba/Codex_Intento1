from __future__ import annotations

import json
from typing import Any

from feriactl.commands import debug


class _FakeAPI:
    def __init__(self, *_: Any, **__: Any) -> None:
        self.last_payload: dict[str, Any] | None = None

    def __enter__(self) -> "_FakeAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        return None

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        assert path == "/v1/debug"
        self.last_payload = payload
        return {"debug_id": "abc123", "location": "/tmp/debug", "artifact_count": 1}


class _FakeSnapshot:
    def __init__(self) -> None:
        self.working_directory = "/workspace"
        self.python_version = "3.12"
        self.platform = "linux"

    def to_dict(self) -> dict[str, str]:
        return {"python_version": self.python_version}


def test_report_returns_command_result_json(monkeypatch):
    fake_api = _FakeAPI()
    monkeypatch.setattr(debug, "FeriaAPI", lambda *args, **kwargs: fake_api)
    monkeypatch.setattr(debug, "collect_snapshot", lambda: _FakeSnapshot())

    result = debug.report(as_json=True)

    payload = json.loads(result.stdout)
    assert payload["debug_id"] == "abc123"
    assert fake_api.last_payload is not None
    assert fake_api.last_payload["artifacts"]


def test_report_returns_human_text(monkeypatch):
    fake_api = _FakeAPI()
    monkeypatch.setattr(debug, "FeriaAPI", lambda *args, **kwargs: fake_api)
    monkeypatch.setattr(debug, "collect_snapshot", lambda: _FakeSnapshot())

    result = debug.report(as_json=False)

    assert "Sesión de depuración" in result.stdout
    assert "abc123" in result.stdout
