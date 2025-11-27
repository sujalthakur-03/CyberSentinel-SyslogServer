#!/bin/bash
# Restore script for CyberSentinel data volumes

set -e

BACKUP_PATH="${1}"

if [ -z "$BACKUP_PATH" ] || [ ! -d "$BACKUP_PATH" ]; then
    echo "Usage: $0 <backup_directory>"
    echo "Example: $0 ./backups/cybersentinel_backup_20240115_103000"
    exit 1
fi

echo "========================================="
echo "CyberSentinel Restore"
echo "========================================="
echo ""
echo "WARNING: This will overwrite existing data!"
echo "Backup location: ${BACKUP_PATH}"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

# Stop services
echo ""
echo "Stopping services..."
docker-compose down

# List of volumes to restore
VOLUMES=(
    "opensearch-data"
    "kafka-data"
    "postgres-data"
    "redis-data"
    "prometheus-data"
    "grafana-data"
)

echo ""
echo "Starting restore..."
echo ""

for volume in "${VOLUMES[@]}"; do
    BACKUP_FILE="${BACKUP_PATH}/${volume}.tar.gz"

    if [ ! -f "$BACKUP_FILE" ]; then
        echo "⚠ Skipping ${volume} (backup file not found)"
        continue
    fi

    echo "Restoring volume: ${volume}..."

    # Remove existing volume
    docker volume rm cybersentinel_${volume} 2>/dev/null || true

    # Create new volume
    docker volume create cybersentinel_${volume}

    # Restore data
    docker run --rm \
        -v cybersentinel_${volume}:/target \
        -v "$(pwd)/${BACKUP_PATH}:/backup:ro" \
        alpine \
        tar xzf /backup/${volume}.tar.gz -C /target

    if [ $? -eq 0 ]; then
        echo "✓ ${volume} restored"
    else
        echo "✗ Failed to restore ${volume}"
    fi
done

echo ""
echo "========================================="
echo "Restore Complete!"
echo "========================================="
echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Services started. Use 'make health' to check status."
