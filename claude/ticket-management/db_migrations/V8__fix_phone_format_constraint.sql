-- V8: Fix phone number format constraint to allow common formats
-- Author: System
-- Date: 2025-11-16
-- Description: Updates phone_number CHECK constraint to accept hyphens, spaces, and parentheses

-- Drop the old phone format constraint
ALTER TABLE users
DROP CONSTRAINT IF EXISTS chk_users_phone_format;

-- Add new phone format constraint that accepts common formats:
-- Examples: +1-555-0100, +1 (555) 012-3456, 555-0100, +44 20 1234 5678
ALTER TABLE users
ADD CONSTRAINT chk_users_phone_format CHECK (
    phone_number IS NULL OR
    phone_number ~* '^\+?[0-9\s\-\(\)]{10,20}$'
);

-- Add comment
COMMENT ON CONSTRAINT chk_users_phone_format ON users IS
'Phone number format: 10-20 characters, optional + prefix, allows digits, spaces, hyphens, parentheses';
