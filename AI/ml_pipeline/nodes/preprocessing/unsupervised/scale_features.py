"""
Scale Features Node (Unsupervised Learning)

For unsupervised learning, feature scaling is CRITICAL:
- Distance-based algorithms (K-means, DBSCAN, KNN) absolutely require scaling
- Features with larger ranges dominate distance calculations
- StandardScaler or MinMaxScaler are essential for clustering

Key Differences from Supervised:
- Scaling is MANDATORY (not optional like tree models in supervised)
- Focus on preserving distances and variance
- StandardScaler preferred (preserves Gaussian structure)
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
import json

from utils.bedrock_client import BedrockClient
from ..techniques.scale_features import (
    standard_scaler, minmax_scaler, robust_scaler, maxabs_scaler
)

logger = logging.getLogger(__name__)

# Available techniques (all scaling methods appropriate for unsupervised)
TECHNIQUES = {
    "standard_scaler": standard_scaler,
    "minmax_scaler": minmax_scaler,
    "robust_scaler": robust_scaler,
    "maxabs_scaler": maxabs_scaler
    # "none" is NOT recommended for unsupervised distance-based algorithms!
}


def scale_features_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scale Features Node for Unsupervised Learning.

    Uses Bedrock LLM to select appropriate scaling technique.
    For unsupervised learning, scaling is MANDATORY for distance-based algorithms.

    Args:
        state: Pipeline state containing:
            - df: Input DataFrame
            - review_answers: User's choices from review form
            - algorithm_category: Clustering/dimensionality_reduction/etc.

    Returns:
        Updated state with:
            - df: DataFrame with scaled features
            - technique_metadata: Scaling technique and Bedrock reasoning
            - scaler: Fitted scaler object (for inference)
    """
    logger.info("=" * 80)
    logger.info("UNSUPERVISED SCALE FEATURES NODE: Starting feature scaling")
    logger.info("=" * 80)

    try:
        df = state.get("df")
        if df is None or df.empty:
            raise ValueError("DataFrame is empty or missing")

        original_shape = df.shape
        logger.info(f"Original shape: {original_shape}")

        # Get user's technique choice
        review_answers = state.get("review_answers", [])
        user_technique = None

        for answer in review_answers:
            if answer.get("question_id", "").startswith("scale_"):
                user_technique = answer.get("technique_name") or answer.get("answer")
                logger.info(f"User selected technique: {user_technique}")
                break

        if not user_technique:
            logger.warning("No technique specified, defaulting to 'standard_scaler' (REQUIRED for clustering)")
            user_technique = "standard_scaler"

        # Get algorithm context
        algorithm_category = state.get("algorithm_category", "clustering")

        # Identify numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_columns:
            logger.warning("No numeric columns found, skipping scaling")
            state["technique_metadata"] = state.get("technique_metadata", {})
            state["technique_metadata"]["scale_features"] = {
                "technique": "none",
                "parameters": {},
                "bedrock_reasoning": "No numeric columns to scale",
                "algorithm_context": algorithm_category,
                "scaler_fitted": False
            }
            return state

        logger.info(f"Found {len(numeric_columns)} numeric columns to scale")

        # Analyze distribution of numeric columns
        distribution_info = []
        for col in numeric_columns[:10]:  # Sample first 10
            col_min = df[col].min()
            col_max = df[col].max()
            col_mean = df[col].mean()
            col_std = df[col].std()
            distribution_info.append(
                f"{col}: range=[{col_min:.2f}, {col_max:.2f}], mean={col_mean:.2f}, std={col_std:.2f}"
            )

        # Build prompt for Bedrock
        bedrock_client = BedrockClient()

        prompt = f"""You are an expert ML engineer selecting feature scaling for UNSUPERVISED LEARNING.

**CRITICAL: Feature scaling is MANDATORY for unsupervised distance-based algorithms!**

**Why scaling is critical:**
- K-means, DBSCAN use Euclidean distance - unscaled features with large ranges dominate
- Example: salary (0-200K) vs age (0-100) → salary dominates distance calculation
- Dimensionality reduction (PCA, t-SNE) needs scaled features for variance calculations

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Numeric columns: {len(numeric_columns)}
- Sample distributions (first 10 columns):
{chr(10).join(distribution_info)}

**Algorithm Context:**
- Algorithm category: {algorithm_category}
- Learning paradigm: UNSUPERVISED

**Available Techniques (ALL REQUIRE SCALING for distance-based algorithms):**
1. standard_scaler(df, numeric_columns=[...]) - Standardize to mean=0, std=1 (RECOMMENDED)
   - Pros: Preserves Gaussian structure, works with all distance-based algorithms
   - Cons: Sensitive to outliers
   - Use for: K-means, hierarchical clustering, PCA, t-SNE

2. minmax_scaler(df, numeric_columns=[...]) - Scale to [0, 1] range
   - Pros: Bounded range, preserves zero values
   - Cons: Sensitive to outliers
   - Use for: Neural networks, algorithms needing bounded features

3. robust_scaler(df, numeric_columns=[...]) - Use median and IQR (robust to outliers)
   - Pros: Robust to outliers, preserves outlier information
   - Cons: Doesn't guarantee bounded range
   - Use for: DBSCAN (outlier-aware clustering), data with outliers

4. maxabs_scaler(df, numeric_columns=[...]) - Scale to [-1, 1] by max absolute value
   - Pros: Preserves sparsity, doesn't shift data
   - Cons: Sensitive to outliers
   - Use for: Sparse data

**Algorithm-Specific Recommendations:**
- **clustering** (K-means, DBSCAN, Hierarchical): standard_scaler or robust_scaler (MANDATORY!)
- **dimensionality_reduction** (PCA, t-SNE, UMAP): standard_scaler (MANDATORY!)
- **anomaly_detection**: robust_scaler (preserve outlier information)

**Task:**
Based on "{user_technique}" and algorithm category "{algorithm_category}", return optimal parameters.

**Required Output (JSON only):**
{{
    "technique": "{user_technique}",
    "parameters": {{"numeric_columns": [...]}},
    "reasoning": "Why this scaler is optimal for {algorithm_category} (emphasize MANDATORY nature for distance-based algorithms)"
}}
"""

        logger.info("Invoking Bedrock for scaling strategy...")
        bedrock_response = bedrock_client.invoke(
            prompt=prompt,
            temperature=0.2,
            max_tokens=1000
        )

        # Parse Bedrock response
        try:
            response_text = bedrock_response.get("content", "")
            json_match = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_match == -1 or json_end == 0:
                raise ValueError("No JSON found in Bedrock response")

            bedrock_decision = json.loads(response_text[json_match:json_end])
            technique_name = bedrock_decision.get("technique", user_technique)
            technique_params = bedrock_decision.get("parameters", {"numeric_columns": numeric_columns})
            bedrock_reasoning = bedrock_decision.get("reasoning", "")

            logger.info(f"✓ Bedrock selected: {technique_name}")
            logger.info(f"✓ Parameters: {technique_params}")
            logger.info(f"✓ Reasoning: {bedrock_reasoning}")

        except Exception as parse_error:
            logger.warning(f"Failed to parse Bedrock response: {parse_error}")
            technique_name = user_technique
            technique_params = {"numeric_columns": numeric_columns}
            bedrock_reasoning = "Using default parameters (Bedrock parse failed)"

        # Execute scaling
        if technique_name not in TECHNIQUES:
            logger.warning(f"Unknown technique '{technique_name}', defaulting to 'standard_scaler'")
            technique_name = "standard_scaler"

        technique_func = TECHNIQUES[technique_name]
        df_scaled, scaler = technique_func(df.copy(), **technique_params)

        logger.info(f"✓ Scaling complete: {original_shape} → {df_scaled.shape}")
        logger.info(f"  Scaler fitted: {scaler is not None}")

        # Update state
        state["df"] = df_scaled
        state["scaler"] = scaler  # Store for inference

        # Store metadata
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["scale_features"] = {
            "technique": technique_name,
            "parameters": technique_params,
            "bedrock_reasoning": bedrock_reasoning,
            "algorithm_context": algorithm_category,
            "scaler_fitted": scaler is not None,
            "scaler_type": type(scaler).__name__ if scaler else None,
            "shape_before": original_shape,
            "shape_after": df_scaled.shape
        }
        state["technique_metadata"] = technique_metadata

        logger.info("=" * 80)
        logger.info("UNSUPERVISED SCALE FEATURES NODE: Complete")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"Error in scale_features_node: {e}", exc_info=True)
        errors = state.get("errors", [])
        errors.append(f"scale_features_node error: {str(e)}")
        state["errors"] = errors
        return state
