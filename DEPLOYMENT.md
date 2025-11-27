# Deployment Guide - CyberSentinel SyslogServer

Comprehensive deployment guide for various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [High Availability Setup](#high-availability-setup)
- [Performance Tuning](#performance-tuning)
- [Security Hardening](#security-hardening)
- [Monitoring Setup](#monitoring-setup)
- [Backup and Recovery](#backup-and-recovery)

## Prerequisites

### System Requirements

**Minimum (Testing/Development)**:
- 4 CPU cores
- 8 GB RAM
- 50 GB disk (SSD recommended)

**Recommended (Production)**:
- 8+ CPU cores
- 16+ GB RAM
- 500+ GB SSD
- 1 Gbps network

### Software Requirements

```bash
# Check Docker version (24.0+)
docker --version

# Check Docker Compose version (2.0+)
docker-compose --version

# Check available disk space (50GB+)
df -h

# Check available memory (8GB+)
free -h
```

## Installation Methods

### Method 1: Standard Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/SyslogServer.git
cd SyslogServer

# Initialize
make init

# Configure
vim .env  # Update configuration

# Build and start
make build
make up

# Verify
make health
```

### Method 2: Systemd Service

```bash
# Copy project to /opt
sudo cp -r SyslogServer /opt/cybersentinel
cd /opt/cybersentinel

# Initialize
sudo make init

# Configure
sudo vim .env

# Build
sudo make build

# Install systemd service
sudo cp configs/cybersentinel.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable cybersentinel
sudo systemctl start cybersentinel

# Check status
sudo systemctl status cybersentinel
```

### Method 3: Manual Docker Commands

```bash
# Create network
docker network create cybersentinel-network

# Start infrastructure services
docker-compose up -d zookeeper kafka opensearch redis postgres

# Wait for infrastructure to be ready
sleep 60

# Start application services
docker-compose up -d receiver processor api alerting

# Start monitoring
docker-compose up -d prometheus grafana
```

## Production Deployment

### 1. Pre-Deployment Checklist

```bash
# Security
□ Changed all default passwords
□ Generated unique API_SECRET_KEY
□ Generated unique JWT_SECRET_KEY
□ Created proper SSL/TLS certificates
□ Configured firewall rules
□ Reviewed user permissions

# Configuration
□ Set appropriate resource limits
□ Configured log retention policies
□ Set up email/Slack alerting
□ Reviewed alert rules
□ Configured backup schedule

# Infrastructure
□ Sufficient disk space allocated
□ Network connectivity verified
□ DNS resolution working
□ NTP synchronized
□ Monitoring configured
```

### 2. Generate Production Secrets

```bash
# Generate API secret
export API_SECRET_KEY=$(openssl rand -hex 32)

# Generate JWT secret
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Generate database password
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Update .env file
cat >> .env << EOF
API_SECRET_KEY=${API_SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF
```

### 3. SSL/TLS Configuration

```bash
# For production, use proper certificates
# Option 1: Let's Encrypt (if using reverse proxy)
sudo certbot certonly --standalone -d syslog.yourdomain.com

# Option 2: Corporate CA certificates
cp /path/to/corporate/cert.crt certs/server.crt
cp /path/to/corporate/key.key certs/server.key

# Option 3: Self-signed (testing only)
make setup-certs

# Update .env
echo "RECEIVER_TLS_ENABLED=true" >> .env
```

### 4. Resource Configuration

Edit `.env` for production resources:

```bash
# Application resources
RECEIVER_MAX_MEMORY=1g
PROCESSOR_MAX_MEMORY=2g
API_MAX_MEMORY=1g
ALERTING_MAX_MEMORY=512m

# OpenSearch heap (50% of container memory)
OPENSEARCH_JAVA_OPTS=-Xms4g -Xmx4g

# Processor workers (based on CPU cores)
PROCESSOR_WORKERS=8

# Kafka settings
KAFKA_PARTITIONS=12
KAFKA_RETENTION_MS=604800000  # 7 days
```

### 5. Start Production Deployment

```bash
# Build with production settings
docker-compose build --no-cache

# Start services
docker-compose up -d

# Monitor startup
docker-compose logs -f

# Wait for all services to be healthy
watch -n 5 'docker-compose ps'

# Verify health
make health
```

### 6. Post-Deployment Verification

```bash
# Test syslog reception
make test-receiver

# Test API
make test-api

# Check metrics
curl http://localhost:9090/targets

# Verify alerting
docker-compose logs alerting | grep "alert_rules_loaded"

# Check OpenSearch indices
curl http://localhost:9200/_cat/indices?v
```

## Cloud Deployment

### AWS Deployment

#### Using EC2

```bash
# Launch EC2 instance
# - Instance type: m5.xlarge or larger
# - Storage: 500 GB GP3 SSD
# - Security group: Ports 514 (UDP/TCP), 6514, 8000, 3001, 9090

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy CyberSentinel
git clone <repo> && cd SyslogServer
make init
# Edit .env
make build && make up
```

#### Using ECS Fargate

Convert `docker-compose.yml` to ECS task definitions or use Docker Compose ECS integration.

### Azure Deployment

#### Using Azure VM

```bash
# Create VM
az vm create \
  --resource-group cybersentinel-rg \
  --name cybersentinel-vm \
  --image UbuntuLTS \
  --size Standard_D4s_v3 \
  --admin-username azureuser

# Open ports
az vm open-port --port 514 --resource-group cybersentinel-rg --name cybersentinel-vm
az vm open-port --port 8000 --resource-group cybersentinel-rg --name cybersentinel-vm

# SSH and deploy
ssh azureuser@<public-ip>
# Follow standard deployment steps
```

### GCP Deployment

```bash
# Create instance
gcloud compute instances create cybersentinel \
  --machine-type n1-standard-4 \
  --image-family ubuntu-2004-lts \
  --image-project ubuntu-os-cloud \
  --boot-disk-size 500GB

# Configure firewall
gcloud compute firewall-rules create allow-syslog \
  --allow udp:514,tcp:514,tcp:6514,tcp:8000,tcp:3001

# SSH and deploy
gcloud compute ssh cybersentinel
# Follow standard deployment steps
```

## High Availability Setup

### Multi-Node Kafka Cluster

Update `docker-compose.yml`:

```yaml
services:
  kafka-1:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 1
      # ... other configs

  kafka-2:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 2
      # ... other configs

  kafka-3:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 3
      # ... other configs
```

### OpenSearch Cluster

```yaml
services:
  opensearch-node1:
    image: opensearchproject/opensearch:2.11.0
    environment:
      - cluster.name=cybersentinel-cluster
      - node.name=opensearch-node1
      - discovery.seed_hosts=opensearch-node2,opensearch-node3
      - cluster.initial_master_nodes=opensearch-node1,opensearch-node2,opensearch-node3

  opensearch-node2:
    # Similar configuration

  opensearch-node3:
    # Similar configuration
```

### Load Balancer for API

Use nginx or HAProxy:

```nginx
upstream api_backend {
    least_conn;
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://api_backend;
    }
}
```

## Performance Tuning

### High Volume (>50k logs/sec)

```bash
# Increase processor replicas
docker-compose up -d --scale processor=16

# Increase Kafka partitions
KAFKA_PARTITIONS=24

# Tune OpenSearch
OPENSEARCH_JAVA_OPTS=-Xms16g -Xmx16g
OPENSEARCH_BULK_SIZE=2000

# Increase receiver workers
RECEIVER_WORKERS=8
```

### Low Latency

```bash
# Reduce batch sizes
OPENSEARCH_BULK_SIZE=100
PROCESSOR_BATCH_SIZE=50

# Reduce linger time
KAFKA_LINGER_MS=1
```

### Resource Optimization

```bash
# Monitor resource usage
make stats

# Adjust based on bottlenecks
# CPU bound: Increase workers
# Memory bound: Reduce batch sizes
# Disk bound: Use faster storage, reduce retention
```

## Security Hardening

### 1. Network Security

```bash
# Use firewall (ufw example)
sudo ufw allow 514/udp
sudo ufw allow 514/tcp
sudo ufw allow 6514/tcp
sudo ufw allow from <trusted-ip> to any port 8000
sudo ufw enable

# Or iptables
sudo iptables -A INPUT -p udp --dport 514 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 514 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 6514 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -s <trusted-ip> -j ACCEPT
```

### 2. Use Reverse Proxy

```nginx
# nginx configuration
server {
    listen 443 ssl http2;
    server_name api.cybersentinel.local;

    ssl_certificate /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Enable Authentication

All API endpoints require JWT tokens. Configure users in API service.

### 4. Secrets Management

Use Docker secrets or external secret managers:

```yaml
services:
  api:
    secrets:
      - api_secret_key
      - jwt_secret_key

secrets:
  api_secret_key:
    external: true
  jwt_secret_key:
    external: true
```

## Monitoring Setup

### Grafana Dashboards

1. Access Grafana: http://localhost:3001
2. Login with admin/admin
3. Add Prometheus data source
4. Import dashboards from `configs/grafana/dashboards/`

### Alert Rules

Configure in Grafana or Prometheus:

```yaml
# prometheus/alerts.yml
groups:
  - name: cybersentinel
    rules:
      - alert: HighErrorRate
        expr: rate(syslog_messages_received_total{status="failed"}[5m]) > 100
        annotations:
          summary: "High syslog error rate"
```

## Backup and Recovery

### Automated Backups

```bash
# Create cron job
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /opt/cybersentinel && ./scripts/backup.sh /backups/daily

# Weekly full backup
0 2 * * 0 cd /opt/cybersentinel && ./scripts/backup.sh /backups/weekly
```

### Manual Backup

```bash
make backup
```

### Restore

```bash
./scripts/restore.sh /backups/cybersentinel_backup_20240115_020000
```

### Disaster Recovery

1. Maintain off-site backups
2. Document restore procedure
3. Test recovery regularly
4. Keep configuration in version control
5. Document custom configurations

## Maintenance

### Updates

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
make rebuild
```

### Log Rotation

```bash
# Configure Docker logging
# Add to docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Index Management

```bash
# Delete old indices
curl -X DELETE "localhost:9200/cybersentinel-logs-2024.01.01"

# Or use curator (install separately)
curator_cli --host localhost delete-indices \
  --filter_list '[{"filtertype":"age","source":"name","direction":"older","timestring":"%Y.%m.%d","unit":"days","unit_count":30}]'
```

## Troubleshooting

See main README.md for common issues and solutions.

---

For additional help:
- Documentation: README.md
- Quick Start: QUICKSTART.md
- Assumptions: ASSUMPTIONS.md
