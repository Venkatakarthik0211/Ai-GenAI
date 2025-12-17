-- ============================================================================
-- Review Questions Storage Database Schema (Algorithm-Aware HITL)
-- ============================================================================
--
-- Purpose: Store algorithm-aware validation questions from two-agent HITL system
--          - Agent 1A (AlgorithmCategoryPredictor): Predicts algorithm category
--          - Agent 1B (PreprocessingQuestionGenerator): Generates algorithm-aware questions
--
-- Storage Architecture: PostgreSQL with pgvector
-- 1. MLflow Artifacts - Experiment lineage
-- 2. PostgreSQL (this) - Structured data, full-text search, and vector embeddings
--
-- Database: PostgreSQL 12+ with pgvector extension
-- Features: JSONB columns, full-text search, vector similarity search, indexing
-- ============================================================================

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop table if exists (for clean recreate)
DROP TABLE IF EXISTS review_questions CASCADE;

-- ============================================================================
-- Main Review Questions Table (Algorithm-Aware Two-Agent System)
-- ============================================================================

CREATE TABLE review_questions (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Pipeline identifiers
    pipeline_run_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,

    -- ========================================================================
    -- AGENT 1A: AlgorithmCategoryPredictor Outputs
    -- ========================================================================
    algorithm_category VARCHAR(50),  -- linear_models, tree_models, neural_networks, ensemble, time_series
    algorithm_confidence FLOAT,      -- Confidence score (0.0-1.0)
    algorithm_requirements JSONB,    -- {scaling_required, outlier_sensitive, handles_missing, categorical_encoding_preference}
    preprocessing_priorities JSONB,  -- {clean_data: priority, handle_missing: priority, ...}
    agent_1a_response JSONB,         -- Full Agent 1A response for lineage

    -- ========================================================================
    -- AGENT 1B: PreprocessingQuestionGenerator Outputs
    -- ========================================================================
    questions JSONB NOT NULL,               -- Array of algorithm-aware question objects
    question_count INTEGER,                 -- Total number of questions (4-20)
    question_count_by_step JSONB,           -- {clean_data: 2, handle_missing: 3, ...}
    preprocessing_recommendations JSONB,    -- Algorithm-specific preprocessing recommendations
    agent_1b_response JSONB,                -- Full Agent 1B response for lineage

    -- ========================================================================
    -- Review State and User Responses
    -- ========================================================================
    answers JSONB,                          -- User answers to questions
    review_status VARCHAR(50) DEFAULT 'awaiting_review',  -- awaiting_review, approved, rejected, modified
    user_feedback TEXT,                     -- Optional user feedback
    approved BOOLEAN,                       -- Whether user approved

    -- ========================================================================
    -- Context and Metadata
    -- ========================================================================
    user_prompt TEXT,                       -- Original user prompt
    data_profile JSONB,                     -- Data profile from load_data node
    mlflow_run_id VARCHAR(64),              -- MLflow run ID for experiment tracking
    bedrock_model_id VARCHAR(256),          -- AWS Bedrock model ID used

    -- Vector embedding for semantic search (384 dimensions)
    embedding vector(384),

    -- ========================================================================
    -- Timestamps
    -- ========================================================================
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    answered_at TIMESTAMP,

    -- ========================================================================
    -- Constraints
    -- ========================================================================
    CONSTRAINT review_questions_pipeline_run_unique UNIQUE (pipeline_run_id)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Time-based queries
CREATE INDEX idx_review_questions_created_at ON review_questions(created_at DESC);
CREATE INDEX idx_review_questions_updated_at ON review_questions(updated_at DESC);
CREATE INDEX idx_review_questions_answered_at ON review_questions(answered_at DESC);

-- Pipeline and session lookups
CREATE INDEX idx_pipeline_run_id ON review_questions(pipeline_run_id);
CREATE INDEX idx_session_id ON review_questions(session_id);
CREATE INDEX idx_mlflow_run_id ON review_questions(mlflow_run_id);

-- Status and approval filtering
CREATE INDEX idx_review_status ON review_questions(review_status);
CREATE INDEX idx_approved ON review_questions(approved);

-- Algorithm category filtering (for analytics)
CREATE INDEX idx_algorithm_category ON review_questions(algorithm_category);

-- JSONB indexes for querying nested data
CREATE INDEX idx_algorithm_requirements_gin ON review_questions USING gin(algorithm_requirements);
CREATE INDEX idx_preprocessing_priorities_gin ON review_questions USING gin(preprocessing_priorities);
CREATE INDEX idx_questions_gin ON review_questions USING gin(questions);
CREATE INDEX idx_answers_gin ON review_questions USING gin(answers);
CREATE INDEX idx_data_profile_gin ON review_questions USING gin(data_profile);
CREATE INDEX idx_agent_1a_response_gin ON review_questions USING gin(agent_1a_response);
CREATE INDEX idx_agent_1b_response_gin ON review_questions USING gin(agent_1b_response);

-- Full-text search on user prompts
CREATE INDEX idx_user_prompt_fts ON review_questions USING gin(to_tsvector('english', COALESCE(user_prompt, '')));

-- Vector similarity search index (HNSW for fast approximate nearest neighbor search)
CREATE INDEX idx_embedding_hnsw ON review_questions USING hnsw (embedding vector_cosine_ops);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE review_questions IS 'Stores algorithm-aware validation questions from two-agent HITL system';

COMMENT ON COLUMN review_questions.id IS 'Auto-incrementing primary key';
COMMENT ON COLUMN review_questions.pipeline_run_id IS 'Unique identifier for pipeline run';
COMMENT ON COLUMN review_questions.session_id IS 'Review session identifier';

-- Agent 1A comments
COMMENT ON COLUMN review_questions.algorithm_category IS 'Predicted algorithm category (Agent 1A)';
COMMENT ON COLUMN review_questions.algorithm_confidence IS 'Agent 1A confidence score (0.0-1.0)';
COMMENT ON COLUMN review_questions.algorithm_requirements IS 'Algorithm requirements (scaling, outlier sensitivity, etc.)';
COMMENT ON COLUMN review_questions.preprocessing_priorities IS 'Preprocessing step priorities (critical/required/optional)';
COMMENT ON COLUMN review_questions.agent_1a_response IS 'Full Agent 1A response for lineage tracking';

-- Agent 1B comments
COMMENT ON COLUMN review_questions.questions IS 'Array of algorithm-aware question objects (Agent 1B)';
COMMENT ON COLUMN review_questions.question_count IS 'Total number of questions generated (4-20)';
COMMENT ON COLUMN review_questions.question_count_by_step IS 'Question count by preprocessing step';
COMMENT ON COLUMN review_questions.preprocessing_recommendations IS 'Algorithm-specific preprocessing recommendations';
COMMENT ON COLUMN review_questions.agent_1b_response IS 'Full Agent 1B response for lineage tracking';

-- Review state comments
COMMENT ON COLUMN review_questions.answers IS 'User answers to questions';
COMMENT ON COLUMN review_questions.review_status IS 'Status: awaiting_review, approved, rejected, modified';
COMMENT ON COLUMN review_questions.user_feedback IS 'Optional feedback from user';
COMMENT ON COLUMN review_questions.approved IS 'Whether user approved the configuration';

-- Metadata comments
COMMENT ON COLUMN review_questions.user_prompt IS 'Original user prompt';
COMMENT ON COLUMN review_questions.data_profile IS 'Data profile from load_data node';
COMMENT ON COLUMN review_questions.mlflow_run_id IS 'MLflow run ID for experiment tracking';
COMMENT ON COLUMN review_questions.bedrock_model_id IS 'AWS Bedrock model ID used';
COMMENT ON COLUMN review_questions.embedding IS 'Vector embedding for semantic similarity search (384 dimensions)';

-- Timestamp comments
COMMENT ON COLUMN review_questions.created_at IS 'When the review session was created';
COMMENT ON COLUMN review_questions.updated_at IS 'When the review session was last updated';
COMMENT ON COLUMN review_questions.answered_at IS 'When the user answered the questions';

-- ============================================================================
-- Example Queries
-- ============================================================================

-- Query 1: Find all pending reviews
-- SELECT * FROM review_questions WHERE review_status = 'awaiting_review' ORDER BY created_at DESC;

-- Query 2: Find reviews with low algorithm confidence
-- SELECT pipeline_run_id, algorithm_category, algorithm_confidence, approved
-- FROM review_questions
-- WHERE algorithm_confidence < 0.75
-- ORDER BY created_at DESC;

-- Query 3: Get average approval rate by algorithm category
-- SELECT
--     algorithm_category,
--     COUNT(*) AS total_reviews,
--     SUM(CASE WHEN approved THEN 1 ELSE 0 END) AS approved_count,
--     ROUND(100.0 * SUM(CASE WHEN approved THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate
-- FROM review_questions
-- WHERE review_status != 'awaiting_review'
-- GROUP BY algorithm_category;

-- Query 4: Find preprocessing priorities for tree models
-- SELECT pipeline_run_id, preprocessing_priorities, question_count
-- FROM review_questions
-- WHERE algorithm_category = 'tree_models'
-- ORDER BY created_at DESC;

-- Query 5: Get question count distribution by preprocessing step
-- SELECT
--     algorithm_category,
--     AVG((question_count_by_step->>'clean_data')::int) AS avg_clean_data_questions,
--     AVG((question_count_by_step->>'handle_missing')::int) AS avg_missing_questions,
--     AVG((question_count_by_step->>'encode_features')::int) AS avg_encode_questions,
--     AVG((question_count_by_step->>'scale_features')::int) AS avg_scale_questions
-- FROM review_questions
-- WHERE question_count_by_step IS NOT NULL
-- GROUP BY algorithm_category;

-- Query 6: Find all reviews for a specific algorithm category with answers
-- SELECT pipeline_run_id, algorithm_confidence, question_count, approved, user_feedback
-- FROM review_questions
-- WHERE algorithm_category = 'neural_networks'
-- AND answers IS NOT NULL
-- ORDER BY created_at DESC;

-- Query 7: Get preprocessing technique selections by algorithm category
-- SELECT
--     algorithm_category,
--     answers->0->>'technique' AS clean_data_technique,
--     COUNT(*) AS usage_count
-- FROM review_questions
-- WHERE answers IS NOT NULL
-- GROUP BY algorithm_category, clean_data_technique
-- ORDER BY algorithm_category, usage_count DESC;

-- ============================================================================
-- End of Schema
-- ============================================================================
