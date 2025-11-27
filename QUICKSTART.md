# Quick Start Guide - CyberSentinel SyslogServer

Get up and running in 5 minutes!

## Prerequisites

- Docker 24.0+
- Docker Compose 2.0+
- 8 GB RAM minimum
- 50 GB disk space

## Step-by-Step Installation

### 1. Initialize

```bash
cd /home/sujal/SyslogServer
make init
```

This will:
- Create `.env` file from template
- Generate self-signed TLS certificates

### 2. Configure (Optional)

Edit `.env` and update:

```bash
# Required: Change these!
API_SECRET_KEY=YOUR_RANDOM_SECRET_HERE
JWT_SECRET_KEY=YOUR_RANDOM_JWT_SECRET_HERE
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE

# Optional: Email alerts
ALERTING_SMTP_USER=your-email@gmail.com
ALERTING_SMTP_PASSWORD=your-app-password
ALERTING_TO_EMAILS=admin@example.com
```

### 3. Build and Start

```bash
# Build all images (takes 5-10 minutes)
make build

# Start all services
make up
```

Wait for services to be healthy (~2 minutes).

### 4. Verify Installation

```bash
# Check health
make health

# You should see:
# ✓ api (8000): HEALTHY
# ✓ opensearch (9200): HEALTHY
# ✓ receiver (9100): HEALTHY
# ✓ processor (9101): HEALTHY
# ✓ alerting (9103): HEALTHY
# ✓ redis (6379): HEALTHY
# ✓ kafka (9092): HEALTHY
```

### 5. Send Test Logs

```bash
make test-receiver
```

### 6. Access Services

Open in your browser:
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### 7. Test API

```bash
make test-api
```

## Next Steps

### Configure Your Devices

Point your syslog sources to your server:

**For rsyslog** (add to `/etc/rsyslog.d/50-cybersentinel.conf`):
```
*.* @<your-server-ip>:514
```

**For syslog-ng**:
```
destination d_cybersentinel {
    network("<your-server-ip>" port(514) transport("udp"));
};
log { source(s_src); destination(d_cybersentinel); };
```

**For network devices**:
- Server: `<your-server-ip>`
- Port: `514`
- Protocol: `UDP` or `TCP`

### View Logs in API

```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r .access_token)

# Search logs
curl -s -X POST http://localhost:8000/logs/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"page":1,"page_size":10}' | jq
```

### Enable Email Alerts

1. Update `.env`:
```bash
ALERTING_SMTP_HOST=smtp.gmail.com
ALERTING_SMTP_PORT=587
ALERTING_SMTP_USER=your-email@gmail.com
ALERTING_SMTP_PASSWORD=your-gmail-app-password
ALERTING_TO_EMAILS=admin@example.com
```

2. Restart alerting service:
```bash
docker-compose restart alerting
```

### Enable Slack Alerts

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Update `.env`:
```bash
ALERTING_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

3. Restart alerting service:
```bash
docker-compose restart alerting
```

## Common Commands

```bash
make up              # Start all services
make down            # Stop all services
make logs            # View all logs
make health          # Check service health
make test-receiver   # Send test syslog messages
make test-api        # Test API endpoints
make dashboard       # Open Grafana
make api-docs        # Open API documentation
```

## Troubleshooting

### Services won't start
```bash
# Check what's running
make ps

# View logs
make logs

# Try rebuilding
make rebuild
```

### Can't receive logs
```bash
# Check if ports are open
sudo netstat -tuln | grep 514

# Test UDP connectivity
echo "test" | nc -u <server-ip> 514

# View receiver logs
make logs-receiver
```

### API authentication fails
```bash
# Verify credentials in .env match what you're using
# Default is admin/admin

# Check API logs
make logs-api
```

### Out of disk space
```bash
# Check disk usage
df -h

# Clean old data (WARNING: removes all data!)
make clean-data
```

## Need Help?

- Full documentation: See README.md
- Check logs: `make logs`
- Health status: `make health`
- Report issues: GitHub Issues

## Production Checklist

Before going to production:

- [ ] Change all default passwords in `.env`
- [ ] Generate proper SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Enable TLS for syslog (`RECEIVER_TLS_ENABLED=true`)
- [ ] Configure log retention policies
- [ ] Set up monitoring alerts in Grafana
- [ ] Test disaster recovery
- [ ] Review alert rules and recipients
- [ ] Scale processor workers if needed
- [ ] Document your configuration

## System Status

Check if everything is running:

```bash
docker-compose ps
```

Expected output:
```
NAME                          STATUS
cybersentinel-alerting        Up (healthy)
cybersentinel-api             Up (healthy)
cybersentinel-grafana         Up
cybersentinel-kafka           Up (healthy)
cybersentinel-opensearch      Up (healthy)
cybersentinel-postgres        Up (healthy)
cybersentinel-processor       Up (healthy)
cybersentinel-prometheus      Up
cybersentinel-receiver        Up (healthy)
cybersentinel-redis           Up (healthy)
cybersentinel-zookeeper       Up (healthy)
```

Congratulations! Your CyberSentinel SyslogServer is ready! 🎉
