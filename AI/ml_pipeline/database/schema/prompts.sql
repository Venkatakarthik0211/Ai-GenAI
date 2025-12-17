-- ============================================================================
-- Prompt Storage Database Schema
-- ============================================================================
--
-- Purpose: Store user prompts and extracted configurations for ML pipeline
--
-- Storage Architecture: PostgreSQL with pgvector
-- 1. MLflow Artifacts - Experiment lineage
-- 2. PostgreSQL (this) - Structured data, full-text search, and vector embeddings
--
-- Database: PostgreSQL 12+ with pgvector extension
-- Features: JSONB columns, full-text search, vector similarity search, indexing
-- ============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop table if exists (for clean recreate)
DROP TABLE IF EXISTS prompts CASCADE;

-- ============================================================================
-- Main Prompts Table
-- ============================================================================

CREATE TABLE prompts (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Timestamps
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Pipeline identifiers
    pipeline_run_id VARCHAR(64) NOT NULL,
    mlflow_run_id VARCHAR(64),
    mlflow_experiment_id VARCHAR(64),

    -- User inputs
    user_prompt TEXT NOT NULL,
    user_hints JSONB,

    -- Vector embedding for semantic search (384 dimensions for sentence-transformers/all-MiniLM-L6-v2)
    embedding vector(384),

    -- Extracted configuration (JSONB for querying)
    extracted_config JSONB NOT NULL,

    -- Confidence and quality metrics
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),

    -- Agent reasoning and metadata
    reasoning TEXT,
    assumptions JSONB,
    warnings JSONB,

    -- Bedrock metadata
    bedrock_model_id VARCHAR(256),
    bedrock_tokens_used INTEGER,

    -- Execution status
    extraction_success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,

    -- Additional metadata
    data_path TEXT,

    CONSTRAINT prompts_pipeline_run_unique UNIQUE (pipeline_run_id)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Time-based queries (most recent prompts)
CREATE INDEX idx_prompts_timestamp ON prompts(timestamp DESC);
CREATE INDEX idx_prompts_created_at ON prompts(created_at DESC);

-- Pipeline and MLflow lookups
CREATE INDEX idx_prompts_pipeline_run ON prompts(pipeline_run_id);
CREATE INDEX idx_prompts_mlflow_run ON prompts(mlflow_run_id);
CREATE INDEX idx_prompts_mlflow_experiment ON prompts(mlflow_experiment_id);

-- Confidence filtering (find high/low confidence extractions)
CREATE INDEX idx_prompts_confidence ON prompts(confidence);

-- Success status filtering
CREATE INDEX idx_prompts_extraction_success ON prompts(extraction_success);

-- JSONB indexes for extracted configuration queries
CREATE INDEX idx_prompts_target_column ON prompts((extracted_config->>'target_column'));
CREATE INDEX idx_prompts_analysis_type ON prompts((extracted_config->>'analysis_type'));
CREATE INDEX idx_prompts_experiment_name ON prompts((extracted_config->>'experiment_name'));

-- Full-text search on user prompts (for similarity search)
CREATE INDEX idx_prompts_user_prompt_fts ON prompts USING gin(to_tsvector('english', user_prompt));

-- GIN index for JSONB querying
CREATE INDEX idx_prompts_extracted_config_gin ON prompts USING gin(extracted_config);
CREATE INDEX idx_prompts_assumptions_gin ON prompts USING gin(assumptions);
CREATE INDEX idx_prompts_warnings_gin ON prompts USING gin(warnings);

-- Vector similarity search index (HNSW for fast approximate nearest neighbor search)
-- Using cosine distance for semantic similarity
CREATE INDEX idx_prompts_embedding_hnsw ON prompts USING hnsw (embedding vector_cosine_ops);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE prompts IS 'Stores user prompts and extracted ML pipeline configurations';

COMMENT ON COLUMN prompts.id IS 'Auto-incrementing primary key';
COMMENT ON COLUMN prompts.timestamp IS 'When the prompt was submitted';
COMMENT ON COLUMN prompts.pipeline_run_id IS 'Unique identifier for pipeline run (UUID)';
COMMENT ON COLUMN prompts.mlflow_run_id IS 'MLflow run ID for experiment tracking';
COMMENT ON COLUMN prompts.mlflow_experiment_id IS 'MLflow experiment ID';
COMMENT ON COLUMN prompts.user_prompt IS 'Natural language prompt from user';
COMMENT ON COLUMN prompts.user_hints IS 'Optional hints provided by user (JSONB)';
COMMENT ON COLUMN prompts.embedding IS 'Vector embedding of user_prompt for semantic similarity search (384 dimensions)';
COMMENT ON COLUMN prompts.extracted_config IS 'Extracted configuration (JSONB) with target_column, experiment_name, etc.';
COMMENT ON COLUMN prompts.confidence IS 'Agent confidence score (0.0-1.0)';
COMMENT ON COLUMN prompts.reasoning IS 'Agent reasoning for extraction decisions';
COMMENT ON COLUMN prompts.assumptions IS 'List of assumptions made during extraction (JSONB array)';
COMMENT ON COLUMN prompts.warnings IS 'List of warnings about ambiguities (JSONB array)';
COMMENT ON COLUMN prompts.bedrock_model_id IS 'AWS Bedrock model ID used for extraction';
COMMENT ON COLUMN prompts.bedrock_tokens_used IS 'Total tokens used (input + output)';
COMMENT ON COLUMN prompts.extraction_success IS 'Whether extraction succeeded';
COMMENT ON COLUMN prompts.error_message IS 'Error message if extraction failed';
COMMENT ON COLUMN prompts.data_path IS 'Path to data file';

-- ============================================================================
-- Example Queries
-- ============================================================================

-- Query 1: Find all prompts for a specific target column
-- SELECT * FROM prompts WHERE extracted_config->>'target_column' = 'price';

-- Query 2: Find high confidence classification tasks
-- SELECT * FROM prompts
-- WHERE confidence > 0.9
-- AND extracted_config->>'analysis_type' = 'classification';

-- Query 3: Full-text search for similar prompts
-- SELECT *, ts_rank(to_tsvector('english', user_prompt), plainto_tsquery('predict house prices')) AS rank
-- FROM prompts
-- WHERE to_tsvector('english', user_prompt) @@ plainto_tsquery('predict house prices')
-- ORDER BY rank DESC
-- LIMIT 5;

-- Query 4: Get prompts with warnings
-- SELECT user_prompt, warnings
-- FROM prompts
-- WHERE jsonb_array_length(warnings) > 0;

-- Query 5: Average confidence by analysis type
-- SELECT
--     extracted_config->>'analysis_type' AS analysis_type,
--     COUNT(*) AS count,
--     AVG(confidence) AS avg_confidence,
--     MIN(confidence) AS min_confidence,
--     MAX(confidence) AS max_confidence
-- FROM prompts
-- WHERE extraction_success = TRUE
-- GROUP BY extracted_config->>'analysis_type';

-- Query 6: Most common target columns
-- SELECT
--     extracted_config->>'target_column' AS target_column,
--     COUNT(*) AS frequency
-- FROM prompts
-- WHERE extraction_success = TRUE
-- GROUP BY extracted_config->>'target_column'
-- ORDER BY frequency DESC
-- LIMIT 10;

-- Query 7: Recent failed extractions
-- SELECT timestamp, user_prompt, error_message, confidence
-- FROM prompts
-- WHERE extraction_success = FALSE
-- ORDER BY timestamp DESC
-- LIMIT 10;

-- Query 8: Find semantically similar prompts using vector search
-- Given an embedding vector, find the 5 most similar prompts
-- SELECT user_prompt, extracted_config, confidence,
--        1 - (embedding <=> '[0.1, 0.2, ..., 0.384]'::vector) AS similarity
-- FROM prompts
-- WHERE embedding IS NOT NULL
-- ORDER BY embedding <=> '[0.1, 0.2, ..., 0.384]'::vector
-- LIMIT 5;

-- Query 9: Hybrid search (combine vector similarity + full-text search)
-- SELECT user_prompt, extracted_config,
--        1 - (embedding <=> '[0.1, 0.2, ..., 0.384]'::vector) AS vector_similarity,
--        ts_rank(to_tsvector('english', user_prompt), plainto_tsquery('classify data')) AS text_rank
-- FROM prompts
-- WHERE to_tsvector('english', user_prompt) @@ plainto_tsquery('classify data')
--   AND embedding IS NOT NULL
-- ORDER BY (1 - (embedding <=> '[0.1, 0.2, ..., 0.384]'::vector)) * 0.7 + ts_rank(to_tsvector('english', user_prompt), plainto_tsquery('classify data')) * 0.3 DESC
-- LIMIT 5;

-- Query 10: Find prompts within a similarity threshold
-- SELECT user_prompt, extracted_config, confidence,
--        1 - (embedding <=> '[0.1, 0.2, ..., 0.384]'::vector) AS similarity
-- FROM prompts
-- WHERE embedding IS NOT NULL
--   AND (1 - (embedding <=> '[0.1, 0.2, ..., 0.384]'::vector)) > 0.8
-- ORDER BY similarity DESC;

-- ============================================================================
-- Notes on Vector Operations
-- ============================================================================
-- <-> : L2 distance (Euclidean)
-- <#> : Inner product (negative, so larger is better)
-- <=> : Cosine distance (0 = identical, 2 = opposite)
--
-- Cosine similarity = 1 - cosine_distance
-- Higher similarity (closer to 1) means more similar prompts
-- ============================================================================

-- ============================================================================
-- End of Schema
-- ============================================================================
