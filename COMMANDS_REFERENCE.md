# CyberSentinel SyslogServer - Commands Reference

Quick reference for all commands and operations.

## Getting Started

```bash
# Navigate to project
cd /home/sujal/SyslogServer

# Initialize (first time only)
make init

# Review and edit configuration
vim .env

# Build all services
make build

# Start all services
make up

# Check health
make health
```

## Service Management

### Start/Stop Services

```bash
# Start all services
make up
docker-compose up -d

# Stop all services
make down
docker-compose down

# Restart all services
make restart
docker-compose restart

# Stop without removing containers
make stop
docker-compose stop

# Start existing containers
make start
docker-compose start

# Rebuild and restart
make rebuild
docker-compose up -d --build
```

### Individual Service Control

```bash
# Restart specific service
docker-compose restart receiver
docker-compose restart processor
docker-compose restart api
docker-compose restart alerting

# View service status
make ps
docker-compose ps

# Scale processor
make scale-processor REPLICAS=4
docker-compose up -d --scale processor=4
```

## Logs & Monitoring

### View Logs

```bash
# All services
make logs
docker-compose logs -f

# Specific service
make logs-receiver
make logs-processor
make logs-api
make logs-alerting

# Or directly
docker-compose logs -f receiver
docker-compose logs -f processor
docker-compose logs -f api
docker-compose logs -f alerting

# Last N lines
docker-compose logs --tail=100 receiver

# Since timestamp
docker-compose logs --since 2024-01-15T10:00:00 api
```

### Health Checks

```bash
# All services
make health
./scripts/health-check.sh

# Individual checks
curl http://localhost:8000/health
curl http://localhost:9200/_cluster/health
docker exec cybersentinel-redis redis-cli ping
docker exec cybersentinel-kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### Monitoring

```bash
# Open Prometheus
make metrics
xdg-open http://localhost:9090

# Open Grafana
make dashboard
xdg-open http://localhost:3001

# View resource usage
make stats
docker stats --no-stream

# Continuous monitoring
docker stats
```

## Testing

### Send Test Logs

```bash
# Send sample syslog messages
make test-receiver
./scripts/test-syslog.sh

# Send to specific host/port
./scripts/test-syslog.sh 192.168.1.100 514

# Manual test
echo "<134>1 2024-01-15T10:30:00Z test app - - - Test message" | nc -u localhost 514
```

### Test API

```bash
# Run API tests
make test-api
./scripts/test-api.sh

# Test specific endpoint
./scripts/test-api.sh http://192.168.1.100:8000
```

## API Operations

### Authentication

```bash
# Get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Save token
export TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r .access_token)

# Get user info
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/me
```

### Search Logs

```bash
# Search all logs
curl -X POST http://localhost:8000/logs/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"page":1,"page_size":100}'

# Search with filters
curl -X POST http://localhost:8000/logs/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "error",
    "severity": ["error", "critical"],
    "hostname": "webserver01",
    "page": 1,
    "page_size": 50
  }'

# Search by time range
curl -X POST http://localhost:8000/logs/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2024-01-15T00:00:00Z",
    "end_time": "2024-01-15T23:59:59Z",
    "page": 1,
    "page_size": 100
  }'
```

### Get Statistics

```bash
# Get statistics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/logs/statistics

# Statistics for time range
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/logs/statistics?start_time=2024-01-15T00:00:00Z&end_time=2024-01-15T23:59:59Z"
```

### Get Threat Logs

```bash
# Get threat logs
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/logs/threats?page=1&page_size=100"
```

## OpenSearch Operations

### Index Management

```bash
# List indices
curl http://localhost:9200/_cat/indices?v

# Get index info
curl http://localhost:9200/cybersentinel-logs-*/_stats?pretty

# Delete old index
curl -X DELETE http://localhost:9200/cybersentinel-logs-2024.01.01

# Delete indices older than 30 days
curl -X DELETE "http://localhost:9200/cybersentinel-logs-$(date -d '30 days ago' +%Y.%m.%d)"
```

### Cluster Operations

```bash
# Cluster health
curl http://localhost:9200/_cluster/health?pretty

# Node stats
curl http://localhost:9200/_nodes/stats?pretty

# Cluster settings
curl http://localhost:9200/_cluster/settings?pretty
```

### Direct Queries

```bash
# Count all logs
curl http://localhost:9200/cybersentinel-logs-*/_count?pretty

# Search logs
curl -X POST http://localhost:9200/cybersentinel-logs-*/_search?pretty \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match": {
        "message": "error"
      }
    },
    "size": 10
  }'

# Aggregation by severity
curl -X POST http://localhost:9200/cybersentinel-logs-*/_search?pretty \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "aggs": {
      "by_severity": {
        "terms": {
          "field": "severity_name.keyword"
        }
      }
    }
  }'
```

## Kafka Operations

### Topic Management

```bash
# List topics
docker exec cybersentinel-kafka kafka-topics \
  --bootstrap-server localhost:9092 --list

# Describe topic
docker exec cybersentinel-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe --topic raw-logs

# Create topic
docker exec cybersentinel-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic test-topic \
  --partitions 3 --replication-factor 1

# Delete topic
docker exec cybersentinel-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete --topic test-topic
```

### Consumer Groups

```bash
# List consumer groups
docker exec cybersentinel-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 --list

# Describe consumer group
docker exec cybersentinel-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group log-processor-group

# Reset consumer group offset
docker exec cybersentinel-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group log-processor-group \
  --reset-offsets --to-earliest \
  --topic raw-logs --execute
```

### Message Operations

```bash
# Consume messages
docker exec -it cybersentinel-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic raw-logs --from-beginning

# Produce test message
docker exec -it cybersentinel-kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic raw-logs

# Count messages in topic
docker exec cybersentinel-kafka kafka-run-class \
  kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic raw-logs
```

## Redis Operations

```bash
# Connect to Redis
docker exec -it cybersentinel-redis redis-cli

# Check keys
docker exec cybersentinel-redis redis-cli KEYS '*'

# Get value
docker exec cybersentinel-redis redis-cli GET 'alert:critical_severity:abc123'

# Flush all (WARNING: deletes all data)
docker exec cybersentinel-redis redis-cli FLUSHALL

# Get info
docker exec cybersentinel-redis redis-cli INFO

# Monitor commands
docker exec cybersentinel-redis redis-cli MONITOR
```

## PostgreSQL Operations

```bash
# Connect to PostgreSQL
docker exec -it cybersentinel-postgres psql -U cybersentinel

# List databases
docker exec cybersentinel-postgres psql -U cybersentinel -c '\l'

# List tables
docker exec cybersentinel-postgres psql -U cybersentinel -d cybersentinel -c '\dt'

# Query users
docker exec cybersentinel-postgres psql -U cybersentinel -d cybersentinel \
  -c 'SELECT * FROM users;'

# Backup database
docker exec cybersentinel-postgres pg_dump -U cybersentinel cybersentinel > backup.sql

# Restore database
cat backup.sql | docker exec -i cybersentinel-postgres psql -U cybersentinel cybersentinel
```

## Backup & Recovery

### Backup

```bash
# Backup all data
make backup
./scripts/backup.sh

# Backup to specific location
./scripts/backup.sh /path/to/backups

# Manual volume backup
docker run --rm \
  -v cybersentinel_opensearch-data:/source:ro \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/opensearch-data.tar.gz -C /source .
```

### Restore

```bash
# Restore from backup
make restore
./scripts/restore.sh /path/to/backup/directory

# Restore specific volume
docker run --rm \
  -v cybersentinel_opensearch-data:/target \
  -v $(pwd)/backup:/backup:ro \
  alpine tar xzf /backup/opensearch-data.tar.gz -C /target
```

## Security Operations

### Generate Certificates

```bash
# Generate TLS certificates
make setup-certs
./scripts/generate-certs.sh

# Generate with custom parameters
openssl req -newkey rsa:2048 -nodes \
  -keyout certs/server.key \
  -x509 -days 365 \
  -out certs/server.crt \
  -subj "/C=US/ST=State/L=City/O=Org/CN=syslog.example.com"
```

### Change Passwords

```bash
# Edit .env file
vim .env

# Update these values:
# POSTGRES_PASSWORD=new_password
# API_SECRET_KEY=new_secret_key
# JWT_SECRET_KEY=new_jwt_secret

# Restart services
make restart
```

### User Management

```bash
# Add user via API (requires admin token)
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password",
    "email": "user@example.com",
    "scopes": ["read"]
  }'
```

## Cleanup Operations

### Clean Logs

```bash
# View log files
docker-compose logs --tail=0 2>&1 | wc -l

# Clear specific service logs
docker logs cybersentinel-receiver --tail 0 > /dev/null

# Configure log rotation in docker-compose.yml
# logging:
#   driver: "json-file"
#   options:
#     max-size: "10m"
#     max-file: "3"
```

### Clean Data

```bash
# Remove all data (WARNING: destructive!)
make clean-data

# Remove everything including images
make clean

# Remove specific volume
docker volume rm cybersentinel_opensearch-data

# Prune unused resources
docker system prune -a
```

## Troubleshooting Commands

### Service Issues

```bash
# Check service status
docker-compose ps

# Inspect service
docker inspect cybersentinel-receiver

# Check service logs for errors
docker-compose logs receiver | grep -i error

# Restart problematic service
docker-compose restart receiver

# Rebuild service
docker-compose up -d --build receiver
```

### Network Issues

```bash
# Test port connectivity
nc -zv localhost 514
nc -zu localhost 514

# Check listening ports
sudo netstat -tuln | grep 514
sudo ss -tuln | grep 514

# Test syslog sending
logger -n localhost -P 514 "Test message"

# Check firewall
sudo ufw status
sudo iptables -L -n
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Check disk usage
df -h
docker system df

# Check container logs size
du -sh /var/lib/docker/containers/*/*-json.log

# Check service metrics
curl http://localhost:9100/metrics
curl http://localhost:9101/metrics
curl http://localhost:8000/metrics
curl http://localhost:9103/metrics
```

### Data Issues

```bash
# Check Kafka lag
docker exec cybersentinel-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group log-processor-group

# Check OpenSearch indices size
curl http://localhost:9200/_cat/indices?v&h=index,docs.count,store.size

# Check Redis memory
docker exec cybersentinel-redis redis-cli INFO memory
```

## Development Commands

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Run tests
make test
cd services/receiver && pytest
cd services/processor && pytest
cd services/api && pytest
cd services/alerting && pytest
```

### Development Mode

```bash
# Run in development mode (if dev compose exists)
make dev

# View real-time logs
make logs
```

## Configuration Commands

### View Configuration

```bash
# View environment variables
cat .env

# View docker-compose configuration
docker-compose config

# Validate docker-compose file
docker-compose config --quiet && echo "Valid" || echo "Invalid"
```

### Update Configuration

```bash
# Edit configuration
vim .env

# Apply changes (restart required)
make restart

# Or reload specific service
docker-compose up -d --force-recreate api
```

## Useful One-Liners

```bash
# Count logs in last hour
curl -X POST http://localhost:9200/cybersentinel-logs-*/_count?pretty \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "range": {
        "received_at": {
          "gte": "now-1h"
        }
      }
    }
  }'

# Get top 10 hosts by log count
curl -X POST http://localhost:9200/cybersentinel-logs-*/_search?pretty \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "aggs": {
      "top_hosts": {
        "terms": {
          "field": "hostname.keyword",
          "size": 10
        }
      }
    }
  }'

# Check all service health in one command
for service in receiver processor api alerting opensearch redis kafka; do
  echo -n "$service: "
  docker inspect cybersentinel-$service --format '{{.State.Health.Status}}' 2>/dev/null || echo "no health check"
done

# Tail all service logs
docker-compose logs -f --tail=10 receiver processor api alerting

# Quick restart of application services only
docker-compose restart receiver processor api alerting
```

## Emergency Commands

### Service Recovery

```bash
# Stop all services
docker-compose down

# Remove containers but keep data
docker-compose rm -f

# Rebuild and start
docker-compose up -d --build

# Check health
make health
```

### Data Recovery

```bash
# Restore from latest backup
./scripts/restore.sh $(ls -td backups/* | head -1)

# Restart services
make up
```

### Full Reset

```bash
# WARNING: This removes everything!
make clean
make init
make build
make up
```

## Systemd Service Commands

If installed as systemd service:

```bash
# Start service
sudo systemctl start cybersentinel

# Stop service
sudo systemctl stop cybersentinel

# Restart service
sudo systemctl restart cybersentinel

# Enable at boot
sudo systemctl enable cybersentinel

# Disable at boot
sudo systemctl disable cybersentinel

# Check status
sudo systemctl status cybersentinel

# View logs
sudo journalctl -u cybersentinel -f
```

---

## Quick Reference Card

```
ESSENTIAL COMMANDS
==================
make up              - Start all services
make down            - Stop all services
make health          - Check service health
make logs            - View all logs
make test-receiver   - Send test syslog
make test-api        - Test API
make backup          - Backup data
make help            - Show all commands

SERVICE URLS
============
API Docs:    http://localhost:8000/docs
Grafana:     http://localhost:3001
Prometheus:  http://localhost:9090
OpenSearch:  http://localhost:9200

DEFAULT CREDENTIALS
===================
Admin:       admin / admin
User:        user / user
Grafana:     admin / admin

SYSLOG PORTS
============
UDP:         514
TCP:         514
TLS:         6514
```

---

For more detailed information, see:
- README.md - Complete documentation
- QUICKSTART.md - Getting started guide
- DEPLOYMENT.md - Production deployment
- ARCHITECTURE.md - System architecture
