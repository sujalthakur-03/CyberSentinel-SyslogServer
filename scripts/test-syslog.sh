#!/bin/bash
# Test script to send sample syslog messages

set -e

HOST=${1:-localhost}
PORT=${2:-514}

echo "Sending test syslog messages to ${HOST}:${PORT}..."
echo ""

# Sample syslog messages
MESSAGES=(
    "<134>1 2024-01-15T10:30:00.000Z webserver01 nginx 1234 - - User login successful from 192.168.1.100"
    "<131>1 2024-01-15T10:31:00.000Z firewall01 iptables - - - Connection denied from 10.0.0.50 to 192.168.1.10:22"
    "<28>1 2024-01-15T10:32:00.000Z database01 postgresql 5678 - - Database connection failed: authentication error"
    "<133>1 2024-01-15T10:33:00.000Z appserver01 myapp - - - Processing request for user admin"
    "<19>1 2024-01-15T10:34:00.000Z security01 ids - - - ALERT: Potential SQL injection attempt detected from 203.0.113.50"
    "<18>1 2024-01-15T10:35:00.000Z security01 av - - - WARNING: Malware detected in file upload.exe"
    "<17>1 2024-01-15T10:36:00.000Z security01 auth - - - CRITICAL: Multiple failed authentication attempts from 198.51.100.25"
    "<134>1 2024-01-15T10:37:00.000Z loadbalancer01 haproxy - - - Backend server health check passed"
    "<20>1 2024-01-15T10:38:00.000Z vpn01 openvpn - - - Unauthorized access attempt blocked"
    "<131>1 2024-01-15T10:39:00.000Z webserver02 apache - - - HTTP 500 Internal Server Error on /api/users"
)

# Send messages via UDP
for msg in "${MESSAGES[@]}"; do
    echo "Sending: $msg"
    echo "$msg" | nc -u -w1 ${HOST} ${PORT}
    sleep 0.5
done

echo ""
echo "✓ Sent ${#MESSAGES[@]} test messages to ${HOST}:${PORT}"
echo ""
echo "Check the logs with: make logs-receiver"
echo "View in API: curl -u admin:admin http://localhost:8000/logs/search"
