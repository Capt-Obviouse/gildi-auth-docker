#!/bin/bash
# Backup Alliance Auth MariaDB to S3
# Usage: ./scripts/backup-db.sh
#
# Prerequisites:
#   - AWS CLI configured with credentials (aws configure)
#   - S3 bucket created
#
# Set up as cron job for daily backups:
#   0 4 * * * /path/to/aa-docker/scripts/backup-db.sh >> /var/log/aa-backup.log 2>&1

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_BUCKET="${AA_BACKUP_BUCKET:-}"
BACKUP_PREFIX="${AA_BACKUP_PREFIX:-alliance-auth-backups}"
RETENTION_DAYS="${AA_BACKUP_RETENTION_DAYS:-7}"

# Load .env file for database credentials
if [[ -f "$PROJECT_DIR/.env" ]]; then
    export $(grep -E '^(AA_DB_ROOT_PASSWORD|AA_DB_NAME)=' "$PROJECT_DIR/.env" | xargs)
fi

DB_NAME="${AA_DB_NAME:-alliance_auth}"
DB_PASSWORD="${AA_DB_ROOT_PASSWORD:-}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="aa-backup-${TIMESTAMP}.sql.gz"

# Validate configuration
if [[ -z "$BACKUP_BUCKET" ]]; then
    echo "ERROR: AA_BACKUP_BUCKET environment variable not set"
    echo "Set it in .env or export it before running this script"
    exit 1
fi

if [[ -z "$DB_PASSWORD" ]]; then
    echo "ERROR: AA_DB_ROOT_PASSWORD not found in .env"
    exit 1
fi

echo "[$(date)] Starting backup of $DB_NAME to s3://$BACKUP_BUCKET/$BACKUP_PREFIX/"

# Create backup using docker exec
docker exec aa-docker-auth_mysql-1 mariadb-dump \
    -u root \
    -p"$DB_PASSWORD" \
    --single-transaction \
    --routines \
    --triggers \
    "$DB_NAME" | gzip > "/tmp/$BACKUP_FILE"

BACKUP_SIZE=$(du -h "/tmp/$BACKUP_FILE" | cut -f1)
echo "[$(date)] Backup created: $BACKUP_FILE ($BACKUP_SIZE)"

# Upload to S3
aws s3 cp "/tmp/$BACKUP_FILE" "s3://$BACKUP_BUCKET/$BACKUP_PREFIX/$BACKUP_FILE"
echo "[$(date)] Uploaded to S3"

# Clean up local file
rm -f "/tmp/$BACKUP_FILE"

# Delete old backups from S3 (older than RETENTION_DAYS)
echo "[$(date)] Cleaning up backups older than $RETENTION_DAYS days..."
CUTOFF_DATE=$(date -d "-$RETENTION_DAYS days" +%Y%m%d)

aws s3 ls "s3://$BACKUP_BUCKET/$BACKUP_PREFIX/" | while read -r line; do
    FILE_DATE=$(echo "$line" | awk '{print $4}' | grep -oP 'aa-backup-\K\d{8}' || true)
    FILE_NAME=$(echo "$line" | awk '{print $4}')

    if [[ -n "$FILE_DATE" && "$FILE_DATE" < "$CUTOFF_DATE" ]]; then
        echo "[$(date)] Deleting old backup: $FILE_NAME"
        aws s3 rm "s3://$BACKUP_BUCKET/$BACKUP_PREFIX/$FILE_NAME"
    fi
done

echo "[$(date)] Backup complete"
