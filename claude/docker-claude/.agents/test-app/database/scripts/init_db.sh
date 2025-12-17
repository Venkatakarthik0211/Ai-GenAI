#!/bin/bash
# Initialize UserHub database
# This script creates the database, runs migrations, and seeds data

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
echo "UserHub Database Initialization"
echo "==================================="
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
if ! PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -lqt | cut -d \| -f 1 | grep -qw template1; then
    echo "Error: Cannot connect to PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT"
    echo "Make sure PostgreSQL is running and credentials are correct"
    exit 1
fi
echo "PostgreSQL connection successful"
echo ""

# Create database if it doesn't exist
echo "Creating database '$POSTGRES_DB' if it doesn't exist..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 || \
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB"
echo "Database '$POSTGRES_DB' ready"
echo ""

# Run schema migration
echo "Running schema migration..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f schema.sql
echo "Schema migration completed"
echo ""

# Run seed data
echo "Seeding database with sample data..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f seed_data.sql
echo "Database seeding completed"
echo ""

# Verify setup
echo "Verifying database setup..."
RESULT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -t -c "SELECT COUNT(*) FROM users")
echo "Total users in database: $RESULT"
echo ""

echo "==================================="
echo "Database initialization completed!"
echo "==================================="
echo ""
echo "Connection details:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo ""
echo "Connection string:"
echo "  postgresql://$POSTGRES_USER:****@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo ""
echo "Test credentials:"
echo "  Admin: admin@userhub.com / Admin123!"
echo "  User: john.doe@example.com / User123!"
