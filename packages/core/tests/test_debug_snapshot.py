from __future__ import annotations

import json

from core import debug


def test_collect_snapshot_contains_expected_fields(monkeypatch):
    monkeypatch.setenv("FERIA_DEBUG", "1")
    monkeypatch.setenv("FERIA_LOG_LEVEL", "DEBUG")

    monkeypatch.setattr(
        debug,
        "_gather_git_metadata",
        lambda: ("main", "abc123", False),
    )

    snapshot = debug.collect_snapshot(env_keys=("FERIA_DEBUG", "FERIA_LOG_LEVEL"))

    assert snapshot.feria_debug_flag is True
    assert snapshot.feria_log_level == "DEBUG"
    assert "FERIA_LOG_LEVEL" in snapshot.env
    assert snapshot.loaded_modules
    assert snapshot.working_directory
    assert snapshot.git_branch == "main"
    assert snapshot.git_commit == "abc123"
    assert snapshot.git_dirty is False
    assert snapshot.python_path


def test_format_snapshot_returns_json(monkeypatch):
    monkeypatch.setattr(
        debug,
        "_gather_git_metadata",
        lambda: ("main", "abc123", False),
    )

    snapshot = debug.collect_snapshot()
    rendered = debug.format_snapshot(snapshot)

    payload = json.loads(rendered)
    assert payload["python_version"]
    assert "git_branch" in payload
    assert "working_directory" in payload
    assert "loaded_modules_count" in payload
    assert "python_path" in payload
