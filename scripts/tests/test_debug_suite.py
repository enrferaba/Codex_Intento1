from __future__ import annotations

import json

from scripts import debug_suite


def test_build_parser_parses_flags():
    parser = debug_suite.build_parser()
    args = parser.parse_args(["--json"])
    assert args.json is True


def test_snapshot_prints_json(monkeypatch, capsys):
    def fake_collect():
        class _Fake:
            def to_dict(self):
                return {"python_version": "3.12", "loaded_modules": ()}

        return _Fake()

    monkeypatch.setattr(debug_suite, "collect_snapshot", fake_collect)
    debug_suite.main(["--json"])
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert payload["python_version"] == "3.12"


def test_output_file_is_written(tmp_path, monkeypatch, capsys):
    def fake_collect():
        class _Fake:
            def to_dict(self):
                return {"python_version": "3.12"}

        return _Fake()

    monkeypatch.setattr(debug_suite, "collect_snapshot", fake_collect)
    monkeypatch.setattr(debug_suite, "format_snapshot", lambda snapshot: "rendered")

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
