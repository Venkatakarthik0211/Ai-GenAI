# UserHub Database

PostgreSQL database setup for the UserHub user management application.

## Overview

This directory contains all database-related files including:
- Database schema definitions
- Sample seed data
- Docker Compose configuration
- Database migrations
- Utility scripts for database management

## Quick Start

### Using Docker (Recommended)

1. **Start the database**:
```bash
cd database
cp .env.example .env
# Edit .env with your preferred settings
docker compose up -d
```

This will start:
- PostgreSQL 16 on port 5432
- pgAdmin 4 on port 5050

2. **Access pgAdmin**:
- Open http://localhost:5050
- Login with credentials from .env (default: admin@userhub.com / admin)
- Add server connection:
  - Name: UserHub
  - Host: postgres (or localhost if accessing from host machine)
  - Port: 5432
  - Database: userhub
  - Username: userhub
  - Password: userhub123

3. **Stop the database**:
```bash
docker compose down
```

4. **Remove all data** (including volumes):
```bash
docker compose down -v
```

### Using Local PostgreSQL

1. **Create database**:
```bash
createdb userhub
```

2. **Run schema**:
```bash
psql -d userhub -f schema.sql
```

3. **Seed data** (optional):
```bash
psql -d userhub -f seed_data.sql
```

## Database Schema

### Users Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Username |
| full_name | VARCHAR(255) | NOT NULL | Full name |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete flag |
| is_superuser | BOOLEAN | DEFAULT FALSE | Admin flag |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| last_login | TIMESTAMP | NULLABLE | Last login time |
| bio | TEXT | NULLABLE | User biography |

### Indexes

1. `idx_users_id` - Primary key index
2. `idx_users_email` - Email lookup (unique)
3. `idx_users_username` - Username lookup (unique)
4. `idx_users_is_active` - Active user filtering
5. `idx_users_created_at` - Creation date sorting
6. `idx_users_last_login` - Last login sorting
7. `idx_users_active_only` - Partial index for active users

### Triggers

- `update_users_updated_at` - Automatically updates `updated_at` on row changes

## Default Test Credentials

When using seed data, the following test accounts are available:

**Admin User:**
- Email: admin@userhub.com
- Password: Admin123!
- Role: Superuser

**Regular Users:**
- Email: john.doe@example.com
- Password: User123!
- Role: User

(Additional users available - check seed_data.sql)

**IMPORTANT**: Change these passwords before deploying to production!

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# PostgreSQL Configuration
POSTGRES_USER=userhub
POSTGRES_PASSWORD=userhub123
POSTGRES_DB=userhub
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# PgAdmin Configuration
PGADMIN_EMAIL=admin@userhub.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050

# Connection String
DATABASE_URL=postgresql://userhub:userhub123@localhost:5432/userhub
```

## Utility Scripts

All scripts are located in the `scripts/` directory.

### Initialize Database

Creates database, runs migrations, and seeds data:

```bash
./scripts/init_db.sh
```

### Reset Database

Drops and recreates database (WARNING: deletes all data):

```bash
./scripts/reset_db.sh
```

### Backup Database

Creates a timestamped backup file:

```bash
./scripts/backup_db.sh
```

Backups are stored in `./backups/` directory.

### Restore Database

To restore from a backup:

```bash
gunzip -c backups/userhub_backup_TIMESTAMP.sql.gz | psql -d userhub
```

## Migrations

Database migrations are stored in `migrations/` directory.

### Current Migrations

1. **001_initial_schema.sql** - Creates users table with indexes and constraints
2. **002_add_refresh_tokens.sql** - Adds refresh tokens table (future enhancement)

### Running Migrations Manually

```bash
psql -d userhub -f migrations/001_initial_schema.sql
psql -d userhub -f migrations/002_add_refresh_tokens.sql
```

### Rollback Migrations

Each migration file contains rollback instructions in comments.

## Connecting from Application

### Python (asyncpg)

```python
DATABASE_URL = "postgresql+asyncpg://userhub:userhub123@localhost:5432/userhub"
```

### Python (psycopg2)

```python
DATABASE_URL = "postgresql://userhub:userhub123@localhost:5432/userhub"
```

### Node.js

```javascript
const connectionString = "postgresql://userhub:userhub123@localhost:5432/userhub"
```

### Docker Container

If connecting from a Docker container, use `postgres` as the host:

```
postgresql://userhub:userhub123@postgres:5432/userhub
```

## Common SQL Queries

### Get all active users

```sql
SELECT * FROM users WHERE is_active = true ORDER BY created_at DESC;
```

### Find user by email

```sql
SELECT * FROM users WHERE email = 'user@example.com';
```

### Count users by status

```sql
SELECT
    is_active,
    is_superuser,
    COUNT(*) as count
FROM users
GROUP BY is_active, is_superuser;
```

### Get recently logged in users

```sql
SELECT
    username,
    email,
    last_login
FROM users
WHERE last_login IS NOT NULL
ORDER BY last_login DESC
LIMIT 10;
```

### Soft delete a user

```sql
UPDATE users SET is_active = false WHERE id = 'user-uuid-here';
```

### Hard delete a user

```sql
DELETE FROM users WHERE id = 'user-uuid-here';
```

## Performance Tuning

### Index Usage

Monitor index usage with:

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Table Statistics

Check table statistics:

```sql
SELECT
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

### Vacuum and Analyze

Regular maintenance:

```sql
VACUUM ANALYZE users;
```

## Security Best Practices

1. **Change default passwords** - Never use default passwords in production
2. **Use strong passwords** - Generate with: `openssl rand -base64 32`
3. **Enable SSL/TLS** - For production PostgreSQL connections
4. **Restrict network access** - Use firewall rules and security groups
5. **Regular backups** - Automate daily backups
6. **Monitor access logs** - Track database access and queries
7. **Use connection pooling** - PgBouncer for production
8. **Principle of least privilege** - Grant only necessary permissions

## Troubleshooting

### Cannot connect to PostgreSQL

Check if PostgreSQL is running:

```bash
docker ps | grep postgres
# or
pg_isready -h localhost -p 5432
```

### Permission denied errors

Ensure proper file permissions on scripts:

```bash
chmod +x scripts/*.sh
```

### Database already exists error

Drop and recreate:

```bash
./scripts/reset_db.sh
```

### Port already in use

Change port in .env file:

```env
POSTGRES_PORT=5433
PGADMIN_PORT=5051
```

## Docker Commands

### View logs

```bash
docker logs userhub-postgres
docker logs userhub-pgadmin
```

### Access PostgreSQL CLI

```bash
docker exec -it userhub-postgres psql -U userhub -d userhub
```

### Check container status

```bash
docker ps -a | grep userhub
```

### Restart containers

```bash
docker compose restart
```

## Production Deployment

For production deployment:

1. Use managed PostgreSQL service (AWS RDS, DigitalOcean, etc.)
2. Enable SSL/TLS connections
3. Set up automated backups
4. Configure connection pooling (PgBouncer)
5. Set up monitoring and alerting
6. Use strong, unique passwords
7. Implement proper firewall rules
8. Regular security updates
9. Database replication for high availability
10. Regular performance tuning

## Support

For issues or questions:
- Check logs: `docker logs userhub-postgres`
- Review PostgreSQL documentation: https://www.postgresql.org/docs/
- Check pgAdmin documentation: https://www.pgadmin.org/docs/

## License

MIT License - See LICENSE file for details
