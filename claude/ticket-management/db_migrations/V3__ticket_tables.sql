-- ============================================================================
-- Flyway Migration V3: Ticket Management Tables
-- ============================================================================
-- Description: Creates tickets, comments, attachments, and ticket_history tables
-- Author: Ticket Management System
-- Date: 2025-11-16
-- Reference: /backend/DATABASE_SCHEMA.md (Core Tables section), /design/state-diagram.md
-- ============================================================================


-- Table: tickets
-- ============================================================================
-- Purpose: Core ticket entity storing all ticket information and workflow state
-- Row Estimate: 10,000-1,000,000+ tickets (primary application data)

CREATE TABLE tickets (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Unique Identifier
    ticket_number       VARCHAR(20) UNIQUE NOT NULL DEFAULT generate_ticket_number(),

    -- Basic Information
    title               VARCHAR(255) NOT NULL,
    description         TEXT NOT NULL,
    category            VARCHAR(50) NOT NULL,
    subcategory         VARCHAR(50),

    -- Status & Priority
    status              VARCHAR(30) NOT NULL DEFAULT 'NEW',
    priority            VARCHAR(10) NOT NULL DEFAULT 'P3',

    -- Assignment
    requestor_id        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assigned_to         UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_team       VARCHAR(100),

    -- SLA & Tracking
    sla_policy_id       UUID,  -- Foreign key will be added in V5 after sla_policies table is created
    due_date            TIMESTAMP WITH TIME ZONE,
    response_due_at     TIMESTAMP WITH TIME ZONE,
    resolution_due_at   TIMESTAMP WITH TIME ZONE,
    first_response_at   TIMESTAMP WITH TIME ZONE,
    resolved_at         TIMESTAMP WITH TIME ZONE,

    -- Closure Information
    resolution_notes    TEXT,
    closed_by           UUID REFERENCES users(id) ON DELETE SET NULL,
    closure_code        VARCHAR(50),

    -- Metadata
    tags                TEXT[],
    environment         VARCHAR(50),  -- DEV, QA, STAGING, PRODUCTION
    affected_service    VARCHAR(100),
    impact_level        VARCHAR(20),  -- LOW, MEDIUM, HIGH, CRITICAL

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by          UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at          TIMESTAMP WITH TIME ZONE,

    -- Full-text Search
    search_vector       TSVECTOR,

    -- Constraints
    CONSTRAINT chk_tickets_status CHECK (status IN (
        'NEW', 'OPEN', 'IN_PROGRESS', 'PENDING_INFO',
        'RESOLVED', 'CLOSED', 'REOPENED', 'ESCALATED'
    )),
    CONSTRAINT chk_tickets_priority CHECK (priority IN ('P1', 'P2', 'P3', 'P4')),
    CONSTRAINT chk_tickets_category CHECK (category IN (
        'INCIDENT', 'SERVICE_REQUEST', 'CHANGE_REQUEST', 'PROBLEM', 'MAINTENANCE'
    )),
    CONSTRAINT chk_tickets_environment CHECK (environment IN (
        'DEV', 'QA', 'STAGING', 'PRODUCTION', 'DR', 'UNKNOWN'
    ) OR environment IS NULL),
    CONSTRAINT chk_tickets_impact_level CHECK (impact_level IN (
        'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    ) OR impact_level IS NULL),
    CONSTRAINT chk_tickets_closure_code CHECK (closure_code IN (
        'RESOLVED', 'WORKAROUND', 'DUPLICATE', 'CANNOT_REPRODUCE',
        'NOT_AN_ISSUE', 'CANCELLED', 'DEFERRED'
    ) OR closure_code IS NULL),
    CONSTRAINT chk_tickets_title_length CHECK (LENGTH(title) >= 10),
    CONSTRAINT chk_tickets_description_length CHECK (LENGTH(description) >= 20)
);

-- Indexes for tickets table
CREATE INDEX idx_tickets_ticket_number ON tickets(ticket_number);
CREATE INDEX idx_tickets_status ON tickets(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_priority ON tickets(priority) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_category ON tickets(category) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_requestor_id ON tickets(requestor_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX idx_tickets_assigned_team ON tickets(assigned_team) WHERE assigned_team IS NOT NULL;
CREATE INDEX idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX idx_tickets_updated_at ON tickets(updated_at DESC);
CREATE INDEX idx_tickets_due_date ON tickets(due_date) WHERE status NOT IN ('CLOSED', 'RESOLVED');
CREATE INDEX idx_tickets_tags_gin ON tickets USING GIN (tags);

-- Full-text search index
CREATE INDEX idx_tickets_search_vector ON tickets USING GIN (search_vector);

-- Composite indexes for common queries
CREATE INDEX idx_tickets_status_priority ON tickets(status, priority) WHERE deleted_at IS NULL;
CREATE INDEX idx_tickets_assigned_status ON tickets(assigned_to, status) WHERE deleted_at IS NULL AND assigned_to IS NOT NULL;

-- Trigger: Auto-update updated_at timestamp
CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Log ticket changes to history
CREATE TRIGGER trg_tickets_history
    AFTER UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION log_ticket_history();

-- Trigger: Update full-text search vector
CREATE OR REPLACE FUNCTION update_tickets_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.ticket_number, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.resolution_notes, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tickets_search_vector
    BEFORE INSERT OR UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_tickets_search_vector();

-- Comments
COMMENT ON TABLE tickets IS 'Core ticket entity with complete workflow state machine and SLA tracking';
COMMENT ON COLUMN tickets.status IS 'Ticket workflow status: NEW, OPEN, IN_PROGRESS, PENDING_INFO, RESOLVED, CLOSED, REOPENED, ESCALATED';
COMMENT ON COLUMN tickets.priority IS 'Ticket priority level: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)';
COMMENT ON COLUMN tickets.search_vector IS 'Full-text search vector for fast ticket searching';


-- Table: comments
-- ============================================================================
-- Purpose: Stores comments and updates on tickets with rich text support
-- Row Estimate: 50,000-5,000,000+ comments (5-10 per ticket average)

CREATE TABLE comments (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    ticket_id           UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    author_id           UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,

    -- Comment Content
    content             TEXT NOT NULL,
    comment_type        VARCHAR(30) NOT NULL DEFAULT 'COMMENT',

    -- Visibility & Privacy
    is_internal         BOOLEAN NOT NULL DEFAULT FALSE,
    is_system_generated BOOLEAN NOT NULL DEFAULT FALSE,

    -- Attachments
    has_attachments     BOOLEAN NOT NULL DEFAULT FALSE,

    -- Metadata
    edited_at           TIMESTAMP WITH TIME ZONE,
    edited_by           UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_comments_type CHECK (comment_type IN (
        'COMMENT', 'NOTE', 'SOLUTION', 'WORKAROUND',
        'STATUS_CHANGE', 'ASSIGNMENT_CHANGE', 'ESCALATION'
    )),
    CONSTRAINT chk_comments_content_length CHECK (LENGTH(content) >= 1)
);

-- Indexes for comments table
CREATE INDEX idx_comments_ticket_id ON comments(ticket_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);
CREATE INDEX idx_comments_type ON comments(comment_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_comments_internal ON comments(is_internal) WHERE deleted_at IS NULL AND is_internal = TRUE;

-- Full-text search on comments
CREATE INDEX idx_comments_content_fulltext ON comments USING GIN (to_tsvector('english', content)) WHERE deleted_at IS NULL;

-- Comments
COMMENT ON TABLE comments IS 'Stores all comments and updates on tickets with support for internal notes';
COMMENT ON COLUMN comments.is_internal IS 'Internal comments visible only to support team, not end users';
COMMENT ON COLUMN comments.comment_type IS 'Type of comment: COMMENT, NOTE, SOLUTION, WORKAROUND, STATUS_CHANGE, etc.';


-- Table: attachments
-- ============================================================================
-- Purpose: Manages file attachments for tickets and comments
-- Row Estimate: 20,000-500,000+ attachments (2-5 per ticket average)

CREATE TABLE attachments (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys (one of these must be set)
    ticket_id           UUID REFERENCES tickets(id) ON DELETE CASCADE,
    comment_id          UUID REFERENCES comments(id) ON DELETE CASCADE,

    -- Uploader
    uploaded_by         UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,

    -- File Information
    file_name           VARCHAR(255) NOT NULL,
    file_path           VARCHAR(500) NOT NULL,
    file_size           BIGINT NOT NULL,  -- Size in bytes
    file_type           VARCHAR(100) NOT NULL,  -- MIME type
    file_extension      VARCHAR(20),

    -- Storage Information
    storage_type        VARCHAR(30) NOT NULL DEFAULT 'LOCAL',  -- LOCAL, S3, AZURE_BLOB
    storage_location    VARCHAR(500) NOT NULL,
    storage_key         VARCHAR(255),

    -- Security
    is_scanned          BOOLEAN NOT NULL DEFAULT FALSE,
    scan_status         VARCHAR(30),  -- PENDING, CLEAN, INFECTED, ERROR
    scan_result         TEXT,

    -- Metadata
    content_hash        VARCHAR(64),  -- SHA-256 hash for deduplication
    thumbnail_path      VARCHAR(500),

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_attachments_reference CHECK (
        (ticket_id IS NOT NULL AND comment_id IS NULL) OR
        (ticket_id IS NULL AND comment_id IS NOT NULL)
    ),
    CONSTRAINT chk_attachments_file_size CHECK (file_size > 0 AND file_size <= 52428800),  -- Max 50MB
    CONSTRAINT chk_attachments_storage_type CHECK (storage_type IN ('LOCAL', 'S3', 'AZURE_BLOB', 'GCS')),
    CONSTRAINT chk_attachments_scan_status CHECK (scan_status IN ('PENDING', 'CLEAN', 'INFECTED', 'ERROR', 'SKIPPED') OR scan_status IS NULL)
);

-- Indexes for attachments table
CREATE INDEX idx_attachments_ticket_id ON attachments(ticket_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_attachments_comment_id ON attachments(comment_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_attachments_uploaded_by ON attachments(uploaded_by);
CREATE INDEX idx_attachments_created_at ON attachments(created_at DESC);
CREATE INDEX idx_attachments_file_type ON attachments(file_type);
CREATE INDEX idx_attachments_content_hash ON attachments(content_hash) WHERE content_hash IS NOT NULL;
CREATE INDEX idx_attachments_scan_status ON attachments(scan_status) WHERE scan_status IN ('PENDING', 'INFECTED');

-- Comments
COMMENT ON TABLE attachments IS 'Manages file attachments for tickets and comments with virus scanning support';
COMMENT ON COLUMN attachments.file_size IS 'File size in bytes (max 50MB = 52428800 bytes)';
COMMENT ON COLUMN attachments.content_hash IS 'SHA-256 hash for file deduplication and integrity verification';


-- Table: ticket_history
-- ============================================================================
-- Purpose: Complete audit trail of all changes made to tickets
-- Row Estimate: 100,000-10,000,000+ history records (10-100 per ticket)

CREATE TABLE ticket_history (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    ticket_id           UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    changed_by          UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Change Information
    change_type         VARCHAR(50) NOT NULL,
    field_name          VARCHAR(100),
    old_value           TEXT,
    new_value           TEXT,

    -- Additional Context
    change_description  TEXT,
    change_metadata     JSONB,

    -- Timestamp
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_ticket_history_change_type CHECK (change_type IN (
        'CREATED', 'STATUS_CHANGE', 'PRIORITY_CHANGE', 'ASSIGNMENT_CHANGE',
        'UPDATE', 'COMMENT_ADDED', 'ATTACHMENT_ADDED', 'ESCALATED',
        'REOPENED', 'RESOLVED', 'CLOSED', 'SLA_BREACH', 'DUE_DATE_CHANGE'
    ))
);

-- Indexes for ticket_history table
CREATE INDEX idx_ticket_history_ticket_id ON ticket_history(ticket_id, created_at DESC);
CREATE INDEX idx_ticket_history_changed_by ON ticket_history(changed_by);
CREATE INDEX idx_ticket_history_change_type ON ticket_history(change_type, created_at DESC);
CREATE INDEX idx_ticket_history_created_at ON ticket_history(created_at DESC);
CREATE INDEX idx_ticket_history_field_name ON ticket_history(field_name) WHERE field_name IS NOT NULL;

-- JSONB index for metadata queries
CREATE INDEX idx_ticket_history_metadata_gin ON ticket_history USING GIN (change_metadata);

-- Comments
COMMENT ON TABLE ticket_history IS 'Complete audit trail of all changes made to tickets for compliance and tracking';
COMMENT ON COLUMN ticket_history.change_type IS 'Type of change: CREATED, STATUS_CHANGE, PRIORITY_CHANGE, ASSIGNMENT_CHANGE, etc.';
COMMENT ON COLUMN ticket_history.change_metadata IS 'Additional JSON metadata about the change (e.g., previous assignee details, SLA breach info)';


-- Migration Verification
-- ============================================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('tickets', 'comments', 'attachments', 'ticket_history');

    RAISE NOTICE 'V3 Migration completed successfully';
    RAISE NOTICE 'Tables created: tickets, comments, attachments, ticket_history';
    RAISE NOTICE 'Total ticket-related tables: %', table_count;
    RAISE NOTICE 'Triggers created: updated_at, history logging, full-text search';
END $$;
