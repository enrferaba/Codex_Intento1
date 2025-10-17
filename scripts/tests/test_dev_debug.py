from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts import dev_debug


def test_run_sets_feria_debug(monkeypatch):
    called = {}

    def fake_run(cmd, env, check):  # noqa: ANN001 - firma controlada
        called["cmd"] = cmd
        called["env"] = env
        called["check"] = check
        return SimpleNamespace(returncode=0)

    monkeypatch.setenv("FERIA_DEBUG", "0")
    monkeypatch.setattr(dev_debug.subprocess, "run", fake_run)

    exit_code = dev_debug.run(["echo", "hola"])

    assert exit_code == 0
    assert called["cmd"] == ["echo", "hola"]
    assert called["check"] is False
    assert called["env"].get("FERIA_DEBUG") == "1"


def test_main_errors_without_command(monkeypatch):
    class FakeParser:
        def __init__(self):
            self.error_called_with: str | None = None

        def add_argument(self, *args, **kwargs):
            return None

        def parse_args(self, argv=None):
            return SimpleNamespace(command=[])

        def error(self, message: str):  # noqa: D401 - API de argparse
            self.error_called_with = message
            raise SystemExit(2)

    fake_parser = FakeParser()
    monkeypatch.setattr(dev_debug.argparse, "ArgumentParser", lambda **_: fake_parser)

    with pytest.raises(SystemExit) as excinfo:
        dev_debug.main([])

    assert excinfo.value.code == 2
    assert fake_parser.error_called_with is not None
