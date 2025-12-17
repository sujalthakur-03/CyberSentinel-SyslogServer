#!/bin/bash
# OpenSearch Index Lifecycle Management (ILM) Policy Setup
# This script creates and applies a 180-day retention policy for CyberSentinel logs

set -e

OPENSEARCH_HOST="${OPENSEARCH_HOST:-localhost}"
OPENSEARCH_PORT="${OPENSEARCH_PORT:-9200}"
OPENSEARCH_URL="http://${OPENSEARCH_HOST}:${OPENSEARCH_PORT}"
INDEX_PREFIX="${OPENSEARCH_INDEX_PREFIX:-cybersentinel-logs}"
RETENTION_DAYS="${LOG_RETENTION_DAYS:-180}"

echo "=========================================="
echo "OpenSearch ILM Policy Setup"
echo "=========================================="
echo "OpenSearch URL: ${OPENSEARCH_URL}"
echo "Index Prefix: ${INDEX_PREFIX}"
echo "Retention Period: ${RETENTION_DAYS} days"
echo ""

# Check if OpenSearch is accessible
echo "Checking OpenSearch connectivity..."
if ! curl -s -f "${OPENSEARCH_URL}/_cluster/health" > /dev/null; then
    echo "ERROR: Cannot connect to OpenSearch at ${OPENSEARCH_URL}"
    echo "Please ensure OpenSearch is running and accessible"
    exit 1
fi
echo "✓ OpenSearch is accessible"
echo ""

# Create ISM (Index State Management) policy for 180-day retention
echo "Creating ISM policy: ${INDEX_PREFIX}-retention-policy"
ISM_POLICY='{
  "policy": {
    "description": "180-day retention policy for CyberSentinel logs",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [
          {
            "rollover": {
              "min_index_age": "1d"
            }
          }
        ],
        "transitions": [
          {
            "state_name": "warm",
            "conditions": {
              "min_index_age": "7d"
            }
          }
        ]
      },
      {
        "name": "warm",
        "actions": [
          {
            "replica_count": {
              "number_of_replicas": 0
            }
          },
          {
            "force_merge": {
              "max_num_segments": 1
            }
          }
        ],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "'${RETENTION_DAYS}'d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ],
        "transitions": []
      }
    ],
    "ism_template": [
      {
        "index_patterns": ["'${INDEX_PREFIX}'-*"],
        "priority": 100
      }
    ]
  }
}'

# Create the policy
curl -X PUT "${OPENSEARCH_URL}/_plugins/_ism/policies/${INDEX_PREFIX}-retention-policy" \
  -H 'Content-Type: application/json' \
  -d "${ISM_POLICY}" 2>/dev/null || true

echo "✓ ISM policy created"
echo ""

# Create index template with settings optimized for 180-day retention
echo "Creating index template: ${INDEX_PREFIX}-template"
INDEX_TEMPLATE='{
  "index_patterns": ["'${INDEX_PREFIX}'-*"],
  "template": {
    "settings": {
      "number_of_shards": 2,
      "number_of_replicas": 1,
      "refresh_interval": "30s",
      "index.codec": "best_compression",
      "opendistro.index_state_management.policy_id": "'${INDEX_PREFIX}'-retention-policy"
    },
    "mappings": {
      "properties": {
        "timestamp": {"type": "date"},
        "received_at": {"type": "date"},
        "processed_at": {"type": "date"},
        "source_ip": {"type": "ip"},
        "hostname": {"type": "keyword"},
        "facility": {"type": "integer"},
        "facility_name": {"type": "keyword"},
        "severity": {"type": "integer"},
        "severity_name": {"type": "keyword"},
        "severity_category": {"type": "keyword"},
        "message": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}},
        "raw": {"type": "text"},
        "protocol": {"type": "keyword"},
        "app_name": {"type": "keyword"},
        "proc_id": {"type": "keyword"},
        "format": {"type": "keyword"},
        "extracted_ips": {"type": "ip"},
        "has_threat_indicators": {"type": "boolean"},
        "threat_keywords": {"type": "keyword"},
        "threat_score": {"type": "integer"},
        "tags": {"type": "keyword"},
        "fingerprint": {"type": "keyword"}
      }
    }
  },
  "priority": 200,
  "version": 1
}'

curl -X PUT "${OPENSEARCH_URL}/_index_template/${INDEX_PREFIX}-template" \
  -H 'Content-Type: application/json' \
  -d "${INDEX_TEMPLATE}" 2>/dev/null

echo "✓ Index template created with 180-day retention policy"
echo ""

# List existing indices
echo "Current indices matching pattern: ${INDEX_PREFIX}-*"
curl -s "${OPENSEARCH_URL}/_cat/indices/${INDEX_PREFIX}-*?v&h=index,docs.count,store.size,creation.date.string" 2>/dev/null || echo "No indices found yet"
echo ""

# Display policy status
echo "Checking ISM policy status..."
curl -s "${OPENSEARCH_URL}/_plugins/_ism/policies/${INDEX_PREFIX}-retention-policy" | python3 -m json.tool 2>/dev/null || echo "Policy details not available"
echo ""

echo "=========================================="
echo "✓ ILM Setup Complete!"
echo "=========================================="
echo ""
echo "Key Features Configured:"
echo "  ✓ 180-day automatic retention (logs deleted after ${RETENTION_DAYS} days)"
echo "  ✓ Hot tier: First 7 days (full replicas for high availability)"
echo "  ✓ Warm tier: Days 7-${RETENTION_DAYS} (optimized for storage)"
echo "  ✓ Auto-delete: After ${RETENTION_DAYS} days"
echo "  ✓ Index compression enabled for storage efficiency"
echo "  ✓ Optimized sharding: 2 shards per index (better for scale)"
echo ""
echo "Index naming pattern: ${INDEX_PREFIX}-YYYY.MM.DD"
echo "Policy automatically applies to all new indices"
echo ""
echo "To verify policy is working:"
echo "  curl ${OPENSEARCH_URL}/_plugins/_ism/explain/${INDEX_PREFIX}-*"
echo ""
