from __future__ import annotations

import json
from typing import Any

import pytest

from scripts import debug_suite


def test_build_parser_parses_flags():
    parser = debug_suite.build_parser()
    args = parser.parse_args(["--json"])
    assert args.json is True


def test_snapshot_prints_json(monkeypatch, capsys):
    class _Fake:
        def to_dict(self):
            return {"python_version": "3.12", "loaded_modules": ()}

    monkeypatch.setattr(debug_suite, "collect_snapshot", lambda: _Fake())
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)
    monkeypatch.setattr(debug_suite, "execute_commands", lambda commands: [])
    debug_suite.main(["--json"])
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert payload["python_version"] == "3.12"


def test_output_file_is_written(tmp_path, monkeypatch, capsys):
    class _Fake:
        def to_dict(self):
            return {"python_version": "3.12"}

    monkeypatch.setattr(debug_suite, "collect_snapshot", lambda: _Fake())
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)
    monkeypatch.setattr(debug_suite, "format_snapshot", lambda snapshot: "rendered")
    monkeypatch.setattr(debug_suite, "execute_commands", lambda commands: [])
    destination = tmp_path / "snapshot.txt"
    debug_suite.main(["--output", str(destination)])
    captured = capsys.readouterr().out
    assert "rendered" in captured
    assert destination.read_text(encoding="utf-8") == "rendered\n"


def test_output_file_appends(tmp_path, monkeypatch):
    class _Fake:
        def __init__(self, payload: dict[str, str]):
            self._payload = payload

        def to_dict(self):
            return self._payload

    records = [
        _Fake({"python_version": "3.12"}),
        _Fake({"python_version": "3.13"}),
    ]

    def fake_collect():
        return records.pop(0)

    monkeypatch.setattr(debug_suite, "collect_snapshot", fake_collect)
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)

    destination = tmp_path / "snapshots.jsonl"
    debug_suite.main(["--json", "--output", str(destination)])
    debug_suite.main(["--json", "--output", str(destination), "--append"])

    raw = destination.read_text(encoding="utf-8").strip()
    blocks = [block for block in raw.split("\n\n") if block.strip()]
    assert len(blocks) == 2
    payload_first = json.loads(blocks[0])
    payload_second = json.loads(blocks[1])
    assert payload_first["python_version"] == "3.12"
    assert payload_second["python_version"] == "3.13"


def test_command_results_are_recorded(monkeypatch, capsys):
    class _Fake:
        def to_dict(self):
            return {"python_version": "3.12"}

    recorded = {}

    def fake_execute(commands):
        recorded["commands"] = list(commands)
        return [
            {
                "command": ["echo", "hola"],
                "exit_code": 0,
                "stdout": "hola",
                "stderr": "",
                "duration_ms": 1.0,
                "status": "ok",
                "error": None,
            }
        ]

    monkeypatch.setattr(debug_suite, "collect_snapshot", lambda: _Fake())
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)
    monkeypatch.setattr(debug_suite, "format_snapshot", lambda snapshot: "SNAPSHOT")
    monkeypatch.setattr(debug_suite, "execute_commands", fake_execute)

    debug_suite.main(["--command", "echo hola"])
    captured = capsys.readouterr().out

    assert recorded["commands"] == [["echo", "hola"]]
    assert "SNAPSHOT" in captured
    assert "# Resultados de comandos" in captured
    assert "$ echo hola" in captured


def test_json_output_includes_command_results(monkeypatch, capsys):
    class _Fake:
        def to_dict(self):
            return {"python_version": "3.12"}

    def fake_execute(commands):
        return [
            {
                "command": ["echo", "hola"],
                "exit_code": 0,
                "stdout": "hola",
                "stderr": "",
                "duration_ms": 1.0,
                "status": "ok",
                "error": None,
            }
        ]

    monkeypatch.setattr(debug_suite, "collect_snapshot", lambda: _Fake())
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)
    monkeypatch.setattr(debug_suite, "execute_commands", fake_execute)

    debug_suite.main(["--json", "--command", "echo hola"])
    payload = json.loads(capsys.readouterr().out)

    assert "command_results" in payload
    assert payload["command_results"][0]["command"] == ["echo", "hola"]


def test_full_mode_runs_commands_and_tests(monkeypatch):
    class _Fake:
        def to_dict(self):
            return {"python_version": "3.12"}

    recorded: dict[str, Any] = {}

    def fake_execute(commands):
        recorded["commands"] = list(commands)
        return []

    def fake_run_pytest(args):
        recorded["pytest_args"] = list(args)
        return 0

    monkeypatch.setattr(debug_suite, "collect_snapshot", lambda: _Fake())
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)
    monkeypatch.setattr(debug_suite, "format_snapshot", lambda snapshot: "SNAPSHOT")
    monkeypatch.setattr(debug_suite, "execute_commands", fake_execute)
    monkeypatch.setattr(debug_suite, "run_pytest", fake_run_pytest)

    exit_code = debug_suite.main(["--full"])

    assert exit_code == 0
    assert recorded["commands"] == debug_suite.DEFAULT_FULL_COMMANDS
    assert recorded["pytest_args"] == []


def test_error_on_empty_command(monkeypatch):
    class _Fake:
        def to_dict(self):
            return {"python_version": "3.12"}

    monkeypatch.setattr(debug_suite, "collect_snapshot", lambda: _Fake())
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)

    with pytest.raises(SystemExit) as excinfo:
        debug_suite.main(["--command", "   "])

    assert excinfo.value.code == 2


def test_exit_code_reflects_command_failure(monkeypatch, capsys):
    class _Fake:
        def to_dict(self):
            return {"python_version": "3.12"}

    def fake_execute(commands):
        return [
            {
                "command": ["false"],
                "exit_code": 1,
                "stdout": "",
                "stderr": "boom",
                "duration_ms": 1.0,
                "status": "error",
                "error": None,
            }
        ]

    monkeypatch.setattr(debug_suite, "collect_snapshot", lambda: _Fake())
    monkeypatch.setattr(debug_suite, "setup_logging", lambda: None)
    monkeypatch.setattr(debug_suite, "format_snapshot", lambda snapshot: "SNAPSHOT")
    monkeypatch.setattr(debug_suite, "execute_commands", fake_execute)

    exit_code = debug_suite.main(["--command", "false"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Al menos un comando finalizó con errores" in captured.err
