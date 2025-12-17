-- ============================================================================
-- Flyway Migration V6: Indexes and Performance Optimization
-- ============================================================================
-- Description: Creates additional composite indexes, materialized views, and performance optimizations
-- Author: Ticket Management System
-- Date: 2025-11-16
-- Reference: /backend/DATABASE_SCHEMA.md (Indexes section)
-- ============================================================================


-- Additional Composite Indexes for Common Query Patterns
-- ============================================================================

-- Tickets: Find my open tickets (most common query)
CREATE INDEX IF NOT EXISTS idx_tickets_assignee_status_priority
    ON tickets(assigned_to, status, priority DESC, created_at DESC)
    WHERE deleted_at IS NULL AND status NOT IN ('CLOSED', 'RESOLVED');

-- Tickets: Find tickets due soon
CREATE INDEX IF NOT EXISTS idx_tickets_due_soon
    ON tickets(due_date, status, priority)
    WHERE deleted_at IS NULL
    AND due_date IS NOT NULL
    AND status NOT IN ('CLOSED', 'RESOLVED');

-- Tickets: Find SLA breach candidates
CREATE INDEX IF NOT EXISTS idx_tickets_sla_monitoring
    ON tickets(status, sla_policy_id, created_at)
    WHERE deleted_at IS NULL
    AND status NOT IN ('CLOSED', 'RESOLVED')
    AND sla_policy_id IS NOT NULL;

-- Tickets: Find recently updated tickets for a team
CREATE INDEX IF NOT EXISTS idx_tickets_team_activity
    ON tickets(assigned_team, updated_at DESC, status)
    WHERE deleted_at IS NULL AND assigned_team IS NOT NULL;

-- Comments: Find latest comments for ticket list view
CREATE INDEX IF NOT EXISTS idx_comments_latest_per_ticket
    ON comments(ticket_id, created_at DESC, id)
    WHERE deleted_at IS NULL;

-- User Sessions: Find active sessions for security monitoring
CREATE INDEX IF NOT EXISTS idx_user_sessions_security
    ON user_sessions(user_id, is_active, last_activity_at DESC)
    WHERE is_active = TRUE;

-- Audit Logs: Find security events
CREATE INDEX IF NOT EXISTS idx_audit_logs_security_events
    ON audit_logs(action_type, status, created_at DESC)
    WHERE action_type IN ('LOGIN_FAILED', 'ACCOUNT_LOCKED', 'PERMISSION_CHANGE');

-- Notifications: Find pending notifications for processing
CREATE INDEX IF NOT EXISTS idx_notifications_processing
    ON notifications(status, priority DESC, next_retry_at NULLS LAST, created_at)
    WHERE status IN ('PENDING', 'RETRYING');


-- Materialized Views for Reporting and Dashboards
-- ============================================================================

-- View: Ticket Statistics by Status
CREATE MATERIALIZED VIEW mv_ticket_stats_by_status AS
SELECT
    status,
    priority,
    COUNT(*) as ticket_count,
    COUNT(DISTINCT assigned_to) as unique_assignees,
    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, CURRENT_TIMESTAMP) - created_at)) / 3600) as avg_resolution_hours,
    COUNT(CASE WHEN resolved_at IS NOT NULL AND resolved_at > resolution_due_at THEN 1 END) as sla_breached_count,
    MAX(updated_at) as last_updated
FROM tickets
WHERE deleted_at IS NULL
GROUP BY status, priority;

CREATE UNIQUE INDEX idx_mv_ticket_stats_status_priority ON mv_ticket_stats_by_status(status, priority);

COMMENT ON MATERIALIZED VIEW mv_ticket_stats_by_status IS 'Aggregated ticket statistics by status and priority for dashboard (refresh hourly)';


-- View: User Performance Metrics
CREATE MATERIALIZED VIEW mv_user_performance AS
SELECT
    u.id as user_id,
    u.username,
    u.role,
    COUNT(t.id) as total_tickets_assigned,
    COUNT(CASE WHEN t.status = 'RESOLVED' THEN 1 END) as tickets_resolved,
    COUNT(CASE WHEN t.status = 'CLOSED' THEN 1 END) as tickets_closed,
    AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at)) / 3600) as avg_resolution_hours,
    COUNT(CASE WHEN t.resolved_at > t.resolution_due_at THEN 1 END) as sla_breaches,
    MAX(t.updated_at) as last_ticket_update
FROM users u
LEFT JOIN tickets t ON t.assigned_to = u.id AND t.deleted_at IS NULL
WHERE u.deleted_at IS NULL
  AND u.role IN ('TEAM_LEAD', 'SENIOR_ENGINEER', 'DEVOPS_ENGINEER')
GROUP BY u.id, u.username, u.role;

CREATE UNIQUE INDEX idx_mv_user_performance_user_id ON mv_user_performance(user_id);
CREATE INDEX idx_mv_user_performance_role ON mv_user_performance(role);

COMMENT ON MATERIALIZED VIEW mv_user_performance IS 'User performance metrics for reporting (refresh daily)';


-- View: SLA Compliance Report
CREATE MATERIALIZED VIEW mv_sla_compliance AS
SELECT
    t.priority,
    sp.policy_name,
    COUNT(t.id) as total_tickets,
    COUNT(CASE WHEN t.first_response_at IS NOT NULL AND t.first_response_at <= t.response_due_at THEN 1 END) as response_met,
    COUNT(CASE WHEN t.resolved_at IS NOT NULL AND t.resolved_at <= t.resolution_due_at THEN 1 END) as resolution_met,
    COUNT(CASE WHEN t.first_response_at > t.response_due_at THEN 1 END) as response_breached,
    COUNT(CASE WHEN t.resolved_at > t.resolution_due_at THEN 1 END) as resolution_breached,
    ROUND((COUNT(CASE WHEN t.resolved_at <= t.resolution_due_at THEN 1 END)::DECIMAL / NULLIF(COUNT(CASE WHEN t.resolved_at IS NOT NULL THEN 1 END), 0)) * 100, 2) as compliance_percentage,
    MAX(t.updated_at) as last_updated
FROM tickets t
LEFT JOIN sla_policies sp ON t.sla_policy_id = sp.id
WHERE t.deleted_at IS NULL
  AND t.created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY t.priority, sp.policy_name;

CREATE INDEX idx_mv_sla_compliance_priority ON mv_sla_compliance(priority);

COMMENT ON MATERIALIZED VIEW mv_sla_compliance IS 'SLA compliance metrics for last 90 days (refresh daily)';


-- View: Daily Ticket Volume Trend
CREATE MATERIALIZED VIEW mv_daily_ticket_volume AS
SELECT
    DATE(created_at) as ticket_date,
    category,
    priority,
    COUNT(*) as tickets_created,
    COUNT(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN 1 END) as tickets_resolved,
    COUNT(CASE WHEN status NOT IN ('RESOLVED', 'CLOSED') THEN 1 END) as tickets_open
FROM tickets
WHERE deleted_at IS NULL
  AND created_at >= CURRENT_DATE - INTERVAL '365 days'
GROUP BY DATE(created_at), category, priority;

CREATE INDEX idx_mv_daily_ticket_volume_date ON mv_daily_ticket_volume(ticket_date DESC);
CREATE INDEX idx_mv_daily_ticket_volume_category ON mv_daily_ticket_volume(category, ticket_date DESC);

COMMENT ON MATERIALIZED VIEW mv_daily_ticket_volume IS 'Daily ticket volume trends for last 365 days (refresh daily)';


-- Stored Procedure: Refresh All Materialized Views
-- ============================================================================

CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS TABLE(view_name TEXT, refresh_duration INTERVAL) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
BEGIN
    -- Refresh ticket stats
    start_time := CLOCK_TIMESTAMP();
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ticket_stats_by_status;
    end_time := CLOCK_TIMESTAMP();
    view_name := 'mv_ticket_stats_by_status';
    refresh_duration := end_time - start_time;
    RETURN NEXT;

    -- Refresh user performance
    start_time := CLOCK_TIMESTAMP();
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_performance;
    end_time := CLOCK_TIMESTAMP();
    view_name := 'mv_user_performance';
    refresh_duration := end_time - start_time;
    RETURN NEXT;

    -- Refresh SLA compliance
    start_time := CLOCK_TIMESTAMP();
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sla_compliance;
    end_time := CLOCK_TIMESTAMP();
    view_name := 'mv_sla_compliance';
    refresh_duration := end_time - start_time;
    RETURN NEXT;

    -- Refresh daily volume
    start_time := CLOCK_TIMESTAMP();
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_ticket_volume;
    end_time := CLOCK_TIMESTAMP();
    view_name := 'mv_daily_ticket_volume';
    refresh_duration := end_time - start_time;
    RETURN NEXT;

    RETURN;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_all_materialized_views IS 'Refreshes all materialized views concurrently for reporting. Call this via scheduled job.';


-- Database Statistics and Maintenance Functions
-- ============================================================================

-- Function: Get table sizes and row counts
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT,
    total_size TEXT,
    table_size TEXT,
    indexes_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        relname::TEXT as table_name,
        n_live_tup as row_count,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) as total_size,
        pg_size_pretty(pg_relation_size(schemaname||'.'||relname)) as table_size,
        pg_size_pretty(pg_indexes_size(schemaname||'.'||relname)) as indexes_size
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_database_stats IS 'Returns table sizes and row counts for database monitoring';


-- View: Table statistics for maintenance monitoring
CREATE OR REPLACE VIEW vw_table_stats AS
SELECT
    schemaname,
    relname as tablename,
    n_live_tup as row_count,
    n_dead_tup as dead_rows,
    ROUND((n_dead_tup::DECIMAL / NULLIF(n_live_tup, 0)) * 100, 2) as dead_row_percentage,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;

COMMENT ON VIEW vw_table_stats IS 'Table statistics for maintenance monitoring (vacuum, analyze)';


-- View: Index usage statistics
CREATE OR REPLACE VIEW vw_index_usage AS
SELECT
    schemaname,
    relname as tablename,
    indexrelname as indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    CASE
        WHEN idx_scan = 0 THEN 'UNUSED'
        WHEN idx_scan < 100 THEN 'LOW_USAGE'
        ELSE 'ACTIVE'
    END as usage_status
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;

COMMENT ON VIEW vw_index_usage IS 'Index usage statistics for identifying unused indexes';


-- Partial Indexes for Specific Use Cases
-- ============================================================================
-- Note: Cannot use CURRENT_TIMESTAMP in index predicates as it's not immutable

-- Index for finding tickets nearing SLA breach (used by monitoring jobs)
CREATE INDEX IF NOT EXISTS idx_tickets_sla_warning
    ON tickets(resolution_due_at, status, priority)
    WHERE deleted_at IS NULL
    AND status NOT IN ('CLOSED', 'RESOLVED')
    AND resolution_due_at IS NOT NULL;

-- Index for finding stale tickets (queries will filter by date)
CREATE INDEX IF NOT EXISTS idx_tickets_stale
    ON tickets(updated_at DESC, status, assigned_to)
    WHERE deleted_at IS NULL
    AND status NOT IN ('CLOSED', 'RESOLVED');

-- Index for finding unassigned tickets
CREATE INDEX IF NOT EXISTS idx_tickets_unassigned
    ON tickets(created_at DESC, priority, category)
    WHERE deleted_at IS NULL
    AND assigned_to IS NULL
    AND status = 'NEW';


-- Performance Configuration Recommendations
-- ============================================================================

-- Add comments with recommended PostgreSQL configuration for production
COMMENT ON DATABASE ticket_management IS
'Recommended PostgreSQL Configuration for Ticket Management System:
- shared_buffers = 256MB (25% of RAM for dedicated server)
- effective_cache_size = 768MB (50-75% of RAM)
- maintenance_work_mem = 64MB
- checkpoint_completion_target = 0.9
- wal_buffers = 16MB
- default_statistics_target = 100
- random_page_cost = 1.1 (for SSD storage)
- effective_io_concurrency = 200 (for SSD storage)
- work_mem = 4MB (adjust based on concurrent connections)
- min_wal_size = 1GB
- max_wal_size = 4GB
- max_worker_processes = 8
- max_parallel_workers_per_gather = 4
- max_parallel_workers = 8
- autovacuum_max_workers = 3
- autovacuum_naptime = 10s (for high-write workload)';


-- Migration Verification
-- ============================================================================

DO $$
DECLARE
    index_count INTEGER;
    mv_count INTEGER;
BEGIN
    -- Count indexes created in this migration
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%';

    -- Count materialized views
    SELECT COUNT(*) INTO mv_count
    FROM pg_matviews
    WHERE schemaname = 'public';

    RAISE NOTICE 'V6 Migration completed successfully';
    RAISE NOTICE 'Additional performance indexes created';
    RAISE NOTICE 'Total indexes in database: %', index_count;
    RAISE NOTICE 'Materialized views created: % (mv_ticket_stats_by_status, mv_user_performance, mv_sla_compliance, mv_daily_ticket_volume)', mv_count;
    RAISE NOTICE 'Views created: vw_table_stats, vw_index_usage';
    RAISE NOTICE 'Functions created: refresh_all_materialized_views, get_database_stats';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANT: Schedule these maintenance tasks:';
    RAISE NOTICE '  1. Refresh materialized views: SELECT * FROM refresh_all_materialized_views(); (Run hourly/daily)';
    RAISE NOTICE '  2. Monitor index usage: SELECT * FROM vw_index_usage WHERE usage_status = ''UNUSED'';';
    RAISE NOTICE '  3. Monitor table bloat: SELECT * FROM vw_table_stats WHERE dead_row_percentage > 10;';
    RAISE NOTICE '  4. Cleanup old notifications: SELECT cleanup_old_notifications(30); (Run weekly)';
END $$;
