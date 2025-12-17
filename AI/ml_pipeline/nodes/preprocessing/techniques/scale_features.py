"""
Feature Scaling Technique Registry

7 techniques for scaling numerical features:
1. none: Skip scaling (for tree models)
2. standard_scaler: StandardScaler (z-score normalization)
3. minmax_scaler: MinMaxScaler (scale to [0, 1])
4. robust_scaler: RobustScaler (robust to outliers)
5. maxabs_scaler: MaxAbsScaler (scale by max absolute value)
6. normalizer: Normalizer (normalize samples to unit norm)
7. quantile_transformer: QuantileTransformer (transform to uniform/normal)
"""

import pandas as pd
import numpy as np
from typing import Dict, Callable, Optional, List, Tuple
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    MaxAbsScaler,
    Normalizer,
    QuantileTransformer
)
import logging

logger = logging.getLogger(__name__)


def none_scaling(df: pd.DataFrame, **kwargs) -> Tuple[pd.DataFrame, None]:
    """
    Skip feature scaling (no-op).
    Recommended for tree-based models which are scale-invariant.

    Args:
        df: Input dataframe

    Returns:
        Tuple of (unchanged dataframe, None)
    """
    logger.info("Skipping feature scaling (technique: none)")
    return df, None


def standard_scaler_scaling(
    df: pd.DataFrame,
    numeric_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, StandardScaler]:
    """
    StandardScaler: Z-score normalization (mean=0, std=1).
    Recommended for linear models and neural networks.

    Formula: (x - mean) / std

    Args:
        df: Input dataframe
        numeric_columns: Columns to scale (default: all numeric)

    Returns:
        Tuple of (scaled dataframe, fitted scaler)
    """
    df_scaled = df.copy()

    if numeric_columns is None:
        numeric_columns = df_scaled.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for StandardScaler")
        return df_scaled, None

    scaler = StandardScaler()
    df_scaled[numeric_columns] = scaler.fit_transform(df_scaled[numeric_columns])

    logger.info(f"StandardScaler: Scaled {len(numeric_columns)} columns")
    return df_scaled, scaler


def minmax_scaler_scaling(
    df: pd.DataFrame,
    feature_range: Tuple[float, float] = (0, 1),
    numeric_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, MinMaxScaler]:
    """
    MinMaxScaler: Scale features to a given range (default [0, 1]).
    Recommended for neural networks.

    Formula: (x - min) / (max - min) * (range_max - range_min) + range_min

    Args:
        df: Input dataframe
        feature_range: Desired range (default (0, 1))
        numeric_columns: Columns to scale (default: all numeric)

    Returns:
        Tuple of (scaled dataframe, fitted scaler)
    """
    df_scaled = df.copy()

    if numeric_columns is None:
        numeric_columns = df_scaled.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for MinMaxScaler")
        return df_scaled, None

    scaler = MinMaxScaler(feature_range=feature_range)
    df_scaled[numeric_columns] = scaler.fit_transform(df_scaled[numeric_columns])

    logger.info(
        f"MinMaxScaler: Scaled {len(numeric_columns)} columns "
        f"to range {feature_range}"
    )
    return df_scaled, scaler


def robust_scaler_scaling(
    df: pd.DataFrame,
    numeric_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, RobustScaler]:
    """
    RobustScaler: Scale using median and IQR (robust to outliers).
    Recommended for data with outliers, especially with neural networks.

    Formula: (x - median) / IQR

    Args:
        df: Input dataframe
        numeric_columns: Columns to scale (default: all numeric)

    Returns:
        Tuple of (scaled dataframe, fitted scaler)
    """
    df_scaled = df.copy()

    if numeric_columns is None:
        numeric_columns = df_scaled.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for RobustScaler")
        return df_scaled, None

    scaler = RobustScaler()
    df_scaled[numeric_columns] = scaler.fit_transform(df_scaled[numeric_columns])

    logger.info(f"RobustScaler: Scaled {len(numeric_columns)} columns")
    return df_scaled, scaler


def maxabs_scaler_scaling(
    df: pd.DataFrame,
    numeric_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, MaxAbsScaler]:
    """
    MaxAbsScaler: Scale by maximum absolute value to [-1, 1].
    Recommended for sparse data.

    Formula: x / max(abs(x))

    Args:
        df: Input dataframe
        numeric_columns: Columns to scale (default: all numeric)

    Returns:
        Tuple of (scaled dataframe, fitted scaler)
    """
    df_scaled = df.copy()

    if numeric_columns is None:
        numeric_columns = df_scaled.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for MaxAbsScaler")
        return df_scaled, None

    scaler = MaxAbsScaler()
    df_scaled[numeric_columns] = scaler.fit_transform(df_scaled[numeric_columns])

    logger.info(f"MaxAbsScaler: Scaled {len(numeric_columns)} columns")
    return df_scaled, scaler


def normalizer_scaling(
    df: pd.DataFrame,
    norm: str = "l2",
    numeric_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Normalizer]:
    """
    Normalizer: Normalize samples individually to unit norm.
    Recommended when using distance-based algorithms.

    Args:
        df: Input dataframe
        norm: Norm to use ("l1", "l2", or "max") (default "l2")
        numeric_columns: Columns to normalize (default: all numeric)

    Returns:
        Tuple of (normalized dataframe, fitted scaler)
    """
    df_scaled = df.copy()

    if numeric_columns is None:
        numeric_columns = df_scaled.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for Normalizer")
        return df_scaled, None

    scaler = Normalizer(norm=norm)
    df_scaled[numeric_columns] = scaler.fit_transform(df_scaled[numeric_columns])

    logger.info(f"Normalizer: Normalized {len(numeric_columns)} columns (norm={norm})")
    return df_scaled, scaler


def quantile_transformer_scaling(
    df: pd.DataFrame,
    output_distribution: str = "uniform",
    n_quantiles: int = 1000,
    numeric_columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, QuantileTransformer]:
    """
    QuantileTransformer: Transform features to follow uniform or normal distribution.
    Recommended for neural networks to reduce impact of outliers.

    Args:
        df: Input dataframe
        output_distribution: "uniform" or "normal" (default "uniform")
        n_quantiles: Number of quantiles (default 1000)
        numeric_columns: Columns to transform (default: all numeric)

    Returns:
        Tuple of (transformed dataframe, fitted scaler)
    """
    df_scaled = df.copy()

    if numeric_columns is None:
        numeric_columns = df_scaled.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_columns:
        logger.warning("No numeric columns for QuantileTransformer")
        return df_scaled, None

    scaler = QuantileTransformer(
        output_distribution=output_distribution,
        n_quantiles=min(n_quantiles, len(df_scaled))
    )
    df_scaled[numeric_columns] = scaler.fit_transform(df_scaled[numeric_columns])

    logger.info(
        f"QuantileTransformer: Transformed {len(numeric_columns)} columns "
        f"to {output_distribution} distribution"
    )
    return df_scaled, scaler


# Technique registry dictionary
TECHNIQUES: Dict[str, Callable] = {
    "none": none_scaling,
    "standard_scaler": standard_scaler_scaling,
    "minmax_scaler": minmax_scaler_scaling,
    "robust_scaler": robust_scaler_scaling,
    "maxabs_scaler": maxabs_scaler_scaling,
    "normalizer": normalizer_scaling,
    "quantile_transformer": quantile_transformer_scaling
}

# Aliases for easier imports (without _scaling suffix)
standard_scaler = standard_scaler_scaling
minmax_scaler = minmax_scaler_scaling
robust_scaler = robust_scaler_scaling
maxabs_scaler = maxabs_scaler_scaling
normalizer = normalizer_scaling
quantile_transformer = quantile_transformer_scaling
