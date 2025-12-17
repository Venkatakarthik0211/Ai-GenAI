# Error Handling and Validation Strategy - Enhanced Pipeline

## Overview

This document defines the comprehensive error handling and validation strategy for the **Enhanced ML Pipeline** with **AI decision agents**, **MLflow integration**, and **performance monitoring**. The strategy ensures robustness, debuggability, and graceful degradation across all components including AWS Bedrock agents, MLflow tracking, and drift detection.

## Error Classification

### Severity Levels

```python
class ErrorSeverity(Enum):
    """Error severity levels"""
    WARNING = "WARNING"    # Non-critical, pipeline continues
    ERROR = "ERROR"        # Critical, pipeline stops at stage
    FATAL = "FATAL"        # Unrecoverable, immediate termination
```

### Error Categories

```
┌──────────────────────────────────────────────────────────────┐
│                      ERROR TAXONOMY                          │
└──────────────────────────────────────────────────────────────┘

1. DATA ERRORS
   ├─ FileNotFoundError         [FATAL]
   ├─ EmptyDataError            [FATAL]
   ├─ ParserError               [FATAL]
   ├─ InvalidDataTypeError      [ERROR]
   ├─ MissingTargetError        [ERROR]
   └─ InsufficientDataError     [ERROR]

2. VALIDATION ERRORS
   ├─ SchemaViolationError      [ERROR]
   ├─ RangeViolationError       [WARNING]
   ├─ ConstraintViolationError  [ERROR]
   └─ ConsistencyError          [ERROR]

3. PROCESSING ERRORS
   ├─ EncodingError             [WARNING]
   ├─ ScalingError              [WARNING]
   ├─ ImputationError           [WARNING]
   └─ TransformationError       [ERROR]

4. MODEL ERRORS
   ├─ TrainingFailureError      [WARNING per model]
   ├─ ConvergenceError          [WARNING]
   ├─ PredictionError           [ERROR]
   └─ AllModelsFailedError      [FATAL]

5. SYSTEM ERRORS
   ├─ OutOfMemoryError          [FATAL]
   ├─ DiskFullError             [FATAL]
   ├─ PermissionError           [ERROR]
   └─ TimeoutError              [ERROR]

6. AGENT ERRORS (NEW)
   ├─ AgentInvocationError      [WARNING → fallback]
   ├─ BedrockAPIError           [WARNING → retry]
   ├─ AgentResponseParseError   [WARNING → fallback]
   ├─ AgentTimeoutError         [WARNING → fallback]
   └─ AllAgentsFailedError      [ERROR → manual intervention]

7. MLFLOW ERRORS (NEW)
   ├─ MLflowConnectionError     [WARNING → continue]
   ├─ MLflowLoggingError        [WARNING → continue]
   ├─ ExperimentNotFoundError   [WARNING → create]
   └─ ModelRegistryError        [WARNING → continue]

8. MONITORING ERRORS (NEW)
   ├─ DriftDetectionError       [WARNING → skip]
   ├─ PerformanceComparisonError [WARNING → skip]
   ├─ BaselineNotFoundError     [WARNING → skip]
   └─ MetricCalculationError    [WARNING → skip]

9. TUNING ERRORS (NEW)
   ├─ GridSearchFailureError    [WARNING per algorithm]
   ├─ HyperparameterError       [WARNING → use defaults]
   ├─ CrossValidationError      [WARNING → single train]
   └─ AllAlgorithmsFailedError  [FATAL]
```

## Error Handling Framework

### Error Entry Structure

```python
class ErrorEntry(TypedDict):
    """Standard error entry"""
    stage: str                  # Pipeline stage where error occurred
    error_type: str            # Type of error (class name)
    message: str               # Human-readable error message
    timestamp: str             # ISO format timestamp
    severity: str              # WARNING, ERROR, FATAL
    traceback: Optional[str]   # Full stack trace (optional)
    context: Dict[str, Any]    # Additional context
```

### Error Logging Pattern

```python
def log_error(
    state: PipelineState,
    stage: str,
    error: Exception,
    severity: str = "ERROR",
    context: Optional[Dict[str, Any]] = None
) -> PipelineState:
    """
    Log an error to the pipeline state.

    Args:
        state: Current pipeline state
        stage: Name of the stage
        error: Exception object
        severity: Error severity level
        context: Additional context information

    Returns:
        Updated state with error logged

    Example:
        >>> try:
        ...     risky_operation()
        ... except ValueError as e:
        ...     state = log_error(state, "preprocessing", e, "WARNING")
    """
    error_entry = {
        "stage": stage,
        "error_type": type(error).__name__,
        "message": str(error),
        "timestamp": datetime.now().isoformat(),
        "severity": severity,
        "traceback": traceback.format_exc() if severity == "FATAL" else None,
        "context": context or {}
    }

    new_state = state.copy()
    if "errors" not in new_state:
        new_state["errors"] = []
    new_state["errors"].append(error_entry)

    return new_state
```

### Warning Logging Pattern

```python
def log_warning(
    state: PipelineState,
    message: str,
    stage: str
) -> PipelineState:
    """
    Log a warning to the pipeline state.

    Args:
        state: Current pipeline state
        message: Warning message
        stage: Stage name

    Returns:
        Updated state with warning logged

    Example:
        >>> state = log_warning(state, "Low variance feature dropped", "feature_selection")
    """
    warning_entry = f"[{stage}] {message}"

    new_state = state.copy()
    if "warnings" not in new_state:
        new_state["warnings"] = []
    new_state["warnings"].append(warning_entry)

    return new_state
```

## Validation Strategy

### Input Validation Decorators

```python
from functools import wraps
from typing import Callable

def validate_state_inputs(*required_fields: str) -> Callable:
    """
    Decorator to validate required state fields.

    Args:
        *required_fields: Names of required state fields

    Example:
        >>> @validate_state_inputs("raw_data", "pipeline_config")
        ... def preprocess_data_node(state: PipelineState) -> PipelineState:
        ...     # Implementation
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: PipelineState) -> PipelineState:
            # Check all required fields present
            missing_fields = [
                field for field in required_fields
                if field not in state or state[field] is None
            ]

            if missing_fields:
                raise ValueError(
                    f"Missing required state fields: {missing_fields}"
                )

            # Execute function
            return func(state)

        return wrapper
    return decorator


def validate_dataframe(
    min_rows: int = 0,
    min_cols: int = 0,
    no_missing: bool = False
) -> Callable:
    """
    Decorator to validate DataFrame constraints.

    Args:
        min_rows: Minimum number of rows
        min_cols: Minimum number of columns
        no_missing: Require no missing values

    Example:
        >>> @validate_dataframe(min_rows=10, min_cols=2, no_missing=True)
        ... def process_data(df: pd.DataFrame) -> pd.DataFrame:
        ...     # Implementation
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            # Validate rows
            if df.shape[0] < min_rows:
                raise ValueError(
                    f"DataFrame has {df.shape[0]} rows, minimum {min_rows} required"
                )

            # Validate columns
            if df.shape[1] < min_cols:
                raise ValueError(
                    f"DataFrame has {df.shape[1]} columns, minimum {min_cols} required"
                )

            # Validate no missing
            if no_missing and df.isnull().any().any():
                raise ValueError("DataFrame contains missing values")

            return func(df, *args, **kwargs)

        return wrapper
    return decorator
```

### Validation Checkpoints

```python
class ValidationCheckpoint:
    """Validation checkpoint for pipeline stages"""

    @staticmethod
    def validate_load_data(state: PipelineState) -> Tuple[bool, List[str]]:
        """
        Validate data loading stage.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check raw_data exists
        if "raw_data" not in state or state["raw_data"] is None:
            errors.append("raw_data not loaded")

        # Check non-empty
        if state.get("raw_data") is not None:
            df = state["raw_data"]
            if df.shape[0] == 0:
                errors.append("raw_data is empty")
            if df.shape[1] < 2:
                errors.append("raw_data has less than 2 columns")

        return len(errors) == 0, errors

    @staticmethod
    def validate_preprocessing(state: PipelineState) -> Tuple[bool, List[str]]:
        """Validate preprocessing stage"""
        errors = []

        cleaned_data = state.get("cleaned_data")
        if cleaned_data is None:
            errors.append("cleaned_data not present")
            return False, errors

        # No missing values
        if cleaned_data.isnull().any().any():
            errors.append("cleaned_data contains missing values")

        # At least some rows
        if cleaned_data.shape[0] < 10:
            errors.append("cleaned_data has too few rows (< 10)")

        # At least 2 columns (1 feature + 1 target)
        if cleaned_data.shape[1] < 2:
            errors.append("cleaned_data has too few columns (< 2)")

        return len(errors) == 0, errors

    @staticmethod
    def validate_split(state: PipelineState) -> Tuple[bool, List[str]]:
        """Validate train/test split"""
        errors = []

        # Check all split components exist
        required = ["X_train", "X_test", "y_train", "y_test"]
        for field in required:
            if field not in state or state[field] is None:
                errors.append(f"{field} not present")

        if errors:
            return False, errors

        X_train = state["X_train"]
        X_test = state["X_test"]
        y_train = state["y_train"]
        y_test = state["y_test"]

        # Same number of features
        if X_train.shape[1] != X_test.shape[1]:
            errors.append("X_train and X_test have different number of features")

        # Alignment
        if len(X_train) != len(y_train):
            errors.append("X_train and y_train have different lengths")

        if len(X_test) != len(y_test):
            errors.append("X_test and y_test have different lengths")

        # Minimum samples
        if len(X_train) < 10:
            errors.append("X_train has too few samples (< 10)")

        if len(X_test) < 5:
            errors.append("X_test has too few samples (< 5)")

        # No overlap
        if not set(X_train.index).isdisjoint(set(X_test.index)):
            errors.append("X_train and X_test have overlapping indices")

        return len(errors) == 0, errors

    @staticmethod
    def validate_feature_selection(state: PipelineState) -> Tuple[bool, List[str]]:
        """Validate feature selection"""
        errors = []

        # Check selected_features exists
        if "selected_features" not in state or not state["selected_features"]:
            errors.append("No features selected")
            return False, errors

        selected = state["selected_features"]
        X_train = state.get("X_train")

        # At least one feature
        if len(selected) < 1:
            errors.append("selected_features list is empty")

        # Features exist in X_train
        if X_train is not None:
            missing = [f for f in selected if f not in X_train.columns]
            if missing:
                errors.append(f"Selected features not in X_train: {missing}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_training(state: PipelineState) -> Tuple[bool, List[str]]:
        """Validate model training"""
        errors = []

        trained_models = state.get("trained_models", {})

        # At least one model trained
        if not trained_models:
            errors.append("No models trained")
            return False, errors

        # All models are fitted
        for model_name, model in trained_models.items():
            if not hasattr(model, "predict"):
                errors.append(f"Model {model_name} doesn't have predict method")

        # Best model exists
        best_name = state.get("best_model_name")
        if best_name and best_name not in trained_models:
            errors.append(f"Best model {best_name} not in trained_models")

        return len(errors) == 0, errors

    @staticmethod
    def validate_evaluation(state: PipelineState) -> Tuple[bool, List[str]]:
        """Validate model evaluation"""
        errors = []

        eval_results = state.get("evaluation_results", {})
        trained_models = state.get("trained_models", {})

        # Evaluation results exist
        if not eval_results:
            errors.append("No evaluation results")
            return False, errors

        # Results for all models
        for model_name in trained_models.keys():
            if model_name not in eval_results:
                errors.append(f"No evaluation results for model {model_name}")

        # Valid metrics
        for model_name, metrics in eval_results.items():
            if not isinstance(metrics, dict):
                errors.append(f"Invalid metrics type for {model_name}")

        return len(errors) == 0, errors
```

## Error Recovery Strategies

### Strategy 1: Fallback Defaults

```python
def safe_impute(
    df: pd.DataFrame,
    strategy: str = "mean"
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Impute missing values with fallback strategies.

    Strategy priority:
    1. Specified strategy
    2. Mean (for numerical)
    3. Most frequent (for categorical)
    4. Drop column (if all else fails)

    Returns:
        Tuple of (imputed DataFrame, warnings)
    """
    warnings = []

    for col in df.columns:
        if df[col].isnull().sum() > 0:
            try:
                # Try specified strategy
                if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                    df[col].fillna(df[col].mean(), inplace=True)
                elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    # Fallback to mode
                    df[col].fillna(df[col].mode()[0], inplace=True)

            except Exception as e:
                # Last resort: drop column
                warnings.append(f"Failed to impute {col}, dropping: {str(e)}")
                df.drop(columns=[col], inplace=True)

    return df, warnings
```

### Strategy 2: Graceful Degradation

```python
def train_models_with_fallback(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_names: List[str],
    configs: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Train models with graceful degradation.

    If a model fails, log and continue with others.
    If all models fail, raise exception.

    Returns:
        Tuple of (trained_models, warnings)
    """
    trained_models = {}
    warnings = []

    for model_name in model_names:
        try:
            model = initialize_model(model_name, configs.get(model_name, {}))
            model.fit(X_train, y_train)
            trained_models[model_name] = model

        except Exception as e:
            warnings.append(f"Failed to train {model_name}: {str(e)}")
            continue

    if not trained_models:
        raise RuntimeError("All models failed to train")

    return trained_models, warnings
```

### Strategy 3: Retry with Backoff

```python
import time

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Any:
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        backoff_factor: Backoff multiplier

    Returns:
        Function result

    Example:
        >>> result = retry_with_backoff(lambda: load_data("file.csv"), 3, 2.0)
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_factor ** attempt
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
```

### Strategy 4: Agent Fallback Strategy (NEW)

```python
class AgentFallbackStrategy:
    """
    Fallback strategy for AI agent failures.

    When an agent fails, use predefined fallback decisions.
    """

    @staticmethod
    def algorithm_selection_fallback(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback decision when Algorithm Selection Agent fails.

        Returns safe default algorithms based on problem type.
        """
        target_type = context.get("target_type", "classification")

        if target_type == "classification":
            return {
                "selected_algorithms": [
                    "random_forest",
                    "gradient_boosting",
                    "logistic_regression"
                ],
                "reasoning": "Fallback: Safe default classification algorithms",
                "hyperparameter_suggestions": {},
                "fallback": True
            }
        else:  # regression
            return {
                "selected_algorithms": [
                    "random_forest_regressor",
                    "gradient_boosting_regressor",
                    "linear_regression"
                ],
                "reasoning": "Fallback: Safe default regression algorithms",
                "hyperparameter_suggestions": {},
                "fallback": True
            }

    @staticmethod
    def model_selection_fallback(
        trained_models: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fallback decision when Model Selection Agent fails.

        Selects model with highest test accuracy.
        """
        best_model = max(
            trained_models.items(),
            key=lambda x: x[1].get("test_accuracy", 0)
        )

        return {
            "selected_model": best_model[0],
            "reasoning": "Fallback: Selected model with highest test accuracy",
            "confidence": 0.5,
            "fallback": True
        }

    @staticmethod
    def retraining_decision_fallback(
        performance_drop: float,
        drift_detected: bool
    ) -> Dict[str, Any]:
        """
        Fallback decision when Retraining Decision Agent fails.

        Uses simple threshold rules.
        """
        # Rule: Retrain if performance drop > 10% OR (drift + drop > 5%)
        should_retrain = (
            performance_drop > 0.10 or
            (drift_detected and performance_drop > 0.05)
        )

        return {
            "retrain": should_retrain,
            "reasoning": f"Fallback: Rule-based decision (drop={performance_drop:.2%}, drift={drift_detected})",
            "urgency": "high" if performance_drop > 0.10 else "medium",
            "fallback": True
        }


def safe_agent_invoke(
    agent: BaseDecisionAgent,
    context: Dict[str, Any],
    fallback_func: Callable,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Safely invoke an agent with retry and fallback.

    Args:
        agent: The agent to invoke
        context: Context for the agent
        fallback_func: Fallback function if agent fails
        max_retries: Number of retry attempts

    Returns:
        Agent decision or fallback decision

    Example:
        >>> result = safe_agent_invoke(
        ...     agent=algorithm_selection_agent,
        ...     context={"n_samples": 1000, "n_features": 10},
        ...     fallback_func=AgentFallbackStrategy.algorithm_selection_fallback,
        ...     max_retries=3
        ... )
    """
    for attempt in range(max_retries):
        try:
            result = agent.invoke(context)
            result["fallback"] = False
            return result

        except BedrockAPIError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Bedrock API error, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Agent failed after {max_retries} attempts, using fallback")
                return fallback_func(context)

        except AgentResponseParseError as e:
            logger.error(f"Failed to parse agent response: {e}, using fallback")
            return fallback_func(context)

        except Exception as e:
            logger.error(f"Unexpected agent error: {e}, using fallback")
            return fallback_func(context)
```

### Strategy 5: MLflow Error Handling (NEW)

```python
class SafeMLflowLogger:
    """
    MLflow logger with error handling.

    Logs errors but never fails the pipeline.
    """

    @staticmethod
    def safe_log_params(params: Dict[str, Any]) -> bool:
        """
        Safely log parameters to MLflow.

        Returns True if successful, False otherwise.
        """
        try:
            mlflow.log_params(params)
            return True
        except Exception as e:
            logger.warning(f"Failed to log params to MLflow: {e}")
            return False

    @staticmethod
    def safe_log_metrics(metrics: Dict[str, float]) -> bool:
        """Safely log metrics to MLflow."""
        try:
            mlflow.log_metrics(metrics)
            return True
        except Exception as e:
            logger.warning(f"Failed to log metrics to MLflow: {e}")
            return False

    @staticmethod
    def safe_log_artifact(artifact_path: str) -> bool:
        """Safely log artifact to MLflow."""
        try:
            mlflow.log_artifact(artifact_path)
            return True
        except Exception as e:
            logger.warning(f"Failed to log artifact to MLflow: {e}")
            return False

    @staticmethod
    def safe_register_model(
        model_uri: str,
        model_name: str
    ) -> Optional[str]:
        """
        Safely register model to MLflow registry.

        Returns model version or None if failed.
        """
        try:
            result = mlflow.register_model(model_uri, model_name)
            return result.version
        except Exception as e:
            logger.warning(f"Failed to register model to MLflow: {e}")
            return None


def ensure_mlflow_run(
    experiment_name: str,
    run_name: Optional[str] = None
) -> Optional[str]:
    """
    Ensure MLflow run is active, create if needed.

    Returns run_id or None if MLflow is unavailable.

    Example:
        >>> run_id = ensure_mlflow_run("my_experiment", "run_1")
        >>> if run_id:
        ...     mlflow.log_param("param1", "value1")
    """
    try:
        # Check if run is already active
        if mlflow.active_run() is not None:
            return mlflow.active_run().info.run_id

        # Create or get experiment
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
            else:
                experiment_id = experiment.experiment_id
        except Exception as e:
            logger.warning(f"Failed to get/create experiment: {e}")
            return None

        # Start run
        run = mlflow.start_run(
            experiment_id=experiment_id,
            run_name=run_name
        )
        return run.info.run_id

    except Exception as e:
        logger.error(f"Failed to start MLflow run: {e}")
        return None
```

### Strategy 6: Monitoring Error Handling (NEW)

```python
def safe_drift_detection(
    train_data: pd.DataFrame,
    test_data: pd.DataFrame,
    threshold: float = 0.1
) -> Dict[str, Any]:
    """
    Safely detect drift with error handling.

    Returns drift results or safe defaults if detection fails.
    """
    try:
        detector = DriftDetector()
        result = detector.detect_drift(train_data, test_data)
        return result

    except Exception as e:
        logger.warning(f"Drift detection failed: {e}")
        return {
            "drift_detected": False,
            "overall_drift_score": 0.0,
            "drifted_features": [],
            "feature_drift_scores": {},
            "error": str(e),
            "fallback": True
        }


def safe_performance_monitoring(
    current_metrics: Dict[str, float],
    baseline_metrics: Dict[str, float],
    threshold: float = 0.05
) -> Dict[str, Any]:
    """
    Safely monitor performance with error handling.

    Returns performance comparison or safe defaults if monitoring fails.
    """
    try:
        monitor = PerformanceMonitor()
        result = monitor.compare_to_baseline(
            current_metrics,
            baseline_metrics,
            threshold
        )
        return result

    except KeyError as e:
        logger.warning(f"Missing baseline metrics: {e}")
        return {
            "performance_drop": 0.0,
            "degradation_detected": False,
            "error": f"Missing baseline: {e}",
            "fallback": True
        }

    except Exception as e:
        logger.warning(f"Performance monitoring failed: {e}")
        return {
            "performance_drop": 0.0,
            "degradation_detected": False,
            "error": str(e),
            "fallback": True
        }
```

## Node-Level Error Handling Pattern

### Template for Robust Node

```python
def robust_node_template(state: PipelineState) -> PipelineState:
    """
    Template for a robust pipeline node.

    Pattern:
    1. Validate inputs
    2. Try main logic
    3. Handle errors gracefully
    4. Validate outputs
    5. Update state safely
    """
    stage_name = "node_name"
    new_state = state.copy()

    try:
        # ========== INPUT VALIDATION ==========
        required_fields = ["field1", "field2"]
        for field in required_fields:
            if field not in state or state[field] is None:
                raise ValueError(f"Missing required field: {field}")

        # ========== MAIN LOGIC ==========
        input_data = state["field1"]

        # Process with error handling
        try:
            output_data = process_data(input_data)
        except SpecificError as e:
            # Handle specific error with fallback
            new_state = log_warning(new_state, f"Fallback applied: {e}", stage_name)
            output_data = fallback_process(input_data)

        # ========== OUTPUT VALIDATION ==========
        if output_data is None or len(output_data) == 0:
            raise ValueError("Processing produced no output")

        # ========== UPDATE STATE ==========
        new_state["output_field"] = output_data
        new_state["current_stage"] = stage_name
        new_state["validation_status"][stage_name] = True

        return new_state

    except Exception as e:
        # ========== ERROR HANDLING ==========
        new_state = log_error(new_state, stage_name, e, "ERROR")
        new_state["validation_status"][stage_name] = False

        # Decide whether to stop or continue
        if isinstance(e, FatalError):
            raise
        else:
            # Return state with error logged
            return new_state
```

## Integration with LangGraph

### Error Propagation in Graph

```python
def create_error_aware_graph() -> StateGraph:
    """
    Create a LangGraph that handles errors.

    Each node checks validation_status and can decide to skip or stop.
    """
    workflow = StateGraph(PipelineState)

    # Add error-aware nodes
    workflow.add_node("load_data", error_aware_wrapper(load_data_node))
    workflow.add_node("preprocess", error_aware_wrapper(preprocess_data_node))
    # ... more nodes

    return workflow.compile()


def error_aware_wrapper(node_func: Callable) -> Callable:
    """
    Wrap a node function with error awareness.

    Checks if previous stage failed before executing.
    """
    def wrapper(state: PipelineState) -> PipelineState:
        # Check for fatal errors in previous stages
        for error in state.get("errors", []):
            if error["severity"] == "FATAL":
                # Don't execute, just pass state through
                return state

        # Execute node
        try:
            return node_func(state)
        except Exception as e:
            # Log error and return state
            return log_error(state, "unknown", e, "FATAL")

    return wrapper
```

## Monitoring and Alerting

### Error Summary Generation

```python
def generate_error_summary(state: PipelineState) -> Dict[str, Any]:
    """
    Generate a summary of errors and warnings.

    Returns:
        Dictionary with error statistics and details
    """
    errors = state.get("errors", [])
    warnings = state.get("warnings", [])

    summary = {
        "total_errors": len(errors),
        "total_warnings": len(warnings),
        "errors_by_severity": {},
        "errors_by_stage": {},
        "fatal_errors": [],
        "recent_errors": errors[-5:] if errors else []
    }

    # Group by severity
    for error in errors:
        severity = error["severity"]
        summary["errors_by_severity"][severity] = \
            summary["errors_by_severity"].get(severity, 0) + 1

        # Group by stage
        stage = error["stage"]
        summary["errors_by_stage"][stage] = \
            summary["errors_by_stage"].get(stage, 0) + 1

        # Collect fatal errors
        if severity == "FATAL":
            summary["fatal_errors"].append(error)

    return summary


def print_error_summary(summary: Dict[str, Any]):
    """Print error summary to console"""
    print("\n" + "=" * 60)
    print("ERROR SUMMARY")
    print("=" * 60)
    print(f"Total Errors: {summary['total_errors']}")
    print(f"Total Warnings: {summary['total_warnings']}")

    if summary['errors_by_severity']:
        print("\nErrors by Severity:")
        for severity, count in summary['errors_by_severity'].items():
            print(f"  {severity}: {count}")

    if summary['errors_by_stage']:
        print("\nErrors by Stage:")
        for stage, count in summary['errors_by_stage'].items():
            print(f"  {stage}: {count}")

    if summary['fatal_errors']:
        print("\nFATAL ERRORS:")
        for error in summary['fatal_errors']:
            print(f"  [{error['stage']}] {error['message']}")

    print("=" * 60 + "\n")
```

### Logging Configuration

```python
import logging

def setup_logging(output_dir: str) -> logging.Logger:
    """
    Configure logging for the pipeline.

    Args:
        output_dir: Directory for log files

    Returns:
        Configured logger
    """
    logger = logging.getLogger("ml_pipeline")
    logger.setLevel(logging.DEBUG)

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(
        f"{output_dir}/pipeline.log"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

## Testing Error Handling

### Unit Tests for Error Cases

```python
import pytest

def test_missing_data_error():
    """Test that missing data raises appropriate error"""
    state = {"pipeline_config": {"data_path": "nonexistent.csv"}}

    with pytest.raises(FileNotFoundError):
        load_data_node(state)


def test_empty_dataframe_error():
    """Test that empty DataFrame is caught"""
    empty_df = pd.DataFrame()
    state = {"raw_data": empty_df}

    result = preprocess_data_node(state)

    assert len(result["errors"]) > 0
    assert any("empty" in error["message"].lower()
               for error in result["errors"])


def test_all_models_fail():
    """Test graceful handling when all models fail"""
    state = {
        "X_train": pd.DataFrame(),  # Invalid empty data
        "y_train": pd.Series(),
        "pipeline_config": {"model": {"models": ["random_forest"]}}
    }

    with pytest.raises(RuntimeError, match="All models failed"):
        train_classification_node(state)


def test_warning_logged():
    """Test that warnings are properly logged"""
    state = {
        "raw_data": pd.DataFrame({"A": [1, 2, None, 4]}),
        "warnings": []
    }

    result = preprocess_data_node(state)

    assert "warnings" in result
    assert len(result["warnings"]) >= 0
```

## Best Practices Summary

### DO's
1. ✅ Always validate inputs before processing
2. ✅ Use specific exception types
3. ✅ Log all errors and warnings to state
4. ✅ Provide context in error messages
5. ✅ Implement fallback strategies
6. ✅ Test error paths
7. ✅ Use decorators for common validations
8. ✅ Check validation_status before proceeding

### DON'Ts
1. ❌ Silently catch and ignore exceptions
2. ❌ Use bare `except:` clauses
3. ❌ Fail without logging
4. ❌ Continue after fatal errors
5. ❌ Lose error context
6. ❌ Mix error handling with business logic
7. ❌ Assume inputs are valid
8. ❌ Skip output validation

## Summary

This **Enhanced** error handling strategy provides:

### Core Error Handling
1. **Clear error taxonomy** with severity levels (9 categories including agents, MLflow, monitoring)
2. **Consistent error logging** to pipeline state
3. **Validation checkpoints** at each stage
4. **Graceful degradation** with fallbacks
5. **Integration with LangGraph** state management

### Agent Error Handling (NEW)
6. **AI Agent fallback strategies** for all 3 decision agents
7. **Bedrock API retry logic** with exponential backoff
8. **Response parsing error recovery** with fallback to safe defaults
9. **Agent failure isolation** - pipeline continues with fallback decisions

### MLflow Error Handling (NEW)
10. **Safe MLflow logging** - errors logged but pipeline continues
11. **Automatic experiment creation** if not found
12. **Model registry error recovery** - continues without registration
13. **Connection error handling** - pipeline works offline if MLflow unavailable

### Monitoring Error Handling (NEW)
14. **Drift detection error recovery** - skips if failed, continues pipeline
15. **Performance monitoring fallbacks** - uses safe defaults
16. **Baseline missing handling** - continues without comparison
17. **Metric calculation error recovery** - skips problematic metrics

### Testing & Best Practices
18. **Testable error paths** for all components
19. **Best practices** and patterns for robust code
20. **Comprehensive monitoring** and alerting

The system is designed to be **robust**, **debuggable**, and **recoverable**, ensuring that:
- **No single failure stops the entire pipeline** (except FATAL errors)
- **All errors are logged** with context and severity
- **Fallback strategies** exist for all critical decision points
- **MLflow failures don't break pipeline** execution
- **Agent failures use intelligent defaults**
- Users can **diagnose and fix issues quickly** while maintaining pipeline integrity

This enhanced strategy ensures the pipeline is **production-ready** and can handle real-world failures gracefully.
