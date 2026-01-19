FROM python:3.12-slim

RUN apt update && apt-get install -y --no-install-recommends \
    sqlite3 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /workspace
COPY ./data /data

EXPOSE 8000

# Make the entrypoint executable and use it so we can run initialization tasks
RUN chmod +x /workspace/entrypoint.sh
ENTRYPOINT ["sh", "/workspace/entrypoint.sh"]

CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "8000"]
