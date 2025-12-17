"""MLflow experiment management utilities."""

import mlflow
from mlflow.entities import Experiment
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ExperimentManager:
    """Manages MLflow experiments."""

    def __init__(self, tracking_uri: str = None):
        """
        Initialize ExperimentManager.

        Args:
            tracking_uri: MLflow tracking server URI
        """
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        self.tracking_uri = tracking_uri or mlflow.get_tracking_uri()
        logger.info(f"Initialized ExperimentManager with tracking URI: {self.tracking_uri}")

    def get_or_create_experiment(
        self,
        name: str,
        artifact_location: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Experiment:
        """
        Get existing experiment or create new one.
        If experiment exists but is deleted, restore it.

        Args:
            name: Experiment name
            artifact_location: Optional artifact storage location
            tags: Optional experiment tags

        Returns:
            MLflow Experiment object
        """
        try:
            # Try to get existing experiment (including deleted ones)
            experiment = mlflow.get_experiment_by_name(name)

            if experiment is not None:
                # Check if experiment is deleted
                if experiment.lifecycle_stage == "deleted":
                    logger.info(f"Experiment {name} (ID: {experiment.experiment_id}) is deleted. Restoring it.")
                    # Restore the experiment
                    mlflow.tracking.MlflowClient().restore_experiment(experiment.experiment_id)
                    # Get the restored experiment
                    experiment = mlflow.get_experiment(experiment.experiment_id)
                    logger.info(f"Restored experiment: {name} (ID: {experiment.experiment_id})")
                else:
                    logger.info(f"Found existing experiment: {name} (ID: {experiment.experiment_id})")

                return experiment

            # Create new experiment
            logger.info(f"Creating new experiment: {name}")
            experiment_id = mlflow.create_experiment(
                name=name,
                artifact_location=artifact_location,
                tags=tags
            )

            experiment = mlflow.get_experiment(experiment_id)
            logger.info(f"Created experiment: {name} (ID: {experiment_id})")

            return experiment

        except Exception as e:
            logger.error(f"Error managing experiment {name}: {e}")
            raise

    def list_experiments(
        self,
        view_type: str = "ACTIVE_ONLY",
        max_results: int = 100
    ) -> List[Experiment]:
        """
        List all experiments.

        Args:
            view_type: View type (ACTIVE_ONLY, DELETED_ONLY, ALL)
            max_results: Maximum number of results

        Returns:
            List of Experiment objects
        """
        try:
            experiments = mlflow.search_experiments(
                view_type=view_type,
                max_results=max_results
            )
            logger.info(f"Found {len(experiments)} experiments")
            return experiments
        except Exception as e:
            logger.error(f"Error listing experiments: {e}")
            raise

    def delete_experiment(self, experiment_id: str) -> None:
        """
        Delete (archive) an experiment.

        Args:
            experiment_id: Experiment ID to delete
        """
        try:
            mlflow.delete_experiment(experiment_id)
            logger.info(f"Deleted experiment: {experiment_id}")
        except Exception as e:
            logger.error(f"Error deleting experiment {experiment_id}: {e}")
            raise

    def set_experiment_tag(
        self,
        experiment_id: str,
        key: str,
        value: str
    ) -> None:
        """
        Set a tag on an experiment.

        Args:
            experiment_id: Experiment ID
            key: Tag key
            value: Tag value
        """
        try:
            mlflow.set_experiment_tag(key, value)
            logger.info(f"Set tag {key}={value} on experiment {experiment_id}")
        except Exception as e:
            logger.error(f"Error setting tag on experiment {experiment_id}: {e}")
            raise

    def get_experiment_by_name(self, name: str) -> Optional[Experiment]:
        """
        Get experiment by name.

        Args:
            name: Experiment name

        Returns:
            Experiment object or None if not found
        """
        try:
            experiment = mlflow.get_experiment_by_name(name)
            if experiment:
                logger.info(f"Found experiment: {name} (ID: {experiment.experiment_id})")
            else:
                logger.info(f"Experiment not found: {name}")
            return experiment
        except Exception as e:
            logger.error(f"Error getting experiment {name}: {e}")
            raise

    def get_experiment_by_id(self, experiment_id: str) -> Experiment:
        """
        Get experiment by ID.

        Args:
            experiment_id: Experiment ID

        Returns:
            Experiment object
        """
        try:
            experiment = mlflow.get_experiment(experiment_id)
            logger.info(f"Retrieved experiment ID: {experiment_id}")
            return experiment
        except Exception as e:
            logger.error(f"Error getting experiment {experiment_id}: {e}")
            raise
