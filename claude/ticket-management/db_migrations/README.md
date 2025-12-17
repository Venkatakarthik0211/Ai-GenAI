# Database Migrations

## Overview

This directory contains SQL migration scripts for the Ticket Management System database. We use **Flyway** for managing database schema migrations, ensuring consistent and versioned database changes across all environments.

**Database**: PostgreSQL 16
**Migration Tool**: Flyway 11
**Alternative**: Alembic (Python-based, see `/backend/alembic/` directory)

**Design Reference**: Based on schema defined in `/backend/DATABASE_SCHEMA.md` and entities from `/design/uml-diagram.md`

---

## Table of Contents

1. [Database Schema Overview](#database-schema-overview)
2. [Entity Relationships](#entity-relationships)
3. [Migration Strategy](#migration-strategy)
4. [Flyway Configuration](#flyway-configuration)
5. [Migration Scripts](#migration-scripts)
6. [Running Migrations](#running-migrations)
7. [Migration Best Practices](#migration-best-practices)
8. [Rollback Strategy](#rollback-strategy)
9. [Troubleshooting](#troubleshooting)

---

## Database Schema Overview

The Ticket Management System database consists of **12 core tables** organized into four logical groups:

### 1. Authentication & User Management (5 tables)
- **users** - User accounts and profiles
- **refresh_tokens** - JWT refresh token management
- **user_sessions** - Active session tracking
- **password_resets** - Password reset token management
- **audit_logs** - Security audit trail

### 2. Ticket Management (4 tables)
- **tickets** - Core ticket entity
- **comments** - Ticket comments and updates
- **attachments** - File attachments
- **ticket_history** - Complete change audit trail

### 3. Notification & Communication (1 table)
- **notifications** - Multi-channel notification management

### 4. SLA & Escalation (2 tables)
- **sla_policies** - Service Level Agreement definitions
- **escalations** - Ticket escalation tracking

**Total Database Objects:**
- 12 Tables
- 6 Utility Functions
- 4 Materialized Views
- 2 Standard Views
- 80+ Indexes
- Multiple Triggers

---

## Entity Relationships

### Core Relationship Diagram

```
                    ┌─────────────────────────────────────────────────┐
                    │                    USERS                        │
                    │  - id (PK)                                      │
                    │  - username, email, password_hash               │
                    │  - role, status, is_active                      │
                    │  - mfa_enabled, mfa_secret                      │
                    │  - created_at, updated_at, deleted_at           │
                    └──────────┬──────────────────────┬───────────────┘
                               │                      │
                ┌──────────────┴──────────────┐      │
                │                             │      │
                │ 1:N (requestor)       1:N (assigned_to)
                │                             │      │
                ▼                             ▼      │
    ┌─────────────────────┐       ┌─────────────────────┐
    │   REFRESH_TOKENS    │       │    USER_SESSIONS    │
    │  - id (PK)          │       │  - id (PK)          │
    │  - user_id (FK)     │       │  - user_id (FK)     │
    │  - token_hash       │       │  - session_token    │
    │  - device_info      │       │  - is_active        │
    │  - expires_at       │       │  - last_activity_at │
    └─────────────────────┘       └─────────────────────┘
                │
                │ 1:N
                ▼
    ┌─────────────────────┐       ┌─────────────────────┐
    │  PASSWORD_RESETS    │       │    AUDIT_LOGS       │
    │  - id (PK)          │       │  - id (PK)          │
    │  - user_id (FK)     │       │  - user_id (FK)     │
    │  - token_hash       │       │  - action_type      │
    │  - is_used          │       │  - resource_type    │
    │  - expires_at       │       │  - old_values       │
    └─────────────────────┘       │  - new_values       │
                                   └─────────────────────┘


                    ┌─────────────────────────────────────────────────┐
                    │                   TICKETS                       │
                    │  - id (PK)                                      │
                    │  - ticket_number (UNIQUE)                       │
                    │  - title, description, category                 │
                    │  - status, priority                             │
                    │  - requestor_id (FK → users)                    │
                    │  - assigned_to (FK → users)                     │
                    │  - sla_policy_id (FK → sla_policies)            │
                    │  - response_due_at, resolution_due_at           │
                    │  - search_vector (full-text search)             │
                    │  - created_at, updated_at, deleted_at           │
                    └──────────┬────────────┬─────────────────────────┘
                               │            │
                    ┌──────────┴────┐      │
                    │               │      │
            1:N (ticket)       1:N (ticket)
                    │               │      │
                    ▼               ▼      │
        ┌──────────────────┐  ┌──────────────────┐
        │    COMMENTS      │  │   ATTACHMENTS    │
        │  - id (PK)       │  │  - id (PK)       │
        │  - ticket_id(FK) │  │  - ticket_id(FK) │
        │  - author_id(FK) │  │  - comment_id(FK)│
        │  - content       │  │  - uploaded_by(FK)│
        │  - is_internal   │  │  - file_name     │
        │  - created_at    │  │  - file_path     │
        └──────────────────┘  │  - file_size     │
                │             │  - scan_status   │
                │             └──────────────────┘
                │ 1:N                   │
                └───────────────────────┘
                          │
                          │ 1:N
                          ▼
              ┌──────────────────────┐
              │   TICKET_HISTORY     │
              │  - id (PK)           │
              │  - ticket_id (FK)    │
              │  - changed_by (FK)   │
              │  - change_type       │
              │  - field_name        │
              │  - old_value         │
              │  - new_value         │
              │  - change_metadata   │
              │  - created_at        │
              └──────────────────────┘


                    ┌─────────────────────────────────────────────────┐
                    │                SLA_POLICIES                     │
                    │  - id (PK)                                      │
                    │  - policy_name (UNIQUE)                         │
                    │  - priority (P1/P2/P3/P4)                       │
                    │  - response_time (hours)                        │
                    │  - resolution_time (hours)                      │
                    │  - escalation_levels (JSONB)                    │
                    │  - is_active                                    │
                    └──────────┬──────────────────────────────────────┘
                               │
                               │ 1:N
                               ▼
                    ┌─────────────────────┐
                    │    ESCALATIONS      │
                    │  - id (PK)          │
                    │  - ticket_id (FK)   │
                    │  - sla_policy_id(FK)│
                    │  - escalated_by(FK) │
                    │  - escalated_to(FK) │
                    │  - escalation_level │
                    │  - escalation_reason│
                    │  - is_sla_breach    │
                    │  - is_resolved      │
                    └─────────────────────┘


                    ┌─────────────────────────────────────────────────┐
                    │               NOTIFICATIONS                      │
                    │  - id (PK)                                      │
                    │  - user_id (FK → users)                         │
                    │  - ticket_id (FK → tickets)                     │
                    │  - notification_type                            │
                    │  - channels (ARRAY: EMAIL, SMS, IN_APP, SLACK) │
                    │  - email_sent_at, sms_sent_at                   │
                    │  - is_read, read_at                             │
                    │  - status (PENDING, SENT, DELIVERED, FAILED)    │
                    │  - retry_count, max_retries                     │
                    └─────────────────────────────────────────────────┘
```

### Relationship Details

#### 1. User → Tickets (One-to-Many)
- **Relationship**: A user can be the requestor for multiple tickets
- **Foreign Key**: `tickets.requestor_id → users.id`
- **Constraint**: `ON DELETE RESTRICT` (cannot delete user with open tickets)
- **Business Rule**: Every ticket must have a requestor

#### 2. User → Tickets (One-to-Many, Optional)
- **Relationship**: A user can be assigned to multiple tickets
- **Foreign Key**: `tickets.assigned_to → users.id`
- **Constraint**: `ON DELETE SET NULL` (tickets remain if user deleted)
- **Business Rule**: Tickets can be unassigned

#### 3. Tickets → Comments (One-to-Many)
- **Relationship**: A ticket can have multiple comments
- **Foreign Key**: `comments.ticket_id → tickets.id`
- **Constraint**: `ON DELETE CASCADE` (delete comments when ticket deleted)
- **Business Rule**: Comments are inseparable from tickets

#### 4. Tickets → Attachments (One-to-Many)
- **Relationship**: A ticket can have multiple attachments
- **Foreign Key**: `attachments.ticket_id → tickets.id`
- **Constraint**: `ON DELETE CASCADE` (delete attachments when ticket deleted)
- **Business Rule**: Max 50MB per attachment, virus scanning required

#### 5. Comments → Attachments (One-to-Many)
- **Relationship**: A comment can have multiple attachments
- **Foreign Key**: `attachments.comment_id → comments.id`
- **Constraint**: `ON DELETE CASCADE` (delete attachments when comment deleted)
- **Business Rule**: Each attachment belongs to either ticket OR comment (not both)

#### 6. Tickets → Ticket History (One-to-Many)
- **Relationship**: A ticket has complete change history
- **Foreign Key**: `ticket_history.ticket_id → tickets.id`
- **Constraint**: `ON DELETE CASCADE` (history deleted with ticket)
- **Business Rule**: Automatically logged via trigger, immutable

#### 7. SLA Policies → Tickets (One-to-Many)
- **Relationship**: An SLA policy applies to multiple tickets
- **Foreign Key**: `tickets.sla_policy_id → sla_policies.id`
- **Constraint**: `ON DELETE SET NULL` (tickets retain data if policy deleted)
- **Business Rule**: Policy determined by ticket priority

#### 8. Tickets → Escalations (One-to-Many)
- **Relationship**: A ticket can be escalated multiple times
- **Foreign Key**: `escalations.ticket_id → tickets.id`
- **Constraint**: `ON DELETE CASCADE` (escalations deleted with ticket)
- **Business Rule**: Tracks escalation chain with levels 1-5

#### 9. User → Notifications (One-to-Many)
- **Relationship**: A user receives multiple notifications
- **Foreign Key**: `notifications.user_id → users.id`
- **Constraint**: `ON DELETE CASCADE` (notifications deleted with user)
- **Business Rule**: Multi-channel delivery with retry logic

#### 10. Tickets → Notifications (One-to-Many, Optional)
- **Relationship**: A ticket generates multiple notifications
- **Foreign Key**: `notifications.ticket_id → tickets.id`
- **Constraint**: `ON DELETE CASCADE` (notifications deleted with ticket)
- **Business Rule**: Notifications can exist without ticket (system notifications)

#### 11. User → Refresh Tokens (One-to-Many)
- **Relationship**: A user can have multiple active refresh tokens (multi-device)
- **Foreign Key**: `refresh_tokens.user_id → users.id`
- **Constraint**: `ON DELETE CASCADE` (tokens deleted when user deleted)
- **Business Rule**: Token family tracking prevents reuse attacks

#### 12. User → User Sessions (One-to-Many)
- **Relationship**: A user can have multiple concurrent sessions
- **Foreign Key**: `user_sessions.user_id → users.id`
- **Constraint**: `ON DELETE CASCADE` (sessions terminated when user deleted)
- **Business Rule**: Track device, IP, location for security monitoring

#### 13. User → Password Resets (One-to-Many)
- **Relationship**: A user can request multiple password resets
- **Foreign Key**: `password_resets.user_id → users.id`
- **Constraint**: `ON DELETE CASCADE` (reset tokens deleted with user)
- **Business Rule**: Tokens expire after 1 hour, single use only

#### 14. User → Audit Logs (One-to-Many, Optional)
- **Relationship**: A user's actions are logged in audit trail
- **Foreign Key**: `audit_logs.user_id → users.id`
- **Constraint**: `ON DELETE SET NULL` (preserve logs even if user deleted)
- **Business Rule**: Immutable logs for compliance and security

### Data Flow & State Machine

#### Ticket Lifecycle States
```
NEW → OPEN → IN_PROGRESS → PENDING_INFO → RESOLVED → CLOSED
                    ↓                           ↓
                ESCALATED                   REOPENED
                    ↓                           ↓
                IN_PROGRESS ← ← ← ← ← ← ← ← ← ←
```

#### SLA Workflow
```
Ticket Created → Assign SLA Policy (by priority)
       ↓
Start SLA Timer → Monitor response_due_at
       ↓
First Response → Check resolution_due_at
       ↓
Approaching Breach → Send Warning Notification
       ↓
SLA Breach → Auto-Escalate → Create Escalation Record
       ↓
Escalation Level 1 → Team Lead
       ↓
Escalation Level 2 → Manager
       ↓
Escalation Level 3 → Admin
```

#### Notification Flow
```
Event Trigger (ticket created, status changed, etc.)
       ↓
Create Notification → Determine Channels (EMAIL, SMS, IN_APP, SLACK)
       ↓
Queue for Delivery → Status: PENDING
       ↓
Process Delivery → Attempt Send
       ↓
   Success? → Status: SENT → Mark delivered → Status: DELIVERED
       ↓
   Failure? → Status: FAILED → Increment retry_count
       ↓
Retry Logic → Wait (exponential backoff) → Status: RETRYING
       ↓
Max Retries? → Permanent Failure
```

### Cardinality Summary

| Relationship | From Table | To Table | Cardinality | Constraint |
|-------------|------------|----------|-------------|------------|
| User creates tickets | users | tickets | 1:N | RESTRICT |
| User assigned to tickets | users | tickets | 1:N (optional) | SET NULL |
| Ticket has comments | tickets | comments | 1:N | CASCADE |
| Ticket has attachments | tickets | attachments | 1:N | CASCADE |
| Comment has attachments | comments | attachments | 1:N | CASCADE |
| Ticket has history | tickets | ticket_history | 1:N | CASCADE |
| SLA policy for tickets | sla_policies | tickets | 1:N | SET NULL |
| Ticket has escalations | tickets | escalations | 1:N | CASCADE |
| User receives notifications | users | notifications | 1:N | CASCADE |
| Ticket generates notifications | tickets | notifications | 1:N (optional) | CASCADE |
| User has refresh tokens | users | refresh_tokens | 1:N | CASCADE |
| User has sessions | users | user_sessions | 1:N | CASCADE |
| User requests password reset | users | password_resets | 1:N | CASCADE |
| User actions logged | users | audit_logs | 1:N (optional) | SET NULL |

### Indexes & Performance

**Primary Indexes**: 12 (one per table)
**Foreign Key Indexes**: 14 (for relationship integrity)
**Search Indexes**: 8 (full-text search, GIN indexes)
**Composite Indexes**: 12 (for common query patterns)
**Partial Indexes**: 15 (filtered for active records)

**Materialized Views**: 4 reporting views (refresh daily/hourly)
**Standard Views**: 2 monitoring views (real-time)

---

## Migration Strategy

### Versioning Scheme

Flyway uses a versioned migration approach with the naming convention:

```
V{VERSION}__{DESCRIPTION}.sql

Examples:
V1__initial_schema.sql
V2__auth_tables.sql
V3__ticket_tables.sql
V4__notification_tables.sql
V5__sla_escalation_tables.sql
V6__indexes_optimization.sql
V7__add_ticket_tags.sql
```

### Migration Types

1. **Versioned Migrations** (V prefix): Applied once in order
2. **Repeatable Migrations** (R prefix): Applied whenever checksum changes
3. **Undo Migrations** (U prefix): Rollback versioned migrations (Flyway Teams)

---

## Flyway Configuration

### flyway.conf

```properties
# Flyway Configuration File
# Location: backend/db_migrations/flyway.conf

# Database connection
flyway.url=jdbc:postgresql://localhost:5432/ticket_management
flyway.user=ticket_user
flyway.password=secure_password

# Schema
flyway.schemas=public
flyway.defaultSchema=public

# Migration locations
flyway.locations=filesystem:./

# Table to track migrations
flyway.table=flyway_schema_history

# Placeholders (for environment-specific values)
flyway.placeholders.app_user=ticket_app
flyway.placeholders.environment=development

# Validation
flyway.validateOnMigrate=true
flyway.cleanDisabled=true  # Prevent accidental data loss

# Out of order migrations (not recommended for production)
flyway.outOfOrder=false

# Baseline
flyway.baselineOnMigrate=true
flyway.baselineVersion=0
flyway.baselineDescription=<< Flyway Baseline >>

# Mixed migrations (SQL and Java)
flyway.mixed=false

# Encoding
flyway.encoding=UTF-8

# SQL Migration Prefix
flyway.sqlMigrationPrefix=V
flyway.repeatableSqlMigrationPrefix=R
flyway.sqlMigrationSeparator=__
flyway.sqlMigrationSuffixes=.sql

# Connection
flyway.connectRetries=3
flyway.connectRetriesInterval=10
```

### Environment-Specific Configuration

```bash
# Development
flyway.conf.dev
flyway.url=jdbc:postgresql://localhost:5432/ticket_dev
flyway.user=ticket_dev_user

# Staging
flyway.conf.staging
flyway.url=jdbc:postgresql://staging-db:5432/ticket_staging
flyway.user=ticket_staging_user

# Production
flyway.conf.prod
flyway.url=jdbc:postgresql://prod-db:5432/ticket_prod
flyway.user=ticket_prod_user
flyway.cleanDisabled=true
flyway.outOfOrder=false
```

---
## Running Migrations

### Using Flyway CLI

```bash
# Validate migrations
flyway -configFiles=flyway.conf validate

# Show migration info
flyway -configFiles=flyway.conf info

# Migrate to latest version
flyway -configFiles=flyway.conf migrate

# Clean database (DANGEROUS - only for development)
flyway -configFiles=flyway.conf clean

# Repair metadata table
flyway -configFiles=flyway.conf repair

# Baseline existing database
flyway -configFiles=flyway.conf baseline
```

### Using Docker

```bash
# Run Flyway in Docker
docker run --rm \
  -v $(pwd):/flyway/sql \
  -v $(pwd)/flyway.conf:/flyway/conf/flyway.conf \
  flyway/flyway:latest \
  migrate
```

### Using Python (with Flyway wrapper)

```python
# In your application startup (main.py)
from flyway import Flyway

def run_migrations():
    flyway = Flyway(
        url="jdbc:postgresql://localhost:5432/ticket_db",
        user="ticket_user",
        password="secure_password",
        locations=["filesystem:backend/db_migrations"]
    )

    flyway.migrate()

# Run at startup
if __name__ == "__main__":
    run_migrations()
    # Start application
```

---

## Migration Best Practices

### 1. Version Control
- ✅ Always commit migration scripts to version control
- ✅ Never modify applied migrations
- ✅ Use descriptive names for migrations

### 2. Testing
- ✅ Test migrations on development database first
- ✅ Test rollback procedures
- ✅ Verify data integrity after migration

### 3. Production Deployment
- ✅ Backup database before migration
- ✅ Run migrations during maintenance window
- ✅ Monitor migration progress
- ✅ Have rollback plan ready

### 4. Writing Migrations
```sql
-- ✅ GOOD: Idempotent operations
CREATE TABLE IF NOT EXISTS tickets (...);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);

-- ❌ BAD: Non-idempotent operations
CREATE TABLE tickets (...);  -- Fails if table exists
CREATE INDEX idx_tickets_status ON tickets(status);  -- Fails if index exists
```

### 5. Data Migrations
```sql
-- Always use transactions for data migrations
BEGIN;

-- Update existing data
UPDATE tickets SET category = 'INFRASTRUCTURE'
WHERE category IS NULL;

-- Verify changes
SELECT COUNT(*) FROM tickets WHERE category IS NULL;

COMMIT;
```

---

## Rollback Strategy

### Using Undo Migrations (Flyway Teams)

```sql
-- U3__undo_ticket_tables.sql
DROP TABLE IF EXISTS ticket_history CASCADE;
DROP TABLE IF EXISTS attachments CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
```

### Manual Rollback

```sql
-- Document rollback procedures in migration comments

-- ============================================================================
-- ROLLBACK PROCEDURE:
-- 1. Stop application
-- 2. Backup database
-- 3. Run rollback script: psql -f rollback_v3.sql
-- 4. Restore from backup if needed
-- ============================================================================
```

---

## Troubleshooting

### Common Issues

**"Migration checksum mismatch"**
```bash
# Fix: Repair Flyway metadata
flyway repair

# Or update checksum in database
UPDATE flyway_schema_history
SET checksum = <new_checksum>
WHERE version = '3';
```

**"Out of order migration detected"**
```bash
# Allow out of order migrations (not recommended for production)
flyway -outOfOrder=true migrate
```

**"Failed migration"**
```bash
# Check Flyway history
SELECT * FROM flyway_schema_history WHERE success = false;

# Fix the issue and repair
flyway repair

# Retry migration
flyway migrate
```

**"Baseline on migrate"**
```bash
# For existing databases without Flyway history
flyway -baselineOnMigrate=true migrate
```

---

## Monitoring & Maintenance

### Check Migration Status

```sql
-- View all migrations
SELECT * FROM flyway_schema_history ORDER BY installed_rank;

-- Check for failed migrations
SELECT * FROM flyway_schema_history WHERE success = false;

-- View latest migration
SELECT * FROM flyway_schema_history
ORDER BY installed_rank DESC LIMIT 1;
```

### Database Statistics

```sql
-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## References

- **Database Schema**: `/backend/DATABASE_SCHEMA.md`
- **Entity Definitions**: `/design/uml-diagram.md`
- **Flyway Documentation**: https://flywaydb.org/documentation/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

## Support

For migration-related issues:
- Backend README: `/backend/README.md`
- Database schema documentation: `/backend/DATABASE_SCHEMA.md`
- Flyway troubleshooting section above
