-- ============================================================================
-- Flyway Migration V1: Initial Schema Setup
-- ============================================================================
-- Description: Creates database extensions, custom types, and utility functions
-- Author: Ticket Management System
-- Date: 2025-11-16
-- Reference: /backend/DATABASE_SCHEMA.md, /backend/db_migrations/README.md
-- ============================================================================

-- Enable required PostgreSQL extensions
-- ============================================================================

-- UUID generation functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Cryptographic functions for password hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Full-text search support with trigram matching
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Text search without accents for better search results
CREATE EXTENSION IF NOT EXISTS "unaccent";


-- Custom Functions
-- ============================================================================

-- Function: generate_ticket_number()
-- Purpose: Generates unique ticket numbers in format TKT-YYYY-NNNNNN
-- Returns: VARCHAR(20)
-- Example: TKT-2025-000001
CREATE OR REPLACE FUNCTION generate_ticket_number() RETURNS VARCHAR(20) AS $$
DECLARE
    year_part VARCHAR(4);
    sequence_part VARCHAR(6);
    ticket_number VARCHAR(20);
    max_sequence INTEGER;
BEGIN
    -- Get current year
    year_part := TO_CHAR(CURRENT_DATE, 'YYYY');

    -- Get the maximum sequence number for current year
    SELECT COALESCE(MAX(
        CAST(SUBSTRING(ticket_number FROM 10) AS INTEGER)
    ), 0) INTO max_sequence
    FROM tickets
    WHERE ticket_number LIKE 'TKT-' || year_part || '-%';

    -- Increment and format sequence
    sequence_part := LPAD((max_sequence + 1)::TEXT, 6, '0');

    -- Construct ticket number
    ticket_number := 'TKT-' || year_part || '-' || sequence_part;

    RETURN ticket_number;
END;
$$ LANGUAGE plpgsql;


-- Function: update_updated_at_column()
-- Purpose: Automatically updates the updated_at timestamp on row modification
-- Returns: TRIGGER
-- Usage: Applied to all tables with updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Function: log_ticket_history()
-- Purpose: Automatically logs changes to tickets in ticket_history table
-- Returns: TRIGGER
-- Usage: Applied to tickets table on UPDATE
CREATE OR REPLACE FUNCTION log_ticket_history()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if there are actual changes
    IF (OLD.status IS DISTINCT FROM NEW.status) OR
       (OLD.priority IS DISTINCT FROM NEW.priority) OR
       (OLD.assigned_to IS DISTINCT FROM NEW.assigned_to) OR
       (OLD.title IS DISTINCT FROM NEW.title) OR
       (OLD.description IS DISTINCT FROM NEW.description) THEN

        INSERT INTO ticket_history (
            id,
            ticket_id,
            changed_by,
            change_type,
            field_name,
            old_value,
            new_value,
            created_at
        ) VALUES (
            gen_random_uuid(),
            NEW.id,
            COALESCE(NEW.updated_by, NEW.assigned_to),
            CASE
                WHEN OLD.status IS DISTINCT FROM NEW.status THEN 'STATUS_CHANGE'
                WHEN OLD.priority IS DISTINCT FROM NEW.priority THEN 'PRIORITY_CHANGE'
                WHEN OLD.assigned_to IS DISTINCT FROM NEW.assigned_to THEN 'ASSIGNMENT_CHANGE'
                ELSE 'UPDATE'
            END,
            CASE
                WHEN OLD.status IS DISTINCT FROM NEW.status THEN 'status'
                WHEN OLD.priority IS DISTINCT FROM NEW.priority THEN 'priority'
                WHEN OLD.assigned_to IS DISTINCT FROM NEW.assigned_to THEN 'assigned_to'
                ELSE 'general'
            END,
            CASE
                WHEN OLD.status IS DISTINCT FROM NEW.status THEN OLD.status
                WHEN OLD.priority IS DISTINCT FROM NEW.priority THEN OLD.priority
                WHEN OLD.assigned_to IS DISTINCT FROM NEW.assigned_to THEN OLD.assigned_to::TEXT
                ELSE 'N/A'
            END,
            CASE
                WHEN OLD.status IS DISTINCT FROM NEW.status THEN NEW.status
                WHEN OLD.priority IS DISTINCT FROM NEW.priority THEN NEW.priority
                WHEN OLD.assigned_to IS DISTINCT FROM NEW.assigned_to THEN NEW.assigned_to::TEXT
                ELSE 'N/A'
            END,
            CURRENT_TIMESTAMP
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Function: check_sla_breach()
-- Purpose: Checks if a ticket has breached its SLA and triggers escalation
-- Returns: BOOLEAN
-- Usage: Called by scheduled job or trigger
CREATE OR REPLACE FUNCTION check_sla_breach(ticket_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    ticket_record RECORD;
    sla_record RECORD;
    is_breached BOOLEAN := FALSE;
    time_elapsed INTERVAL;
BEGIN
    -- Get ticket details
    SELECT * INTO ticket_record FROM tickets WHERE id = ticket_uuid;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Get applicable SLA policy
    SELECT * INTO sla_record FROM sla_policies
    WHERE priority = ticket_record.priority
    AND is_active = TRUE
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Calculate time elapsed since ticket creation
    time_elapsed := CURRENT_TIMESTAMP - ticket_record.created_at;

    -- Check response time breach
    IF ticket_record.status = 'NEW' AND
       time_elapsed > (sla_record.response_time || ' hours')::INTERVAL THEN
        is_breached := TRUE;
    END IF;

    -- Check resolution time breach
    IF ticket_record.status NOT IN ('RESOLVED', 'CLOSED') AND
       time_elapsed > (sla_record.resolution_time || ' hours')::INTERVAL THEN
        is_breached := TRUE;
    END IF;

    RETURN is_breached;
END;
$$ LANGUAGE plpgsql;


-- Function: calculate_business_hours()
-- Purpose: Calculates business hours between two timestamps (Mon-Fri, 9AM-5PM)
-- Returns: NUMERIC
-- Usage: For SLA calculations excluding weekends and off-hours
CREATE OR REPLACE FUNCTION calculate_business_hours(
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE
) RETURNS NUMERIC AS $$
DECLARE
    curr_time TIMESTAMP WITH TIME ZONE;
    business_hours NUMERIC := 0;
    day_of_week INTEGER;
    hour_of_day INTEGER;
BEGIN
    curr_time := start_time;

    WHILE curr_time < end_time LOOP
        day_of_week := EXTRACT(DOW FROM curr_time);
        hour_of_day := EXTRACT(HOUR FROM curr_time);

        -- Check if it's a weekday (Mon-Fri) and business hours (9AM-5PM)
        IF day_of_week BETWEEN 1 AND 5 AND hour_of_day BETWEEN 9 AND 16 THEN
            business_hours := business_hours + 1;
        END IF;

        curr_time := curr_time + INTERVAL '1 hour';
    END LOOP;

    RETURN business_hours;
END;
$$ LANGUAGE plpgsql;


-- Utility Function: soft_delete_record()
-- Purpose: Performs soft delete by setting deleted_at timestamp
-- Returns: BOOLEAN
-- Usage: Generic soft delete function for tables with deleted_at column
CREATE OR REPLACE FUNCTION soft_delete_record(
    table_name TEXT,
    record_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    sql_query TEXT;
    rows_affected INTEGER;
BEGIN
    sql_query := FORMAT(
        'UPDATE %I SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1 AND deleted_at IS NULL',
        table_name
    );

    EXECUTE sql_query USING record_id;
    GET DIAGNOSTICS rows_affected = ROW_COUNT;

    RETURN rows_affected > 0;
END;
$$ LANGUAGE plpgsql;


-- Schema Verification
-- ============================================================================

-- Log successful migration
DO $$
BEGIN
    RAISE NOTICE 'V1 Migration completed successfully';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pgcrypto, pg_trgm, unaccent';
    RAISE NOTICE 'Functions created: generate_ticket_number, update_updated_at_column, log_ticket_history, check_sla_breach, calculate_business_hours, soft_delete_record';
END $$;
