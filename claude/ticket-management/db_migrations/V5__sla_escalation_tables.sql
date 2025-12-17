-- ============================================================================
-- Flyway Migration V5: SLA and Escalation Tables
-- ============================================================================
-- Description: Creates sla_policies and escalations tables with default SLA policies
-- Author: Ticket Management System
-- Date: 2025-11-16
-- Reference: /backend/DATABASE_SCHEMA.md (Supporting Tables section), PROMPT.md (Priority Levels)
-- ============================================================================


-- Table: sla_policies
-- ============================================================================
-- Purpose: Defines Service Level Agreement policies for different ticket priorities
-- Row Estimate: 10-100 policies (typically 4-10 active policies)

CREATE TABLE sla_policies (
    -- Primary Key
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Policy Identification
    policy_name             VARCHAR(100) UNIQUE NOT NULL,
    policy_description      TEXT,

    -- Priority Mapping
    priority                VARCHAR(10) NOT NULL,

    -- Time-based SLAs (in hours)
    response_time           INTEGER NOT NULL,  -- First response time in hours
    resolution_time         INTEGER NOT NULL,  -- Resolution time in hours

    -- Business Hours Configuration
    business_hours_only     BOOLEAN NOT NULL DEFAULT FALSE,
    business_start_hour     INTEGER DEFAULT 9,   -- 9 AM
    business_end_hour       INTEGER DEFAULT 17,  -- 5 PM
    business_days           TEXT[] DEFAULT ARRAY['MON', 'TUE', 'WED', 'THU', 'FRI'],

    -- Escalation Rules
    auto_escalate           BOOLEAN NOT NULL DEFAULT TRUE,
    escalation_levels       JSONB,  -- Array of escalation rules with time thresholds

    -- Notification Rules
    notify_on_breach        BOOLEAN NOT NULL DEFAULT TRUE,
    notify_before_breach    INTEGER DEFAULT 30,  -- Minutes before breach to send warning

    -- Applicable Scope
    applicable_to_categories TEXT[],  -- If NULL, applies to all
    applicable_to_teams      TEXT[],  -- If NULL, applies to all

    -- Status
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,

    -- Metadata
    created_by              UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by              UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_from          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_until         TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_sla_policies_priority CHECK (priority IN ('P1', 'P2', 'P3', 'P4')),
    CONSTRAINT chk_sla_policies_response_time CHECK (response_time > 0),
    CONSTRAINT chk_sla_policies_resolution_time CHECK (resolution_time > response_time),
    CONSTRAINT chk_sla_policies_business_hours CHECK (
        business_start_hour >= 0 AND business_start_hour < 24 AND
        business_end_hour > business_start_hour AND business_end_hour <= 24
    ),
    CONSTRAINT chk_sla_policies_notify_before CHECK (notify_before_breach >= 0)
);

-- Indexes for sla_policies table
CREATE UNIQUE INDEX idx_sla_policies_priority_active ON sla_policies(priority) WHERE is_active = TRUE;
CREATE INDEX idx_sla_policies_name ON sla_policies(policy_name);
CREATE INDEX idx_sla_policies_active ON sla_policies(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_sla_policies_effective_dates ON sla_policies(effective_from, effective_until);

-- JSONB index for escalation rules
CREATE INDEX idx_sla_policies_escalation_rules_gin ON sla_policies USING GIN (escalation_levels);

-- Trigger: Auto-update updated_at timestamp
CREATE TRIGGER trg_sla_policies_updated_at
    BEFORE UPDATE ON sla_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE sla_policies IS 'Defines Service Level Agreement policies for different ticket priorities with escalation rules';
COMMENT ON COLUMN sla_policies.response_time IS 'Maximum time in hours for first response';
COMMENT ON COLUMN sla_policies.resolution_time IS 'Maximum time in hours for ticket resolution';
COMMENT ON COLUMN sla_policies.escalation_levels IS 'JSON array of escalation rules: [{"level": 1, "after_hours": 2, "escalate_to_role": "TEAM_LEAD"}]';


-- Table: escalations
-- ============================================================================
-- Purpose: Tracks ticket escalations with escalation hierarchy and reasons
-- Row Estimate: 1,000-100,000+ escalations (5-10% of tickets get escalated)

CREATE TABLE escalations (
    -- Primary Key
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    ticket_id               UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    escalated_by            UUID REFERENCES users(id) ON DELETE SET NULL,
    escalated_to            UUID REFERENCES users(id) ON DELETE SET NULL,
    sla_policy_id           UUID REFERENCES sla_policies(id) ON DELETE SET NULL,

    -- Escalation Details
    escalation_level        INTEGER NOT NULL DEFAULT 1,
    escalation_reason       VARCHAR(100) NOT NULL,
    escalation_type         VARCHAR(50) NOT NULL,

    -- Detailed Information
    reason_description      TEXT,
    previous_assignee       UUID REFERENCES users(id) ON DELETE SET NULL,
    escalation_path         JSONB,  -- Track escalation chain

    -- SLA Breach Information
    is_sla_breach           BOOLEAN NOT NULL DEFAULT FALSE,
    breach_type             VARCHAR(50),  -- RESPONSE_TIME, RESOLUTION_TIME
    breach_duration         INTEGER,  -- Hours breached

    -- Priority Change
    original_priority       VARCHAR(10),
    new_priority            VARCHAR(10),

    -- Resolution
    is_resolved             BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at             TIMESTAMP WITH TIME ZONE,
    resolved_by             UUID REFERENCES users(id) ON DELETE SET NULL,
    resolution_notes        TEXT,

    -- Timestamps
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at         TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_escalations_level CHECK (escalation_level BETWEEN 1 AND 5),
    CONSTRAINT chk_escalations_reason CHECK (escalation_reason IN (
        'SLA_BREACH', 'COMPLEXITY', 'CUSTOMER_REQUEST',
        'TECHNICAL_EXPERTISE', 'MANAGEMENT_DECISION', 'AUTO_ESCALATION',
        'PRIORITY_UPGRADE', 'RESOURCE_UNAVAILABLE'
    )),
    CONSTRAINT chk_escalations_type CHECK (escalation_type IN (
        'AUTOMATIC', 'MANUAL', 'SLA_BASED', 'CUSTOMER_REQUESTED'
    )),
    CONSTRAINT chk_escalations_breach_type CHECK (breach_type IN (
        'RESPONSE_TIME', 'RESOLUTION_TIME', 'BOTH'
    ) OR breach_type IS NULL),
    CONSTRAINT chk_escalations_priority CHECK (
        original_priority IN ('P1', 'P2', 'P3', 'P4') OR original_priority IS NULL
    ),
    CONSTRAINT chk_escalations_new_priority CHECK (
        new_priority IN ('P1', 'P2', 'P3', 'P4') OR new_priority IS NULL
    )
);

-- Indexes for escalations table
CREATE INDEX idx_escalations_ticket_id ON escalations(ticket_id, created_at DESC);
CREATE INDEX idx_escalations_escalated_by ON escalations(escalated_by);
CREATE INDEX idx_escalations_escalated_to ON escalations(escalated_to) WHERE is_resolved = FALSE;
CREATE INDEX idx_escalations_level ON escalations(escalation_level);
CREATE INDEX idx_escalations_reason ON escalations(escalation_reason);
CREATE INDEX idx_escalations_type ON escalations(escalation_type);
CREATE INDEX idx_escalations_sla_breach ON escalations(is_sla_breach) WHERE is_sla_breach = TRUE;
CREATE INDEX idx_escalations_resolved ON escalations(is_resolved) WHERE is_resolved = FALSE;
CREATE INDEX idx_escalations_created_at ON escalations(created_at DESC);

-- JSONB index for escalation path
CREATE INDEX idx_escalations_path_gin ON escalations USING GIN (escalation_path);

-- Comments
COMMENT ON TABLE escalations IS 'Tracks all ticket escalations with detailed reason tracking and resolution status';
COMMENT ON COLUMN escalations.escalation_level IS 'Escalation hierarchy level (1-5): 1=Team Lead, 2=Manager, 3=Senior Manager, etc.';
COMMENT ON COLUMN escalations.escalation_path IS 'JSON array tracking complete escalation chain with timestamps';
COMMENT ON COLUMN escalations.breach_duration IS 'Number of hours the SLA was breached by';


-- Insert Default SLA Policies
-- ============================================================================
-- Based on PROMPT.md Priority Levels specification:
-- P1 (Critical): 1 hour response, 4 hours resolution
-- P2 (High): 4 hours response, 24 hours resolution
-- P3 (Medium): 24 hours response, 72 hours resolution
-- P4 (Low): 48 hours response, 168 hours resolution

-- P1 (Critical) Policy
INSERT INTO sla_policies (
    id,
    policy_name,
    policy_description,
    priority,
    response_time,
    resolution_time,
    business_hours_only,
    auto_escalate,
    escalation_levels,
    notify_on_breach,
    notify_before_breach,
    is_active,
    created_at,
    effective_from
) VALUES (
    gen_random_uuid(),
    'P1 - Critical Priority SLA',
    'Critical priority incidents requiring immediate attention. Typically production outages or critical system failures.',
    'P1',
    1,    -- 1 hour response
    4,    -- 4 hours resolution
    FALSE,  -- 24/7 support
    TRUE,
    '[
        {"level": 1, "after_hours": 0.5, "escalate_to_role": "TEAM_LEAD", "notify": true},
        {"level": 2, "after_hours": 1, "escalate_to_role": "MANAGER", "notify": true},
        {"level": 3, "after_hours": 2, "escalate_to_role": "ADMIN", "notify": true}
    ]'::JSONB,
    TRUE,
    15,  -- Notify 15 minutes before breach
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- P2 (High) Policy
INSERT INTO sla_policies (
    id,
    policy_name,
    policy_description,
    priority,
    response_time,
    resolution_time,
    business_hours_only,
    auto_escalate,
    escalation_levels,
    notify_on_breach,
    notify_before_breach,
    is_active,
    created_at,
    effective_from
) VALUES (
    gen_random_uuid(),
    'P2 - High Priority SLA',
    'High priority issues with significant business impact but not production-critical.',
    'P2',
    4,    -- 4 hours response
    24,   -- 24 hours resolution
    FALSE,
    TRUE,
    '[
        {"level": 1, "after_hours": 2, "escalate_to_role": "TEAM_LEAD", "notify": true},
        {"level": 2, "after_hours": 8, "escalate_to_role": "MANAGER", "notify": true}
    ]'::JSONB,
    TRUE,
    30,  -- Notify 30 minutes before breach
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- P3 (Medium) Policy
INSERT INTO sla_policies (
    id,
    policy_name,
    policy_description,
    priority,
    response_time,
    resolution_time,
    business_hours_only,
    auto_escalate,
    escalation_levels,
    notify_on_breach,
    notify_before_breach,
    is_active,
    created_at,
    effective_from
) VALUES (
    gen_random_uuid(),
    'P3 - Medium Priority SLA',
    'Medium priority issues with moderate business impact handled during business hours.',
    'P3',
    24,   -- 24 hours response
    72,   -- 72 hours (3 days) resolution
    TRUE,  -- Business hours only
    TRUE,
    '[
        {"level": 1, "after_hours": 48, "escalate_to_role": "TEAM_LEAD", "notify": true}
    ]'::JSONB,
    TRUE,
    60,  -- Notify 1 hour before breach
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- P4 (Low) Policy
INSERT INTO sla_policies (
    id,
    policy_name,
    policy_description,
    priority,
    response_time,
    resolution_time,
    business_hours_only,
    auto_escalate,
    escalation_levels,
    notify_on_breach,
    notify_before_breach,
    is_active,
    created_at,
    effective_from
) VALUES (
    gen_random_uuid(),
    'P4 - Low Priority SLA',
    'Low priority issues such as feature requests or minor enhancements handled during business hours.',
    'P4',
    48,   -- 48 hours (2 days) response
    168,  -- 168 hours (7 days) resolution
    TRUE,  -- Business hours only
    FALSE,  -- No auto-escalation for low priority
    '[]'::JSONB,
    FALSE,  -- No breach notifications
    120,  -- Notify 2 hours before breach (if enabled)
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);


-- Add Foreign Key Constraint to tickets table
-- ============================================================================
-- Now that sla_policies table exists, add the foreign key constraint

ALTER TABLE tickets
ADD CONSTRAINT fk_tickets_sla_policy_id
FOREIGN KEY (sla_policy_id)
REFERENCES sla_policies(id)
ON DELETE SET NULL;

-- Create index for the foreign key
CREATE INDEX idx_tickets_sla_policy_id ON tickets(sla_policy_id) WHERE sla_policy_id IS NOT NULL;


-- Migration Verification
-- ============================================================================

DO $$
DECLARE
    sla_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO sla_count FROM sla_policies WHERE is_active = TRUE;

    RAISE NOTICE 'V5 Migration completed successfully';
    RAISE NOTICE 'Tables created: sla_policies, escalations';
    RAISE NOTICE 'Default SLA policies created: %', sla_count;
    RAISE NOTICE 'SLA Policies:';
    RAISE NOTICE '  - P1 (Critical): 1h response, 4h resolution (24/7)';
    RAISE NOTICE '  - P2 (High): 4h response, 24h resolution (24/7)';
    RAISE NOTICE '  - P3 (Medium): 24h response, 72h resolution (Business hours)';
    RAISE NOTICE '  - P4 (Low): 48h response, 168h resolution (Business hours)';
END $$;
