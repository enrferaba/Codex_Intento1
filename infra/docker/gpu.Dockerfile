FROM nvidia/cuda:12.2.2-base-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3-pip git build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN python3.11 -m pip install --upgrade pip uv

WORKDIR /app
COPY pyproject.toml /app/
RUN uv pip install -r requirements-dev.txt

COPY . /app
