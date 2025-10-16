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
