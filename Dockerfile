# Build stage: Compile Tailwind CSS
FROM node:20-alpine AS tailwind-builder

WORKDIR /build

COPY package.json package-lock.json tailwind.config.js ./
RUN npm ci

COPY src/static/tailwind.css src/static/tailwind.css
COPY src/templates src/templates
RUN npm run build:css

# Production stage
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

# Copy compiled CSS from builder stage
COPY --from=tailwind-builder /build/src/static/styles.css /workspace/static/styles.css

EXPOSE 8000

# Make the entrypoint executable and use it so we can run initialization tasks
RUN chmod +x /workspace/entrypoint.sh
ENTRYPOINT ["sh", "/workspace/entrypoint.sh"]

CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "8000"]
