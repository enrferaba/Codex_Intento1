"""FastAPI retrieval service placeholder."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
