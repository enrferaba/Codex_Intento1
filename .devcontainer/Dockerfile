FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV UV_SYSTEM_PYTHON=1

WORKDIR /workspace
