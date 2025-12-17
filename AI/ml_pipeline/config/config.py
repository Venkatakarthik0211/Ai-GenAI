"""Configuration dataclasses for Enhanced ML Pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import os
from dotenv import load_dotenv


@dataclass
class MLflowConfig:
    """MLflow tracking and registry configuration."""

    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "ml_pipeline_experiment"
    enable_logging: bool = True
    registry_uri: Optional[str] = None
    artifact_root: Optional[str] = None

    @classmethod
    def from_env(cls) -> "MLflowConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
            experiment_name=os.getenv("MLFLOW_EXPERIMENT_NAME", "ml_pipeline_experiment"),
            enable_logging=os.getenv("MLFLOW_ENABLE_LOGGING", "true").lower() == "true",
            registry_uri=os.getenv("MLFLOW_REGISTRY_URI"),
            artifact_root=os.getenv("MLFLOW_DEFAULT_ARTIFACT_ROOT"),
        )


@dataclass
class BedrockConfig:
    """AWS Bedrock configuration for AI agents."""

    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    region: str = "us-east-1"
    temperature: float = 0.0
    max_tokens: int = 4096
    enable_agents: bool = True
    max_retries: int = 3
    retry_delay: int = 2
    timeout: int = 60

    @classmethod
    def from_env(cls) -> "BedrockConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"),
            region=os.getenv("AWS_REGION", "us-east-1"),
            temperature=float(os.getenv("BEDROCK_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("BEDROCK_MAX_TOKENS", "4096")),
            enable_agents=os.getenv("BEDROCK_ENABLE_AGENTS", "true").lower() == "true",
            max_retries=int(os.getenv("AGENT_MAX_RETRIES", "3")),
            retry_delay=int(os.getenv("AGENT_RETRY_DELAY", "2")),
            timeout=int(os.getenv("AGENT_TIMEOUT", "60")),
        )


@dataclass
class TuningConfig:
    """Hyperparameter tuning configuration."""

    enable_tuning: bool = True
    method: str = "grid_search"  # Options: grid_search, random_search
    cv_folds: int = 5
    n_jobs: int = -1
    verbose: int = 1
    scoring: str = "accuracy"  # For classification; use 'neg_mean_squared_error' for regression

    @classmethod
    def from_env(cls) -> "TuningConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            enable_tuning=os.getenv("ENABLE_HYPERPARAMETER_TUNING", "true").lower() == "true",
            method=os.getenv("TUNING_METHOD", "grid_search"),
            cv_folds=int(os.getenv("TUNING_CV_FOLDS", "5")),
            n_jobs=int(os.getenv("TUNING_N_JOBS", "-1")),
            verbose=int(os.getenv("TUNING_VERBOSE", "1")),
        )


@dataclass
class MonitoringConfig:
    """Performance monitoring and drift detection configuration."""

    enable_drift_detection: bool = True
    drift_threshold_p_value: float = 0.05
    drift_threshold_psi: float = 0.2
    enable_performance_monitoring: bool = True
    performance_degradation_threshold: float = 0.05

    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            enable_drift_detection=os.getenv("ENABLE_DRIFT_DETECTION", "true").lower() == "true",
            drift_threshold_p_value=float(os.getenv("DRIFT_THRESHOLD_P_VALUE", "0.05")),
            drift_threshold_psi=float(os.getenv("DRIFT_THRESHOLD_PSI", "0.2")),
            enable_performance_monitoring=os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true",
            performance_degradation_threshold=float(os.getenv("PERFORMANCE_DEGRADATION_THRESHOLD", "0.05")),
        )


@dataclass
class RetrainingConfig:
    """Retraining configuration."""

    enable_auto_retraining: bool = True
    performance_threshold: float = 0.1
    drift_threshold: int = 3
    schedule_cron: Optional[str] = "0 2 * * *"

    @classmethod
    def from_env(cls) -> "RetrainingConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            enable_auto_retraining=os.getenv("ENABLE_AUTO_RETRAINING", "true").lower() == "true",
            performance_threshold=float(os.getenv("RETRAINING_PERFORMANCE_THRESHOLD", "0.1")),
            drift_threshold=int(os.getenv("RETRAINING_DRIFT_THRESHOLD", "3")),
            schedule_cron=os.getenv("RETRAINING_SCHEDULE_CRON", "0 2 * * *"),
        )


@dataclass
class DataConfig:
    """Data loading and preprocessing configuration."""

    train_path: str = "data/raw/train.csv"
    target_column: str = "target"
    test_size: float = 0.2
    random_state: int = 42
    min_samples: int = 100
    max_missing_ratio: float = 0.3

    @classmethod
    def from_env(cls) -> "DataConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            train_path=os.getenv("DEFAULT_DATA_PATH", "data/raw/train.csv"),
            target_column=os.getenv("DEFAULT_TARGET_COLUMN", "target"),
            test_size=float(os.getenv("DEFAULT_TEST_SIZE", "0.2")),
            random_state=int(os.getenv("DEFAULT_RANDOM_STATE", "42")),
            min_samples=int(os.getenv("MIN_SAMPLES", "100")),
            max_missing_ratio=float(os.getenv("MAX_MISSING_RATIO", "0.3")),
        )


@dataclass
class AlgorithmConfig:
    """Algorithm selection configuration."""

    classification_algorithms: List[str] = field(default_factory=lambda: [
        "logistic_regression",
        "random_forest",
        "gradient_boosting",
        "svm",
        "knn"
    ])
    regression_algorithms: List[str] = field(default_factory=lambda: [
        "linear_regression",
        "ridge",
        "lasso",
        "random_forest",
        "gradient_boosting"
    ])
    enable_xgboost: bool = False
    enable_lightgbm: bool = False
    enable_catboost: bool = False

    @classmethod
    def from_env(cls) -> "AlgorithmConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        # Parse comma-separated algorithm lists
        classification_str = os.getenv("CLASSIFICATION_ALGORITHMS", "")
        regression_str = os.getenv("REGRESSION_ALGORITHMS", "")

        classification_algos = [a.strip() for a in classification_str.split(",")] if classification_str else [
            "logistic_regression", "random_forest", "gradient_boosting", "svm", "knn"
        ]
        regression_algos = [a.strip() for a in regression_str.split(",")] if regression_str else [
            "linear_regression", "ridge", "lasso", "random_forest", "gradient_boosting"
        ]

        return cls(
            classification_algorithms=classification_algos,
            regression_algorithms=regression_algos,
            enable_xgboost=os.getenv("ENABLE_XGBOOST", "false").lower() == "true",
            enable_lightgbm=os.getenv("ENABLE_LIGHTGBM", "false").lower() == "true",
            enable_catboost=os.getenv("ENABLE_CATBOOST", "false").lower() == "true",
        )


@dataclass
class OutputConfig:
    """Output directories configuration."""

    output_dir: str = "outputs"
    models_dir: str = "outputs/models"
    metrics_dir: str = "outputs/metrics"
    plots_dir: str = "outputs/plots"
    reports_dir: str = "outputs/reports"
    logs_dir: str = "outputs/logs"

    @classmethod
    def from_env(cls) -> "OutputConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            output_dir=os.getenv("OUTPUT_DIR", "outputs"),
            models_dir=os.getenv("MODELS_DIR", "outputs/models"),
            metrics_dir=os.getenv("METRICS_DIR", "outputs/metrics"),
            plots_dir=os.getenv("PLOTS_DIR", "outputs/plots"),
            reports_dir=os.getenv("REPORTS_DIR", "outputs/reports"),
            logs_dir=os.getenv("LOGS_DIR", "outputs/logs"),
        )


@dataclass
class EnhancedMLPipelineConfig:
    """Main configuration class for Enhanced ML Pipeline."""

    mlflow: MLflowConfig = field(default_factory=MLflowConfig)
    bedrock: BedrockConfig = field(default_factory=BedrockConfig)
    tuning: TuningConfig = field(default_factory=TuningConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    retraining: RetrainingConfig = field(default_factory=RetrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    algorithms: AlgorithmConfig = field(default_factory=AlgorithmConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @classmethod
    def from_env(cls) -> "EnhancedMLPipelineConfig":
        """Load configuration from environment variables."""
        return cls(
            mlflow=MLflowConfig.from_env(),
            bedrock=BedrockConfig.from_env(),
            tuning=TuningConfig.from_env(),
            monitoring=MonitoringConfig.from_env(),
            retraining=RetrainingConfig.from_env(),
            data=DataConfig.from_env(),
            algorithms=AlgorithmConfig.from_env(),
            output=OutputConfig.from_env(),
        )

    @classmethod
    def from_yaml(cls, config_path: str) -> "EnhancedMLPipelineConfig":
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        return cls(
            mlflow=MLflowConfig(**config_dict.get("mlflow", {})),
            bedrock=BedrockConfig(**config_dict.get("bedrock", {})),
            tuning=TuningConfig(**config_dict.get("tuning", {})),
            monitoring=MonitoringConfig(**config_dict.get("monitoring", {})),
            retraining=RetrainingConfig(**config_dict.get("retraining", {})),
            data=DataConfig(**config_dict.get("data", {})),
            algorithms=AlgorithmConfig(**config_dict.get("algorithms", {})),
            output=OutputConfig(**config_dict.get("output", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    def save_to_yaml(self, config_path: str) -> None:
        """Save configuration to YAML file."""
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)


def load_config(config_path: Optional[str] = None) -> EnhancedMLPipelineConfig:
    """
    Load configuration from YAML file or environment variables.

    Args:
        config_path: Path to YAML configuration file. If None, loads from environment.

    Returns:
        EnhancedMLPipelineConfig instance
    """
    if config_path:
        return EnhancedMLPipelineConfig.from_yaml(config_path)
    return EnhancedMLPipelineConfig.from_env()


def get_default_config() -> EnhancedMLPipelineConfig:
    """Get default configuration with default values."""
    return EnhancedMLPipelineConfig()
