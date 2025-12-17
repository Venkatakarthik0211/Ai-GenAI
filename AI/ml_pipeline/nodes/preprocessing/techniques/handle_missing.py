"""
Missing Value Imputation Technique Registry

8 techniques for handling missing values:
1. drop_rows: Drop rows with any missing values
2. drop_columns: Drop columns with high percentage of missing values
3. simple_imputation: Mean/median/mode imputation
4. knn_imputation: KNN-based imputation
5. mice: Multiple Imputation by Chained Equations
6. domain_specific: Domain-specific imputation
7. forward_fill: Forward fill (for time series)
8. interpolation: Linear/polynomial interpolation
"""

import pandas as pd
import numpy as np
from typing import Dict, Callable, Optional, List
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
import logging

logger = logging.getLogger(__name__)


def drop_rows(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Drop rows with any missing values.
    Simple but can lose significant data.

    Args:
        df: Input dataframe

    Returns:
        Dataframe with rows containing NaN removed
    """
    df_clean = df.dropna()
    rows_dropped = len(df) - len(df_clean)

    logger.info(f"Dropped {rows_dropped} rows with missing values")
    return df_clean


def drop_columns(df: pd.DataFrame, threshold: float = 0.5, **kwargs) -> pd.DataFrame:
    """
    Drop columns with high percentage of missing values.
    Useful for unsupervised learning to remove columns with too much missing data.

    Args:
        df: Input dataframe
        threshold: Drop columns with missing percentage > threshold (default 0.5)

    Returns:
        Dataframe with high-missing columns removed
    """
    df_clean = df.copy()
    missing_percentages = df.isnull().sum() / len(df)
    cols_to_drop = missing_percentages[missing_percentages > threshold].index.tolist()

    if cols_to_drop:
        df_clean = df_clean.drop(columns=cols_to_drop)
        logger.info(f"Dropped {len(cols_to_drop)} columns with >{threshold*100}% missing values: {cols_to_drop}")
    else:
        logger.info(f"No columns with >{threshold*100}% missing values")

    return df_clean


def simple_imputation(
    df: pd.DataFrame,
    strategy: str = "mean",
    numeric_columns: Optional[List[str]] = None,
    categorical_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Simple imputation using mean/median/mode.

    Args:
        df: Input dataframe
        strategy: "mean", "median", or "most_frequent" (default "mean")
        numeric_columns: Numeric columns to impute (default: all numeric)
        categorical_columns: Categorical columns to impute (default: all categorical)

    Returns:
        Dataframe with imputed values
    """
    df_clean = df.copy()

    # Impute numeric columns
    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    if numeric_columns:
        numeric_strategy = strategy if strategy in ["mean", "median"] else "mean"
        imputer_numeric = SimpleImputer(strategy=numeric_strategy)
        df_clean[numeric_columns] = imputer_numeric.fit_transform(df_clean[numeric_columns])
        logger.info(
            f"Simple imputation ({numeric_strategy}): Imputed {len(numeric_columns)} numeric columns"
        )

    # Impute categorical columns with mode
    if categorical_columns is None:
        categorical_columns = df_clean.select_dtypes(include=['object', 'category']).columns.tolist()

    if categorical_columns:
        imputer_categorical = SimpleImputer(strategy="most_frequent")
        df_clean[categorical_columns] = imputer_categorical.fit_transform(df_clean[categorical_columns])
        logger.info(
            f"Simple imputation (mode): Imputed {len(categorical_columns)} categorical columns"
        )

    return df_clean


def knn_imputation(
    df: pd.DataFrame,
    n_neighbors: int = 5,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    KNN-based imputation using k-nearest neighbors.
    Recommended for neural networks and when data has patterns.

    Args:
        df: Input dataframe
        n_neighbors: Number of neighbors to use (default 5)
        numeric_columns: Columns to impute (default: all numeric)

    Returns:
        Dataframe with imputed values
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for KNN imputation")
        return df_clean

    imputer = KNNImputer(n_neighbors=n_neighbors)
    df_clean[numeric_columns] = imputer.fit_transform(df_clean[numeric_columns])

    logger.info(
        f"KNN imputation: Imputed {len(numeric_columns)} columns "
        f"(k={n_neighbors})"
    )
    return df_clean


def mice_imputation(
    df: pd.DataFrame,
    max_iter: int = 10,
    random_state: int = 42,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    MICE (Multiple Imputation by Chained Equations).
    Uses iterative modeling to impute missing values.

    Args:
        df: Input dataframe
        max_iter: Maximum iterations (default 10)
        random_state: Random state for reproducibility
        numeric_columns: Columns to impute (default: all numeric)

    Returns:
        Dataframe with imputed values
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for MICE imputation")
        return df_clean

    imputer = IterativeImputer(max_iter=max_iter, random_state=random_state)
    df_clean[numeric_columns] = imputer.fit_transform(df_clean[numeric_columns])

    logger.info(
        f"MICE imputation: Imputed {len(numeric_columns)} columns "
        f"(max_iter={max_iter})"
    )
    return df_clean


def domain_specific_imputation(
    df: pd.DataFrame,
    imputation_rules: Dict[str, any]
) -> pd.DataFrame:
    """
    Domain-specific imputation using custom rules.

    Args:
        df: Input dataframe
        imputation_rules: Dict mapping column names to imputation values
            Example: {"age": 30, "income": "median", "category": "unknown"}
            - Numeric value: Fill with that value
            - "median"/"mean"/"mode": Fill with that statistic
            - String value: Fill with that string

    Returns:
        Dataframe with imputed values
    """
    df_clean = df.copy()

    for col, rule in imputation_rules.items():
        if col not in df_clean.columns:
            continue

        if isinstance(rule, str):
            if rule == "median":
                fill_value = df_clean[col].median()
            elif rule == "mean":
                fill_value = df_clean[col].mean()
            elif rule == "mode":
                fill_value = df_clean[col].mode()[0] if not df_clean[col].mode().empty else None
            else:
                fill_value = rule  # Use as literal string
        else:
            fill_value = rule

        missing_count = df_clean[col].isna().sum()
        df_clean[col] = df_clean[col].fillna(fill_value)

        logger.info(
            f"Domain-specific imputation: Filled {missing_count} values "
            f"in '{col}' with {fill_value}"
        )

    return df_clean


def forward_fill_imputation(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Forward fill imputation (use previous value).
    Recommended for time series data.

    Args:
        df: Input dataframe
        columns: Columns to apply (default: all columns with missing values)

    Returns:
        Dataframe with forward-filled values
    """
    df_clean = df.copy()

    if columns is None:
        columns = df_clean.columns[df_clean.isna().any()].tolist()

    for col in columns:
        missing_count = df_clean[col].isna().sum()
        df_clean[col] = df_clean[col].fillna(method='ffill')
        logger.info(f"Forward fill: Filled {missing_count} values in '{col}'")

    return df_clean


def interpolation_imputation(
    df: pd.DataFrame,
    method: str = "linear",
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Interpolation-based imputation.
    Recommended for time series or sequential data.

    Args:
        df: Input dataframe
        method: Interpolation method ("linear", "polynomial", "spline")
        numeric_columns: Columns to apply (default: all numeric)

    Returns:
        Dataframe with interpolated values
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_columns:
        missing_count = df_clean[col].isna().sum()
        if missing_count > 0:
            df_clean[col] = df_clean[col].interpolate(method=method)
            logger.info(
                f"Interpolation ({method}): Filled {missing_count} values in '{col}'"
            )

    return df_clean


# Technique registry dictionary
TECHNIQUES: Dict[str, Callable] = {
    "drop_rows": drop_rows,
    "simple_imputation": simple_imputation,
    "knn_imputation": knn_imputation,
    "mice": mice_imputation,
    "domain_specific": domain_specific_imputation,
    "forward_fill": forward_fill_imputation,
    "interpolation": interpolation_imputation
}
