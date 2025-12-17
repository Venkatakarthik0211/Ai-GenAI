#!/bin/bash
# Reset UserHub database
# WARNING: This will delete all data and recreate the database

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

echo "==================================="
echo "UserHub Database Reset"
echo "==================================="
echo ""
echo "WARNING: This will delete ALL data in database '$POSTGRES_DB'"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Database reset cancelled"
    exit 0
fi

echo ""
echo "Resetting database..."
echo ""

# Drop database
echo "Dropping database '$POSTGRES_DB'..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -c "DROP DATABASE IF EXISTS $POSTGRES_DB"
echo "Database dropped"
echo ""

# Recreate database
echo "Creating database '$POSTGRES_DB'..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB"
echo "Database created"
echo ""

# Run schema
echo "Running schema migration..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f schema.sql
echo "Schema migration completed"
echo ""

# Seed data
echo "Seeding database..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f seed_data.sql
echo "Database seeding completed"
echo ""

echo "==================================="
echo "Database reset completed!"
echo "==================================="
echo ""
echo "Test credentials:"
echo "  Admin: admin@userhub.com / Admin123!"
echo "  User: john.doe@example.com / User123!"
