FROM python:3.12-slim

RUN apt update && apt install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Make the entrypoint executable and use it so we can run initialization tasks
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "./entrypoint.sh"]

CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "8000"]
