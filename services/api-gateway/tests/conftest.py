from __future__ import annotations

from pathlib import Path

import pytest

from api_gateway.framework import TestClient
from api_gateway.main import app
from api_gateway.services.debug import reset_debug_state_for_tests
from api_gateway.services.documents import reset_document_state_for_tests


@pytest.fixture(autouse=True)
def _reset_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FERIA_STORAGE_PATH", str(tmp_path))
    reset_document_state_for_tests()
    reset_debug_state_for_tests()
    yield
    reset_document_state_for_tests()
    reset_debug_state_for_tests()
    monkeypatch.delenv("FERIA_STORAGE_PATH", raising=False)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
