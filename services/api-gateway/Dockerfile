FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install uv && uv pip install fastapi uvicorn
COPY src /app/src
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
