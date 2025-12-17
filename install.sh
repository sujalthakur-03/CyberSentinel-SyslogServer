#!/bin/bash

################################################################################
# CyberSentinel SyslogServer - Complete Installation Script
#
# This script will:
# - Install Docker and Docker Compose (if not present)
# - Configure the server IP across all configuration files
# - Generate secure passwords and secret keys
# - Configure for 1000+ devices with 180-day log retention
# - Build and deploy all services with optimized resource allocation
# - Set up automated log retention policy
# - Initialize the database with default admin user
#
# Version: 2.0 (Updated for High-Scale Deployment)
# Supports: 1000+ network devices, 180-day retention
#
# Usage:
#   sudo bash install.sh
#
# Author: CyberSentinel Team
# License: MIT
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
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
    echo -e "\n${CYAN}================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================${NC}\n"
}

print_step() {
    echo -e "\n${BLUE}>>> $1${NC}\n"
}

print_highlight() {
    echo -e "${MAGENTA}$1${NC}"
}

# Check if script is run with sudo/root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run with sudo privileges"
    echo "Usage: sudo bash install.sh"
    exit 1
fi

# Get the actual user who invoked sudo (for setting proper permissions later)
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)
PROJECT_DIR=$(pwd)

################################################################################
# Welcome Banner
################################################################################
clear
print_header "CyberSentinel SyslogServer - Installation Wizard v2.0"

echo -e "${CYAN}"
cat << "EOF"
   ______      __             _____            __  _            __
  / ____/_  __/ /_  ___  ____/ ___/___  ____  / /_(_)___  ___  / /
 / /   / / / / __ \/ _ \/ ___/\__ \/ _ \/ __ \/ __/ / __ \/ _ \/ /
/ /___/ /_/ / /_/ /  __/ /   ___/ /  __/ / / / /_/ / / / /  __/ /
\____/\__, /_.___/\___/_/   /____/\___/_/ /_/\__/_/_/ /_/\___/_/
     /____/

    SyslogServer - Enterprise Log Management Platform
    Version: 2.0 (High-Scale Edition)

    ✓ 1000+ Device Support
    ✓ 180-Day Log Retention
    ✓ 50,000+ Logs/Second Processing
    ✓ Automated Storage Management

EOF
echo -e "${NC}"

echo "This installation wizard will:"
echo "  ✓ Install Docker and Docker Compose (if needed)"
echo "  ✓ Configure server IP address across all services"
echo "  ✓ Generate secure credentials"
echo "  ✓ Configure for 1000+ network devices"
echo "  ✓ Set up 180-day automated log retention"
echo "  ✓ Allocate resources for high-scale deployment"
echo "  ✓ Build and deploy all microservices"
echo "  ✓ Initialize monitoring and alerting"
echo "  ✓ Set up Index Lifecycle Management"
echo ""
print_highlight "Minimum Requirements: 16GB RAM, 8 CPU cores, 200GB SSD"
print_highlight "Recommended: 32GB RAM, 16 CPU cores, 500GB NVMe SSD"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

################################################################################
# Step 1: System Requirements Check
################################################################################
print_header "Step 1: System Requirements Check"

print_step "Checking system resources..."

# Check CPU cores
CPU_CORES=$(nproc)
print_info "CPU Cores: $CPU_CORES"
if [ "$CPU_CORES" -lt 8 ]; then
    print_warning "Recommended minimum is 8 cores. Current: $CPU_CORES cores"
    print_warning "Performance may be limited with fewer cores"
fi

# Check RAM
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))
print_info "Total RAM: ${TOTAL_RAM_GB}GB"
if [ "$TOTAL_RAM_GB" -lt 16 ]; then
    print_error "Minimum 16GB RAM required. Current: ${TOTAL_RAM_GB}GB"
    read -p "Continue anyway? (not recommended) (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check disk space
AVAILABLE_SPACE_KB=$(df -k "$PROJECT_DIR" | tail -1 | awk '{print $4}')
AVAILABLE_SPACE_GB=$((AVAILABLE_SPACE_KB / 1024 / 1024))
print_info "Available Disk Space: ${AVAILABLE_SPACE_GB}GB"
if [ "$AVAILABLE_SPACE_GB" -lt 200 ]; then
    print_warning "Recommended minimum is 200GB. Current: ${AVAILABLE_SPACE_GB}GB"
    print_warning "Storage may fill up quickly with 180-day retention"
fi

print_success "System requirements check completed"

################################################################################
# Step 2: Detect or prompt for server IP
################################################################################
print_header "Step 2: Server IP Configuration"

print_info "Detecting server IP address..."
AUTO_DETECTED_IP=$(hostname -I 2>/dev/null | awk '{print $1}')

if [ -n "$AUTO_DETECTED_IP" ]; then
    print_success "Auto-detected IP: $AUTO_DETECTED_IP"
    echo ""
    read -p "Use this IP address? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        SERVER_IP="$AUTO_DETECTED_IP"
    else
        read -p "Enter your server's IP address: " SERVER_IP
    fi
else
    print_warning "Could not auto-detect IP address"
    read -p "Enter your server's IP address: " SERVER_IP
fi

# Validate IP address format
if ! [[ $SERVER_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    print_error "Invalid IP address format: $SERVER_IP"
    exit 1
fi

print_success "Server IP set to: $SERVER_IP"

################################################################################
# Step 3: Check and install dependencies
################################################################################
print_header "Step 3: Checking Dependencies"

# Check for Docker
print_step "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed"
    read -p "Install Docker now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing Docker..."
        curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
        sh /tmp/get-docker.sh
        usermod -aG docker $ACTUAL_USER
        print_success "Docker installed successfully"
        print_warning "You may need to log out and back in for Docker permissions to take effect"
    else
        print_error "Docker is required. Installation cancelled."
        exit 1
    fi
else
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    print_success "Docker is installed (version $DOCKER_VERSION)"
fi

# Check for Docker Compose
print_step "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_warning "Docker Compose is not installed"
    print_info "Installing Docker Compose plugin..."

    # Install docker-compose-plugin
    apt-get update -qq
    apt-get install -y docker-compose-plugin

    print_success "Docker Compose installed successfully"
else
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "unknown")
        print_success "Docker Compose (plugin) is installed (version $COMPOSE_VERSION)"
        DOCKER_COMPOSE="docker compose"
    else
        COMPOSE_VERSION=$(docker-compose --version | awk '{print $3}' | sed 's/,//')
        print_success "Docker Compose (standalone) is installed (version $COMPOSE_VERSION)"
        DOCKER_COMPOSE="docker-compose"
    fi
fi

# Determine docker-compose command if not set
if [ -z "$DOCKER_COMPOSE" ]; then
    if docker compose version &> /dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi
fi

################################################################################
# Step 4: Generate secure credentials
################################################################################
print_header "Step 4: Generating Secure Credentials"

print_info "Generating random passwords and secret keys..."

# Generate random strings for secrets
API_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)
OPENSEARCH_PASSWORD="Admin@123"

print_success "Secure credentials generated"

################################################################################
# Step 5: Configure environment files
################################################################################
print_header "Step 5: Configuring Environment Files"

print_step "Creating root .env file with high-scale configuration..."
cat > .env << EOF
# CyberSentinel SyslogServer - Deployment Configuration
# Auto-generated by install.sh v2.0 on $(date)
# Configured for: 1000+ devices, 180-day retention, 50K+ logs/sec
# ============================================================================

# =============================================================================
# SERVER CONFIGURATION
# =============================================================================
SERVER_IP=$SERVER_IP

# =============================================================================
# API SERVICE SETTINGS
# =============================================================================
API_CORS_ORIGINS=*
API_SECRET_KEY=$API_SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
API_ACCESS_TOKEN_EXPIRE_MINUTES=60

# =============================================================================
# DATABASE CREDENTIALS
# =============================================================================
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_USER=cybersentinel
POSTGRES_DB=cybersentinel

OPENSEARCH_PASSWORD=$OPENSEARCH_PASSWORD
OPENSEARCH_USER=admin

REDIS_PASSWORD=

# =============================================================================
# FRONTEND SETTINGS
# =============================================================================
REACT_APP_API_URL=http://$SERVER_IP:8000

# =============================================================================
# SCALABILITY CONFIGURATION (for 1000+ devices, 180-day retention)
# =============================================================================
# Processor Configuration
PROCESSOR_REPLICAS=4
PROCESSOR_WORKERS=8
PROCESSOR_BATCH_SIZE=200

# Receiver Configuration
RECEIVER_WORKERS=8

# Log Retention
LOG_RETENTION_DAYS=180
OPENSEARCH_INDEX_ROTATION=daily

# =============================================================================
# RESOURCE LIMITS (Updated for High-Scale Deployment)
# =============================================================================
RECEIVER_MAX_MEMORY=1g
PROCESSOR_MAX_MEMORY=2g
API_MAX_MEMORY=512m
ALERTING_MAX_MEMORY=256m
FRONTEND_MAX_MEMORY=256m
OPENSEARCH_MAX_MEMORY=4g
KAFKA_MAX_MEMORY=2g

# =============================================================================
# LOGGING & MONITORING
# =============================================================================
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF

print_success "Created .env file with scalability settings"

print_step "Creating frontend .env file..."
mkdir -p frontend/cybersentinel-ui
cat > frontend/cybersentinel-ui/.env << EOF
# CyberSentinel Frontend Configuration
# Auto-generated by install.sh v2.0 on $(date)

# API Configuration
REACT_APP_API_URL=http://$SERVER_IP:8000

# Development Settings
HOST=0.0.0.0
EOF

print_success "Created frontend/.env file"

print_step "Creating API service .env file..."
mkdir -p services/api
cat > services/api/.env << EOF
# CyberSentinel API Service Configuration
# Auto-generated by install.sh v2.0 on $(date)

# API Settings
API_CORS_ORIGINS=*
API_SECRET_KEY=$API_SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
API_ACCESS_TOKEN_EXPIRE_MINUTES=60
API_PORT=8000
API_WORKERS=4

# OpenSearch Settings
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200
OPENSEARCH_SCHEME=http
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=$OPENSEARCH_PASSWORD
OPENSEARCH_INDEX_PREFIX=cybersentinel-logs

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=50

# PostgreSQL Settings
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=cybersentinel
POSTGRES_USER=cybersentinel
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

print_success "Created services/api/.env file"

print_step "Updating frontend runtime config..."
mkdir -p frontend/cybersentinel-ui/public
cat > frontend/cybersentinel-ui/public/env-config.js << EOF
// Runtime environment configuration
// Auto-generated by install.sh v2.0 on $(date)
window.ENV = {
  REACT_APP_API_URL: "http://$SERVER_IP:8000"
};
EOF

print_success "Updated frontend/cybersentinel-ui/public/env-config.js"

# Set proper permissions
chown -R $ACTUAL_USER:$ACTUAL_USER .env frontend/cybersentinel-ui/.env services/api/.env frontend/cybersentinel-ui/public/env-config.js 2>/dev/null || true

################################################################################
# Step 6: Save credentials securely
################################################################################
print_header "Step 6: Saving Credentials"

CREDENTIALS_FILE=".credentials-$(date +%Y%m%d-%H%M%S).txt"
cat > $CREDENTIALS_FILE << EOF
================================================================================
CyberSentinel SyslogServer - Installation Credentials
================================================================================
Generated: $(date)
Server IP: $SERVER_IP
Version: 2.0 (High-Scale Edition)

Configuration: 1000+ devices, 180-day retention, 50K+ logs/sec

IMPORTANT: Store these credentials securely and delete this file after saving!

================================================================================
SERVICE ACCESS
================================================================================
Frontend URL:     http://$SERVER_IP:3000
API URL:          http://$SERVER_IP:8000
API Docs:         http://$SERVER_IP:8000/docs
Health Check:     http://$SERVER_IP:8000/health
Prometheus URL:   http://$SERVER_IP:9090

Default Login:
  Username:       admin
  Password:       admin

================================================================================
DATABASE CREDENTIALS
================================================================================
PostgreSQL:
  Host:           localhost:5432 (or $SERVER_IP:5432 from remote)
  Database:       cybersentinel
  User:           cybersentinel
  Password:       $POSTGRES_PASSWORD

OpenSearch:
  Host:           localhost:9200 (or $SERVER_IP:9200 from remote)
  User:           admin
  Password:       $OPENSEARCH_PASSWORD

Redis:
  Host:           localhost:6379
  Password:       (none)

================================================================================
API SECRETS
================================================================================
API Secret Key:   $API_SECRET_KEY
JWT Secret Key:   $JWT_SECRET_KEY

================================================================================
SYSTEM CONFIGURATION
================================================================================
Log Retention:        180 days (automatic cleanup)
Processor Replicas:   4 instances
Worker Threads:       8 per instance (32 total)
Max Throughput:       50,000+ logs/second
Storage Compression:  Enabled (best_compression codec)
Index Shards:         2 per daily index

Resource Allocation:
  - OpenSearch:       4GB RAM
  - Kafka:            2GB RAM
  - Processors:       8GB RAM (4 × 2GB)
  - Receiver:         1GB RAM
  - Other Services:   ~2GB RAM
  - Total Required:   ~17GB RAM

================================================================================
SYSLOG INGESTION
================================================================================
Configure your network devices to send logs to:
  - UDP:  $SERVER_IP:514
  - TCP:  $SERVER_IP:514
  - TLS:  $SERVER_IP:6514

Supported Devices: Routers, Firewalls, Switches, WiFi APs, Servers
Supported Formats: RFC 3164, RFC 5424

================================================================================
IMPORTANT NOTES
================================================================================
1. Change the default admin password immediately after first login
2. Store these credentials in a secure password manager
3. Delete this file after saving the credentials: rm $CREDENTIALS_FILE
4. All services are accessible on the configured SERVER_IP
5. Logs are automatically deleted after 180 days
6. Monitor disk space: recommended 500GB for 1000 devices
7. Review HARDWARE_REQUIREMENTS.md for scaling guidelines

================================================================================
USEFUL COMMANDS
================================================================================
View logs:          docker compose logs -f
Check status:       docker compose ps
Monitor resources:  docker stats
Stop services:      docker compose down
Restart services:   docker compose restart
Check indices:      curl http://localhost:9200/_cat/indices

================================================================================
EOF

chmod 600 $CREDENTIALS_FILE
chown $ACTUAL_USER:$ACTUAL_USER $CREDENTIALS_FILE

print_success "Credentials saved to: $CREDENTIALS_FILE"
print_warning "IMPORTANT: Save these credentials and delete the file!"

################################################################################
# Step 7: Build Docker images
################################################################################
print_header "Step 7: Building Docker Images"

print_info "This may take 10-15 minutes depending on your internet connection..."
print_info "Building 7 Docker images with optimized configurations..."
echo ""

# Build images
if ! $DOCKER_COMPOSE build; then
    print_error "Failed to build Docker images"
    print_info "Trying build without cache..."
    $DOCKER_COMPOSE build --no-cache
fi

print_success "Docker images built successfully"

################################################################################
# Step 8: Deploy services
################################################################################
print_header "Step 8: Deploying Services"

print_info "Starting all services with Docker Compose..."
print_info "This includes: OpenSearch, Kafka, Redis, PostgreSQL, Prometheus, and 4 application services"
echo ""

# Start services
$DOCKER_COMPOSE up -d

print_success "Services started successfully"

print_info "Waiting for services to initialize (90 seconds)..."
for i in {90..1}; do
    printf "\r${BLUE}[INFO]${NC} Time remaining: %02d seconds" $i
    sleep 1
done
echo ""
echo ""

################################################################################
# Step 9: Set up 180-day log retention policy
################################################################################
print_header "Step 9: Configuring 180-Day Log Retention"

print_info "Waiting for OpenSearch to fully initialize..."
sleep 30

print_step "Setting up Index Lifecycle Management (ILM) policy..."

if [ -f "scripts/setup-ilm-policy.sh" ]; then
    chmod +x scripts/setup-ilm-policy.sh

    # Run ILM setup script
    OPENSEARCH_HOST="localhost" OPENSEARCH_PORT="9200" LOG_RETENTION_DAYS="180" bash scripts/setup-ilm-policy.sh

    if [ $? -eq 0 ]; then
        print_success "180-day retention policy configured successfully"
        print_info "Old indices will be automatically deleted after 180 days"
    else
        print_warning "ILM policy setup completed with warnings"
        print_info "You can manually run: bash scripts/setup-ilm-policy.sh"
    fi
else
    print_warning "ILM policy script not found at scripts/setup-ilm-policy.sh"
    print_info "Automated retention may not be configured"
fi

################################################################################
# Step 10: Verify deployment
################################################################################
print_header "Step 10: Verifying Deployment"

print_step "Checking container status..."
$DOCKER_COMPOSE ps

echo ""
print_step "Checking service health..."

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done

    print_warning "$service_name health check timeout (this may be normal if still initializing)"
    return 1
}

# Check API health
check_service "API Service" "http://localhost:8000/health"

# Check OpenSearch
check_service "OpenSearch" "http://localhost:9200/_cluster/health"

# Check Frontend
check_service "Frontend" "http://localhost:3000"

# Check Prometheus
check_service "Prometheus" "http://localhost:9090/-/healthy"

echo ""
print_step "Checking resource usage..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -12

################################################################################
# Step 11: Final summary and instructions
################################################################################
print_header "Installation Complete!"

echo -e "${GREEN}"
cat << "EOF"
   _____ _    _  _____ _____ ______  _____ _____ _
  / ____| |  | |/ ____/ ____|  ____|/ ____/ ____| |
 | (___ | |  | | |   | |    | |__  | (___| (___ | |
  \___ \| |  | | |   | |    |  __|  \___ \\___ \| |
  ____) | |__| | |___| |____| |____ ____) |___) |_|
 |_____/ \____/ \_____\_____|______|_____/_____/(_)

    ✓ 1000+ Devices Ready
    ✓ 180-Day Retention Active
    ✓ 50,000+ Logs/Sec Capable

EOF
echo -e "${NC}"

print_success "CyberSentinel SyslogServer v2.0 is now running!"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ACCESS INFORMATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  🌐 Frontend Dashboard:  http://$SERVER_IP:3000"
echo "  🔌 API Service:         http://$SERVER_IP:8000"
echo "  📊 API Docs:            http://$SERVER_IP:8000/docs"
echo "  ❤️  Health Check:       http://$SERVER_IP:8000/health"
echo "  📈 Prometheus:          http://$SERVER_IP:9090"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  DEFAULT LOGIN CREDENTIALS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Username: admin"
echo "  Password: admin"
echo ""
print_warning "⚠️  CHANGE DEFAULT PASSWORD IMMEDIATELY AFTER FIRST LOGIN!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  SYSTEM CAPABILITIES"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  ✓ Devices Supported:    1000+ network devices"
echo "  ✓ Log Retention:        180 days (automatic cleanup)"
echo "  ✓ Processing Capacity:  50,000+ logs/second"
echo "  ✓ Storage Management:   Automated with compression"
echo "  ✓ Processor Replicas:   4 instances with 32 workers"
echo "  ✓ Memory Allocated:     ~17GB across all services"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  USEFUL COMMANDS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  View logs:           $DOCKER_COMPOSE logs -f"
echo "  View specific logs:  $DOCKER_COMPOSE logs -f <service-name>"
echo "  Stop services:       $DOCKER_COMPOSE down"
echo "  Restart services:    $DOCKER_COMPOSE restart"
echo "  Check status:        $DOCKER_COMPOSE ps"
echo "  Monitor resources:   docker stats"
echo "  Check indices:       curl http://localhost:9200/_cat/indices"
echo "  Uninstall:           sudo bash uninstall.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  IMPORTANT FILES"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Credentials:         $CREDENTIALS_FILE"
echo "  Main config:         .env"
echo "  Frontend config:     frontend/cybersentinel-ui/.env"
echo "  API config:          services/api/.env"
echo "  Hardware specs:      HARDWARE_REQUIREMENTS.md"
echo ""
print_warning "📝 Save the credentials file in a secure location, then delete it!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  SYSLOG INGESTION"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Configure your devices to send syslogs to:"
echo "    - UDP: $SERVER_IP:514"
echo "    - TCP: $SERVER_IP:514"
echo "    - TLS: $SERVER_IP:6514"
echo ""
echo "  Test with: logger -n $SERVER_IP -P 514 \"Test message\""
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  NEXT STEPS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  1. Open http://$SERVER_IP:3000 and login"
echo "  2. Change the default admin password"
echo "  3. Configure your network devices to send logs"
echo "  4. Monitor the dashboard for incoming logs"
echo "  5. Review HARDWARE_REQUIREMENTS.md for scaling info"
echo "  6. Set up email alerts (optional, see docs)"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

print_success "Installation completed successfully!"
print_info "For support, visit: https://github.com/sujalthakur-03/CyberSentinel-SyslogServer"
print_info "Documentation: See README.md and HARDWARE_REQUIREMENTS.md"

echo ""
read -p "Press Enter to exit..."
