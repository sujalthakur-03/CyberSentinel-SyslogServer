# 🛡️ CyberSentinel - Syslog Server

<div align="center">

![CyberSentinel](https://img.shields.io/badge/CyberSentinel-Syslog%20Server-00ff9f?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-00d4ff?style=for-the-badge)
![Status](https://img.shields.io/badge/status-production%20ready-00ff9f?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-ff0080?style=for-the-badge)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-detailed-documentation) • [Architecture](#-system-architecture) • [API Docs](#-api-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Detailed Documentation](#-detailed-documentation)
- [Sending Logs](#sending-logs-to-cybersentinel)
- [Using the Web Interface](#using-the-web-interface)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)
- [Uninstallation](#-uninstallation)

---

## 🎯 Overview

**CyberSentinel** is a comprehensive, syslog monitoring and analysis platform designed for enterprise security operations. It provides real-time log collection, processing, and visualization.

### Why CyberSentinel?

- ✅ **Real-time Processing**: Handle 10,000+ logs/second with Kafka-based architecture
- ✅ **Scalable**: Horizontal scaling support with multiple processor replicas
- ✅ **Comprehensive**: Full-stack solution from ingestion to visualization

---

## ✨ Features

### 🔐 Core Features

- **Multi-Protocol Syslog Ingestion**
  - UDP/TCP support on port 514
  - TLS encrypted reception on port 6514
  - RFC 3164 & RFC 5424 parsing
  - 10,000+ messages/second throughput

- **Real-time Log Processing**
  - Kafka-based message queue for reliability
  - Batch processing with 100 logs/batch
  - OpenSearch indexing for fast search
  - Horizontal scaling with multiple processors

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│          (Routers, Servers, Firewalls, Applications)            │
└────────────────────────┬────────────────────────────────────────┘
                         │ Syslog (UDP/TCP/TLS)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Syslog Receiver Service                      │
│              (UDP:514, TCP:514, TLS:6514)                       │
│           RFC 3164/5424 Parser • 10K+ msgs/sec                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Apache Kafka Cluster                        │
│                   (Message Queue & Buffer)                       │
│              Topic: raw-logs • LZ4 Compression                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Log Processor Service (x2)                      │
│                 Enrichment  • Normalization                              │
│              OpenSearch Indexing • Redis Cache                   │
└────────────┬────────────────────────────────┬───────────────────┘
             │                                 │
             ▼                                 ▼
┌──────────────────────────┐    ┌────────────────────────────────┐
│   OpenSearch Cluster     │    │    Alerting Service            │
│   (Log Storage)          │    │    (Threat Monitoring)         │
│   - Full-text search     │    │    - Email/Slack notifications │
│   - Aggregations         │    │    - Pattern-based rules       │
└──────────────────────────┘    └────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        REST API Service                          │
│              FastAPI • JWT Auth • Swagger Docs                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    React Web Interface                           │
│        Cyberpunk Theme • Real-time Dashboard • Alerts            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Software

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For cloning the repository

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | 8 GB | 16+ GB |
| **Disk** | 50 GB | 100+ GB SSD |

### Port Requirements

| Port | Service | Protocol |
|------|---------|----------|
| 514 | Syslog Receiver | UDP/TCP |
| 6514 | Syslog Receiver (TLS) | TCP |
| 3000 | Web Interface | HTTP |
| 8000 | REST API | HTTP |
| 9090 | Prometheus | HTTP |

---

## 🚀 Quick Start

### Method 1: Automated Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git
cd CyberSentinel-SyslogServer

# Run the automated deployment script
bash deploy.sh
```

The deployment script will:
- Auto-detect your server IP
- Configure all environment variables
- Build and start all services
- Display access URLs

### Method 2: Manual Deployment

```bash
# 1. Clone the repository
git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git
cd CyberSentinel-SyslogServer

# 2. Configure environment
cp .env.template .env
# Edit .env and set SERVER_IP to your server's IP address
nano .env

# 3. Build all services
docker-compose build

# 4. Start the system
docker-compose up -d

# 5. Verify health
curl http://localhost:8000/health
```

### Access the Interface

- **Web Interface**: http://YOUR_SERVER_IP:3000
- **Login**: `admin` / `admin`
- **API Docs**: http://YOUR_SERVER_IP:8000/docs
- **Prometheus**: http://YOUR_SERVER_IP:9090

**🎉 CyberSentinel is now running!**

---

## 📚 Detailed Documentation

### Installation

#### Prerequisites

Before you begin, ensure you have:
- **Ubuntu Server 20.04+** (or any Linux distribution)
- **Minimum 8GB RAM** (16GB recommended)
- **50GB free disk space** (100GB+ recommended)
- **Root or sudo access**

#### Step 1: Install Docker and Docker Compose

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker using the official script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to the docker group
sudo usermod -aG docker $USER

# Apply group changes (or logout and login again)
newgrp docker

# Verify Docker installation
docker --version
docker-compose --version
```

#### Step 2: Clone the Repository

```bash
# Clone the project
git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git
cd CyberSentinel-SyslogServer
```

#### Step 3: Automated Deployment (Recommended)

The easiest way to deploy CyberSentinel is using the automated deployment script:

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
bash deploy.sh
```

The script will:
- ✅ Auto-detect your server's IP address
- ✅ Configure all environment variables
- ✅ Update CORS settings
- ✅ Build all Docker images
- ✅ Start all services
- ✅ Display access URLs

**That's it! Your system will be ready in 5-10 minutes.**

#### Step 4: Manual Deployment (Alternative)

If you prefer manual configuration:

```bash
# 1. Copy the environment template
cp .env.template .env

# 2. Get your server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "Your server IP: $SERVER_IP"

# 3. Update the .env file with your server IP
sed -i "s|^SERVER_IP=.*|SERVER_IP=$SERVER_IP|" .env
sed -i "s|^REACT_APP_API_URL=.*|REACT_APP_API_URL=http://$SERVER_IP:8000|" .env

# 4. (Optional) Edit other configuration values
nano .env

# 5. Build all services
docker-compose build

# 6. Start all services
docker-compose up -d

# 7. Wait for services to initialize (2-3 minutes)
sleep 120

# 8. Check service status
docker-compose ps

# 9. Verify API health
curl http://localhost:8000/health
```

#### Step 5: Verify Installation

After deployment, verify all services are running:

```bash
# Check all containers
docker-compose ps

# Check logs for any errors
docker-compose logs

# Test API health
curl http://localhost:8000/health

# Test frontend accessibility
curl http://localhost:3000
```

Expected output: All services should show status as "healthy"

#### Step 6: Access the Dashboard

Once deployed, access your services:

1. **Web Dashboard**: Open your browser to `http://YOUR_SERVER_IP:3000`
   - Replace `YOUR_SERVER_IP` with your actual server IP
   - Example: `http://192.168.1.100:3000`

2. **Login** with default credentials:
   - Username: `admin`
   - Password: `admin`
   - ⚠️ **Important**: Change these credentials in production!

3. **API Documentation**: `http://YOUR_SERVER_IP:8000/docs`

4. **Prometheus Metrics**: `http://YOUR_SERVER_IP:9090`

---

## Sending Logs to CyberSentinel

### Method 1: Using rsyslog (Linux)

1. Edit `/etc/rsyslog.conf`:
   ```bash
   sudo nano /etc/rsyslog.conf
   ```

2. Add this line:
   ```
   *.* @your-server-ip:514
   ```

3. Restart rsyslog:
   ```bash
   sudo systemctl restart rsyslog
   ```

### Method 2: Using logger Command (Testing)

```bash
# Send test log
logger -n your-server-ip -P 514 "Test message from $(hostname)"

# Send 100 test logs
for i in {1..100}; do
    logger -n your-server-ip -P 514 "Test log #$i from $(hostname)"
done
```

### Method 3: Router Configuration

**Cisco Example**:
```
logging host your-server-ip transport udp port 514
logging trap informational
```

**pfSense Example**:
1. Status > System Logs > Settings
2. Enable "Remote Logging"
3. Add: `your-server-ip:514`
4. Save

### Method 4: Application Integration

**Python**:
```python
import socket

def send_syslog(message, host='your-server-ip', port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    syslog_msg = f"<134>1 {message}"
    sock.sendto(syslog_msg.encode(), (host, port))
    sock.close()
```

---

## Using the Web Interface

### 1. Login
- Navigate to `http://your-server-ip:3000`
- Username: `admin` or `user`
- Password: `admin` or `user`

### 2. Dashboard
- **Date Range**: Select time period
- **Statistics**: View total logs, errors, warnings
- **Log Table**: Browse recent logs
- **Search**: Quick search functionality
- **Export**: Download as CSV/JSON

### 3. Logs Page
- Advanced filtering
- Full-text search
- Date range selection
- Export capabilities

### 4. Search Page
- Query builder
- Saved searches
- Advanced filters

### 5. Alerts Page
- Security threat monitoring
- Severity filtering
- Alert management
- Statistics dashboard

### 6. Settings
- User profile
- System preferences
- Configuration

---

## 🔌 API Documentation

### Authentication

```bash
# Get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Use token
curl http://localhost:8000/logs/search \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Key Endpoints

- `POST /auth/login` - Authentication
- `POST /logs/search` - Search logs
- `GET /logs/statistics` - Get statistics
- `GET /logs/threats` - Get threat logs
- `GET /system/info` - System information
- `GET /health` - Health check

**Interactive Docs**: http://localhost:8000/docs

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Services Won't Start

```bash
# Check logs for all services
docker-compose logs

# Check specific service
docker-compose logs frontend
docker-compose logs api

# Restart all services
docker-compose restart

# Complete rebuild (if needed)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 2. Port Already in Use

```bash
# Check which process is using the port
sudo netstat -tulpn | grep 514
sudo netstat -tulpn | grep 3000
sudo netstat -tulpn | grep 8000

# Stop conflicting service (usually rsyslog on port 514)
sudo systemctl stop rsyslog
sudo systemctl disable rsyslog
```

#### 3. Frontend Login Error (405)

If you see "Request failed with status code 405":

```bash
# 1. Check if env-config.js was created correctly
docker-compose exec frontend cat /usr/share/nginx/html/env-config.js

# 2. Verify it contains your server IP (not localhost)
# Should show: REACT_APP_API_URL: "http://YOUR_SERVER_IP:8000"

# 3. If incorrect, update .env and restart
nano .env  # Set correct SERVER_IP
docker-compose restart frontend

# 4. Check frontend logs
docker-compose logs frontend | grep "API URL"
```

#### 4. No Logs Appearing in Dashboard

```bash
# 1. Check receiver service
docker-compose logs receiver

# 2. Send test log
logger -n YOUR_SERVER_IP -P 514 "Test log message"

# 3. Verify Kafka is receiving logs
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic raw-logs --from-beginning --max-messages 5

# 4. Check OpenSearch indices
curl http://localhost:9200/_cat/indices
```

#### 5. CORS Issues

The system uses `API_CORS_ORIGINS=*` by default (allows any origin).

For production with specific domains:
```bash
# Edit .env
nano .env

# Set specific origins
API_CORS_ORIGINS=http://YOUR_SERVER_IP:3000,https://yourdomain.com

# Restart API
docker-compose restart api
```

#### 6. Out of Memory

```bash
# Check container memory usage
docker stats

# Reduce memory limits in .env
nano .env
# Adjust: PROCESSOR_MAX_MEMORY, API_MAX_MEMORY, etc.

# Restart services
docker-compose restart
```

#### 7. Permission Denied Errors

```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh
```

---

## 🔒 Production Deployment

### Security Checklist

Before deploying to production:

#### 1. Change Default Passwords

```bash
# Edit .env file
nano .env

# Update these critical values:
API_SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
POSTGRES_PASSWORD=strong-database-password
OPENSEARCH_PASSWORD=strong-opensearch-password
```

Generate secure random keys:
```bash
# Generate API secret key
openssl rand -hex 32

# Generate JWT secret key
openssl rand -hex 32
```

#### 2. Configure CORS for Production

```bash
# In .env, restrict CORS to your domains only
API_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 3. Enable HTTPS with Reverse Proxy

**Using nginx:**

```bash
# Install nginx
sudo apt install nginx certbot python3-certbot-nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/cybersentinel

# Add configuration:
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/cybersentinel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

#### 4. Configure Firewall

```bash
# Using UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 514/tcp   # Syslog TCP
sudo ufw allow 514/udp   # Syslog UDP
sudo ufw allow 6514/tcp  # Syslog TLS
sudo ufw enable
```

#### 5. Enable TLS for Syslog

```bash
# Generate TLS certificates
cd certs
openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key

# Update .env
nano .env
# Set: RECEIVER_TLS_ENABLED=true

# Restart receiver
docker-compose restart receiver
```

#### 6. Set Up Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/cybersentinel-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup volumes
docker-compose exec postgres pg_dump -U cybersentinel cybersentinel > $BACKUP_DIR/postgres.sql
docker-compose exec opensearch curl -X POST "localhost:9200/_snapshot/my_backup" > $BACKUP_DIR/opensearch.json

# Backup configs
cp .env $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

#### 7. Enable Monitoring

```bash
# Access Prometheus
http://YOUR_SERVER_IP:9090

# Set up alerts for:
# - Service health
# - Disk usage
# - Memory usage
# - Log ingestion rate
```

#### 8. Log Rotation

```bash
# Configure Docker log rotation
sudo nano /etc/docker/daemon.json

# Add:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "5"
  }
}

# Restart Docker
sudo systemctl restart docker
```

### Performance Tuning

#### For High-Volume Deployments (>10K logs/sec)

```bash
# Edit .env
nano .env

# Increase resources:
PROCESSOR_WORKERS=8
PROCESSOR_MAX_MEMORY=4g
KAFKA_PARTITIONS=12
RECEIVER_WORKERS=8
RECEIVER_MAX_MEMORY=2g

# Increase processor replicas in docker-compose.yml:
# replicas: 4

# Restart services
docker-compose up -d --scale processor=4
```

---

## 🗑️ Uninstallation

If you need to completely remove CyberSentinel from your system, we provide an automated uninstallation script.

### ⚠️ WARNING

**The uninstallation process will:**
- ✗ Remove ALL Docker containers
- ✗ Remove ALL Docker volumes (**ALL DATA WILL BE PERMANENTLY DELETED**)
- ✗ Remove ALL Docker images
- ✗ Remove ALL Docker networks
- ✗ Delete generated SSL certificates
- ✗ Delete all logs and alerts

**The uninstallation will NOT remove:**
- ✓ Docker Engine
- ✓ Docker Compose
- ✓ Source code files

### Automated Uninstallation

```bash
# Run the uninstallation script
sudo bash uninstall.sh
```

The script will:
1. Ask for confirmation (you'll need to type "DELETE ALL DATA")
2. Stop all running containers
3. Remove all containers
4. Remove all volumes (permanent data deletion)
5. Remove all Docker images
6. Remove all networks
7. Clean up generated files (certs, logs, configs)
8. Optionally run Docker system prune
9. Verify complete removal

### Manual Uninstallation

If you prefer to uninstall manually:

```bash
# Stop and remove all containers
docker-compose down -v

# Remove all images
docker images | grep cybersentinel | awk '{print $3}' | xargs docker rmi -f

# Remove networks
docker network ls | grep cybersentinel | awk '{print $1}' | xargs docker network rm

# Clean up generated files
rm -rf certs/ logs/ frontend/cybersentinel-ui/build/ frontend/cybersentinel-ui/node_modules/

# (Optional) Prune Docker system
docker system prune -af --volumes
```

### Verification

After uninstallation, verify all components are removed:

```bash
# Check for remaining containers
docker ps -a | grep cybersentinel

# Check for remaining volumes
docker volume ls | grep cybersentinel

# Check for remaining images
docker images | grep cybersentinel

# Check for remaining networks
docker network ls | grep cybersentinel
```

All commands should return empty results.

### Reinstallation

To reinstall CyberSentinel after uninstallation:

```bash
# Automated deployment
sudo bash deploy.sh

# Or manual deployment
docker-compose build
docker-compose up -d
```

---

## 📞 Support

- **Issues**: https://github.com/sujalthakur-03/CyberSentinel-SyslogServer/issues
- **Documentation**: Check `docs/` folder
- **Logs**: `docker-compose logs <service-name>`

---

<div align="center">

⭐ Star this repo if you find it helpful!

</div>
