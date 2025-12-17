"""Database service for pipeline runs persistence."""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)


class PipelineRunsDB:
    """Database service for pipeline runs."""

    def __init__(self):
        """Initialize database connection parameters from environment."""
        self.conn_params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "ml_pipeline"),
            "user": os.getenv("POSTGRES_USER", "ml_pipeline_user"),
            "password": os.getenv("POSTGRES_PASSWORD", "changeme"),
        }

    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = None
        try:
            conn = psycopg2.connect(**self.conn_params)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def save_run(self, run_data: Dict[str, Any]) -> None:
        """
        Save or update a pipeline run.

        Args:
            run_data: Dictionary containing run data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Convert lists to JSON
            completed_nodes = Json(run_data.get("completed_nodes", []))
            failed_nodes = Json(run_data.get("failed_nodes", []))
            errors = Json(run_data.get("errors", []))
            warnings = Json(run_data.get("warnings", []))
            extracted_config = Json(run_data.get("extracted_config")) if run_data.get("extracted_config") else None
            assumptions = Json(run_data.get("assumptions")) if run_data.get("assumptions") else None
            config_warnings = Json(run_data.get("config_warnings")) if run_data.get("config_warnings") else None
            data_profile = Json(run_data.get("data_profile")) if run_data.get("data_profile") else None
            pipeline_config = Json(run_data.get("pipeline_config")) if run_data.get("pipeline_config") else None
            node_outputs = Json(run_data.get("node_outputs", {}))
            evaluation_metrics = Json(run_data.get("evaluation_metrics")) if run_data.get("evaluation_metrics") else None
            metadata = Json(run_data.get("metadata", {}))

            # Upsert query
            query = """
                INSERT INTO pipeline_runs (
                    pipeline_run_id, mlflow_run_id, mlflow_experiment_id,
                    experiment_name, user_prompt, data_path,
                    created_at, start_time, end_time,
                    status, current_node,
                    completed_nodes, failed_nodes, errors, warnings,
                    extracted_config, confidence, reasoning, assumptions, config_warnings,
                    bedrock_model_id, bedrock_tokens_used,
                    data_profile, pipeline_config, node_outputs,
                    best_model_name, best_model_score, evaluation_metrics,
                    metadata
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (pipeline_run_id) DO UPDATE SET
                    mlflow_run_id = EXCLUDED.mlflow_run_id,
                    status = EXCLUDED.status,
                    current_node = EXCLUDED.current_node,
                    completed_nodes = EXCLUDED.completed_nodes,
                    failed_nodes = EXCLUDED.failed_nodes,
                    errors = EXCLUDED.errors,
                    warnings = EXCLUDED.warnings,
                    end_time = EXCLUDED.end_time,
                    node_outputs = EXCLUDED.node_outputs,
                    best_model_name = EXCLUDED.best_model_name,
                    best_model_score = EXCLUDED.best_model_score,
                    evaluation_metrics = EXCLUDED.evaluation_metrics,
                    metadata = EXCLUDED.metadata
            """

            cursor.execute(query, (
                run_data["pipeline_run_id"],
                run_data.get("mlflow_run_id"),
                run_data.get("mlflow_experiment_id"),
                run_data.get("experiment_name"),
                run_data.get("user_prompt"),
                run_data.get("data_path"),
                run_data.get("created_at", datetime.now()),
                run_data.get("start_time"),
                run_data.get("end_time"),
                run_data.get("status", "pending"),
                run_data.get("current_node"),
                completed_nodes,
                failed_nodes,
                errors,
                warnings,
                extracted_config,
                run_data.get("confidence"),
                run_data.get("reasoning"),
                assumptions,
                config_warnings,
                run_data.get("bedrock_model_id"),
                run_data.get("bedrock_tokens_used"),
                data_profile,
                pipeline_config,
                node_outputs,
                run_data.get("best_model_name"),
                run_data.get("best_model_score"),
                evaluation_metrics,
                metadata
            ))

            cursor.close()
            logger.info(f"Saved pipeline run: {run_data['pipeline_run_id']}")

    def get_run(self, pipeline_run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a pipeline run by ID.

        Args:
            pipeline_run_id: Pipeline run identifier

        Returns:
            Run data dictionary or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM pipeline_runs WHERE pipeline_run_id = %s",
                (pipeline_run_id,)
            )
            row = cursor.fetchone()
            cursor.close()

            if row:
                return dict(row)
            return None

    def get_all_runs(
        self,
        limit: int = 100,
        status: Optional[str] = None,
        experiment_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all pipeline runs with optional filtering.

        Args:
            limit: Maximum number of runs to return
            status: Filter by status (optional)
            experiment_id: Filter by experiment ID (optional)

        Returns:
            List of run data dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Build query
            query = "SELECT * FROM pipeline_runs WHERE 1=1"
            params = []

            if status:
                query += " AND status = %s"
                params.append(status)

            if experiment_id:
                query += " AND mlflow_experiment_id = %s"
                params.append(experiment_id)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in rows]

    def update_run_status(
        self,
        pipeline_run_id: str,
        status: str,
        current_node: Optional[str] = None,
        end_time: Optional[datetime] = None
    ) -> None:
        """
        Update run status and current node.

        Args:
            pipeline_run_id: Pipeline run identifier
            status: New status
            current_node: Current node (optional)
            end_time: End time (optional)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                UPDATE pipeline_runs
                SET status = %s, current_node = %s, end_time = %s
                WHERE pipeline_run_id = %s
            """

            cursor.execute(query, (status, current_node, end_time, pipeline_run_id))
            cursor.close()
            logger.info(f"Updated run status: {pipeline_run_id} -> {status}")

    def add_node_output(
        self,
        pipeline_run_id: str,
        node_name: str,
        output: Dict[str, Any]
    ) -> None:
        """
        Add output from a node execution.

        Args:
            pipeline_run_id: Pipeline run identifier
            node_name: Name of the node
            output: Output data from the node
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                UPDATE pipeline_runs
                SET node_outputs = jsonb_set(
                    COALESCE(node_outputs, '{}'::jsonb),
                    %s,
                    %s
                )
                WHERE pipeline_run_id = %s
            """

            cursor.execute(query, (
                [node_name],  # JSONB path
                Json(output),  # Value to set
                pipeline_run_id
            ))
            cursor.close()
            logger.info(f"Added output for node {node_name} in run {pipeline_run_id}")

    def delete_run(self, pipeline_run_id: str) -> None:
        """
        Delete a pipeline run.

        Args:
            pipeline_run_id: Pipeline run identifier
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM pipeline_runs WHERE pipeline_run_id = %s",
                (pipeline_run_id,)
            )
            cursor.close()
            logger.info(f"Deleted pipeline run: {pipeline_run_id}")


# Singleton instance
_pipeline_runs_db = None


def get_pipeline_runs_db() -> PipelineRunsDB:
    """Get singleton instance of PipelineRunsDB."""
    global _pipeline_runs_db
    if _pipeline_runs_db is None:
        _pipeline_runs_db = PipelineRunsDB()
    return _pipeline_runs_db
