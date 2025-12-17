"""
Categorical Encoding Technique Registry

8 techniques for encoding categorical features:
1. one_hot: One-hot encoding (binary columns)
2. label_encoding: Label encoding (ordinal integers)
3. ordinal_encoding: Ordinal encoding with custom ordering
4. target_encoding: Target/mean encoding
5. frequency_encoding: Frequency-based encoding
6. binary_encoding: Binary encoding
7. hash_encoding: Hash encoding
8. embeddings: Learned embeddings (for neural networks)
"""

import pandas as pd
import numpy as np
from typing import Dict, Callable, Optional, List
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from category_encoders import TargetEncoder, BinaryEncoder, HashingEncoder
import logging

logger = logging.getLogger(__name__)


def one_hot_encoding(
    df: pd.DataFrame,
    categorical_columns: Optional[List[str]] = None,
    drop_first: bool = True
) -> pd.DataFrame:
    """
    One-hot encoding: Create binary column for each category.
    Recommended for tree models and when cardinality is low (<10 categories).

    Args:
        df: Input dataframe
        categorical_columns: Columns to encode (default: all object/category columns)
        drop_first: Drop first category to avoid multicollinearity (default True)

    Returns:
        Dataframe with one-hot encoded columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

    if not categorical_columns:
        logger.warning("No categorical columns for one-hot encoding")
        return df_encoded

    # Apply one-hot encoding
    df_encoded = pd.get_dummies(
        df_encoded,
        columns=categorical_columns,
        drop_first=drop_first
    )

    logger.info(
        f"One-hot encoding: Encoded {len(categorical_columns)} columns "
        f"(drop_first={drop_first}), result shape: {df_encoded.shape}"
    )
    return df_encoded


def label_encoding(
    df: pd.DataFrame,
    categorical_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Label encoding: Map categories to integers (0, 1, 2, ...).
    Recommended for tree models with ordinal categories.

    Args:
        df: Input dataframe
        categorical_columns: Columns to encode (default: all object/category columns)

    Returns:
        Dataframe with label encoded columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

    if not categorical_columns:
        logger.warning("No categorical columns for label encoding")
        return df_encoded

    encoders = {}
    for col in categorical_columns:
        encoder = LabelEncoder()
        df_encoded[col] = encoder.fit_transform(df_encoded[col].astype(str))
        encoders[col] = encoder

    logger.info(f"Label encoding: Encoded {len(categorical_columns)} columns")
    return df_encoded


def ordinal_encoding(
    df: pd.DataFrame,
    categorical_columns: Optional[List[str]] = None,
    category_orders: Optional[Dict[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Ordinal encoding: Encode categories with specified ordering.
    Useful for unsupervised learning when categories have inherent order.

    Args:
        df: Input dataframe
        categorical_columns: Columns to encode (default: all object/category columns)
        category_orders: Dict mapping column names to ordered category lists
                        e.g., {"size": ["small", "medium", "large"]}
                        If not provided, uses alphabetical order

    Returns:
        Dataframe with ordinal encoded columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

    if not categorical_columns:
        logger.warning("No categorical columns for ordinal encoding")
        return df_encoded

    if category_orders is None:
        category_orders = {}

    for col in categorical_columns:
        # Get ordering for this column
        if col in category_orders:
            categories = category_orders[col]
        else:
            # Use alphabetical order if not specified
            categories = sorted(df_encoded[col].dropna().unique())

        # Create mapping from category to integer
        mapping = {cat: i for i, cat in enumerate(categories)}

        # Apply mapping
        df_encoded[col] = df_encoded[col].map(mapping)

        logger.info(
            f"Ordinal encoding: {col} → {len(categories)} categories "
            f"(order: {categories[:3]}{'...' if len(categories) > 3 else ''})"
        )

    return df_encoded


def target_encoding(
    df: pd.DataFrame,
    target_column: str,
    categorical_columns: Optional[List[str]] = None,
    smoothing: float = 1.0
) -> pd.DataFrame:
    """
    Target encoding: Replace categories with target mean.
    Recommended for high-cardinality features with tree models.

    Args:
        df: Input dataframe
        target_column: Name of target column
        categorical_columns: Columns to encode (default: all object/category columns)
        smoothing: Smoothing factor to prevent overfitting (default 1.0)

    Returns:
        Dataframe with target encoded columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()
        # Remove target column if it's categorical
        if target_column in categorical_columns:
            categorical_columns.remove(target_column)

    if not categorical_columns:
        logger.warning("No categorical columns for target encoding")
        return df_encoded

    # Ensure target column exists
    if target_column not in df_encoded.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataframe")

    encoder = TargetEncoder(cols=categorical_columns, smoothing=smoothing)
    df_encoded[categorical_columns] = encoder.fit_transform(
        df_encoded[categorical_columns],
        df_encoded[target_column]
    )

    logger.info(
        f"Target encoding: Encoded {len(categorical_columns)} columns "
        f"(smoothing={smoothing})"
    )
    return df_encoded


def frequency_encoding(
    df: pd.DataFrame,
    categorical_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Frequency encoding: Replace categories with their frequency.

    Args:
        df: Input dataframe
        categorical_columns: Columns to encode (default: all object/category columns)

    Returns:
        Dataframe with frequency encoded columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

    if not categorical_columns:
        logger.warning("No categorical columns for frequency encoding")
        return df_encoded

    for col in categorical_columns:
        freq_map = df_encoded[col].value_counts(normalize=True).to_dict()
        df_encoded[col] = df_encoded[col].map(freq_map)

    logger.info(f"Frequency encoding: Encoded {len(categorical_columns)} columns")
    return df_encoded


def binary_encoding(
    df: pd.DataFrame,
    categorical_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Binary encoding: Encode categories as binary digits.
    More compact than one-hot for high-cardinality features.

    Args:
        df: Input dataframe
        categorical_columns: Columns to encode (default: all object/category columns)

    Returns:
        Dataframe with binary encoded columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

    if not categorical_columns:
        logger.warning("No categorical columns for binary encoding")
        return df_encoded

    encoder = BinaryEncoder(cols=categorical_columns)
    df_encoded = encoder.fit_transform(df_encoded)

    logger.info(
        f"Binary encoding: Encoded {len(categorical_columns)} columns, "
        f"result shape: {df_encoded.shape}"
    )
    return df_encoded


def hash_encoding(
    df: pd.DataFrame,
    categorical_columns: Optional[List[str]] = None,
    n_components: int = 8
) -> pd.DataFrame:
    """
    Hash encoding: Hash categories to fixed-size feature space.
    Useful for very high-cardinality features.

    Args:
        df: Input dataframe
        categorical_columns: Columns to encode (default: all object/category columns)
        n_components: Number of hash buckets (default 8)

    Returns:
        Dataframe with hash encoded columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

    if not categorical_columns:
        logger.warning("No categorical columns for hash encoding")
        return df_encoded

    encoder = HashingEncoder(cols=categorical_columns, n_components=n_components)
    df_encoded = encoder.fit_transform(df_encoded)

    logger.info(
        f"Hash encoding: Encoded {len(categorical_columns)} columns "
        f"into {n_components} components"
    )
    return df_encoded


def embedding_encoding(
    df: pd.DataFrame,
    categorical_columns: Optional[List[str]] = None,
    embedding_dim: int = 10
) -> pd.DataFrame:
    """
    Learned embeddings: Create embedding vectors for categories.
    Recommended for neural networks with high-cardinality features.

    Note: This is a placeholder that creates random embeddings.
    For production, use actual learned embeddings from neural network training.

    Args:
        df: Input dataframe
        categorical_columns: Columns to encode (default: all object/category columns)
        embedding_dim: Embedding dimensionality (default 10)

    Returns:
        Dataframe with embedding columns
    """
    df_encoded = df.copy()

    if categorical_columns is None:
        categorical_columns = df_encoded.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

    if not categorical_columns:
        logger.warning("No categorical columns for embedding encoding")
        return df_encoded

    logger.warning(
        "Embedding encoding is a placeholder. "
        "For production, use learned embeddings from neural network training."
    )

    # Placeholder: Create random embeddings for each category
    for col in categorical_columns:
        unique_values = df_encoded[col].unique()
        embedding_map = {
            val: np.random.randn(embedding_dim)
            for val in unique_values
        }

        # Create embedding columns
        embeddings = df_encoded[col].map(embedding_map)
        embedding_df = pd.DataFrame(
            embeddings.tolist(),
            columns=[f"{col}_emb_{i}" for i in range(embedding_dim)],
            index=df_encoded.index
        )

        # Drop original column and add embedding columns
        df_encoded = df_encoded.drop(columns=[col])
        df_encoded = pd.concat([df_encoded, embedding_df], axis=1)

    logger.info(
        f"Embedding encoding: Encoded {len(categorical_columns)} columns "
        f"with dimension {embedding_dim}"
    )
    return df_encoded


# Technique registry dictionary
TECHNIQUES: Dict[str, Callable] = {
    "one_hot": one_hot_encoding,
    "label_encoding": label_encoding,
    "target_encoding": target_encoding,
    "frequency_encoding": frequency_encoding,
    "binary_encoding": binary_encoding,
    "hash_encoding": hash_encoding,
    "embeddings": embedding_encoding
}
