# ===== Build stage =====
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy application files
COPY . .

# Build the application
ENV REACT_APP_API_URL=http://localhost:8000
RUN npm run build

# ===== Runtime stage (nginx) =====
FROM nginx:alpine

# Install only what we actually need
RUN apk add --no-cache wget

# Copy built files from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create startup script directly in the image
RUN printf '%s\n' \
'#!/bin/sh' \
'set -e' \
'' \
'echo "========================================="' \
'echo "CyberSentinel Frontend Starting"' \
'echo "========================================="' \
'' \
'# Get the API URL from environment or use default' \
'API_URL=${REACT_APP_API_URL:-http://localhost:8000}' \
'' \
'echo "Configuring API URL: $API_URL"' \
'' \
'# Create the runtime configuration file using echo' \
'echo "window.ENV = {" > /usr/share/nginx/html/env-config.js' \
'echo "  REACT_APP_API_URL: \"$API_URL\"" >> /usr/share/nginx/html/env-config.js' \
'echo "};" >> /usr/share/nginx/html/env-config.js' \
'' \
'echo "Runtime configuration created successfully"' \
'cat /usr/share/nginx/html/env-config.js' \
'' \
'# Start nginx in foreground' \
'echo "Starting nginx..."' \
'exec nginx -g "daemon off;"' \
> /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Expose port 3000 (make sure nginx.conf listens on 3000)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# IMPORTANT: call script via /bin/sh explicitly
ENTRYPOINT ["sh", "/docker-entrypoint.sh"]
