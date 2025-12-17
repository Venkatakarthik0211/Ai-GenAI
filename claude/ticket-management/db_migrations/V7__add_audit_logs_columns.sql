-- V7: Add missing columns to audit_logs table and modify constraints
-- Author: System
-- Description: Adds severity, session_id, and details columns; makes action_description nullable; updates status constraint

-- Make action_description nullable (was NOT NULL in V2)
ALTER TABLE audit_logs
ALTER COLUMN action_description DROP NOT NULL;

-- Drop old status CHECK constraint and recreate with FAILURE included
ALTER TABLE audit_logs
DROP CONSTRAINT IF EXISTS chk_audit_logs_status;

ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_status CHECK (status IN ('SUCCESS', 'FAILED', 'FAILURE', 'ERROR'));

-- Add severity column to track log severity levels
ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS severity VARCHAR(20) DEFAULT 'INFO';

-- Add session_id column to link audit logs to user sessions
ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS session_id UUID;

-- Add details column for additional structured information
ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS details JSONB;

-- Add comments
COMMENT ON COLUMN audit_logs.action_description IS 'Human-readable description of the action (nullable)';
COMMENT ON COLUMN audit_logs.severity IS 'Log severity level: INFO, WARNING, ERROR, CRITICAL';
COMMENT ON COLUMN audit_logs.session_id IS 'Reference to user session (if applicable)';
COMMENT ON COLUMN audit_logs.details IS 'Additional structured details about the audit event';
