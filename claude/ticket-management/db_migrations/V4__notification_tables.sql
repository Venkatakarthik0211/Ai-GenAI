-- ============================================================================
-- Flyway Migration V4: Notification Tables
-- ============================================================================
-- Description: Creates notifications table for multi-channel notification management
-- Author: Ticket Management System
-- Date: 2025-11-16
-- Reference: /backend/DATABASE_SCHEMA.md (Supporting Tables section)
-- ============================================================================


-- Table: notifications
-- ============================================================================
-- Purpose: Manages multi-channel notifications (Email, SMS, In-App, Slack) with delivery tracking
-- Row Estimate: 50,000-5,000,000+ notifications (5-10 per ticket)

CREATE TABLE notifications (
    -- Primary Key
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ticket_id           UUID REFERENCES tickets(id) ON DELETE CASCADE,

    -- Notification Content
    notification_type   VARCHAR(50) NOT NULL,
    title               VARCHAR(255) NOT NULL,
    message             TEXT NOT NULL,
    action_url          VARCHAR(500),

    -- Delivery Channels
    channels            TEXT[] NOT NULL,  -- ['EMAIL', 'SMS', 'IN_APP', 'SLACK']

    -- Email Channel
    email_to            VARCHAR(255),
    email_subject       VARCHAR(255),
    email_sent_at       TIMESTAMP WITH TIME ZONE,
    email_delivered_at  TIMESTAMP WITH TIME ZONE,
    email_opened_at     TIMESTAMP WITH TIME ZONE,
    email_error         TEXT,

    -- SMS Channel
    sms_to              VARCHAR(20),
    sms_sent_at         TIMESTAMP WITH TIME ZONE,
    sms_delivered_at    TIMESTAMP WITH TIME ZONE,
    sms_error           TEXT,

    -- In-App Channel
    is_read             BOOLEAN NOT NULL DEFAULT FALSE,
    read_at             TIMESTAMP WITH TIME ZONE,

    -- Slack Channel
    slack_channel       VARCHAR(100),
    slack_sent_at       TIMESTAMP WITH TIME ZONE,
    slack_message_id    VARCHAR(100),
    slack_error         TEXT,

    -- Priority & Status
    priority            VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    status              VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    retry_count         INTEGER NOT NULL DEFAULT 0,
    max_retries         INTEGER NOT NULL DEFAULT 3,
    next_retry_at       TIMESTAMP WITH TIME ZONE,

    -- Metadata
    metadata            JSONB,
    template_id         VARCHAR(100),
    template_variables  JSONB,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at             TIMESTAMP WITH TIME ZONE,
    failed_at           TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_notifications_type CHECK (notification_type IN (
        'TICKET_CREATED', 'TICKET_ASSIGNED', 'TICKET_STATUS_CHANGED',
        'TICKET_COMMENT_ADDED', 'TICKET_ESCALATED', 'TICKET_RESOLVED',
        'TICKET_REOPENED', 'TICKET_CLOSED', 'SLA_BREACH_WARNING',
        'SLA_BREACH', 'DUE_DATE_REMINDER', 'MENTION', 'DAILY_DIGEST'
    )),
    CONSTRAINT chk_notifications_priority CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')),
    CONSTRAINT chk_notifications_status CHECK (status IN (
        'PENDING', 'SENT', 'DELIVERED', 'FAILED', 'CANCELLED', 'RETRYING'
    )),
    CONSTRAINT chk_notifications_channels_not_empty CHECK (array_length(channels, 1) > 0),
    CONSTRAINT chk_notifications_retry_count CHECK (retry_count <= max_retries)
);

-- Indexes for notifications table
CREATE INDEX idx_notifications_user_id ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_ticket_id ON notifications(ticket_id) WHERE ticket_id IS NOT NULL;
CREATE INDEX idx_notifications_type ON notifications(notification_type, created_at DESC);
CREATE INDEX idx_notifications_status ON notifications(status) WHERE status IN ('PENDING', 'RETRYING', 'FAILED');
CREATE INDEX idx_notifications_priority ON notifications(priority, created_at) WHERE status = 'PENDING';
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_next_retry ON notifications(next_retry_at) WHERE status = 'RETRYING';

-- Composite indexes for common queries
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_channels_gin ON notifications USING GIN (channels);

-- JSONB indexes
CREATE INDEX idx_notifications_metadata_gin ON notifications USING GIN (metadata);
CREATE INDEX idx_notifications_template_variables_gin ON notifications USING GIN (template_variables);

-- Comments
COMMENT ON TABLE notifications IS 'Multi-channel notification management with delivery tracking and retry logic';
COMMENT ON COLUMN notifications.channels IS 'Array of delivery channels: EMAIL, SMS, IN_APP, SLACK';
COMMENT ON COLUMN notifications.notification_type IS 'Type of notification: TICKET_CREATED, TICKET_ASSIGNED, SLA_BREACH, etc.';
COMMENT ON COLUMN notifications.status IS 'Delivery status: PENDING, SENT, DELIVERED, FAILED, CANCELLED, RETRYING';
COMMENT ON COLUMN notifications.metadata IS 'Additional JSON metadata for notification context';


-- Function: create_notification()
-- ============================================================================
-- Purpose: Helper function to create notifications with automatic channel detection
-- Usage: SELECT create_notification(user_id, ticket_id, notification_type, title, message);

CREATE OR REPLACE FUNCTION create_notification(
    p_user_id UUID,
    p_ticket_id UUID,
    p_notification_type VARCHAR(50),
    p_title VARCHAR(255),
    p_message TEXT,
    p_priority VARCHAR(20) DEFAULT 'NORMAL'
) RETURNS UUID AS $$
DECLARE
    v_notification_id UUID;
    v_user_email VARCHAR(255);
    v_user_phone VARCHAR(20);
    v_channels TEXT[];
BEGIN
    -- Generate notification ID
    v_notification_id := gen_random_uuid();

    -- Get user contact details
    SELECT email, phone_number INTO v_user_email, v_user_phone
    FROM users
    WHERE id = p_user_id;

    -- Determine channels based on priority and user preferences
    v_channels := ARRAY['IN_APP'];

    IF v_user_email IS NOT NULL THEN
        v_channels := array_append(v_channels, 'EMAIL');
    END IF;

    IF p_priority IN ('HIGH', 'URGENT') AND v_user_phone IS NOT NULL THEN
        v_channels := array_append(v_channels, 'SMS');
    END IF;

    -- Insert notification
    INSERT INTO notifications (
        id,
        user_id,
        ticket_id,
        notification_type,
        title,
        message,
        channels,
        email_to,
        sms_to,
        priority,
        status,
        created_at
    ) VALUES (
        v_notification_id,
        p_user_id,
        p_ticket_id,
        p_notification_type,
        p_title,
        p_message,
        v_channels,
        v_user_email,
        v_user_phone,
        p_priority,
        'PENDING',
        CURRENT_TIMESTAMP
    );

    RETURN v_notification_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_notification IS 'Helper function to create notifications with automatic channel detection based on user preferences';


-- Function: mark_notification_as_read()
-- ============================================================================
-- Purpose: Marks a notification as read for a specific user
-- Usage: SELECT mark_notification_as_read(notification_id, user_id);

CREATE OR REPLACE FUNCTION mark_notification_as_read(
    p_notification_id UUID,
    p_user_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_rows_affected INTEGER;
BEGIN
    UPDATE notifications
    SET is_read = TRUE,
        read_at = CURRENT_TIMESTAMP
    WHERE id = p_notification_id
    AND user_id = p_user_id
    AND is_read = FALSE;

    GET DIAGNOSTICS v_rows_affected = ROW_COUNT;

    RETURN v_rows_affected > 0;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mark_notification_as_read IS 'Marks a notification as read for the specified user';


-- Function: get_unread_notification_count()
-- ============================================================================
-- Purpose: Gets the count of unread notifications for a user
-- Usage: SELECT get_unread_notification_count(user_id);

CREATE OR REPLACE FUNCTION get_unread_notification_count(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM notifications
    WHERE user_id = p_user_id
    AND is_read = FALSE
    AND 'IN_APP' = ANY(channels);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_unread_notification_count IS 'Returns the count of unread in-app notifications for a user';


-- Function: retry_failed_notifications()
-- ============================================================================
-- Purpose: Resets failed notifications for retry based on retry policy
-- Usage: SELECT retry_failed_notifications(); (Called by scheduled job)

CREATE OR REPLACE FUNCTION retry_failed_notifications()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE notifications
    SET status = 'RETRYING',
        retry_count = retry_count + 1,
        next_retry_at = CURRENT_TIMESTAMP + (INTERVAL '5 minutes' * (retry_count + 1))
    WHERE status = 'FAILED'
    AND retry_count < max_retries
    AND (next_retry_at IS NULL OR next_retry_at <= CURRENT_TIMESTAMP);

    GET DIAGNOSTICS v_count = ROW_COUNT;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION retry_failed_notifications IS 'Resets failed notifications for retry with exponential backoff';


-- Function: cleanup_old_notifications()
-- ============================================================================
-- Purpose: Archives or deletes old read notifications (30+ days old)
-- Usage: SELECT cleanup_old_notifications(30); (Called by scheduled job)

CREATE OR REPLACE FUNCTION cleanup_old_notifications(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM notifications
    WHERE is_read = TRUE
    AND read_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL
    AND status IN ('SENT', 'DELIVERED');

    GET DIAGNOSTICS v_count = ROW_COUNT;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_notifications IS 'Deletes old read notifications to maintain database performance';


-- Migration Verification
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'V4 Migration completed successfully';
    RAISE NOTICE 'Table created: notifications';
    RAISE NOTICE 'Functions created: create_notification, mark_notification_as_read, get_unread_notification_count, retry_failed_notifications, cleanup_old_notifications';
    RAISE NOTICE 'Multi-channel notification support: EMAIL, SMS, IN_APP, SLACK';
END $$;
