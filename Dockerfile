FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r pyproject.toml || pip install rich pyjwt requests
EXPOSE 8000 8080 5000 8081
CMD ["python3", "modules/art_01.py"]
