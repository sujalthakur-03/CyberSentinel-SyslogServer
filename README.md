# 🛡️ CyberSentinel SyslogServer

<div align="center">

![CyberSentinel Banner](https://img.shields.io/badge/CyberSentinel-Enterprise%20Log%20Management-00ff9f?style=for-the-badge&logo=shield&logoColor=white)

![Version](https://img.shields.io/badge/version-1.0.0-00d4ff?style=for-the-badge)
![Status](https://img.shields.io/badge/status-production%20ready-00ff9f?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-ff0080?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**Enterprise-Grade Centralized Log Management & Security Monitoring Platform**

[✨ Features](#-key-features) • [🚀 Quick Install](#-one-command-installation) • [📚 Documentation](#-documentation) • [🔌 API](#-api-documentation) • [💬 Support](#-support)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [One-Command Installation](#-one-command-installation)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Manual Installation](#-manual-installation)
- [Accessing the Dashboard](#-accessing-the-dashboard)
- [Sending Logs](#-sending-logs)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Production Deployment](#-production-deployment)
- [Troubleshooting](#-troubleshooting)
- [Uninstallation](#-uninstallation)
- [Support](#-support)
- [License](#-license)

---

## 🎯 Overview

**CyberSentinel SyslogServer** is a production-ready, enterprise-grade log management and security monitoring platform built with modern microservices architecture. It provides real-time syslog collection, intelligent processing, threat detection, and beautiful visualization through a cyberpunk-themed web interface.

### Why Choose CyberSentinel?

- ⚡ **High Performance** - Process 10,000+ logs/second with minimal latency
- 🔒 **Security Focused** - Built-in threat detection with 10+ security patterns
- 📊 **Beautiful UI** - Modern cyberpunk-themed React dashboard
- 🐳 **Easy Deployment** - One-command installation with Docker Compose
- 🔍 **Powerful Search** - Full-text search with OpenSearch backend
- 📈 **Real-time Monitoring** - Live statistics and Prometheus metrics
- 🚀 **Scalable** - Horizontal scaling with Kafka and multiple processors
- 🛠️ **Production Ready** - Complete with health checks, logging, and monitoring

---

## ✨ Key Features

### 🔐 **Enterprise Security**

> **Built for Security Operations Centers (SOC)**

- 🚨 **Real-time Threat Detection** - 10+ pre-configured security patterns
- 🔍 **Full-Text Search** - Lightning-fast log queries with OpenSearch
- 📊 **Security Analytics** - Aggregations and statistics for threat hunting
- 🔔 **Smart Alerting** - Email and Slack notifications with deduplication
- 🛡️ **TLS Support** - Encrypted syslog reception on port 6514
- 🔑 **JWT Authentication** - Secure API access with token-based auth

### 📡 **Advanced Log Collection**

> **Multi-Protocol Syslog Ingestion**

- 📥 **UDP/TCP/TLS** - Support for all syslog protocols (RFC 3164 & 5424)
- ⚡ **High Throughput** - 10,000+ messages/second processing capacity
- 🔄 **Auto-Parsing** - Automatic log format detection and normalization
- 🌐 **Universal Support** - Works with routers, firewalls, servers, applications
- 📍 **Multiple Ports** - UDP:514, TCP:514, TLS:6514
- 🎯 **Intelligent Routing** - Kafka-based message queue for reliability

### 💻 **Modern Web Interface**

> **Beautiful Cyberpunk-Themed Dashboard**

- 🎨 **Stunning UI** - Neon-themed, responsive React interface
- 📊 **Live Dashboard** - Real-time statistics and log visualization
- 🔍 **Advanced Search** - Query builder with filters and date ranges
- 📈 **Statistics** - Visual charts for severity, facility, and trends
- 💾 **Export Options** - Download logs in CSV or JSON format
- 🌓 **Dark Theme** - Easy on the eyes for long monitoring sessions

### 🏗️ **Scalable Architecture**

> **Built with Microservices for Maximum Performance**

- 🐳 **Docker Containerized** - All services in isolated containers
- 📦 **Kafka Message Queue** - Reliable log buffering and distribution
- 🔄 **Horizontal Scaling** - Multiple processor replicas for high volume
- 💾 **OpenSearch** - Distributed search and analytics engine
- 🗄️ **PostgreSQL** - User management and configuration storage
- ⚡ **Redis Cache** - Fast deduplication and rate limiting
- 📊 **Prometheus** - Built-in metrics collection and monitoring

### 🚀 **One-Command Installation**

> **Deploy in Minutes, Not Hours**

- 🎯 **Fully Automated** - Single command installation with `install.sh`
- 🔧 **Auto-Configuration** - Automatic IP detection and setup
- 🔐 **Secure by Default** - Generates random passwords and API keys
- ✅ **Health Checks** - Automatic service verification
- 📦 **All-Inclusive** - Installs Docker if needed
- 🌍 **Portable** - Works on any Ubuntu/Linux server

### 🔌 **RESTful API**

> **Complete API for Integration**

- 📖 **OpenAPI/Swagger** - Interactive API documentation
- 🔍 **Search Endpoints** - Powerful log search and filtering
- 📊 **Statistics API** - Aggregations and analytics
- 🔔 **Alert Management** - Programmatic alert access
- 🔑 **Token Auth** - JWT-based authentication
- 🐍 **Python Backend** - FastAPI for high performance

---

## 🚀 One-Command Installation

> **The fastest way to get CyberSentinel running**

### Step 1️⃣: Download CyberSentinel

```bash
# Clone the repository
git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git

# Navigate to the directory
cd CyberSentinel-SyslogServer
```

### Step 2️⃣: Run the Installer

```bash
# Run the automated installation script
sudo bash install.sh
```

### 🎉 That's It!

The installation script will:

✅ **Detect your server IP** (or ask you to provide it)
✅ **Install Docker & Docker Compose** (if not already installed)
✅ **Generate secure passwords** and API keys automatically
✅ **Configure all services** with your server IP
✅ **Build all Docker images** (~10 minutes)
✅ **Start all services** in the background
✅ **Verify health** of all components
✅ **Display access URLs** and credentials

### ⏱️ Installation Time

- **Fresh Server**: ~15 minutes (includes Docker installation)
- **Server with Docker**: ~10 minutes (just builds and starts services)

### 📝 What You'll Get

After installation completes:

```
🌐 Frontend Dashboard:  http://YOUR_SERVER_IP:3000
🔌 API Service:         http://YOUR_SERVER_IP:8000
📊 API Docs:            http://YOUR_SERVER_IP:8000/docs
❤️  Health Check:       http://YOUR_SERVER_IP:8000/health
📈 Prometheus:          http://YOUR_SERVER_IP:9090

Default Login:
  Username: admin
  Password: admin

⚠️  IMPORTANT: Change the default password after first login!
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Network Devices & Servers                     │
│              (Routers • Firewalls • Switches • Servers)             │
└────────────────────────┬────────────────────────────────────────────┘
                         │ Syslog (UDP/TCP/TLS)
                         │ Ports: 514, 6514
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ┌─────────────────────────────────┐                 │
│                  │   SYSLOG RECEIVER SERVICE       │                 │
│                  │   • RFC 3164/5424 Parser        │                 │
│                  │   • 10,000+ msgs/sec            │                 │
│                  │   • UDP:514, TCP:514, TLS:6514  │                 │
│                  └──────────────┬──────────────────┘                 │
└─────────────────────────────────┼──────────────────────────────────┘
                                  │
                         ┌────────▼─────────┐
                         │  KAFKA CLUSTER   │
                         │  Message Queue   │
                         │  LZ4 Compression │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
          ┌─────────▼────────┐        ┌─────────▼────────┐
          │  LOG PROCESSOR   │        │  LOG PROCESSOR   │
          │    (Replica 1)   │        │    (Replica 2)   │
          │  • Parse & Enrich│        │  • Parse & Enrich│
          │  • Threat Detect │        │  • Threat Detect │
          │  • Normalize     │        │  • Normalize     │
          └─────────┬────────┘        └─────────┬────────┘
                    │                            │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │                            │
          ┌─────────▼────────┐        ┌─────────▼────────┐
          │   OPENSEARCH     │        │   ALERTING       │
          │   • Storage      │        │   • Threat Mon   │
          │   • Full-text    │        │   • Email/Slack  │
          │   • Aggregations │        │   • Deduplication│
          └─────────┬────────┘        └──────────────────┘
                    │
          ┌─────────▼────────┐
          │    REST API      │
          │   • FastAPI      │
          │   • JWT Auth     │
          │   • Swagger Docs │
          └─────────┬────────┘
                    │
          ┌─────────▼────────┐
          │  WEB INTERFACE   │
          │  • React UI      │
          │  • Cyberpunk     │
          │  • Real-time     │
          └──────────────────┘

Infrastructure Services:
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │    Redis     │ │  Prometheus  │ │  Zookeeper   │
│  User DB     │ │  Cache/Rate  │ │  Metrics     │ │  Kafka Coord │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📦 Prerequisites

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Ubuntu 20.04+ (or any Linux with Docker support) |
| **CPU** | 4 cores (8+ cores recommended) |
| **RAM** | 8 GB (16+ GB recommended) |
| **Disk Space** | 50 GB free (100+ GB recommended for logs) |
| **Network** | Static IP or dynamic IP with DNS |

### Required Software

The installation script will install these if missing:

- ✅ **Docker** (20.10+)
- ✅ **Docker Compose** (2.0+)
- ✅ **Git** (for cloning the repository)

### Required Ports

| Port | Service | Protocol | Required |
|------|---------|----------|----------|
| **514** | Syslog Receiver | UDP/TCP | Yes |
| **6514** | Syslog TLS | TCP | Optional |
| **3000** | Web Interface | HTTP | Yes |
| **8000** | REST API | HTTP | Yes |
| **9090** | Prometheus | HTTP | Optional |

---

## 🛠️ Manual Installation

If you prefer manual control over the installation process:

### Step 1: Install Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git
cd CyberSentinel-SyslogServer
```

### Step 3: Configure Environment

```bash
# Copy template
cp .env.template .env

# Get your server IP
hostname -I | awk '{print $1}'

# Edit .env file and set SERVER_IP
nano .env
# Set: SERVER_IP=YOUR_ACTUAL_IP
# Set: REACT_APP_API_URL=http://YOUR_ACTUAL_IP:8000
```

### Step 4: Generate Secure Credentials (Optional)

```bash
# Generate API secret key
openssl rand -hex 32

# Generate JWT secret key
openssl rand -hex 32

# Update .env with these values
nano .env
```

### Step 5: Build and Deploy

```bash
# Build all Docker images (takes ~10 minutes)
docker compose build

# Start all services
docker compose up -d

# Wait for services to initialize
sleep 60

# Check service status
docker compose ps
```

### Step 6: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Check all containers
docker compose logs
```

---

## 🌐 Accessing the Dashboard

### 1. Open the Web Interface

Navigate to: **`http://YOUR_SERVER_IP:3000`**

Replace `YOUR_SERVER_IP` with your actual server IP address.

**Examples:**
- `http://192.168.1.100:3000`
- `http://10.0.0.50:3000`

### 2. Login

**Default Credentials:**

```
Username: admin
Password: admin
```

> ⚠️ **SECURITY WARNING**: Change the default password immediately after first login!

### 3. Dashboard Features

Once logged in, you'll have access to:

- 📊 **Dashboard** - Real-time statistics and log overview
- 🔍 **Logs** - Browse and search all collected logs
- 🔎 **Search** - Advanced search with filters
- 🚨 **Alerts** - Security threat monitoring
- ⚙️ **Settings** - Configuration and user management

---

## 📡 Sending Logs

### Configure Your Devices

#### Linux Servers (rsyslog)

```bash
# Edit rsyslog configuration
sudo nano /etc/rsyslog.conf

# Add this line at the end:
*.* @YOUR_SERVER_IP:514

# Restart rsyslog
sudo systemctl restart rsyslog
```

#### Network Devices

**Cisco Router/Switch:**
```cisco
logging host YOUR_SERVER_IP transport udp port 514
logging trap informational
```

**pfSense Firewall:**
1. Navigate to: **Status > System Logs > Settings**
2. Check **"Enable Remote Logging"**
3. Enter: `YOUR_SERVER_IP:514`
4. Click **Save**

**MikroTik Router:**
```mikrotik
/system logging action
add name=remote target=remote remote=YOUR_SERVER_IP:514
```

#### Test Log Sending

```bash
# Send a test log (Linux)
logger -n YOUR_SERVER_IP -P 514 "Test message from $(hostname)"

# Send multiple test logs
for i in {1..100}; do
    logger -n YOUR_SERVER_IP -P 514 "Test log #$i from $(hostname)"
done
```

#### Application Integration

**Python:**
```python
import socket

def send_syslog(message, host='YOUR_SERVER_IP', port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    syslog_msg = f"<134>1 {message}"
    sock.sendto(syslog_msg.encode(), (host, port))
    sock.close()

send_syslog("Application started successfully")
```

**Node.js:**
```javascript
const dgram = require('dgram');

function sendSyslog(message, host = 'YOUR_SERVER_IP', port = 514) {
    const client = dgram.createSocket('udp4');
    const msg = Buffer.from(`<134>1 ${message}`);
    client.send(msg, port, host, (err) => {
        client.close();
    });
}

sendSyslog('Application started successfully');
```

---

## 🔌 API Documentation

### Authentication

```bash
# Login and get token
curl -X POST http://YOUR_SERVER_IP:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Search Logs

```bash
# Search with authentication
curl -X POST http://YOUR_SERVER_IP:8000/logs/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "error",
    "severity": "error",
    "start_time": "2024-01-01T00:00:00Z",
    "end_time": "2024-12-31T23:59:59Z",
    "page": 1,
    "page_size": 100
  }'
```

### Get Statistics

```bash
# Get log statistics for last 24 hours
curl -X GET http://YOUR_SERVER_IP:8000/logs/statistics?hours=24 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Interactive Documentation

Access the full interactive API documentation at:

**`http://YOUR_SERVER_IP:8000/docs`**

Features:
- 📖 Complete API reference
- 🧪 Try endpoints directly in browser
- 📝 Request/response examples
- 🔐 Built-in authentication

---

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Server Configuration
SERVER_IP=YOUR_SERVER_IP                    # Your server's IP address
REACT_APP_API_URL=http://YOUR_SERVER_IP:8000  # Frontend API URL

# Security (CHANGE IN PRODUCTION!)
API_SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
POSTGRES_PASSWORD=your-postgres-password

# CORS Settings
API_CORS_ORIGINS=*                          # Use specific domains in production

# Resource Limits
PROCESSOR_MAX_MEMORY=1g
API_MAX_MEMORY=512m
RECEIVER_MAX_MEMORY=512m
```

### Scaling Configuration

For high-volume deployments (>10,000 logs/sec):

```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Increase processor replicas:
services:
  processor:
    deploy:
      replicas: 4  # Change from 2 to 4

# Update .env with higher resources
PROCESSOR_MAX_MEMORY=2g
PROCESSOR_WORKERS=8
```

---

## 🔒 Production Deployment

### Security Checklist

#### 1. Change Default Credentials

```bash
# Generate secure keys
openssl rand -hex 32  # For API_SECRET_KEY
openssl rand -hex 32  # For JWT_SECRET_KEY

# Update .env
nano .env
```

#### 2. Configure CORS

```bash
# In .env, restrict to your domain
API_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 3. Enable HTTPS

```bash
# Install nginx and certbot
sudo apt install nginx certbot python3-certbot-nginx

# Configure nginx as reverse proxy
sudo nano /etc/nginx/sites-available/cybersentinel

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

#### 4. Configure Firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 514/tcp   # Syslog TCP
sudo ufw allow 514/udp   # Syslog UDP
sudo ufw enable
```

#### 5. Set Up Backups

```bash
# Create daily backup script
cat > /opt/backup-cybersentinel.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
docker compose exec postgres pg_dump -U cybersentinel > $BACKUP_DIR/db.sql
cp .env $BACKUP_DIR/
EOF

chmod +x /opt/backup-cybersentinel.sh

# Schedule with cron
crontab -e
# Add: 0 2 * * * /opt/backup-cybersentinel.sh
```

---

## 🔧 Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check logs
docker compose logs

# Restart services
docker compose restart

# Complete rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### Port 514 Already in Use

```bash
# Stop system rsyslog
sudo systemctl stop rsyslog
sudo systemctl disable rsyslog
```

#### No Logs Appearing

```bash
# Send test log
logger -n YOUR_SERVER_IP -P 514 "Test message"

# Check receiver logs
docker compose logs receiver

# Check Kafka
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic raw-logs --from-beginning --max-messages 5
```

#### Login Issues (405 Error)

```bash
# Verify frontend config
docker compose exec frontend cat /usr/share/nginx/html/env-config.js

# Should show your server IP, not localhost
# If wrong, update .env and restart
nano .env
docker compose restart frontend
```

### Getting Help

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f receiver

# Check service health
curl http://localhost:8000/health
docker compose ps
```

---

## 🗑️ Uninstallation

### Automated Uninstallation

```bash
# Run uninstall script
sudo bash uninstall.sh
```

> ⚠️ **WARNING**: This will delete ALL data permanently!

The script will:
- Stop all containers
- Remove all volumes (data deletion)
- Remove all images
- Clean up generated files
- Verify complete removal

### Manual Uninstallation

```bash
# Stop and remove everything
docker compose down -v

# Remove images
docker images | grep cybersentinel | awk '{print $3}' | xargs docker rmi -f

# Clean up
rm -rf certs/ logs/
```

---

## 📞 Support

### Documentation

- 📖 **Full Documentation**: Check the `docs/` folder
- 🔌 **API Docs**: http://YOUR_SERVER_IP:8000/docs
- 📊 **Architecture**: See [System Architecture](#-system-architecture)

### Getting Help

- 🐛 **Report Issues**: [GitHub Issues](https://github.com/sujalthakur-03/CyberSentinel-SyslogServer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/sujalthakur-03/CyberSentinel-SyslogServer/discussions)
- 📧 **Email**: Create an issue on GitHub

### Useful Commands

```bash
# View logs
docker compose logs -f

# Check status
docker compose ps

# Restart service
docker compose restart <service-name>

# Update to latest version
git pull
docker compose build
docker compose up -d
```

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 CyberSentinel Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙏 Acknowledgments

Built with these amazing open-source technologies:

- **Docker** - Containerization platform
- **Apache Kafka** - Distributed streaming platform
- **OpenSearch** - Search and analytics engine
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **PostgreSQL** - Relational database
- **Redis** - In-memory data store
- **Prometheus** - Monitoring and alerting

---

## 🌟 Star History

If you find CyberSentinel useful, please consider giving it a ⭐ on GitHub!

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=sujalthakur-03/CyberSentinel-SyslogServer&type=Date)](https://star-history.com/#sujalthakur-03/CyberSentinel-SyslogServer&Date)

---

[⬆ Back to Top](#️-cybersentinel-syslogserver)

</div>
