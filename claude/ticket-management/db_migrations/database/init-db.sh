#!/bin/bash
# PostgreSQL Database Initialization Script
# This script runs automatically when the container is first created

set -e

echo "Starting database initialization..."

# Enable required PostgreSQL extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable UUID generation
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Enable cryptographic functions
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- Enable full-text search extensions
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";

    -- Enable additional text search configurations
    CREATE EXTENSION IF NOT EXISTS "unaccent";

    -- Create Flyway schema history table (Flyway will manage this)
    -- Just ensuring the database is ready

    -- Log successful initialization
    DO \$\$
    BEGIN
        RAISE NOTICE 'Database initialized successfully';
        RAISE NOTICE 'Database: %', current_database();
        RAISE NOTICE 'Extensions enabled: uuid-ossp, pgcrypto, pg_trgm, unaccent';
    END \$\$;
EOSQL

echo "Database initialization completed successfully!"
