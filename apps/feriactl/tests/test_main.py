from __future__ import annotations

import importlib
import os

from feriactl import main as feria_main_function

feria_main = importlib.import_module("feriactl.main")


def test_main_debug_flag_sets_environment(monkeypatch):
    monkeypatch.delenv("FERIA_DEBUG", raising=False)

    class FakeParser(feria_main.argparse.ArgumentParser):
        def __init__(self):
            super().__init__(prog="feriactl")
            self.printed_help = False

        def print_help(self):  # noqa: D401 - override argparse
            self.printed_help = True

        def parse_args(self, argv=None):  # noqa: D401 - override argparse
            return feria_main.argparse.Namespace(debug=True, func=None)

    fake_parser = FakeParser()
    monkeypatch.setattr(feria_main, "build_parser", lambda: fake_parser)
    monkeypatch.setattr(feria_main, "setup_logging", lambda **_: None)

    exit_code = feria_main_function(["--debug"])

    assert exit_code == 0
    assert os.environ.get("FERIA_DEBUG") == "1"
    assert fake_parser.printed_help is True


def test_debug_command_invokes_report(monkeypatch):
    captured = {}

    def fake_report(*, as_json):
        captured["as_json"] = as_json
        from feriactl.commands.base import CommandResult

        return CommandResult(stdout="{}")

    monkeypatch.setattr(feria_main, "setup_logging", lambda **_: None)
    monkeypatch.setattr(feria_main.debug, "report", fake_report)

    exit_code = feria_main.main(["debug", "report", "--json"])

    assert exit_code == 0
    assert captured["as_json"] is True
