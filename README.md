# 🛡️ CyberSentinel - Syslog Server

<div align="center">

![CyberSentinel](https://img.shields.io/badge/CyberSentinel-Syslog%20Server-00ff9f?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-00d4ff?style=for-the-badge)
![Status](https://img.shields.io/badge/status-production%20ready-00ff9f?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-ff0080?style=for-the-badge)

**A Production-Ready, Scalable Syslog Monitoring System with Real-time Threat Detection**

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

---

## 🎯 Overview

**CyberSentinel** is a comprehensive, production-ready syslog monitoring and analysis platform designed for enterprise security operations. It provides real-time log collection, processing, threat detection, and beautiful visualization with a modern cyberpunk-themed interface.

### Why CyberSentinel?

- ✅ **Production Ready**: Built with enterprise-grade reliability and scalability
- ✅ **Real-time Processing**: Handle 10,000+ logs/second with Kafka-based architecture
- ✅ **Threat Detection**: Automated security threat identification and alerting
- ✅ **Beautiful UI**: Modern cyberpunk-themed interface with neon aesthetics
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

- **Advanced Threat Detection**
  - 10+ threat indicators (SQL injection, XSS, brute force, etc.)
  - Automated threat scoring
  - Real-time alerting via Email & Slack
  - Pattern-based alert rules

- **Beautiful Web Interface**
  - 🎨 Cyberpunk-themed UI with neon colors
  - 📊 Real-time dashboard with charts
  - 🔍 Advanced search with filters
  - 🚨 Security alerts monitoring
  - 📈 Statistics and analytics
  - 💾 Export to CSV/JSON

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
│         Enrichment • Threat Detection • Normalization            │
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
| 3001 | Grafana | HTTP |
| 9090 | Prometheus | HTTP |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git
cd CyberSentinel-SyslogServer
```

### 2. Initialize Configuration

```bash
make init
```

### 3. Build All Services

```bash
make build
```

### 4. Start the System

```bash
make up
```

### 5. Verify Health

```bash
make health
```

### 6. Access the Interface

- **Web Interface**: http://localhost:3000
- **Login**: `admin` / `admin`
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001

**🎉 CyberSentinel is now running!**

---

## 📚 Detailed Documentation

### Installation

1. **Install Docker and Docker Compose**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   ```

2. **Clone and Configure**:
   ```bash
   git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git
   cd CyberSentinel-SyslogServer
   cp .env.example .env
   nano .env  # Edit configuration if needed
   ```

3. **Build and Start**:
   ```bash
   make build
   make up
   ```

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

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Rebuild
make clean
make build
make up
```

### Port Already in Use

```bash
# Check port usage
sudo netstat -tulpn | grep 514

# Stop conflicting service
sudo systemctl stop rsyslog
```

### No Logs Appearing

```bash
# Check receiver
docker-compose logs receiver

# Send test log
logger -n localhost -P 514 "Test"

# Verify OpenSearch
curl http://localhost:9200/_cat/indices
```

### CORS Issues

Update `.env`:
```env
API_CORS_ORIGINS=http://localhost:3000,http://your-server-ip:3000
```

Rebuild:
```bash
docker-compose build api
docker-compose up -d api
```

---

## 📞 Support

- **Issues**: https://github.com/sujalthakur-03/CyberSentinel-SyslogServer/issues
- **Documentation**: Check `docs/` folder
- **Logs**: `docker-compose logs <service-name>`

---

<div align="center">

**Made with ❤️ by the CyberSentinel Team**

⭐ Star this repo if you find it helpful!

</div>
