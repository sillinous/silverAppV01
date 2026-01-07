#!/bin/bash

# This script performs a PostgreSQL database backup using pg_dump.

# Load environment variables (if not already loaded)
# This is useful for local testing, but in production, these should be
# provided directly by the environment (e.g., Docker Compose, Kubernetes secrets).
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Database connection details from environment variables
DB_USER=${POSTGRES_USER:-user}
DB_PASSWORD=${POSTGRES_PASSWORD:-password}
DB_NAME=${POSTGRES_DB:-arbitrage_db}
DB_HOST=${DB_HOST:-db} # Assuming 'db' is the service name in docker-compose
DB_PORT=${DB_PORT:-5432}

# Backup directory
BACKUP_DIR="/var/backups/postgresql"
mkdir -p $BACKUP_DIR

# Timestamp for the backup file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/$DB_NAME-$TIMESTAMP.sql"

echo "Starting PostgreSQL backup for database '$DB_NAME' on host '$DB_HOST'..."

# Perform the backup
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
  echo "Database backup successful: $BACKUP_FILE"
else
  echo "Database backup failed!"
  exit 1
fi

# Optional: Remove old backups (e.g., keep last 7 days)
# find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete
# echo "Old backups removed."

exit 0
