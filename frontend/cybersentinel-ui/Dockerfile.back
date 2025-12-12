# Multi-stage build for React Frontend
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy application files
COPY . .

# Build the application without API URL (will be set at runtime)
ENV REACT_APP_API_URL=http://localhost:8000
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Install bash and wget for the startup script
RUN apk add --no-cache bash wget

# Copy built files from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create startup script directly in the image
RUN cat > /docker-entrypoint.sh <<'EOF'
#!/bin/bash
set -e

echo "========================================="
echo "CyberSentinel Frontend Starting"
echo "========================================="

# Get the API URL from environment or use default
API_URL=${REACT_APP_API_URL:-http://localhost:8000}

echo "Configuring API URL: $API_URL"

# Create the runtime configuration file
cat > /usr/share/nginx/html/env-config.js <<ENVEOF
window.ENV = {
  REACT_APP_API_URL: "$API_URL"
};
ENVEOF

echo "Runtime configuration created successfully"
cat /usr/share/nginx/html/env-config.js

# Start nginx in foreground
echo "Starting nginx..."
exec nginx -g 'daemon off;'
EOF

# Make the script executable
RUN chmod +x /docker-entrypoint.sh

# Expose port 3000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start with the entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]
