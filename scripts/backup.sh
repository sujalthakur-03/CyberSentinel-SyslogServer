#!/bin/bash
# Backup script for CyberSentinel data volumes

set -e

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/cybersentinel_backup_${TIMESTAMP}"

echo "========================================="
echo "CyberSentinel Backup"
echo "========================================="
echo ""
echo "Backup location: ${BACKUP_PATH}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# List of volumes to backup
VOLUMES=(
    "opensearch-data"
    "kafka-data"
    "postgres-data"
    "redis-data"
    "prometheus-data"
    "grafana-data"
)

echo "Starting backup..."
echo ""

for volume in "${VOLUMES[@]}"; do
    echo "Backing up volume: ${volume}..."

    docker run --rm \
        -v cybersentinel_${volume}:/source:ro \
        -v "$(pwd)/${BACKUP_PATH}:/backup" \
        alpine \
        tar czf /backup/${volume}.tar.gz -C /source .

    if [ $? -eq 0 ]; then
        SIZE=$(du -sh "${BACKUP_PATH}/${volume}.tar.gz" | cut -f1)
        echo "✓ ${volume} backed up (${SIZE})"
    else
        echo "✗ Failed to backup ${volume}"
    fi
done

echo ""
echo "========================================="
echo "Backup Complete!"
echo "========================================="
echo ""
echo "Backup location: ${BACKUP_PATH}"
echo "Total size: $(du -sh ${BACKUP_PATH} | cut -f1)"
echo ""
echo "To restore: ./scripts/restore.sh ${BACKUP_PATH}"
