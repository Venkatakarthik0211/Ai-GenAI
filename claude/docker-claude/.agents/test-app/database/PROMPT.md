# PostgreSQL Database Setup - UserHub DB

Create a complete PostgreSQL database setup for the UserHub user management application.

## Requirements

### Core Features
1. **Database Schema**
   - Users table with proper columns and constraints
   - Indexes for performance
   - Timestamps for audit trails
   - Soft delete support (is_active flag)

2. **Migrations**
   - Initial schema creation
   - Migration versioning system
   - Rollback support
   - Data seeding

3. **Docker Setup**
   - PostgreSQL Docker container
   - Volume persistence
   - Environment configuration
   - Health checks

4. **Development Data**
   - Seed data for testing
   - Sample users with hashed passwords
   - Admin user

## Files to Create

### 1. `schema.sql` (150-200 lines)
Complete database schema including:

**Users table:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);
```

**Indexes:**
- Index on email for fast lookups
- Index on username for searches
- Index on is_active for filtering
- Index on created_at for sorting

**Functions:**
- Trigger function to auto-update updated_at timestamp

**Constraints:**
- Email format validation
- Username length constraints
- Check constraints for data integrity

### 2. `seed_data.sql` (80-100 lines)
Sample data for development:
- Admin user (admin@userhub.com / Admin123!)
- 5-10 regular users for testing
- Various user states (active, inactive)
- Realistic names and emails

**Important:** Use bcrypt hashed passwords (provide instructions on how passwords were hashed)

### 3. `docker-compose.yml` (60-80 lines)
PostgreSQL service configuration:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    container_name: userhub-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-userhub}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-userhub123}
      POSTGRES_DB: ${POSTGRES_DB:-userhub}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./seed_data.sql:/docker-entrypoint-initdb.d/02-seed.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U userhub"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: userhub-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@userhub.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
    ports:
      - "5050:80"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

### 4. `.env.example`
Database environment variables:
```
# PostgreSQL Configuration
POSTGRES_USER=userhub
POSTGRES_PASSWORD=userhub123
POSTGRES_DB=userhub
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# PgAdmin Configuration
PGADMIN_EMAIL=admin@userhub.com
PGADMIN_PASSWORD=admin

# Connection String
DATABASE_URL=postgresql://userhub:userhub123@localhost:5432/userhub
```

### 5. `migrations/001_initial_schema.sql` (120-150 lines)
Initial migration file:
- Create users table
- Create indexes
- Create trigger functions
- Insert initial data (optional admin user)

### 6. `migrations/002_add_refresh_tokens.sql` (60-80 lines)
Second migration example (for future use):
- Create refresh_tokens table
- Foreign key to users
- Token expiry tracking
- Token revocation support

### 7. `scripts/init_db.sh` (40-60 lines)
Bash script to initialize database:
```bash
#!/bin/bash
# - Load environment variables
# - Create database if not exists
# - Run migrations
# - Seed data
# - Verify setup
```

### 8. `scripts/reset_db.sh` (30-40 lines)
Bash script to reset database:
```bash
#!/bin/bash
# - Drop database
# - Recreate database
# - Run migrations
# - Seed data
```

### 9. `scripts/backup_db.sh` (30-40 lines)
Bash script to backup database:
```bash
#!/bin/bash
# - Create timestamped backup
# - Use pg_dump
# - Compress backup
# - Save to backups/ directory
```

### 10. `README.md` (150-200 lines)
Comprehensive database documentation:
- Setup instructions
- How to run migrations
- How to seed data
- Connection details
- Backup and restore procedures
- Common SQL queries
- Troubleshooting guide

## Technical Stack
- **Database**: PostgreSQL 16
- **Container**: Docker with Docker Compose
- **Admin Tool**: pgAdmin 4
- **Backup**: pg_dump

## Database Schema Details

### Users Table Columns
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Username |
| full_name | VARCHAR(255) | NOT NULL | Full name |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete flag |
| is_superuser | BOOLEAN | DEFAULT FALSE | Admin flag |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| last_login | TIMESTAMP | NULLABLE | Last login time |

### Indexes
1. `idx_users_email` - On email (UNIQUE)
2. `idx_users_username` - On username (UNIQUE)
3. `idx_users_is_active` - On is_active for filtering
4. `idx_users_created_at` - On created_at for sorting

### Triggers
1. `update_users_updated_at` - Auto-update updated_at on row changes

## Code Quality Requirements
- ✅ Proper SQL formatting and indentation
- ✅ Comments explaining complex queries
- ✅ Transaction support for migrations
- ✅ Rollback procedures
- ✅ Idempotent migrations (safe to run multiple times)
- ✅ Data integrity constraints
- ✅ Performance indexes
- ✅ Security best practices (no default passwords in production)

## Directory Structure
```
database/
├── schema.sql
├── seed_data.sql
├── docker-compose.yml
├── .env.example
├── README.md
├── migrations/
│   ├── 001_initial_schema.sql
│   └── 002_add_refresh_tokens.sql
└── scripts/
    ├── init_db.sh
    ├── reset_db.sh
    └── backup_db.sh
```

## Special Instructions

1. **Schema Design**
   - Use UUID for primary keys (more secure than incremental IDs)
   - Add created_at and updated_at to all tables
   - Implement soft deletes with is_active flag
   - Add proper indexes for frequently queried fields

2. **Migrations**
   - Each migration should be in a separate file
   - Include rollback SQL in comments
   - Use transactions for atomic migrations
   - Test migrations on sample data before production

3. **Seed Data**
   - Provide at least one admin user
   - Include diverse test data (active, inactive users)
   - Use realistic data (names, emails)
   - Document default credentials clearly

4. **Docker Setup**
   - Use PostgreSQL 16 Alpine for smaller image
   - Persist data with named volumes
   - Include pgAdmin for database management
   - Add health checks for container orchestration

5. **Security**
   - Never commit .env with real passwords
   - Use strong default passwords
   - Provide instructions to change defaults
   - Document password hashing method (bcrypt)

6. **Documentation**
   - Include connection examples
   - Document all tables and columns
   - Provide sample queries
   - Explain migration process

7. **Backup Strategy**
   - Automated backup script
   - Timestamped backup files
   - Compressed backups to save space
   - Instructions for restore

8. **Performance**
   - Add indexes on foreign keys
   - Create indexes for WHERE clause columns
   - Use partial indexes for is_active
   - Monitor query performance

9. Make the database ready to run with `docker compose up -d`

10. Include instructions for:
    - Connecting from the API (connection string)
    - Accessing pgAdmin (http://localhost:5050)
    - Running migrations manually
    - Backing up and restoring data
