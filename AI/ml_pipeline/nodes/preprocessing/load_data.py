"""Data loading node for ML Pipeline."""

import pandas as pd
import mlflow
from core.state import PipelineState, update_state, mark_node_completed
from core.exceptions import DataValidationError
from core.validators import validate_data


def load_data_node(state: PipelineState) -> PipelineState:
    """
    Load data and initialize MLflow run.

    Args:
        state: Current pipeline state

    Returns:
        Updated pipeline state with raw_data and MLflow run information
    """
    node_name = "load_data"

    try:
        # Extract configuration
        config = state["pipeline_config"]

        # Get data_path - supports both flat and nested structure
        if "data_path" in config:
            data_path = config["data_path"]
        elif "data" in config:
            data_path = config["data"].get("train_path")
        else:
            raise ValueError("data_path not found in pipeline_config")

        # Get target_column - supports both flat and nested structure
        # For unsupervised tasks (clustering, etc.), target_column can be None
        if "target_column" in config:
            target_column = config["target_column"]
        elif "data" in config:
            target_column = config["data"].get("target_column")
        else:
            target_column = None  # Default to None for unsupervised tasks

        # Start MLflow run (only if not already started)
        mlflow_config = config.get("mlflow", {})
        if mlflow_config.get("enable_logging", True):
            if not mlflow.active_run():
                experiment_id = state.get("mlflow_experiment_id")
                mlflow.start_run(
                    experiment_id=experiment_id,
                    run_name=f"pipeline_run_{state['pipeline_run_id']}"
                )

            run_id = mlflow.active_run().info.run_id

        # Load data
        if data_path.endswith('.csv'):
            raw_data = pd.read_csv(data_path)
        elif data_path.endswith('.parquet'):
            raw_data = pd.read_parquet(data_path)
        elif data_path.endswith(('.xlsx', '.xls')):
            raw_data = pd.read_excel(data_path)
        else:
            raise DataValidationError(f"Unsupported file format: {data_path}")

        # Validate data
        validation_results = validate_data(
            raw_data,
            target_column=target_column,
            min_samples=config.get("data", {}).get("min_samples", 100),
            max_missing_ratio=config.get("data", {}).get("max_missing_ratio", 0.3)
        )

        # Log to MLflow
        if mlflow.active_run():
            mlflow.log_params({
                "data_path": data_path,
                "n_rows": raw_data.shape[0],
                "n_columns": raw_data.shape[1],
                "target_column": target_column,
            })

            mlflow.log_dict(validation_results, "data_validation.json")

        # Create data profile
        # For unsupervised tasks (target_column is None), all columns are features
        if target_column and target_column in raw_data.columns:
            # Supervised task: exclude target from features
            target_dist = raw_data[target_column].value_counts().to_dict()
            target_distribution = {str(k): int(v) for k, v in target_dist.items()}
            feature_names = [col for col in raw_data.columns if col != target_column]
            n_features = len(raw_data.columns) - 1
        else:
            # Unsupervised task: all columns are features
            target_distribution = {}
            feature_names = list(raw_data.columns)
            n_features = len(raw_data.columns)

        data_profile = {
            "n_samples": len(raw_data),
            "n_features": n_features,
            "target_column": target_column,
            "feature_names": feature_names,
            "target_distribution": target_distribution,
        }

        # Update state
        updated_state = update_state(
            state,
            raw_data=raw_data,
            data_profile=data_profile,
            mlflow_run_id=run_id if mlflow.active_run() else None,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        from core.state import add_error
        return add_error(state, node_name, e)
