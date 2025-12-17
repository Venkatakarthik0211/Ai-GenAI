# Database Schema Documentation

## Overview

This document provides comprehensive database schema documentation for the Ticket Management System. The schema is designed to support a DevOps ticketing platform with complete audit trails, notification management, and SLA tracking.

**Database**: PostgreSQL 14+
**ORM**: SQLAlchemy 2.0+
**Migration Tool**: Flyway / Alembic

**Design Reference**: Based on entity definitions from `/design/uml-diagram.md`

---

## Table of Contents

1. [Entity Relationship Diagram](#entity-relationship-diagram)
2. [Core Tables](#core-tables)
3. [Authentication Tables](#authentication-tables)
4. [Supporting Tables](#supporting-tables)
5. [Indexes](#indexes)
6. [Constraints](#constraints)
7. [Enumerations](#enumerations)
8. [Relationships](#relationships)

---

## Entity Relationship Diagram

```
┌──────────────┐
│    users     │
└──────┬───────┘
       │
       │ 1:N (requestor)
       │
       ▼
┌──────────────┐     1:N      ┌──────────────┐
│   tickets    │──────────────▶│   comments   │
└──────┬───────┘               └──────┬───────┘
       │                              │
       │ 1:N                          │ 1:N
       │                              │
       ▼                              ▼
┌──────────────┐               ┌──────────────┐
│ attachments  │               │ attachments  │
└──────────────┘               └──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│ticket_history│
└──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐     1:N      ┌──────────────┐
│escalations   │              │notifications │
└──────────────┘              └──────────────┘
       │                              │
       │ N:1                          │ N:1
       │                              │
       └──────────────┬───────────────┘
                      ▼
               ┌──────────────┐
               │    users     │
               └──────────────┘

┌──────────────┐     1:N      ┌──────────────┐
│ sla_policies │──────────────▶│   tickets    │
└──────────────┘               └──────────────┘
```

---

## Core Tables

### 1. users

**Purpose**: Stores user accounts, authentication credentials, and profile information.

**Reference**: `/design/uml-diagram.md` (lines 43-64)

```sql
CREATE TABLE users (
    -- Primary Key
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Authentication
    username                VARCHAR(50) UNIQUE NOT NULL,
    email                   VARCHAR(255) UNIQUE NOT NULL,
    password_hash           VARCHAR(255) NOT NULL,

    -- Profile Information
    first_name              VARCHAR(100) NOT NULL,
    last_name               VARCHAR(100) NOT NULL,
    phone_number            VARCHAR(20),
    department              VARCHAR(100),

    -- Role & Status
    role                    VARCHAR(30) NOT NULL DEFAULT 'END_USER',
    status                  VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,

    -- Security Fields
    is_email_verified       BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    failed_login_attempts   INTEGER NOT NULL DEFAULT 0,
    account_locked_until    TIMESTAMP WITH TIME ZONE,

    -- MFA (Optional)
    mfa_enabled             BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret              VARCHAR(255),

    -- Timestamps
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login              TIMESTAMP WITH TIME ZONE,
    last_password_change    TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_role CHECK (role IN ('ADMIN', 'MANAGER', 'TEAM_LEAD', 'SENIOR_ENGINEER', 'DEVOPS_ENGINEER', 'END_USER')),
    CONSTRAINT chk_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'LOCKED', 'PENDING_ACTIVATION')),
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status_active ON users(status, is_active);
CREATE INDEX idx_users_last_login ON users(last_login DESC);
CREATE INDEX idx_users_department ON users(department);
```

**Row Count Estimate**: 100-10,000 users (depending on organization size)

---

### 2. tickets

**Purpose**: Core ticket entity storing all ticket information and workflow state.

**Reference**: `/design/uml-diagram.md` (lines 11-39), `/design/state-diagram.md`

```sql
CREATE TABLE tickets (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ticket Identification
    ticket_number       VARCHAR(20) UNIQUE NOT NULL,  -- Format: TKT-2025-00001

    -- Ticket Details
    title               VARCHAR(255) NOT NULL,
    description         TEXT NOT NULL,
    category            VARCHAR(50) NOT NULL,
    priority            VARCHAR(20) NOT NULL,
    status              VARCHAR(30) NOT NULL DEFAULT 'NEW',

    -- User Assignments
    requestor_id        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assignee_id         UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at         TIMESTAMP WITH TIME ZONE,
    closed_at           TIMESTAMP WITH TIME ZONE,
    due_date            TIMESTAMP WITH TIME ZONE,

    -- Additional Fields
    tags                TEXT[],  -- Array of tags for categorization
    estimated_hours     DECIMAL(5,2),
    actual_hours        DECIMAL(5,2),
    resolution_notes    TEXT,

    -- SLA Tracking
    sla_policy_id       UUID REFERENCES sla_policies(id) ON DELETE SET NULL,
    sla_breach          BOOLEAN NOT NULL DEFAULT FALSE,
    sla_breach_time     TIMESTAMP WITH TIME ZONE,

    -- Metadata
    environment         VARCHAR(50),  -- Production, Staging, Development
    affected_services   TEXT[],       -- Array of affected services
    impact_level        VARCHAR(20),  -- Low, Medium, High, Critical

    -- Version Control
    version             INTEGER NOT NULL DEFAULT 1,  -- For optimistic locking

    -- Constraints
    CONSTRAINT chk_category CHECK (category IN (
        'VM_ISSUE', 'NETWORK_ISSUE', 'STORAGE_ISSUE', 'DATABASE_ISSUE',
        'SECURITY_ISSUE', 'ACCESS_REQUEST', 'INFRASTRUCTURE', 'MONITORING_ALERT', 'OTHER'
    )),
    CONSTRAINT chk_priority CHECK (priority IN ('P1_CRITICAL', 'P2_HIGH', 'P3_MEDIUM', 'P4_LOW')),
    CONSTRAINT chk_status CHECK (status IN (
        'NEW', 'OPEN', 'IN_PROGRESS', 'PENDING_INFO', 'RESOLVED', 'CLOSED', 'REOPENED', 'ESCALATED'
    )),
    CONSTRAINT chk_impact CHECK (impact_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

-- Indexes
CREATE INDEX idx_tickets_number ON tickets(ticket_number);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_category ON tickets(category);
CREATE INDEX idx_tickets_requestor ON tickets(requestor_id);
CREATE INDEX idx_tickets_assignee ON tickets(assignee_id);
CREATE INDEX idx_tickets_created ON tickets(created_at DESC);
CREATE INDEX idx_tickets_due_date ON tickets(due_date);
CREATE INDEX idx_tickets_sla_breach ON tickets(sla_breach, status);
CREATE INDEX idx_tickets_status_priority ON tickets(status, priority);

-- Full-text search index
CREATE INDEX idx_tickets_fulltext ON tickets USING GIN(to_tsvector('english', title || ' ' || description));
```

**Row Count Estimate**: 10,000 - 1,000,000+ tickets (high volume)

---

### 3. comments

**Purpose**: Store comments and updates on tickets.

**Reference**: `/design/uml-diagram.md` (lines 68-84)

```sql
CREATE TABLE comments (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    ticket_id           UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,

    -- Comment Content
    content             TEXT NOT NULL,
    is_internal         BOOLEAN NOT NULL DEFAULT FALSE,  -- Internal notes vs public comments

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP WITH TIME ZONE,  -- Soft delete

    -- Metadata
    edited              BOOLEAN NOT NULL DEFAULT FALSE,
    edit_count          INTEGER NOT NULL DEFAULT 0,

    -- Constraints
    CONSTRAINT chk_content_not_empty CHECK (LENGTH(TRIM(content)) > 0)
);

-- Indexes
CREATE INDEX idx_comments_ticket ON comments(ticket_id, created_at DESC);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_created ON comments(created_at DESC);
CREATE INDEX idx_comments_internal ON comments(is_internal);
```

**Row Count Estimate**: 50,000 - 5,000,000+ comments

---

### 4. attachments

**Purpose**: Store file attachment metadata for tickets and comments.

**Reference**: `/design/uml-diagram.md` (lines 88-104)

```sql
CREATE TABLE attachments (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- File Information
    file_name           VARCHAR(255) NOT NULL,
    file_type           VARCHAR(100) NOT NULL,  -- MIME type
    file_size           BIGINT NOT NULL,        -- Size in bytes
    file_path           VARCHAR(500) NOT NULL,  -- Storage path or S3 key
    file_hash           VARCHAR(64),            -- SHA-256 hash for deduplication

    -- Relationships
    ticket_id           UUID REFERENCES tickets(id) ON DELETE CASCADE,
    comment_id          UUID REFERENCES comments(id) ON DELETE CASCADE,
    uploaded_by         UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,

    -- Metadata
    uploaded_at         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    storage_provider    VARCHAR(50) NOT NULL DEFAULT 'local',  -- local, s3, azure, gcs
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,

    -- Constraints
    CONSTRAINT chk_file_size CHECK (file_size > 0 AND file_size <= 52428800),  -- Max 50MB
    CONSTRAINT chk_attachment_parent CHECK (
        (ticket_id IS NOT NULL AND comment_id IS NULL) OR
        (ticket_id IS NULL AND comment_id IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_attachments_ticket ON attachments(ticket_id);
CREATE INDEX idx_attachments_comment ON attachments(comment_id);
CREATE INDEX idx_attachments_user ON attachments(uploaded_by);
CREATE INDEX idx_attachments_hash ON attachments(file_hash);
CREATE INDEX idx_attachments_uploaded ON attachments(uploaded_at DESC);
```

**Row Count Estimate**: 20,000 - 2,000,000+ attachments

---

### 5. ticket_history

**Purpose**: Comprehensive audit trail of all ticket changes.

**Reference**: `/design/uml-diagram.md` (lines 108-122)

```sql
CREATE TABLE ticket_history (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    ticket_id           UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Change Information
    action              VARCHAR(50) NOT NULL,  -- CREATED, STATUS_CHANGED, ASSIGNED, etc.
    field_changed       VARCHAR(100),          -- Field name that was changed
    old_value           TEXT,                  -- Previous value (JSON string)
    new_value           TEXT,                  -- New value (JSON string)

    -- Context
    change_reason       TEXT,                  -- Optional reason for change
    ip_address          VARCHAR(45),
    user_agent          TEXT,

    -- Timestamp
    timestamp           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_action CHECK (action IN (
        'CREATED', 'STATUS_CHANGED', 'PRIORITY_CHANGED', 'ASSIGNED',
        'REASSIGNED', 'ESCALATED', 'COMMENT_ADDED', 'ATTACHMENT_ADDED',
        'FIELD_UPDATED', 'CLOSED', 'REOPENED'
    ))
);

-- Indexes
CREATE INDEX idx_history_ticket ON ticket_history(ticket_id, timestamp DESC);
CREATE INDEX idx_history_user ON ticket_history(user_id);
CREATE INDEX idx_history_action ON ticket_history(action);
CREATE INDEX idx_history_timestamp ON ticket_history(timestamp DESC);
CREATE INDEX idx_history_field ON ticket_history(field_changed);

-- Partitioning (for high volume)
-- Consider partitioning by timestamp (monthly) for large datasets
```

**Row Count Estimate**: 100,000 - 10,000,000+ history records

---

### 6. notifications

**Purpose**: Track all notifications sent to users.

**Reference**: `/design/uml-diagram.md` (lines 127-142)

```sql
CREATE TABLE notifications (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ticket_id           UUID REFERENCES tickets(id) ON DELETE CASCADE,

    -- Notification Details
    type                VARCHAR(50) NOT NULL,
    channel             VARCHAR(20) NOT NULL,
    subject             VARCHAR(255),
    message             TEXT NOT NULL,

    -- Delivery Status
    status              VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    sent_at             TIMESTAMP WITH TIME ZONE,
    delivered_at        TIMESTAMP WITH TIME ZONE,
    read_at             TIMESTAMP WITH TIME ZONE,
    failed_reason       TEXT,
    retry_count         INTEGER NOT NULL DEFAULT 0,

    -- Metadata
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP WITH TIME ZONE,
    priority            VARCHAR(20) NOT NULL DEFAULT 'NORMAL',

    -- External IDs (for tracking)
    external_id         VARCHAR(255),  -- Email message ID, SMS ID, etc.

    -- Constraints
    CONSTRAINT chk_notification_type CHECK (type IN (
        'TICKET_CREATED', 'TICKET_ASSIGNED', 'STATUS_CHANGED', 'COMMENT_ADDED',
        'ESCALATED', 'SLA_BREACH', 'RESOLUTION_REQUEST', 'TICKET_CLOSED'
    )),
    CONSTRAINT chk_channel CHECK (channel IN ('EMAIL', 'SMS', 'IN_APP', 'SLACK')),
    CONSTRAINT chk_status CHECK (status IN ('PENDING', 'SENT', 'DELIVERED', 'FAILED', 'READ')),
    CONSTRAINT chk_priority CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT'))
);

-- Indexes
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_ticket ON notifications(ticket_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_channel ON notifications(channel);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_retry ON notifications(status, retry_count) WHERE status = 'FAILED';
```

**Row Count Estimate**: 50,000 - 5,000,000+ notifications

---

### 7. sla_policies

**Purpose**: Define SLA policies for different ticket categories and priorities.

**Reference**: `/design/uml-diagram.md` (lines 146-161)

```sql
CREATE TABLE sla_policies (
    -- Primary Key
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Policy Identification
    name                    VARCHAR(100) NOT NULL,
    description             TEXT,

    -- Policy Criteria
    priority                VARCHAR(20) NOT NULL,
    category                VARCHAR(50),  -- NULL means applies to all categories

    -- Time Limits (in minutes)
    response_time_minutes   INTEGER NOT NULL,
    resolution_time_minutes INTEGER NOT NULL,
    escalation_threshold_minutes INTEGER,

    -- Status
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from          DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_until         DATE,

    -- Business Hours
    business_hours_only     BOOLEAN NOT NULL DEFAULT TRUE,
    business_start_hour     INTEGER DEFAULT 9,   -- 9 AM
    business_end_hour       INTEGER DEFAULT 17,  -- 5 PM
    include_weekends        BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_priority CHECK (priority IN ('P1_CRITICAL', 'P2_HIGH', 'P3_MEDIUM', 'P4_LOW')),
    CONSTRAINT chk_response_time CHECK (response_time_minutes > 0),
    CONSTRAINT chk_resolution_time CHECK (resolution_time_minutes > response_time_minutes),
    CONSTRAINT chk_business_hours CHECK (
        business_start_hour >= 0 AND business_start_hour < 24 AND
        business_end_hour > business_start_hour AND business_end_hour <= 24
    ),
    CONSTRAINT uq_sla_priority_category UNIQUE(priority, category, effective_from)
);

-- Indexes
CREATE INDEX idx_sla_priority ON sla_policies(priority);
CREATE INDEX idx_sla_category ON sla_policies(category);
CREATE INDEX idx_sla_active ON sla_policies(is_active);
CREATE INDEX idx_sla_effective ON sla_policies(effective_from, effective_until);
```

**Row Count Estimate**: 10-100 SLA policies

---

### 8. escalations

**Purpose**: Track ticket escalations and escalation paths.

**Reference**: `/design/uml-diagram.md` (lines 165-180)

```sql
CREATE TABLE escalations (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    ticket_id           UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    from_user_id        UUID REFERENCES users(id) ON DELETE SET NULL,
    to_user_id          UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Escalation Details
    reason              TEXT NOT NULL,
    escalation_level    INTEGER NOT NULL DEFAULT 1,
    escalation_type     VARCHAR(30) NOT NULL,

    -- Timestamps
    escalated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at     TIMESTAMP WITH TIME ZONE,
    resolved_at         TIMESTAMP WITH TIME ZONE,

    -- Status
    status              VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    resolution_notes    TEXT,

    -- Constraints
    CONSTRAINT chk_escalation_level CHECK (escalation_level >= 1 AND escalation_level <= 5),
    CONSTRAINT chk_escalation_type CHECK (escalation_type IN (
        'SLA_BREACH', 'MANUAL', 'COMPLEXITY', 'MULTIPLE_REOPENS', 'CRITICAL_PRIORITY'
    )),
    CONSTRAINT chk_escalation_status CHECK (status IN ('PENDING', 'ACKNOWLEDGED', 'RESOLVED', 'CANCELLED'))
);

-- Indexes
CREATE INDEX idx_escalations_ticket ON escalations(ticket_id, escalated_at DESC);
CREATE INDEX idx_escalations_from_user ON escalations(from_user_id);
CREATE INDEX idx_escalations_to_user ON escalations(to_user_id);
CREATE INDEX idx_escalations_status ON escalations(status);
CREATE INDEX idx_escalations_level ON escalations(escalation_level);
```

**Row Count Estimate**: 5,000 - 500,000+ escalations

---

## Authentication Tables

### 9. refresh_tokens

**Purpose**: Store JWT refresh tokens for token rotation and session management.

```sql
CREATE TABLE refresh_tokens (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token Details
    token               VARCHAR(500) UNIQUE NOT NULL,
    expires_at          TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked          BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at          TIMESTAMP WITH TIME ZONE,

    -- Device Information
    device_info         TEXT,
    ip_address          VARCHAR(45),
    user_agent          TEXT,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at        TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_expires_future CHECK (expires_at > created_at)
);

-- Indexes
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_active ON refresh_tokens(user_id, is_revoked) WHERE is_revoked = FALSE;

-- Cleanup expired tokens periodically
CREATE INDEX idx_refresh_tokens_cleanup ON refresh_tokens(expires_at) WHERE is_revoked = FALSE;
```

**Row Count Estimate**: 1,000 - 50,000 tokens (active sessions)

---

### 10. user_sessions

**Purpose**: Track active user sessions for security and monitoring.

```sql
CREATE TABLE user_sessions (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session Details
    session_token       VARCHAR(255) UNIQUE NOT NULL,
    ip_address          VARCHAR(45),
    user_agent          TEXT,
    device_info         TEXT,
    location            VARCHAR(255),

    -- Session Lifecycle
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,

    -- Constraints
    CONSTRAINT chk_session_expires CHECK (expires_at > created_at)
);

-- Indexes
CREATE INDEX idx_sessions_user ON user_sessions(user_id, is_active);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active, last_activity_at);
```

**Row Count Estimate**: 500 - 10,000 active sessions

---

### 11. password_resets

**Purpose**: Manage password reset tokens and requests.

```sql
CREATE TABLE password_resets (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token Details
    token               VARCHAR(255) UNIQUE NOT NULL,
    expires_at          TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used             BOOLEAN NOT NULL DEFAULT FALSE,
    used_at             TIMESTAMP WITH TIME ZONE,

    -- Security
    ip_address          VARCHAR(45),

    -- Timestamp
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_reset_expires CHECK (expires_at > created_at)
);

-- Indexes
CREATE INDEX idx_password_resets_user ON password_resets(user_id);
CREATE INDEX idx_password_resets_token ON password_resets(token);
CREATE INDEX idx_password_resets_expires ON password_resets(expires_at);
CREATE INDEX idx_password_resets_active ON password_resets(is_used, expires_at);
```

**Row Count Estimate**: 100 - 10,000 reset requests

---

### 12. audit_logs

**Purpose**: Security audit trail for authentication and authorization events.

```sql
CREATE TABLE audit_logs (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Event Details
    event_type          VARCHAR(50) NOT NULL,
    event_status        VARCHAR(20) NOT NULL,
    event_message       TEXT,

    -- Context Information
    ip_address          VARCHAR(45),
    user_agent          TEXT,
    resource_accessed   VARCHAR(255),

    -- Additional Metadata (JSON)
    metadata            JSONB,

    -- Timestamp
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_event_type CHECK (event_type IN (
        'LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'PASSWORD_CHANGE', 'PASSWORD_RESET_REQUEST',
        'PASSWORD_RESET_COMPLETE', 'EMAIL_VERIFICATION', 'ACCOUNT_LOCKED',
        'ACCOUNT_UNLOCKED', 'ROLE_CHANGED', 'PROFILE_UPDATED', 'MFA_ENABLED', 'MFA_DISABLED'
    )),
    CONSTRAINT chk_event_status CHECK (event_status IN ('SUCCESS', 'FAILURE', 'BLOCKED', 'WARNING'))
);

-- Indexes
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_status ON audit_logs(event_status);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_ip ON audit_logs(ip_address, created_at DESC);

-- GIN index for JSONB metadata queries
CREATE INDEX idx_audit_logs_metadata ON audit_logs USING GIN(metadata);

-- Partitioning recommended for high volume (monthly partitions)
```

**Row Count Estimate**: 100,000 - 10,000,000+ audit records

---

## Enumerations

### User Roles
```sql
-- UserRole enumeration (from /design/uml-diagram.md)
'ADMIN'             -- System administrator
'MANAGER'           -- Department/team manager
'TEAM_LEAD'         -- Team lead/supervisor
'SENIOR_ENGINEER'   -- Senior technical staff
'DEVOPS_ENGINEER'   -- DevOps engineer
'END_USER'          -- End user/requestor
```

### Ticket Categories
```sql
-- TicketCategory enumeration (from /design/uml-diagram.md)
'VM_ISSUE'          -- Virtual machine issues
'NETWORK_ISSUE'     -- Network connectivity/configuration
'STORAGE_ISSUE'     -- Storage/disk issues
'DATABASE_ISSUE'    -- Database problems
'SECURITY_ISSUE'    -- Security incidents/vulnerabilities
'ACCESS_REQUEST'    -- Access/permission requests
'INFRASTRUCTURE'    -- General infrastructure
'MONITORING_ALERT'  -- Monitoring/alerting
'OTHER'             -- Other issues
```

### Ticket Priorities
```sql
-- Priority enumeration (from /design/uml-diagram.md)
'P1_CRITICAL'       -- Critical (SLA: 5min response, 4hr resolution)
'P2_HIGH'           -- High (SLA: 30min response, 8hr resolution)
'P3_MEDIUM'         -- Medium (SLA: 2hr response, 24hr resolution)
'P4_LOW'            -- Low (SLA: 1day response, 5day resolution)
```

### Ticket Status
```sql
-- TicketStatus enumeration (from /design/state-diagram.md)
'NEW'               -- Newly created ticket
'OPEN'              -- Assigned and awaiting work
'IN_PROGRESS'       -- Actively being worked on
'PENDING_INFO'      -- Waiting for information
'RESOLVED'          -- Fixed, awaiting verification
'CLOSED'            -- Closed and verified
'REOPENED'          -- Reopened after closure
'ESCALATED'         -- Escalated (overlay state)
```

### Notification Types
```sql
-- NotificationType enumeration (from /design/uml-diagram.md)
'TICKET_CREATED'        -- New ticket created
'TICKET_ASSIGNED'       -- Ticket assigned to engineer
'STATUS_CHANGED'        -- Ticket status changed
'COMMENT_ADDED'         -- New comment added
'ESCALATED'             -- Ticket escalated
'SLA_BREACH'            -- SLA breach warning/notification
'RESOLUTION_REQUEST'    -- Resolution verification request
'TICKET_CLOSED'         -- Ticket closed
```

### Notification Channels
```sql
-- Channel enumeration (from /design/uml-diagram.md)
'EMAIL'             -- Email notification
'SMS'               -- SMS notification
'IN_APP'            -- In-application notification
'SLACK'             -- Slack message
```

---

## Relationships

### One-to-Many (1:N) Relationships

```sql
-- User → Tickets (as requestor)
users.id → tickets.requestor_id

-- User → Tickets (as assignee)
users.id → tickets.assignee_id

-- Ticket → Comments
tickets.id → comments.ticket_id

-- Ticket → Attachments
tickets.id → attachments.ticket_id

-- Comment → Attachments
comments.id → attachments.comment_id

-- Ticket → Ticket History
tickets.id → ticket_history.ticket_id

-- Ticket → Notifications
tickets.id → notifications.ticket_id

-- User → Notifications
users.id → notifications.user_id

-- Ticket → Escalations
tickets.id → escalations.ticket_id

-- SLA Policy → Tickets
sla_policies.id → tickets.sla_policy_id

-- User → Refresh Tokens
users.id → refresh_tokens.user_id

-- User → Sessions
users.id → user_sessions.user_id

-- User → Audit Logs
users.id → audit_logs.user_id
```

---

## Indexes

### Performance Optimization Indexes

```sql
-- Composite indexes for common queries

-- Find tickets by status and priority
CREATE INDEX idx_tickets_status_priority_created
ON tickets(status, priority, created_at DESC);

-- Find unassigned tickets by category
CREATE INDEX idx_tickets_unassigned_category
ON tickets(category, assignee_id) WHERE assignee_id IS NULL;

-- Find overdue tickets
CREATE INDEX idx_tickets_overdue
ON tickets(due_date, status) WHERE status NOT IN ('CLOSED', 'RESOLVED');

-- Find user's open tickets
CREATE INDEX idx_tickets_user_open
ON tickets(requestor_id, status, created_at DESC) WHERE status NOT IN ('CLOSED');

-- Find engineer's assigned tickets
CREATE INDEX idx_tickets_assignee_active
ON tickets(assignee_id, status, priority) WHERE status IN ('OPEN', 'IN_PROGRESS');

-- SLA breach monitoring
CREATE INDEX idx_tickets_sla_monitoring
ON tickets(sla_breach, status, due_date) WHERE status NOT IN ('CLOSED', 'RESOLVED');

-- Notification delivery status
CREATE INDEX idx_notifications_pending_retry
ON notifications(status, retry_count, created_at) WHERE status IN ('PENDING', 'FAILED');

-- Active escalations
CREATE INDEX idx_escalations_active
ON escalations(status, to_user_id, escalated_at) WHERE status = 'PENDING';
```

---

## Constraints

### Foreign Key Constraints

All foreign key constraints include appropriate `ON DELETE` actions:

- `ON DELETE CASCADE`: Child records deleted when parent is deleted
  - Used for: comments, attachments, ticket_history, notifications (when ticket deleted)

- `ON DELETE SET NULL`: Foreign key set to NULL when parent is deleted
  - Used for: ticket assignee, comment author (preserve records even if user deleted)

- `ON DELETE RESTRICT`: Prevent deletion if referenced
  - Used for: ticket requestor (can't delete user who created tickets)

### Check Constraints

All enumeration fields have CHECK constraints to ensure data integrity at database level, matching the application-level enumerations.

---

## Database Maintenance

### Recommended Maintenance Tasks

```sql
-- 1. Vacuum and analyze (weekly)
VACUUM ANALYZE;

-- 2. Reindex (monthly)
REINDEX DATABASE ticket_management;

-- 3. Clean up expired tokens (daily cron)
DELETE FROM refresh_tokens
WHERE expires_at < NOW() - INTERVAL '7 days' AND is_revoked = TRUE;

DELETE FROM password_resets
WHERE expires_at < NOW() - INTERVAL '7 days';

-- 4. Archive old audit logs (monthly)
-- Move records older than 1 year to archive table
INSERT INTO audit_logs_archive
SELECT * FROM audit_logs WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '1 year';

-- 5. Update table statistics (daily)
ANALYZE tickets;
ANALYZE ticket_history;
ANALYZE notifications;
```

### Partitioning Strategy

For high-volume tables, consider range partitioning:

```sql
-- Example: Partition ticket_history by month
CREATE TABLE ticket_history (
    -- columns as defined above
) PARTITION BY RANGE (created_at);

CREATE TABLE ticket_history_2025_01 PARTITION OF ticket_history
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE ticket_history_2025_02 PARTITION OF ticket_history
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Create partitions automatically using pg_partman extension
```

---

## Migration Files

See `/backend/db_migrations/README.md` for Flyway migration scripts that create this schema.

---

## Design References

- **Entity Definitions**: `/design/uml-diagram.md`
- **State Management**: `/design/state-diagram.md`
- **Relationships**: `/design/uml-diagram.md` (lines 255-337)
- **Enumerations**: `/design/uml-diagram.md` (lines 185-253)

---

## Schema Version

**Version**: 1.0
**Last Updated**: 2025-01-16
**Compatible with**: PostgreSQL 14+

---

## Support

For schema-related questions or modifications, refer to:
- Backend README: `/backend/README.md`
- Migration documentation: `/backend/db_migrations/README.md`
- Architecture documentation: `/backend/ARCHITECTURE.md`
