"""Validators for pipeline state and data."""

from typing import List, Dict, Any
import pandas as pd
from .state import PipelineState
from .exceptions import StateValidationError, DataValidationError, InsufficientDataError, MissingTargetError


def validate_state(state: PipelineState, required_keys: List[str]) -> None:
    """
    Validate that state contains all required keys.

    Args:
        state: Pipeline state to validate
        required_keys: List of required state keys

    Raises:
        StateValidationError: If required keys are missing
    """
    missing_keys = [key for key in required_keys if key not in state]

    if missing_keys:
        raise StateValidationError(
            f"Missing required state keys: {', '.join(missing_keys)}",
            missing_keys=missing_keys
        )


def validate_data(
    data: pd.DataFrame,
    target_column: str = None,
    min_samples: int = 100,
    max_missing_ratio: float = 0.3
) -> Dict[str, Any]:
    """
    Validate input data meets minimum requirements.

    Args:
        data: DataFrame to validate
        target_column: Target column name (if applicable)
        min_samples: Minimum number of samples required
        max_missing_ratio: Maximum ratio of missing values per feature

    Returns:
        Dictionary containing validation results and statistics

    Raises:
        DataValidationError: If validation fails
        InsufficientDataError: If not enough samples
        MissingTargetError: If target column is missing
    """
    validation_errors = {}

    # Check minimum samples
    n_samples = len(data)
    if n_samples < min_samples:
        raise InsufficientDataError(
            f"Insufficient data: {n_samples} samples (required: {min_samples})",
            n_samples=n_samples,
            required_samples=min_samples
        )

    # Check target column exists
    if target_column and target_column not in data.columns:
        raise MissingTargetError(target_column)

    # Check missing values
    missing_ratios = data.isnull().sum() / n_samples
    problematic_features = missing_ratios[missing_ratios > max_missing_ratio].index.tolist()

    if problematic_features:
        validation_errors["high_missing_features"] = {
            feat: missing_ratios[feat] for feat in problematic_features
        }

    # Check for duplicate rows
    n_duplicates = data.duplicated().sum()
    if n_duplicates > 0:
        validation_errors["duplicate_rows"] = n_duplicates

    # Check for constant features
    constant_features = [col for col in data.columns if data[col].nunique() == 1]
    if constant_features:
        validation_errors["constant_features"] = constant_features

    # Compile validation results
    validation_results = {
        "valid": len(validation_errors) == 0,
        "n_samples": n_samples,
        "n_features": len(data.columns),
        "missing_ratios": missing_ratios.to_dict(),
        "n_duplicates": n_duplicates,
        "errors": validation_errors,
    }

    return validation_results


def validate_train_test_split(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series
) -> None:
    """
    Validate train/test split data.

    Args:
        X_train: Training features
        X_test: Testing features
        y_train: Training target
        y_test: Testing target

    Raises:
        DataValidationError: If validation fails
    """
    errors = {}

    # Check shapes match
    if len(X_train) != len(y_train):
        errors["train_shape_mismatch"] = f"X_train: {len(X_train)}, y_train: {len(y_train)}"

    if len(X_test) != len(y_test):
        errors["test_shape_mismatch"] = f"X_test: {len(X_test)}, y_test: {len(y_test)}"

    # Check feature consistency
    if not X_train.columns.equals(X_test.columns):
        errors["feature_mismatch"] = "Train and test features don't match"

    # Check for empty splits
    if len(X_train) == 0:
        errors["empty_train"] = "Training set is empty"

    if len(X_test) == 0:
        errors["empty_test"] = "Test set is empty"

    if errors:
        raise DataValidationError("Train/test split validation failed", validation_errors=errors)


def validate_model_input(X: pd.DataFrame) -> None:
    """
    Validate model input data.

    Args:
        X: Input features

    Raises:
        DataValidationError: If validation fails
    """
    errors = {}

    # Check for infinite values
    if X.select_dtypes(include=['float64', 'float32']).isin([float('inf'), float('-inf')]).any().any():
        errors["infinite_values"] = "Data contains infinite values"

    # Check for NaN values
    if X.isnull().any().any():
        errors["missing_values"] = "Data contains missing values"

    # Check data types
    invalid_types = []
    for col in X.columns:
        if X[col].dtype == 'object':
            invalid_types.append(col)

    if invalid_types:
        errors["invalid_dtypes"] = f"Object columns found: {invalid_types}"

    if errors:
        raise DataValidationError("Model input validation failed", validation_errors=errors)


def validate_algorithm_results(results: Dict[str, Any]) -> None:
    """
    Validate algorithm training results.

    Args:
        results: Dictionary of algorithm results

    Raises:
        StateValidationError: If validation fails
    """
    if not results:
        raise StateValidationError("No algorithm results found")

    required_fields = ["algorithm_name", "best_params", "cv_mean_score", "test_score", "model"]

    for algo_name, result in results.items():
        missing = [field for field in required_fields if field not in result]
        if missing:
            raise StateValidationError(
                f"Algorithm result for '{algo_name}' missing fields: {missing}",
                missing_keys=missing
            )
