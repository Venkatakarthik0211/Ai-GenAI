-- V9: Update audit_logs action_type constraint to match application enum
-- Author: System
-- Date: 2025-11-16
-- Description: Drops and recreates chk_audit_logs_action_type to include all AuditEventType values

-- Drop the old action_type CHECK constraint
ALTER TABLE audit_logs
DROP CONSTRAINT IF EXISTS chk_audit_logs_action_type;

-- Add new action_type constraint that matches AuditEventType enum from models.py
ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_action_type CHECK (action_type IN (
    -- Authentication Events
    'LOGIN_SUCCESS',
    'LOGIN_FAILED',
    'LOGOUT',
    'TOKEN_REFRESH',

    -- Password Events
    'PASSWORD_CHANGE',
    'PASSWORD_RESET_REQUEST',
    'PASSWORD_RESET_COMPLETE',

    -- Account Events
    'ACCOUNT_CREATED',
    'ACCOUNT_LOCKED',
    'ACCOUNT_UNLOCKED',
    'ACCOUNT_DELETED',
    'ACCOUNT_ENABLED',
    'ACCOUNT_DISABLED',

    -- Email Events
    'EMAIL_VERIFICATION_SENT',
    'EMAIL_VERIFIED',

    -- Profile Events
    'PROFILE_UPDATED',
    'USER_UPDATED',
    'ROLE_CHANGED',

    -- Token Events
    'TOKEN_REVOKED',
    'TOKENS_REVOKED',

    -- MFA Events
    'MFA_ENABLED',
    'MFA_DISABLED',
    'MFA_CODE_VERIFIED',

    -- Session Events
    'SESSION_CREATED',
    'SESSION_TERMINATED'
));

COMMENT ON CONSTRAINT chk_audit_logs_action_type ON audit_logs IS
'Allowed action types from AuditEventType enum';
