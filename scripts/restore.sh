#!/bin/bash
# =============================================================================
# Database Restore Script for Alechemy
# Usage: ./scripts/restore.sh <backup_file>
# =============================================================================

set -e

# Check argument
if [ -z "$1" ]; then
    echo "Usage: ./scripts/restore.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/alechemy_backup_*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"
DB_CONTAINER="${DB_CONTAINER:-alechemy_db}"
DB_NAME="${DB_NAME:-alechemy_db}"
DB_USER="${DB_USER:-alechemy_user}"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will REPLACE all data in the database!"
echo "   Database: $DB_NAME"
echo "   Backup: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🔄 Stopping web container..."
docker stop alechemy_web 2>/dev/null || true

echo "🔄 Restoring database..."

# Drop existing connections and recreate database
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '$DB_NAME'
    AND pid <> pg_backend_pid();
" 2>/dev/null || true

docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Restore from backup
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" "$DB_NAME"
else
    docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" "$DB_NAME" < "$BACKUP_FILE"
fi

echo "🔄 Starting web container..."
docker start alechemy_web

echo ""
echo "✅ Database restored successfully!"
echo "   You may need to run migrations if the backup is from an older version."
