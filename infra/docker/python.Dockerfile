FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml /app/
RUN pip install uv && uv pip install -r requirements-dev.txt

COPY . /app
