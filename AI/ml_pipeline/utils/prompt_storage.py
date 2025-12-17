"""
Prompt Storage System - PostgreSQL with pgvector

Stores user prompts and extracted configurations with vector embeddings for semantic search:
1. PostgreSQL with pgvector - Structured querying, analytics, and vector similarity search
2. MLflow Artifacts - Experiment lineage and tracking

Uses sentence-transformers for generating embeddings to enable semantic similarity search.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class PromptStorageError(Exception):
    """Base exception for prompt storage errors"""
    pass


class PromptStorage:
    """
    Storage system for user prompts and extracted configurations with vector embeddings.

    Provides unified interface for storing and querying prompts:
    - PostgreSQL with pgvector (structured data + vector embeddings)
    - MLflow Artifacts (experiment tracking integration)

    Features:
    - Semantic similarity search using vector embeddings
    - Full-text search using PostgreSQL FTS
    - Hybrid search combining both approaches
    - Analytics and aggregate queries
    """

    def __init__(
        self,
        postgres_connection_string: str,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        mlflow_client: Optional[Any] = None
    ):
        """
        Initialize prompt storage system.

        Args:
            postgres_connection_string: PostgreSQL connection string
            embedding_model_name: Sentence transformer model name (default: all-MiniLM-L6-v2, 384 dimensions)
            mlflow_client: MLflow client instance (optional)
        """
        self.postgres_connection_string = postgres_connection_string
        self.mlflow_client = mlflow_client

        # Initialize PostgreSQL connection
        self._init_postgres()

        # Initialize embedding model
        self._init_embedding_model(embedding_model_name)

        logger.info(f"PromptStorage initialized with embedding model: {embedding_model_name}")

    def _init_postgres(self):
        """Initialize PostgreSQL connection with pgvector support"""
        try:
            self.postgres_conn = psycopg2.connect(self.postgres_connection_string)

            # Register pgvector type
            register_vector(self.postgres_conn)

            logger.info("PostgreSQL connection established with pgvector support")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise PromptStorageError(f"PostgreSQL connection failed: {e}")

    def _init_embedding_model(self, model_name: str):
        """
        Initialize sentence transformer model for embeddings.

        Args:
            model_name: Sentence transformer model name
        """
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded (dimension: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise PromptStorageError(f"Embedding model initialization failed: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise PromptStorageError(f"Embedding generation failed: {e}")

    def save_prompt(
        self,
        user_prompt: str,
        extracted_config: Dict[str, Any],
        pipeline_run_id: str,
        mlflow_run_id: Optional[str] = None,
        mlflow_experiment_id: Optional[str] = None,
        confidence: float = 0.0,
        reasoning: Optional[Dict[str, str]] = None,
        assumptions: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        bedrock_model_id: Optional[str] = None,
        bedrock_tokens_used: Optional[int] = None,
        user_hints: Optional[Dict[str, Any]] = None,
        data_path: Optional[str] = None,
        extraction_success: bool = True,
        error_message: Optional[str] = None
    ) -> int:
        """
        Save prompt with vector embedding to PostgreSQL and optionally to MLflow.

        Args:
            user_prompt: Natural language prompt from user
            extracted_config: Extracted configuration dictionary
            pipeline_run_id: Unique pipeline run identifier
            mlflow_run_id: MLflow run ID
            mlflow_experiment_id: MLflow experiment ID
            confidence: Agent confidence score (0.0-1.0)
            reasoning: Reasoning dictionary for extraction decisions
            assumptions: List of assumptions made
            warnings: List of warnings about ambiguities
            bedrock_model_id: Bedrock model ID used
            bedrock_tokens_used: Total tokens used
            user_hints: Optional hints provided by user
            data_path: Path to data file
            extraction_success: Whether extraction succeeded
            error_message: Error message if extraction failed

        Returns:
            PostgreSQL record ID (primary key)

        Raises:
            PromptStorageError: If storage fails
        """
        logger.info(f"Saving prompt for pipeline run: {pipeline_run_id}")

        timestamp = datetime.now()

        # Generate embedding for the user prompt
        embedding = self.generate_embedding(user_prompt)
        logger.debug(f"Generated embedding (dim={len(embedding)})")

        # Prepare data for storage
        prompt_data = {
            "timestamp": timestamp,
            "pipeline_run_id": pipeline_run_id,
            "mlflow_run_id": mlflow_run_id,
            "mlflow_experiment_id": mlflow_experiment_id,
            "user_prompt": user_prompt,
            "user_hints": user_hints or {},
            "embedding": embedding,
            "extracted_config": extracted_config,
            "confidence": confidence,
            "reasoning": json.dumps(reasoning) if reasoning else None,
            "assumptions": json.dumps(assumptions) if assumptions else None,
            "warnings": json.dumps(warnings) if warnings else None,
            "bedrock_model_id": bedrock_model_id,
            "bedrock_tokens_used": bedrock_tokens_used,
            "data_path": data_path,
            "extraction_success": extraction_success,
            "error_message": error_message
        }

        # Storage 1: PostgreSQL with embedding
        prompt_id = self._save_to_postgres(prompt_data)
        logger.info(f"✓ Saved to PostgreSQL with embedding (ID: {prompt_id})")

        # Storage 2: MLflow Artifacts
        if self.mlflow_client and mlflow_run_id:
            try:
                self._save_to_mlflow(mlflow_run_id, prompt_data)
                logger.info(f"✓ Saved to MLflow artifacts")
            except Exception as e:
                logger.warning(f"Failed to save to MLflow: {e} (continuing...)")
        else:
            logger.debug("MLflow storage skipped (no client or run_id)")

        logger.info(f"Prompt saved successfully (ID: {prompt_id})")
        return prompt_id

    def _save_to_postgres(self, prompt_data: Dict[str, Any]) -> int:
        """
        Save prompt to PostgreSQL database with vector embedding.

        Args:
            prompt_data: Dictionary with prompt data

        Returns:
            PostgreSQL record ID
        """
        cursor = self.postgres_conn.cursor()

        try:
            sql = """
                INSERT INTO prompts (
                    timestamp, pipeline_run_id, mlflow_run_id, mlflow_experiment_id,
                    user_prompt, user_hints, embedding, extracted_config, confidence,
                    reasoning, assumptions, warnings,
                    bedrock_model_id, bedrock_tokens_used,
                    data_path, extraction_success, error_message
                ) VALUES (
                    %(timestamp)s, %(pipeline_run_id)s, %(mlflow_run_id)s, %(mlflow_experiment_id)s,
                    %(user_prompt)s, %(user_hints)s, %(embedding)s, %(extracted_config)s, %(confidence)s,
                    %(reasoning)s, %(assumptions)s, %(warnings)s,
                    %(bedrock_model_id)s, %(bedrock_tokens_used)s,
                    %(data_path)s, %(extraction)s, %(error_message)s
                )
                RETURNING id;
            """

            cursor.execute(sql, prompt_data)
            prompt_id = cursor.fetchone()[0]

            self.postgres_conn.commit()
            cursor.close()

            return prompt_id

        except psycopg2.Error as e:
            self.postgres_conn.rollback()
            cursor.close()
            logger.error(f"PostgreSQL insert failed: {e}")
            raise PromptStorageError(f"Failed to save to PostgreSQL: {e}")

    def _save_to_mlflow(self, mlflow_run_id: str, prompt_data: Dict[str, Any]):
        """
        Save prompt to MLflow artifacts.

        Args:
            mlflow_run_id: MLflow run ID
            prompt_data: Dictionary with prompt data
        """
        if not self.mlflow_client:
            return

        try:
            import mlflow
            import tempfile
            import os

            # Create temporary directory for artifacts
            with tempfile.TemporaryDirectory() as tmpdir:
                # Save user prompt
                prompt_path = os.path.join(tmpdir, "user_prompt.txt")
                with open(prompt_path, 'w') as f:
                    f.write(prompt_data["user_prompt"])

                # Save extracted config
                config_path = os.path.join(tmpdir, "extracted_config.json")
                with open(config_path, 'w') as f:
                    json.dump(prompt_data["extracted_config"], f, indent=2)

                # Save full prompt data (excluding embedding for space efficiency)
                full_data_path = os.path.join(tmpdir, "prompt_data.json")
                data_copy = {k: v for k, v in prompt_data.items() if k != 'embedding'}
                data_copy["timestamp"] = data_copy["timestamp"].isoformat()
                with open(full_data_path, 'w') as f:
                    json.dump(data_copy, f, indent=2)

                # Log artifacts to MLflow
                with mlflow.start_run(run_id=mlflow_run_id):
                    mlflow.log_artifact(prompt_path, artifact_path="prompts")
                    mlflow.log_artifact(config_path, artifact_path="prompts")
                    mlflow.log_artifact(full_data_path, artifact_path="prompts")

        except Exception as e:
            logger.error(f"MLflow artifact logging failed: {e}")
            raise PromptStorageError(f"Failed to save to MLflow: {e}")

    def get_prompt_by_run_id(self, pipeline_run_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve prompt by pipeline run ID.

        Args:
            pipeline_run_id: Pipeline run identifier

        Returns:
            Dictionary with prompt data or None if not found
        """
        cursor = self.postgres_conn.cursor(cursor_factory=RealDictCursor)

        try:
            sql = """
                SELECT * FROM prompts
                WHERE pipeline_run_id = %s;
            """
            cursor.execute(sql, (pipeline_run_id,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                return dict(result)
            return None

        except psycopg2.Error as e:
            cursor.close()
            logger.error(f"PostgreSQL query failed: {e}")
            raise PromptStorageError(f"Failed to retrieve prompt: {e}")

    def search_similar_prompts_vector(
        self,
        query: str,
        limit: int = 5,
        min_confidence: float = 0.7,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for semantically similar prompts using vector similarity.

        Args:
            query: Search query (will be embedded)
            limit: Maximum number of results
            min_confidence: Minimum confidence threshold
            similarity_threshold: Minimum cosine similarity (0.0-1.0)

        Returns:
            List of dictionaries with prompt data, sorted by similarity
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)

        cursor = self.postgres_conn.cursor(cursor_factory=RealDictCursor)

        try:
            sql = """
                SELECT
                    *,
                    1 - (embedding <=> %s::vector) AS similarity
                FROM prompts
                WHERE
                    confidence >= %s
                    AND extraction_success = TRUE
                    AND embedding IS NOT NULL
                    AND (1 - (embedding <=> %s::vector)) >= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            cursor.execute(sql, (query_embedding, min_confidence, query_embedding,
                                similarity_threshold, query_embedding, limit))
            results = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            cursor.close()
            logger.error(f"PostgreSQL vector search failed: {e}")
            raise PromptStorageError(f"Failed to search prompts: {e}")

    def search_similar_prompts(
        self,
        query: str,
        limit: int = 5,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar prompts using full-text search.

        Args:
            query: Search query
            limit: Maximum number of results
            min_confidence: Minimum confidence threshold

        Returns:
            List of dictionaries with prompt data, sorted by relevance
        """
        cursor = self.postgres_conn.cursor(cursor_factory=RealDictCursor)

        try:
            sql = """
                SELECT
                    *,
                    ts_rank(to_tsvector('english', user_prompt), plainto_tsquery('english', %s)) AS rank
                FROM prompts
                WHERE
                    to_tsvector('english', user_prompt) @@ plainto_tsquery('english', %s)
                    AND confidence >= %s
                    AND extraction_success = TRUE
                ORDER BY rank DESC
                LIMIT %s;
            """
            cursor.execute(sql, (query, query, min_confidence, limit))
            results = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            cursor.close()
            logger.error(f"PostgreSQL search failed: {e}")
            raise PromptStorageError(f"Failed to search prompts: {e}")

    def search_hybrid(
        self,
        query: str,
        limit: int = 5,
        min_confidence: float = 0.7,
        vector_weight: float = 0.7,
        text_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and full-text search.

        Args:
            query: Search query
            limit: Maximum number of results
            min_confidence: Minimum confidence threshold
            vector_weight: Weight for vector similarity score (0.0-1.0)
            text_weight: Weight for text search rank (0.0-1.0)

        Returns:
            List of dictionaries with prompt data, sorted by combined score
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)

        cursor = self.postgres_conn.cursor(cursor_factory=RealDictCursor)

        try:
            sql = """
                SELECT
                    *,
                    1 - (embedding <=> %s::vector) AS vector_similarity,
                    ts_rank(to_tsvector('english', user_prompt), plainto_tsquery('english', %s)) AS text_rank,
                    (1 - (embedding <=> %s::vector)) * %s +
                    ts_rank(to_tsvector('english', user_prompt), plainto_tsquery('english', %s)) * %s AS hybrid_score
                FROM prompts
                WHERE
                    to_tsvector('english', user_prompt) @@ plainto_tsquery('english', %s)
                    AND confidence >= %s
                    AND extraction_success = TRUE
                    AND embedding IS NOT NULL
                ORDER BY hybrid_score DESC
                LIMIT %s;
            """
            cursor.execute(sql, (
                query_embedding, query, query_embedding, vector_weight,
                query, text_weight, query, min_confidence, limit
            ))
            results = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            cursor.close()
            logger.error(f"PostgreSQL hybrid search failed: {e}")
            raise PromptStorageError(f"Failed to search prompts: {e}")

    def get_prompts_by_target_column(
        self,
        target_column: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get prompts that extracted a specific target column.

        Args:
            target_column: Target column name
            limit: Maximum number of results

        Returns:
            List of dictionaries with prompt data
        """
        cursor = self.postgres_conn.cursor(cursor_factory=RealDictCursor)

        try:
            sql = """
                SELECT * FROM prompts
                WHERE
                    extracted_config->>'target_column' = %s
                    AND extraction_success = TRUE
                ORDER BY timestamp DESC
                LIMIT %s;
            """
            cursor.execute(sql, (target_column, limit))
            results = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            cursor.close()
            logger.error(f"PostgreSQL query failed: {e}")
            raise PromptStorageError(f"Failed to query prompts: {e}")

    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Get analytics summary of stored prompts.

        Returns:
            Dictionary with aggregate statistics
        """
        cursor = self.postgres_conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Total prompts and success rate
            cursor.execute("""
                SELECT
                    COUNT(*) AS total_prompts,
                    SUM(CASE WHEN extraction_success THEN 1 ELSE 0 END) AS successful_extractions,
                    AVG(confidence) AS avg_confidence,
                    MIN(confidence) AS min_confidence,
                    MAX(confidence) AS max_confidence
                FROM prompts;
            """)
            overall_stats = dict(cursor.fetchone())

            # By analysis type
            cursor.execute("""
                SELECT
                    extracted_config->>'analysis_type' AS analysis_type,
                    COUNT(*) AS count,
                    AVG(confidence) AS avg_confidence
                FROM prompts
                WHERE extraction_success = TRUE
                GROUP BY extracted_config->>'analysis_type';
            """)
            by_analysis_type = [dict(row) for row in cursor.fetchall()]

            # Most common target columns
            cursor.execute("""
                SELECT
                    extracted_config->>'target_column' AS target_column,
                    COUNT(*) AS frequency
                FROM prompts
                WHERE extraction_success = TRUE
                GROUP BY extracted_config->>'target_column'
                ORDER BY frequency DESC
                LIMIT 10;
            """)
            common_targets = [dict(row) for row in cursor.fetchall()]

            # Recent failures
            cursor.execute("""
                SELECT
                    timestamp,
                    user_prompt,
                    error_message,
                    confidence
                FROM prompts
                WHERE extraction_success = FALSE
                ORDER BY timestamp DESC
                LIMIT 5;
            """)
            recent_failures = [dict(row) for row in cursor.fetchall()]

            cursor.close()

            return {
                "overall": overall_stats,
                "by_analysis_type": by_analysis_type,
                "common_target_columns": common_targets,
                "recent_failures": recent_failures
            }

        except psycopg2.Error as e:
            cursor.close()
            logger.error(f"Analytics query failed: {e}")
            raise PromptStorageError(f"Failed to get analytics: {e}")

    def close(self):
        """Close database connections"""
        if self.postgres_conn:
            self.postgres_conn.close()
            logger.info("PostgreSQL connection closed")


def create_prompt_storage_from_env() -> PromptStorage:
    """
    Create PromptStorage instance from environment variables.

    Expected environment variables:
    - POSTGRES_HOST (default: localhost)
    - POSTGRES_PORT (default: 5432)
    - POSTGRES_DB (default: ml_pipeline)
    - POSTGRES_USER (required)
    - POSTGRES_PASSWORD (required)
    - EMBEDDING_MODEL (default: sentence-transformers/all-MiniLM-L6-v2)

    Returns:
        Configured PromptStorage instance
    """
    import os

    # Build PostgreSQL connection string
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_db = os.getenv('POSTGRES_DB', 'ml_pipeline')
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')

    if not postgres_user or not postgres_password:
        raise ValueError("POSTGRES_USER and POSTGRES_PASSWORD environment variables are required")

    postgres_connection_string = (
        f"postgresql://{postgres_user}:{postgres_password}@"
        f"{postgres_host}:{postgres_port}/{postgres_db}"
    )

    # Get embedding model configuration
    embedding_model = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

    return PromptStorage(
        postgres_connection_string=postgres_connection_string,
        embedding_model_name=embedding_model
    )
