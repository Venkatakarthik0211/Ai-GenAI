"""MLflow logging utilities."""

import mlflow
from typing import Dict, Any


class MLflowLogger:
    """Centralized MLflow logging."""

    @staticmethod
    def log_agent_decision(agent_name: str, decision: Dict[str, Any], prompt: str, response: str):
        """Log AI agent decision to MLflow."""
        if mlflow.active_run():
            mlflow.log_dict(decision, f"agents/{agent_name}_decision.json")
            mlflow.log_text(prompt, f"agents/{agent_name}_prompt.txt")
            mlflow.log_text(response, f"agents/{agent_name}_response.txt")

    @staticmethod
    def log_algorithm_result(algorithm_name: str, result: Dict[str, Any]):
        """Log algorithm training result."""
        if mlflow.active_run():
            mlflow.log_metrics({
                f"{algorithm_name}_cv_mean": result.get("cv_mean_score", 0.0),
                f"{algorithm_name}_test_score": result.get("test_score", 0.0),
                f"{algorithm_name}_train_time": result.get("train_time", 0.0),
            })
            mlflow.log_params({
                f"{algorithm_name}_best_params": str(result.get("best_params", {}))
            })
