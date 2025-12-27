#!/bin/bash
# =============================================================================
# Database Backup Script for Alechemy
# Usage: ./scripts/backup.sh
# =============================================================================

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_CONTAINER="${DB_CONTAINER:-alechemy_db}"
DB_NAME="${DB_NAME:-alechemy_db}"
DB_USER="${DB_USER:-alechemy_user}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/alechemy_backup_$TIMESTAMP.sql.gz"

echo "🔄 Starting database backup..."
echo "   Database: $DB_NAME"
echo "   Container: $DB_CONTAINER"
echo "   Output: $BACKUP_FILE"

# Create backup
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo "✅ Backup completed successfully!"
    echo "   Size: $BACKUP_SIZE"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Remove old backups (older than RETENTION_DAYS)
echo "🧹 Cleaning old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "alechemy_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# List remaining backups
echo ""
echo "📁 Current backups:"
ls -lh "$BACKUP_DIR"/alechemy_backup_*.sql.gz 2>/dev/null || echo "   No backups found"

echo ""
echo "✨ Done!"
