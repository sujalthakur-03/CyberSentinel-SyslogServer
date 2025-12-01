#!/bin/bash

# CyberSentinel SyslogServer - Quick Deployment Script
# This script helps configure and deploy CyberSentinel on any server

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

# Check if .env already exists
if [ -f ".env" ]; then
    print_warning ".env file already exists"
    read -p "Do you want to overwrite it? (y/n): " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        print_info "Skipping .env creation"
    else
        rm .env
        print_info "Removed existing .env file"
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.template .env

    # Update SERVER_IP in .env
    sed -i "s/SERVER_IP=localhost/SERVER_IP=$SERVER_IP/g" .env

    print_success ".env file created"
fi

# Create frontend .env file
echo ""
print_info "Configuring frontend..."

if [ -f "frontend/cybersentinel-ui/.env" ]; then
    print_warning "Frontend .env already exists"
else
    cp frontend/cybersentinel-ui/.env.template frontend/cybersentinel-ui/.env
fi

# Update frontend API URL
sed -i "s|REACT_APP_API_URL=http://localhost:8000|REACT_APP_API_URL=http://$SERVER_IP:8000|g" frontend/cybersentinel-ui/.env

print_success "Frontend configured to use http://$SERVER_IP:8000"

# Create API .env file if needed
echo ""
print_info "Configuring API service..."

if [ ! -f "services/api/.env" ]; then
    cp services/api/.env.template services/api/.env
    print_success "API .env file created"
else
    print_info "API .env already exists"
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
echo ""
echo "Next steps:"
echo "  1. Review and update passwords in .env file:"
echo "     nano .env"
echo ""
echo "  2. Start the services:"
echo "     docker-compose up -d"
echo ""
echo "  3. Check service health:"
echo "     docker-compose ps"
echo "     curl http://$SERVER_IP:8000/health"
echo ""
echo "  4. Access the dashboard:"
echo "     http://$SERVER_IP:3000"
echo ""
echo "  Default login credentials:"
echo "     Username: admin"
echo "     Password: admin"
echo ""
print_warning "Remember to change default passwords in production!"
echo ""
