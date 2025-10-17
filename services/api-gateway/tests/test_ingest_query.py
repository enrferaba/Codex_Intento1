from __future__ import annotations

from api_gateway.framework import TestClient


def test_ingest_and_query_flow(client: TestClient) -> None:
    ingest_payload = {
        "repository": "sample-repo",
        "modes": ["python"],
        "documents": [
            {"path": "README.md", "text": "FERIA es una plataforma de orquestación para depuración"},
            {"path": "docs/setup.md", "text": "Configura la herramienta feriactl para enviar ingestas."},
        ],
    }
    ingest_response = client.post("/v1/ingest", json=ingest_payload)
    assert ingest_response.status_code == 201
    ingest_data = ingest_response.json()
    assert ingest_data["document_count"] == 2

    query_response = client.post("/v1/query", json={"query": "¿Qué es FERIA?"})
    assert query_response.status_code == 200
    query_data = query_response.json()
    assert query_data["citations"]
    assert "FERIA" in query_data["answer"]
