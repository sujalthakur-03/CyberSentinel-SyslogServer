#!/bin/bash

################################################################################
# CyberSentinel SyslogServer - Complete Uninstallation Script
#
# This script will remove:
# - All Docker containers (stopped and running)
# - All Docker volumes (ALL DATA WILL BE LOST)
# - All Docker images
# - All Docker networks
# - Generated SSL certificates
# - Log files
#
# This script will NOT remove:
# - Docker Engine
# - Docker Compose
# - System packages
#
# WARNING: This will DELETE ALL your logs, alerts, and configuration data!
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

# Check if script is run with sudo/root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run with sudo privileges"
    echo "Usage: sudo bash uninstall.sh"
    exit 1
fi

# Display warning
print_header "CyberSentinel SyslogServer - Uninstallation"

echo -e "${RED}⚠️  WARNING: This action is IRREVERSIBLE! ⚠️${NC}\n"
echo "This script will remove:"
echo "  ✗ All CyberSentinel Docker containers"
echo "  ✗ All CyberSentinel Docker volumes"
echo "  ✗ All CyberSentinel Docker images"
echo "  ✗ All CyberSentinel Docker networks"
echo "  ✗ SSL certificates and generated files"
echo "  ✗ ALL stored logs and alerts (permanent data loss)"
echo ""
echo "This script will NOT remove:"
echo "  ✓ Docker Engine"
echo "  ✓ Docker Compose"
echo "  ✓ Source code files"
echo ""

# Ask for confirmation
read -p "Are you sure you want to proceed? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Uninstallation cancelled."
    exit 0
fi

# Double confirmation for data deletion
echo -e "${RED}FINAL WARNING: All data will be permanently deleted!${NC}"
read -p "Type 'DELETE ALL DATA' to confirm: " -r
echo
if [[ ! $REPLY == "DELETE ALL DATA" ]]; then
    print_info "Uninstallation cancelled."
    exit 0
fi

print_info "Starting uninstallation process..."
echo ""

################################################################################
# Step 1: Stop all running containers
################################################################################
print_header "Step 1: Stopping CyberSentinel Containers"

if [ -f "docker-compose.yml" ]; then
    print_info "Stopping all containers with docker-compose..."
    docker-compose down --remove-orphans || print_warning "docker-compose down failed, continuing..."
    print_success "Containers stopped"
else
    print_warning "docker-compose.yml not found, skipping docker-compose down"
fi

# Stop any remaining CyberSentinel containers
print_info "Stopping any remaining CyberSentinel containers..."
RUNNING_CONTAINERS=$(docker ps -a --filter "name=cybersentinel" --format "{{.Names}}" 2>/dev/null || true)
if [ -n "$RUNNING_CONTAINERS" ]; then
    echo "$RUNNING_CONTAINERS" | xargs -r docker stop 2>/dev/null || true
    print_success "Stopped remaining containers"
else
    print_info "No running containers found"
fi

################################################################################
# Step 2: Remove all containers
################################################################################
print_header "Step 2: Removing CyberSentinel Containers"

print_info "Removing all CyberSentinel containers..."
CONTAINERS=$(docker ps -a --filter "name=cybersentinel" --format "{{.Names}}" 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "$CONTAINERS" | xargs -r docker rm -f 2>/dev/null || true
    print_success "Removed $(echo "$CONTAINERS" | wc -l) container(s)"
else
    print_info "No containers to remove"
fi

################################################################################
# Step 3: Remove all volumes
################################################################################
print_header "Step 3: Removing CyberSentinel Volumes (DATA DELETION)"

print_info "Removing all CyberSentinel volumes..."
VOLUMES=$(docker volume ls --filter "name=cybersentinel" --format "{{.Name}}" 2>/dev/null || true)
if [ -n "$VOLUMES" ]; then
    echo "$VOLUMES" | xargs -r docker volume rm -f 2>/dev/null || true
    print_success "Removed $(echo "$VOLUMES" | wc -l) volume(s)"
else
    print_info "No volumes to remove"
fi

# Also remove volumes defined in docker-compose
if [ -f "docker-compose.yml" ]; then
    print_info "Removing volumes defined in docker-compose.yml..."
    docker-compose down -v 2>/dev/null || true
    print_success "Docker-compose volumes removed"
fi

################################################################################
# Step 4: Remove all images
################################################################################
print_header "Step 4: Removing CyberSentinel Docker Images"

print_info "Removing CyberSentinel Docker images..."
IMAGES=$(docker images --filter "reference=*cybersentinel*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || true)
if [ -n "$IMAGES" ]; then
    echo "$IMAGES" | xargs -r docker rmi -f 2>/dev/null || true
    print_success "Removed $(echo "$IMAGES" | wc -l) image(s)"
else
    print_info "No images to remove"
fi

# Remove images from the local build
print_info "Removing locally built images..."
docker images --filter "reference=syslogserver*" --format "{{.Repository}}:{{.Tag}}" | xargs -r docker rmi -f 2>/dev/null || true
docker images --filter "dangling=true" --format "{{.ID}}" | xargs -r docker rmi -f 2>/dev/null || true
print_success "Removed dangling images"

################################################################################
# Step 5: Remove networks
################################################################################
print_header "Step 5: Removing CyberSentinel Docker Networks"

print_info "Removing CyberSentinel networks..."
NETWORKS=$(docker network ls --filter "name=cybersentinel" --format "{{.Name}}" 2>/dev/null || true)
if [ -n "$NETWORKS" ]; then
    echo "$NETWORKS" | xargs -r docker network rm 2>/dev/null || true
    print_success "Removed $(echo "$NETWORKS" | wc -l) network(s)"
else
    print_info "No networks to remove"
fi

################################################################################
# Step 6: Clean up generated files
################################################################################
print_header "Step 6: Cleaning Up Generated Files"

# Remove SSL certificates
if [ -d "certs" ]; then
    print_info "Removing SSL certificates..."
    rm -rf certs/
    print_success "SSL certificates removed"
fi

# Remove log files
if [ -d "logs" ]; then
    print_info "Removing log files..."
    rm -rf logs/
    print_success "Log files removed"
fi

# Remove any generated env-config.js from frontend build
if [ -f "frontend/cybersentinel-ui/public/env-config.js" ]; then
    print_info "Removing generated frontend config..."
    rm -f frontend/cybersentinel-ui/public/env-config.js
    print_success "Frontend config removed"
fi

# Remove node_modules if present (optional - user can keep for development)
read -p "Do you want to remove frontend node_modules? (yes/no): " -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    if [ -d "frontend/cybersentinel-ui/node_modules" ]; then
        print_info "Removing node_modules (this may take a while)..."
        rm -rf frontend/cybersentinel-ui/node_modules/
        print_success "node_modules removed"
    fi
fi

# Remove build directory if present
if [ -d "frontend/cybersentinel-ui/build" ]; then
    print_info "Removing frontend build directory..."
    rm -rf frontend/cybersentinel-ui/build/
    print_success "Build directory removed"
fi

################################################################################
# Step 7: Docker system cleanup
################################################################################
print_header "Step 7: Docker System Cleanup"

print_info "Running Docker system prune..."
read -p "Remove all unused Docker resources (images, containers, networks)? (yes/no): " -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    docker system prune -af --volumes 2>/dev/null || true
    print_success "Docker system pruned"
else
    print_info "Skipping Docker system prune"
fi

################################################################################
# Final Summary
################################################################################
print_header "Uninstallation Complete"

print_success "CyberSentinel SyslogServer has been completely removed!"
echo ""
echo "Removed components:"
echo "  ✓ All containers"
echo "  ✓ All volumes (data deleted)"
echo "  ✓ All images"
echo "  ✓ All networks"
echo "  ✓ Generated files and certificates"
echo ""
echo "Preserved components:"
echo "  ✓ Docker Engine (still installed)"
echo "  ✓ Docker Compose (still installed)"
echo "  ✓ Source code files (still in $(pwd))"
echo ""
print_info "To reinstall, run: sudo bash deploy.sh"
echo ""

# Verify cleanup
print_header "Verification"
REMAINING_CONTAINERS=$(docker ps -a --filter "name=cybersentinel" --format "{{.Names}}" 2>/dev/null || true)
REMAINING_VOLUMES=$(docker volume ls --filter "name=cybersentinel" --format "{{.Name}}" 2>/dev/null || true)
REMAINING_NETWORKS=$(docker network ls --filter "name=cybersentinel" --format "{{.Name}}" 2>/dev/null || true)

if [ -z "$REMAINING_CONTAINERS" ] && [ -z "$REMAINING_VOLUMES" ] && [ -z "$REMAINING_NETWORKS" ]; then
    print_success "Verification passed: No CyberSentinel components found"
else
    print_warning "Some components may still exist:"
    [ -n "$REMAINING_CONTAINERS" ] && echo "  Containers: $REMAINING_CONTAINERS"
    [ -n "$REMAINING_VOLUMES" ] && echo "  Volumes: $REMAINING_VOLUMES"
    [ -n "$REMAINING_NETWORKS" ] && echo "  Networks: $REMAINING_NETWORKS"
fi

echo ""
print_info "Thank you for using CyberSentinel!"
echo ""
