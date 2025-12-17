-- ============================================================================
-- Flyway Migration V2: Authentication Tables
-- ============================================================================
-- Description: Creates users, refresh_tokens, user_sessions, password_resets, and audit_logs tables
-- Author: Ticket Management System
-- Date: 2025-11-16
-- Reference: /backend/DATABASE_SCHEMA.md (Authentication Tables section)
-- ============================================================================


-- Table: users
-- ============================================================================
-- Purpose: Stores user accounts, authentication credentials, and profile information
-- Row Estimate: 100-10,000 users

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

    -- MFA (Multi-Factor Authentication)
    mfa_enabled             BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret              VARCHAR(255),

    -- Timestamps
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login              TIMESTAMP WITH TIME ZONE,
    last_password_change    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at              TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_users_role CHECK (role IN ('ADMIN', 'MANAGER', 'TEAM_LEAD', 'SENIOR_ENGINEER', 'DEVOPS_ENGINEER', 'END_USER')),
    CONSTRAINT chk_users_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'LOCKED', 'PENDING_ACTIVATION')),
    CONSTRAINT chk_users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_users_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT chk_users_phone_format CHECK (phone_number IS NULL OR phone_number ~* '^\+?[0-9]{10,15}$')
);

-- Indexes for users table
CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_role ON users(role) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_status_active ON users(status, is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_last_login ON users(last_login DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_department ON users(department) WHERE deleted_at IS NULL AND department IS NOT NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Trigger: Auto-update updated_at timestamp
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE users IS 'Stores user accounts, authentication credentials, and profile information';
COMMENT ON COLUMN users.role IS 'User role in the system: ADMIN, MANAGER, TEAM_LEAD, SENIOR_ENGINEER, DEVOPS_ENGINEER, END_USER';
COMMENT ON COLUMN users.status IS 'Account status: ACTIVE, INACTIVE, LOCKED, PENDING_ACTIVATION';
COMMENT ON COLUMN users.mfa_secret IS 'TOTP secret for MFA (Time-based One-Time Password)';


-- Table: refresh_tokens
-- ============================================================================
-- Purpose: Manages JWT refresh tokens with device tracking and revocation
-- Row Estimate: 1,000-50,000 tokens (multiple devices per user)

CREATE TABLE refresh_tokens (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token Information
    token_hash          VARCHAR(255) UNIQUE NOT NULL,
    token_family        UUID NOT NULL,  -- For token rotation detection

    -- Device & Location Information
    device_type         VARCHAR(50),    -- mobile, desktop, tablet
    device_name         VARCHAR(100),
    user_agent          TEXT,
    ip_address          INET,
    location            VARCHAR(255),   -- City, Country

    -- Status & Expiry
    is_revoked          BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at          TIMESTAMP WITH TIME ZONE,
    revoked_reason      VARCHAR(255),
    expires_at          TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at        TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_refresh_tokens_device_type CHECK (device_type IN ('mobile', 'desktop', 'tablet', 'unknown')),
    CONSTRAINT chk_refresh_tokens_expires_at CHECK (expires_at > created_at)
);

-- Indexes for refresh_tokens table
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash) WHERE is_revoked = FALSE;
CREATE INDEX idx_refresh_tokens_token_family ON refresh_tokens(token_family);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at) WHERE is_revoked = FALSE;
CREATE INDEX idx_refresh_tokens_created_at ON refresh_tokens(created_at DESC);

-- Comments
COMMENT ON TABLE refresh_tokens IS 'Manages JWT refresh tokens with device tracking and automatic revocation';
COMMENT ON COLUMN refresh_tokens.token_family IS 'Token family ID for detecting token reuse attacks';


-- Table: user_sessions
-- ============================================================================
-- Purpose: Tracks active user sessions with device and location information
-- Row Estimate: 500-10,000 sessions (concurrent active sessions)

CREATE TABLE user_sessions (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session Information
    session_token       VARCHAR(255) UNIQUE NOT NULL,
    refresh_token_id    UUID REFERENCES refresh_tokens(id) ON DELETE SET NULL,

    -- Device & Location
    device_type         VARCHAR(50),
    device_name         VARCHAR(100),
    user_agent          TEXT,
    ip_address          INET NOT NULL,
    location            VARCHAR(255),

    -- Session Status
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    ended_at            TIMESTAMP WITH TIME ZONE,
    end_reason          VARCHAR(100),  -- logout, timeout, revoked, expired

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Constraints
    CONSTRAINT chk_user_sessions_device_type CHECK (device_type IN ('mobile', 'desktop', 'tablet', 'unknown')),
    CONSTRAINT chk_user_sessions_end_reason CHECK (end_reason IN ('logout', 'timeout', 'revoked', 'expired', 'replaced') OR end_reason IS NULL),
    CONSTRAINT chk_user_sessions_expires_at CHECK (expires_at > created_at)
);

-- Indexes for user_sessions table
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id) WHERE is_active = TRUE;
CREATE INDEX idx_user_sessions_session_token ON user_sessions(session_token) WHERE is_active = TRUE;
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at) WHERE is_active = TRUE;
CREATE INDEX idx_user_sessions_last_activity ON user_sessions(last_activity_at DESC) WHERE is_active = TRUE;
CREATE INDEX idx_user_sessions_ip_address ON user_sessions(ip_address);

-- Comments
COMMENT ON TABLE user_sessions IS 'Tracks active user sessions for security monitoring and concurrent session management';
COMMENT ON COLUMN user_sessions.end_reason IS 'Reason for session termination: logout, timeout, revoked, expired, replaced';


-- Table: password_resets
-- ============================================================================
-- Purpose: Manages password reset tokens with expiration and usage tracking
-- Row Estimate: 100-5,000 tokens (temporary, cleaned regularly)

CREATE TABLE password_resets (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token Information
    token_hash          VARCHAR(255) UNIQUE NOT NULL,
    token_plain         VARCHAR(100) NOT NULL,  -- For email sending (one-time view)

    -- Request Information
    ip_address          INET NOT NULL,
    user_agent          TEXT,

    -- Status
    is_used             BOOLEAN NOT NULL DEFAULT FALSE,
    used_at             TIMESTAMP WITH TIME ZONE,
    expires_at          TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_password_resets_expires_at CHECK (expires_at > created_at)
);

-- Indexes for password_resets table
CREATE INDEX idx_password_resets_user_id ON password_resets(user_id) WHERE is_used = FALSE;
CREATE INDEX idx_password_resets_token_hash ON password_resets(token_hash) WHERE is_used = FALSE;
CREATE INDEX idx_password_resets_expires_at ON password_resets(expires_at) WHERE is_used = FALSE;
CREATE INDEX idx_password_resets_created_at ON password_resets(created_at DESC);

-- Comments
COMMENT ON TABLE password_resets IS 'Manages password reset tokens with automatic expiration (typically 1 hour)';
COMMENT ON COLUMN password_resets.token_plain IS 'Plain text token sent in email (stored temporarily, cleared after use)';


-- Table: audit_logs
-- ============================================================================
-- Purpose: Comprehensive audit trail for security-sensitive operations
-- Row Estimate: 10,000-1,000,000+ logs (grows over time, archiving recommended)

CREATE TABLE audit_logs (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Action Information
    action_type         VARCHAR(50) NOT NULL,  -- LOGIN, LOGOUT, CREATE, UPDATE, DELETE, etc.
    resource_type       VARCHAR(50) NOT NULL,  -- USER, TICKET, COMMENT, etc.
    resource_id         UUID,
    action_description  TEXT NOT NULL,

    -- Request Information
    ip_address          INET,
    user_agent          TEXT,
    request_method      VARCHAR(10),   -- GET, POST, PUT, DELETE
    request_path        VARCHAR(255),

    -- Change Details
    old_values          JSONB,
    new_values          JSONB,

    -- Status
    status              VARCHAR(20) NOT NULL,  -- SUCCESS, FAILED, ERROR
    error_message       TEXT,

    -- Timestamp
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_audit_logs_action_type CHECK (action_type IN (
        'LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'PASSWORD_RESET_REQUESTED', 'PASSWORD_RESET_COMPLETED',
        'CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT',
        'PERMISSION_CHANGE', 'ROLE_CHANGE', 'ACCOUNT_LOCKED', 'ACCOUNT_UNLOCKED',
        'MFA_ENABLED', 'MFA_DISABLED', 'SESSION_REVOKED'
    )),
    CONSTRAINT chk_audit_logs_resource_type CHECK (resource_type IN (
        'USER', 'TICKET', 'COMMENT', 'ATTACHMENT', 'NOTIFICATION',
        'SLA_POLICY', 'ESCALATION', 'SESSION', 'TOKEN', 'SYSTEM'
    )),
    CONSTRAINT chk_audit_logs_status CHECK (status IN ('SUCCESS', 'FAILED', 'ERROR')),
    CONSTRAINT chk_audit_logs_request_method CHECK (request_method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE') OR request_method IS NULL)
);

-- Indexes for audit_logs table
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_ip_address ON audit_logs(ip_address);
CREATE INDEX idx_audit_logs_status ON audit_logs(status) WHERE status IN ('FAILED', 'ERROR');

-- JSONB indexes for efficient querying of change details
CREATE INDEX idx_audit_logs_old_values_gin ON audit_logs USING GIN (old_values);
CREATE INDEX idx_audit_logs_new_values_gin ON audit_logs USING GIN (new_values);

-- Comments
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for all security-sensitive operations and data changes';
COMMENT ON COLUMN audit_logs.action_type IS 'Type of action performed (LOGIN, CREATE, UPDATE, DELETE, etc.)';
COMMENT ON COLUMN audit_logs.resource_type IS 'Type of resource affected (USER, TICKET, COMMENT, etc.)';


-- Insert Default Admin User
-- ============================================================================
-- Creates a default admin account (password should be changed on first login)
-- Default password: Admin@123456 (hashed with bcrypt)

INSERT INTO users (
    id,
    username,
    email,
    password_hash,
    first_name,
    last_name,
    role,
    status,
    is_active,
    is_email_verified,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'admin',
    'admin@ticketmanagement.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEZZGu',  -- bcrypt hash of 'Admin@123456'
    'System',
    'Administrator',
    'ADMIN',
    'ACTIVE',
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);


-- Migration Verification
-- ============================================================================

DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;

    RAISE NOTICE 'V2 Migration completed successfully';
    RAISE NOTICE 'Tables created: users, refresh_tokens, user_sessions, password_resets, audit_logs';
    RAISE NOTICE 'Default admin user created: admin@ticketmanagement.com';
    RAISE NOTICE 'Total users in database: %', user_count;
END $$;
