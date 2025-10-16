FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install uv && uv pip install apscheduler
COPY src /app/src
CMD ["python", "-m", "orchestrator.scheduler"]
