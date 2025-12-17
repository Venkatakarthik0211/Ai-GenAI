"""
Outlier Handling Technique Registry

8 techniques for handling outliers in numerical data:
1. none: Skip outlier removal
2. iqr_method: IQR-based outlier removal
3. z_score: Z-score based outlier removal
4. winsorization: Cap outliers at percentiles
5. isolation_forest: Isolation Forest outlier detection
6. dbscan: DBSCAN-based outlier detection
7. robust_scalers: Apply RobustScaler
8. domain_clipping: Domain-specific value clipping
"""

import pandas as pd
import numpy as np
from typing import Dict, Callable, Optional, List
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import RobustScaler
import logging

logger = logging.getLogger(__name__)


def none_technique(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Skip outlier removal (no-op).
    Recommended for tree-based models which are robust to outliers.

    Args:
        df: Input dataframe

    Returns:
        Unchanged dataframe
    """
    logger.info("Skipping outlier removal (technique: none)")
    return df


def iqr_method(
    df: pd.DataFrame,
    multiplier: float = 1.5,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Remove outliers using IQR (Interquartile Range) method.
    Outliers: values < Q1 - multiplier*IQR or > Q3 + multiplier*IQR

    Args:
        df: Input dataframe
        multiplier: IQR multiplier (default 1.5, use 3.0 for more conservative)
        numeric_columns: Columns to apply (default: all numeric)

    Returns:
        Dataframe with outliers removed
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    outliers_removed = 0
    for col in numeric_columns:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        before_count = len(df_clean)
        df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
        outliers_removed += before_count - len(df_clean)

    logger.info(
        f"IQR method: Removed {outliers_removed} outlier rows "
        f"(multiplier={multiplier})"
    )
    return df_clean


def z_score_filtering(
    df: pd.DataFrame,
    threshold: float = 3.0,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Remove outliers using Z-score method.
    Outliers: |z-score| > threshold

    Args:
        df: Input dataframe
        threshold: Z-score threshold (default 3.0)
        numeric_columns: Columns to apply (default: all numeric)

    Returns:
        Dataframe with outliers removed
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    outliers_removed = 0
    for col in numeric_columns:
        z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
        before_count = len(df_clean)
        df_clean = df_clean[z_scores <= threshold]
        outliers_removed += before_count - len(df_clean)

    logger.info(
        f"Z-score filtering: Removed {outliers_removed} outlier rows "
        f"(threshold={threshold})"
    )
    return df_clean


def winsorization(
    df: pd.DataFrame,
    lower_pct: float = 1,
    upper_pct: float = 99,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Cap outliers at specified percentiles (winsorization).
    Recommended for linear models sensitive to extreme values.

    Args:
        df: Input dataframe
        lower_pct: Lower percentile (default 1)
        upper_pct: Upper percentile (default 99)
        numeric_columns: Columns to apply (default: all numeric)

    Returns:
        Dataframe with capped values
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    values_capped = 0
    for col in numeric_columns:
        lower_bound = df_clean[col].quantile(lower_pct / 100)
        upper_bound = df_clean[col].quantile(upper_pct / 100)

        before = df_clean[col].copy()
        df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
        values_capped += (before != df_clean[col]).sum()

    logger.info(
        f"Winsorization: Capped {values_capped} values "
        f"(percentiles: {lower_pct}-{upper_pct})"
    )
    return df_clean


def isolation_forest_outliers(
    df: pd.DataFrame,
    contamination: float = 0.1,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Detect and remove outliers using Isolation Forest algorithm.

    Args:
        df: Input dataframe
        contamination: Expected proportion of outliers (default 0.1)
        numeric_columns: Columns to apply (default: all numeric)

    Returns:
        Dataframe with outliers removed
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_columns) == 0:
        logger.warning("No numeric columns for Isolation Forest")
        return df_clean

    # Fit Isolation Forest
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    predictions = iso_forest.fit_predict(df_clean[numeric_columns])

    # Keep only inliers (prediction == 1)
    outliers_removed = (predictions == -1).sum()
    df_clean = df_clean[predictions == 1]

    logger.info(
        f"Isolation Forest: Removed {outliers_removed} outlier rows "
        f"(contamination={contamination})"
    )
    return df_clean


def dbscan_outliers(
    df: pd.DataFrame,
    eps: float = 0.5,
    min_samples: int = 5,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Identify and remove outliers using DBSCAN clustering.
    Points marked as noise (-1) are considered outliers.

    Args:
        df: Input dataframe
        eps: DBSCAN epsilon parameter
        min_samples: Minimum samples per cluster
        numeric_columns: Columns to apply (default: all numeric)

    Returns:
        Dataframe with outliers removed
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_columns) == 0:
        logger.warning("No numeric columns for DBSCAN")
        return df_clean

    # Fit DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(df_clean[numeric_columns])

    # Keep only non-noise points (cluster != -1)
    outliers_removed = (clusters == -1).sum()
    df_clean = df_clean[clusters != -1]

    logger.info(
        f"DBSCAN: Removed {outliers_removed} outlier rows "
        f"(eps={eps}, min_samples={min_samples})"
    )
    return df_clean


def robust_scalers(
    df: pd.DataFrame,
    numeric_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Apply RobustScaler to reduce outlier impact.
    Uses median and IQR instead of mean and std.

    Args:
        df: Input dataframe
        numeric_columns: Columns to apply (default: all numeric)

    Returns:
        Dataframe with robust scaling applied
    """
    df_clean = df.copy()

    if numeric_columns is None:
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_columns) == 0:
        logger.warning("No numeric columns for RobustScaler")
        return df_clean

    scaler = RobustScaler()
    df_clean[numeric_columns] = scaler.fit_transform(df_clean[numeric_columns])

    logger.info(f"RobustScaler applied to {len(numeric_columns)} columns")
    return df_clean


def domain_clipping(
    df: pd.DataFrame,
    bounds: Dict[str, tuple]
) -> pd.DataFrame:
    """
    Clip values to domain-specific ranges.

    Args:
        df: Input dataframe
        bounds: Dict mapping column names to (min, max) tuples
            Example: {"age": (0, 120), "price": (0, 1000000)}

    Returns:
        Dataframe with clipped values
    """
    df_clean = df.copy()

    values_clipped = 0
    for col, (min_val, max_val) in bounds.items():
        if col in df_clean.columns:
            before = df_clean[col].copy()
            df_clean[col] = df_clean[col].clip(lower=min_val, upper=max_val)
            values_clipped += (before != df_clean[col]).sum()

    logger.info(
        f"Domain clipping: Clipped {values_clipped} values "
        f"across {len(bounds)} columns"
    )
    return df_clean


# Technique registry dictionary
TECHNIQUES: Dict[str, Callable] = {
    "none": none_technique,
    "iqr_method": iqr_method,
    "z_score": z_score_filtering,
    "winsorization": winsorization,
    "isolation_forest": isolation_forest_outliers,
    "dbscan": dbscan_outliers,
    "robust_scalers": robust_scalers,
    "domain_clipping": domain_clipping
}
