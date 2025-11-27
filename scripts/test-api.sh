#!/bin/bash
# Test script for API endpoints

set -e

API_URL=${1:-http://localhost:8000}
USERNAME="admin"
PASSWORD="admin"

echo "========================================="
echo "CyberSentinel API Tests"
echo "========================================="
echo ""

# Get authentication token
echo "1. Testing authentication..."
TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")

if [ $? -eq 0 ]; then
    TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    if [ -n "$TOKEN" ]; then
        echo "✓ Authentication successful"
        echo "  Token: ${TOKEN:0:50}..."
    else
        echo "✗ Failed to get token"
        echo "  Response: $TOKEN_RESPONSE"
        exit 1
    fi
else
    echo "✗ Authentication failed"
    exit 1
fi

echo ""

# Test health endpoint
echo "2. Testing health endpoint..."
HEALTH=$(curl -s "${API_URL}/health")
if echo $HEALTH | grep -q "healthy"; then
    echo "✓ Health check passed"
    echo "$HEALTH" | grep -o '"status":"[^"]*'
else
    echo "✗ Health check failed"
fi

echo ""

# Test user info
echo "3. Testing user info endpoint..."
USER_INFO=$(curl -s -H "Authorization: Bearer ${TOKEN}" "${API_URL}/auth/me")
if echo $USER_INFO | grep -q "username"; then
    echo "✓ User info retrieved"
    echo "$USER_INFO" | grep -o '"username":"[^"]*'
else
    echo "✗ Failed to get user info"
fi

echo ""

# Test log search
echo "4. Testing log search endpoint..."
SEARCH_RESULT=$(curl -s -X POST "${API_URL}/logs/search" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"page":1,"page_size":10}')

if echo $SEARCH_RESULT | grep -q "total"; then
    TOTAL=$(echo $SEARCH_RESULT | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "✓ Log search successful"
    echo "  Total logs: $TOTAL"
else
    echo "✗ Log search failed"
fi

echo ""

# Test statistics
echo "5. Testing statistics endpoint..."
STATS=$(curl -s -H "Authorization: Bearer ${TOKEN}" "${API_URL}/logs/statistics")
if echo $STATS | grep -q "total_logs"; then
    TOTAL_LOGS=$(echo $STATS | grep -o '"total_logs":[0-9]*' | cut -d':' -f2)
    echo "✓ Statistics retrieved"
    echo "  Total logs: $TOTAL_LOGS"
else
    echo "✗ Statistics retrieval failed"
fi

echo ""

# Test threat logs
echo "6. Testing threat logs endpoint..."
THREATS=$(curl -s -H "Authorization: Bearer ${TOKEN}" "${API_URL}/logs/threats?page=1&page_size=10")
if echo $THREATS | grep -q "total"; then
    THREAT_COUNT=$(echo $THREATS | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "✓ Threat logs retrieved"
    echo "  Threat logs: $THREAT_COUNT"
else
    echo "✗ Threat logs retrieval failed"
fi

echo ""
echo "========================================="
echo "API Tests Complete!"
echo "========================================="
echo ""
echo "API Documentation: ${API_URL}/docs"
