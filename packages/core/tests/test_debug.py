from __future__ import annotations

import json

from core import debug


def test_collect_snapshot_contains_expected_fields(monkeypatch):
    monkeypatch.setenv("FERIA_DEBUG", "1")
    monkeypatch.setenv("FERIA_LOG_LEVEL", "DEBUG")

    snapshot = debug.collect_snapshot(env_keys=("FERIA_DEBUG", "FERIA_LOG_LEVEL"))

    assert snapshot.feria_debug_flag is True
    assert snapshot.feria_log_level == "DEBUG"
    assert "FERIA_LOG_LEVEL" in snapshot.env
    assert snapshot.loaded_modules


def test_format_snapshot_returns_json(snapshot=None):
    snapshot = debug.collect_snapshot()
    rendered = debug.format_snapshot(snapshot)

    payload = json.loads(rendered)
    assert payload["python_version"]
    assert "loaded_modules_count" in payload
