FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl git sqlite3 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir requests fastapi uvicorn pydantic pytest
CMD ["tail", "-f", "/dev/null"]
