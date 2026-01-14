# Build stage: Compile Tailwind CSS
# Using slim instead of alpine to avoid native binary (musl) issues
FROM node:20-slim AS tailwind-builder

WORKDIR /build

# Copy package files first to leverage Docker cache
COPY package.json package-lock.json ./

# Install dependencies (Standard slim image handles lightningcss/parcel-watcher binaries)
RUN npm ci

# Copy the source code for the build
COPY ./src ./src

# Run the build script
RUN npm run build:css

# ------------------------------------------------------------------------------
# Production stage
# ------------------------------------------------------------------------------
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

# Copy the compiled CSS from the builder stage
COPY --from=tailwind-builder /build/src/static/styles.css /workspace/static/styles.css

EXPOSE 8000

# Make the entrypoint executable
RUN chmod +x /workspace/entrypoint.sh
ENTRYPOINT ["sh", "/workspace/entrypoint.sh"]

CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "8000"]