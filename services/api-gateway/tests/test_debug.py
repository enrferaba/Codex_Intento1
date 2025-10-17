from __future__ import annotations

from pathlib import Path

from api_gateway.framework import TestClient


def test_debug_creates_artifacts(client: TestClient, tmp_path: Path) -> None:
    payload = {
        "path": "/workspace/project",
        "error_text": "ValueError: boom",
        "modes": ["python", "tests"],
        "artifacts": [
            {"name": "plan.md", "content": "Paso 1: investigar"},
            {"name": "logs.txt", "content": "stderr"},
        ],
    }
    response = client.post("/v1/debug", json=payload)
    assert response.status_code == 201
    data = response.json()
    location = Path(data["location"])
    assert location.exists()
    summary_file = location / "summary.json"
    assert summary_file.exists()
    artifacts_dir = location / "artifacts"
    assert artifacts_dir.exists()
    assert len(list(artifacts_dir.iterdir())) == 2
