#!/bin/bash
# Backup UserHub database
# Creates a timestamped backup file

set -e  # Exit on error

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
POSTGRES_USER=${POSTGRES_USER:-userhub}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-userhub123}
POSTGRES_DB=${POSTGRES_DB:-userhub}
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

# Backup directory
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/userhub_backup_$TIMESTAMP.sql.gz"

echo "==================================="
echo "UserHub Database Backup"
echo "==================================="
echo ""
echo "Database: $POSTGRES_DB"
echo "Backup file: $BACKUP_FILE"
echo ""

# Create backup
echo "Creating backup..."
PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
    -h $POSTGRES_HOST \
    -p $POSTGRES_PORT \
    -U $POSTGRES_USER \
    -d $POSTGRES_DB \
    --format=plain \
    --no-owner \
    --no-acl \
    --verbose \
    | gzip > $BACKUP_FILE

# Get backup file size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo ""
echo "==================================="
echo "Backup completed successfully!"
echo "==================================="
echo ""
echo "Backup details:"
echo "  File: $BACKUP_FILE"
echo "  Size: $BACKUP_SIZE"
echo "  Timestamp: $TIMESTAMP"
echo ""
echo "To restore this backup, run:"
echo "  gunzip -c $BACKUP_FILE | PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB"
echo ""

# Clean up old backups (keep last 10)
echo "Cleaning up old backups (keeping last 10)..."
ls -t $BACKUP_DIR/userhub_backup_*.sql.gz | tail -n +11 | xargs -r rm
echo "Cleanup completed"
