#!/bin/bash
# Health check script for all services

set -e

SERVICES=(
    "receiver:9100"
    "processor:9101"
    "api:8000"
    "alerting:9103"
    "opensearch:9200"
    "redis:6379"
    "kafka:9092"
)

echo "========================================="
echo "CyberSentinel Health Check"
echo "========================================="
echo ""

check_http() {
    local service=$1
    local port=$2
    local path=${3:-"/"}

    if docker exec cybersentinel-${service} curl -sf http://localhost:${port}${path} > /dev/null 2>&1; then
        echo "✓ ${service} (${port}): HEALTHY"
        return 0
    else
        echo "✗ ${service} (${port}): UNHEALTHY"
        return 1
    fi
}

check_tcp() {
    local service=$1
    local port=$2

    if docker exec cybersentinel-${service} nc -z localhost ${port} > /dev/null 2>&1; then
        echo "✓ ${service} (${port}): HEALTHY"
        return 0
    else
        echo "✗ ${service} (${port}): UNHEALTHY"
        return 1
    fi
}

# Check HTTP services
check_http "api" "8000" "/health"
check_http "opensearch" "9200" "/_cluster/health"

# Check TCP/metrics endpoints
check_tcp "receiver" "9100"
check_tcp "processor" "9101"
check_tcp "alerting" "9103"
check_tcp "redis" "6379"

# Check Kafka
if docker exec cybersentinel-kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "✓ kafka (9092): HEALTHY"
else
    echo "✗ kafka (9092): UNHEALTHY"
fi

echo ""
echo "========================================="
echo "Health check complete!"
echo "========================================="
