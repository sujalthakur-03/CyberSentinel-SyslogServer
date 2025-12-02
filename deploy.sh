#!/bin/bash

# CyberSentinel SyslogServer - Quick Deployment Script
# This script helps configure and deploy CyberSentinel on any Ubuntu server

set -e

echo "================================================"
echo "  CyberSentinel SyslogServer Deployment Setup"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${NC}ℹ${NC} $1"
}

# Detect server IP
echo "Detecting server IP address..."
SERVER_IP=$(hostname -I | awk '{print $1}')

if [ -z "$SERVER_IP" ]; then
    print_warning "Could not auto-detect IP address"
    read -p "Please enter your server's IP address: " SERVER_IP
fi

print_success "Server IP: $SERVER_IP"
echo ""

# Update .env file with SERVER_IP
print_info "Updating configuration with server IP..."
if [ -f ".env" ]; then
    # Update SERVER_IP in existing .env
    sed -i "s|^SERVER_IP=.*|SERVER_IP=$SERVER_IP|g" .env
    sed -i "s|^REACT_APP_API_URL=.*|REACT_APP_API_URL=http://$SERVER_IP:8000|g" .env
    print_success "Updated .env file"
else
    # Create from template
    cp .env.template .env
    sed -i "s|^SERVER_IP=.*|SERVER_IP=$SERVER_IP|g" .env
    sed -i "s|^REACT_APP_API_URL=.*|REACT_APP_API_URL=http://$SERVER_IP:8000|g" .env
    print_success "Created .env file from template"
fi

echo ""
echo "================================================"
print_success "Configuration complete!"
echo "================================================"
echo ""
echo "Your CyberSentinel is configured for:"
echo "  Server IP: $SERVER_IP"
echo "  API URL: http://$SERVER_IP:8000"
echo "  Frontend URL: http://$SERVER_IP:3000"
echo "  Prometheus: http://$SERVER_IP:9090"
echo ""

# Ask if user wants to deploy now
read -p "Do you want to start the deployment now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting Docker deployment..."
    echo ""

    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo ""
        echo "To install Docker and Docker Compose on Ubuntu:"
        echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "  sudo sh get-docker.sh"
        echo "  sudo usermod -aG docker \$USER"
        echo ""
        exit 1
    fi

    # Determine docker-compose command
    if docker compose version &> /dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi

    # Build and start services
    print_info "Building Docker images (this may take 5-10 minutes)..."
    $DOCKER_COMPOSE build

    print_info "Starting services..."
    $DOCKER_COMPOSE up -d

    echo ""
    print_success "Deployment started!"
    echo ""
    print_info "Waiting for services to initialize (this may take 2-3 minutes)..."
    sleep 15

    # Show status
    $DOCKER_COMPOSE ps

    echo ""
    echo "================================================"
    print_success "Deployment Complete!"
    echo "================================================"
    echo ""
    echo "Access your services at:"
    echo "  🌐 Frontend: http://$SERVER_IP:3000"
    echo "  🔌 API: http://$SERVER_IP:8000"
    echo "  ❤️  API Health: http://$SERVER_IP:8000/health"
    echo "  📊 Prometheus: http://$SERVER_IP:9090"
    echo ""
    echo "Default login credentials:"
    echo "  Username: admin"
    echo "  Password: admin"
    echo ""
    print_warning "IMPORTANT: Change default passwords in production!"
    echo ""
    echo "Useful commands:"
    echo "  View logs:        $DOCKER_COMPOSE logs -f"
    echo "  Stop services:    $DOCKER_COMPOSE down"
    echo "  Restart services: $DOCKER_COMPOSE restart"
    echo ""
else
    print_info "Deployment skipped. Configuration saved to .env"
    echo ""
    echo "To deploy later, run:"
    echo "  docker-compose up -d"
    echo ""
    echo "Or run this script again:"
    echo "  bash deploy.sh"
    echo ""
fi
