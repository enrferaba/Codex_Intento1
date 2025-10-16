from __future__ import annotations

import json

from feriactl.commands import debug


def test_report_returns_command_result_json(monkeypatch):
    class _FakeSnapshot:
        def to_dict(self):
            return {"python_version": "3.12"}

    monkeypatch.setattr(debug, "collect_snapshot", lambda: _FakeSnapshot())

    result = debug.report(as_json=True)

    payload = json.loads(result.stdout)
    assert payload["python_version"] == "3.12"


def test_report_returns_pretty_text(monkeypatch):
    def fake_format(snapshot):
        return "debug-info"

    monkeypatch.setattr(debug, "collect_snapshot", lambda: object())
    monkeypatch.setattr(debug, "format_snapshot", fake_format)

    result = debug.report(as_json=False)
    assert result.stdout == "debug-info"
