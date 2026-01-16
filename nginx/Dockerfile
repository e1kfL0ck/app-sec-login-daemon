# ------------------------------------------------------------------------------
# Stage 1: Build the Static Assets (Same as your Python Dockerfile)
# ------------------------------------------------------------------------------
FROM node:20-slim AS asset-builder

WORKDIR /build

# Copy manifest files first to maximize Docker caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build the CSS
COPY ./src ./src
RUN npm run build:css

# ------------------------------------------------------------------------------
# Stage 2: Create the Nginx Image
# ------------------------------------------------------------------------------
FROM nginx:alpine

# Install curl for the healthcheck (Alpine doesn't include it by default)
RUN apk add --no-cache curl

# Remove default nginx config to avoid conflicts
RUN rm /etc/nginx/nginx.conf

# Copy custom nginx config
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# 2. Copy "Baked" Static Assets from Stage 1
COPY --from=asset-builder /build/src/static /workspace/static

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD nginx -t && curl -f http://localhost/health 2>/dev/null || exit 1

# ------------------------------------------------------------------------------
# STARTUP COMMAND
# ------------------------------------------------------------------------------
# 1. Background task: Sleeps 2s, then prints the info message 
# 2. Main task: Starts Nginx

# CMD ["nginx", "-g", "daemon off;"] #If nginx hangs, replace the CMD line with this one to get logs.
CMD ["/bin/sh", "-c", "(sleep 2; echo 'INFO:      Nginx running on http://localhost (Press CTRL+C to quit)') & exec nginx -g 'daemon off;'"]