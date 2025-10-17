from __future__ import annotations

import logging
import os
from contextlib import contextmanager

from core import logging as core_logging


@contextmanager
def temp_env(**env: str):
    original = {key: os.environ.get(key) for key in env}
    try:
        os.environ.update(env)
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_setup_uses_explicit_level(monkeypatch):
    monkeypatch.setenv("FERIA_LOG_LEVEL", "warning")
    core_logging.setup(level="DEBUG", force=True)
    assert logging.getLogger().level == logging.DEBUG


def test_setup_reads_env_var(monkeypatch):
    monkeypatch.delenv("FERIA_DEBUG", raising=False)
    monkeypatch.setenv("FERIA_LOG_LEVEL", "warning")
    core_logging.setup(force=True)
    assert logging.getLogger().level == logging.WARNING


def test_setup_respects_debug_flag(monkeypatch):
    monkeypatch.delenv("FERIA_LOG_LEVEL", raising=False)
    monkeypatch.setenv("FERIA_DEBUG", "1")
    core_logging.setup(force=True)
    assert logging.getLogger().level == logging.DEBUG


def test_setup_defaults_to_info(monkeypatch):
    monkeypatch.delenv("FERIA_LOG_LEVEL", raising=False)
    monkeypatch.delenv("FERIA_DEBUG", raising=False)
    core_logging.setup(force=True)
    assert logging.getLogger().level == logging.INFO
