-- ============================================================================
-- Pipeline Runs Database Schema
-- ============================================================================
--
-- Purpose: Store pipeline run state and execution history
--
-- This table persists pipeline run data across container restarts
-- ============================================================================

-- Drop table if exists (for clean recreate)
DROP TABLE IF EXISTS pipeline_runs CASCADE;

-- ============================================================================
-- Pipeline Runs Table
-- ============================================================================

CREATE TABLE pipeline_runs (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Run identifiers
    pipeline_run_id VARCHAR(64) NOT NULL UNIQUE,
    mlflow_run_id VARCHAR(64),
    mlflow_experiment_id VARCHAR(64),

    -- User inputs
    experiment_name VARCHAR(256),
    user_prompt TEXT,
    data_path TEXT,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    start_time TIMESTAMP,
    end_time TIMESTAMP,

    -- Status
    status VARCHAR(32) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed, stopped
    current_node VARCHAR(64),

    -- Node tracking (JSONB arrays)
    completed_nodes JSONB DEFAULT '[]'::jsonb,
    failed_nodes JSONB DEFAULT '[]'::jsonb,

    -- Errors and warnings (JSONB arrays)
    errors JSONB DEFAULT '[]'::jsonb,
    warnings JSONB DEFAULT '[]'::jsonb,

    -- Bedrock extraction data (if natural language mode)
    extracted_config JSONB,
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    reasoning TEXT,
    assumptions JSONB,
    config_warnings JSONB,
    bedrock_model_id VARCHAR(256),
    bedrock_tokens_used INTEGER,

    -- Data profile
    data_profile JSONB,

    -- Pipeline configuration
    pipeline_config JSONB,

    -- Node outputs (stores output from each node)
    node_outputs JSONB DEFAULT '{}'::jsonb,

    -- Results
    best_model_name VARCHAR(128),
    best_model_score FLOAT,
    evaluation_metrics JSONB,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT pipeline_runs_run_id_unique UNIQUE (pipeline_run_id)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Time-based queries
CREATE INDEX idx_pipeline_runs_created_at ON pipeline_runs(created_at DESC);
CREATE INDEX idx_pipeline_runs_start_time ON pipeline_runs(start_time DESC);

-- Status filtering
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status);

-- MLflow lookups
CREATE INDEX idx_pipeline_runs_mlflow_run ON pipeline_runs(mlflow_run_id);
CREATE INDEX idx_pipeline_runs_mlflow_experiment ON pipeline_runs(mlflow_experiment_id);

-- Experiment name filtering
CREATE INDEX idx_pipeline_runs_experiment_name ON pipeline_runs(experiment_name);

-- JSONB indexes
CREATE INDEX idx_pipeline_runs_extracted_config_gin ON pipeline_runs USING gin(extracted_config);
CREATE INDEX idx_pipeline_runs_data_profile_gin ON pipeline_runs USING gin(data_profile);
CREATE INDEX idx_pipeline_runs_node_outputs_gin ON pipeline_runs USING gin(node_outputs);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE pipeline_runs IS 'Stores ML pipeline run state and execution history';

COMMENT ON COLUMN pipeline_runs.pipeline_run_id IS 'Unique identifier for pipeline run';
COMMENT ON COLUMN pipeline_runs.status IS 'Current status: pending, running, completed, failed, stopped';
COMMENT ON COLUMN pipeline_runs.current_node IS 'Currently executing node';
COMMENT ON COLUMN pipeline_runs.completed_nodes IS 'Array of completed node names (JSONB)';
COMMENT ON COLUMN pipeline_runs.failed_nodes IS 'Array of failed node names (JSONB)';
COMMENT ON COLUMN pipeline_runs.node_outputs IS 'Outputs from each node (JSONB map: node_name -> output)';
COMMENT ON COLUMN pipeline_runs.extracted_config IS 'Bedrock-extracted configuration (if natural language mode)';
COMMENT ON COLUMN pipeline_runs.data_profile IS 'Data profile stats (samples, features, target distribution)';

-- ============================================================================
-- Example Queries
-- ============================================================================

-- Get all running pipelines
-- SELECT * FROM pipeline_runs WHERE status = 'running' ORDER BY start_time DESC;

-- Get recent runs
-- SELECT pipeline_run_id, experiment_name, status, created_at
-- FROM pipeline_runs
-- ORDER BY created_at DESC
-- LIMIT 10;

-- Get runs for a specific experiment
-- SELECT * FROM pipeline_runs
-- WHERE mlflow_experiment_id = '1'
-- ORDER BY created_at DESC;

-- Get runs with high confidence extraction
-- SELECT * FROM pipeline_runs
-- WHERE confidence > 0.8
-- ORDER BY created_at DESC;

-- ============================================================================
-- End of Schema
-- ============================================================================
