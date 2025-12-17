"""Custom exceptions for Enhanced ML Pipeline."""


class PipelineException(Exception):
    """Base exception for all pipeline errors."""

    pass


class StateValidationError(PipelineException):
    """Raised when pipeline state validation fails."""

    def __init__(self, message: str, missing_keys: list = None):
        self.missing_keys = missing_keys or []
        super().__init__(message)


class DataValidationError(PipelineException):
    """Raised when data validation fails."""

    def __init__(self, message: str, validation_errors: dict = None):
        self.validation_errors = validation_errors or {}
        super().__init__(message)


class AgentFailureException(PipelineException):
    """Raised when an AI agent fails to make a decision."""

    def __init__(self, agent_name: str, message: str, attempts: int = 0):
        self.agent_name = agent_name
        self.attempts = attempts
        super().__init__(f"Agent '{agent_name}' failed: {message} (attempts: {attempts})")


class DriftDetectedException(PipelineException):
    """Raised when data drift is detected."""

    def __init__(self, message: str, drifted_features: list = None, drift_scores: dict = None):
        self.drifted_features = drifted_features or []
        self.drift_scores = drift_scores or {}
        super().__init__(message)


class ModelTrainingError(PipelineException):
    """Raised when model training fails."""

    def __init__(self, algorithm_name: str, message: str, original_error: Exception = None):
        self.algorithm_name = algorithm_name
        self.original_error = original_error
        super().__init__(f"Model training failed for '{algorithm_name}': {message}")


class HyperparameterTuningError(PipelineException):
    """Raised when hyperparameter tuning fails."""

    def __init__(self, algorithm_name: str, message: str):
        self.algorithm_name = algorithm_name
        super().__init__(f"Hyperparameter tuning failed for '{algorithm_name}': {message}")


class MLflowError(PipelineException):
    """Raised when MLflow operations fail."""

    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"MLflow operation '{operation}' failed: {message}")


class BedrockError(PipelineException):
    """Raised when AWS Bedrock operations fail."""

    def __init__(self, operation: str, message: str, error_code: str = None):
        self.operation = operation
        self.error_code = error_code
        super().__init__(f"Bedrock operation '{operation}' failed: {message}")


class ConfigurationError(PipelineException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message)


class PreprocessingError(PipelineException):
    """Raised when data preprocessing fails."""

    def __init__(self, step: str, message: str):
        self.step = step
        super().__init__(f"Preprocessing step '{step}' failed: {message}")


class FeatureEngineeringError(PipelineException):
    """Raised when feature engineering fails."""

    def __init__(self, step: str, message: str):
        self.step = step
        super().__init__(f"Feature engineering step '{step}' failed: {message}")


class ModelEvaluationError(PipelineException):
    """Raised when model evaluation fails."""

    def __init__(self, message: str, algorithm_name: str = None):
        self.algorithm_name = algorithm_name
        super().__init__(message)


class ModelRegistryError(PipelineException):
    """Raised when model registry operations fail."""

    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Model registry operation '{operation}' failed: {message}")


class PerformanceDegradationError(PipelineException):
    """Raised when significant performance degradation is detected."""

    def __init__(self, message: str, degradation_percent: float, threshold: float):
        self.degradation_percent = degradation_percent
        self.threshold = threshold
        super().__init__(message)


class InsufficientDataError(DataValidationError):
    """Raised when insufficient data is available."""

    def __init__(self, message: str, n_samples: int, required_samples: int):
        self.n_samples = n_samples
        self.required_samples = required_samples
        super().__init__(message)


class MissingTargetError(DataValidationError):
    """Raised when target column is missing."""

    def __init__(self, target_column: str):
        self.target_column = target_column
        super().__init__(f"Target column '{target_column}' not found in data")


class InvalidAlgorithmError(PipelineException):
    """Raised when an invalid algorithm is specified."""

    def __init__(self, algorithm_name: str, available_algorithms: list = None):
        self.algorithm_name = algorithm_name
        self.available_algorithms = available_algorithms or []
        super().__init__(
            f"Invalid algorithm '{algorithm_name}'. "
            f"Available: {', '.join(self.available_algorithms)}"
        )
