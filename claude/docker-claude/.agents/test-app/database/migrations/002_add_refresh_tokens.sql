-- Migration: 002_add_refresh_tokens
-- Description: Create refresh_tokens table for JWT refresh token management
-- Author: UserHub Team
-- Date: 2024-01-15
-- Note: This is a future migration example for token revocation and tracking

-- Forward Migration
-- ==================

BEGIN;

-- Create refresh_tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    is_revoked BOOLEAN DEFAULT FALSE NOT NULL,
    user_agent TEXT,
    ip_address INET,

    -- Constraints
    CONSTRAINT refresh_tokens_expires_check CHECK (expires_at > created_at)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_is_revoked ON refresh_tokens(is_revoked) WHERE is_revoked = false;

-- Create partial index for active tokens only
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_active ON refresh_tokens(user_id, expires_at)
WHERE is_revoked = false AND expires_at > CURRENT_TIMESTAMP;

-- Add trigger for automatic cleanup of expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS TRIGGER AS $$
BEGIN
    -- Delete expired tokens older than 30 days
    DELETE FROM refresh_tokens
    WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to cleanup expired tokens periodically
DROP TRIGGER IF EXISTS trigger_cleanup_expired_tokens ON refresh_tokens;
CREATE TRIGGER trigger_cleanup_expired_tokens
    AFTER INSERT ON refresh_tokens
    EXECUTE FUNCTION cleanup_expired_tokens();

-- Add comments
COMMENT ON TABLE refresh_tokens IS 'Stores JWT refresh tokens for user sessions';
COMMENT ON COLUMN refresh_tokens.id IS 'Unique token identifier';
COMMENT ON COLUMN refresh_tokens.user_id IS 'Reference to the user who owns this token';
COMMENT ON COLUMN refresh_tokens.token_hash IS 'Hashed refresh token for security';
COMMENT ON COLUMN refresh_tokens.expires_at IS 'Token expiration timestamp';
COMMENT ON COLUMN refresh_tokens.created_at IS 'Token creation timestamp';
COMMENT ON COLUMN refresh_tokens.revoked_at IS 'Token revocation timestamp (if revoked)';
COMMENT ON COLUMN refresh_tokens.is_revoked IS 'Whether the token has been revoked';
COMMENT ON COLUMN refresh_tokens.user_agent IS 'User agent string from token request';
COMMENT ON COLUMN refresh_tokens.ip_address IS 'IP address from token request';

COMMIT;

-- Rollback Migration
-- ===================
-- To rollback this migration, run the following commands:
--
-- BEGIN;
-- DROP TRIGGER IF EXISTS trigger_cleanup_expired_tokens ON refresh_tokens;
-- DROP FUNCTION IF EXISTS cleanup_expired_tokens();
-- DROP TABLE IF EXISTS refresh_tokens CASCADE;
-- COMMIT;
