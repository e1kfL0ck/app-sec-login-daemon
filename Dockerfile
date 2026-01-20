FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY ./src /workspace
COPY ./data /data

# Expose port
EXPOSE 8000

# Make the entrypoint executable
RUN chmod +x /workspace/entrypoint.sh
ENTRYPOINT ["sh", "/workspace/entrypoint.sh"]

CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "8000"]