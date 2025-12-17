"""
Encode Categorical Features Node (Unsupervised Learning)

For unsupervised learning, NO TARGET ENCODING is possible (no target variable!).
Use label encoding or ordinal encoding to preserve numerical distances for clustering.

Key Differences from Supervised:
- NO target encoding (no target variable!)
- NO one-hot encoding (creates dimension explosion, hurts distance metrics)
- Label encoding or Ordinal encoding ONLY
- Keep numerical representation compact for distance calculations
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
import json

from utils.bedrock_client import BedrockClient
from ..techniques.encode_features import (
    label_encoding, ordinal_encoding, frequency_encoding, hash_encoding
)

logger = logging.getLogger(__name__)

# Available techniques (NO target encoding or one-hot for unsupervised!)
TECHNIQUES = {
    "label_encoding": label_encoding,
    "ordinal_encoding": ordinal_encoding,
    "frequency_encoding": frequency_encoding,
    "hash_encoding": hash_encoding
    # NOT INCLUDED: target_encoding (no target!), one_hot (dimension explosion)
}


def encode_features_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Encode Categorical Features Node for Unsupervised Learning.

    Uses Bedrock LLM to select encoding strategy.
    Critical constraint: NO target encoding (no target variable in unsupervised!).

    Args:
        state: Pipeline state containing:
            - df: Input DataFrame
            - review_answers: User's choices from review form
            - algorithm_category: Clustering/dimensionality_reduction/etc.

    Returns:
        Updated state with:
            - df: DataFrame with encoded categorical features
            - technique_metadata: Encoding technique and Bedrock reasoning
    """
    logger.info("=" * 80)
    logger.info("UNSUPERVISED ENCODE FEATURES NODE: Starting categorical encoding")
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
            if answer.get("question_id", "").startswith("encode_"):
                user_technique = answer.get("technique_name") or answer.get("answer")
                logger.info(f"User selected technique: {user_technique}")
                break

        if not user_technique:
            logger.warning("No technique specified, defaulting to 'label_encoding'")
            user_technique = "label_encoding"

        # Get algorithm context
        algorithm_category = state.get("algorithm_category", "clustering")

        # Identify categorical columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if not categorical_columns:
            logger.info("No categorical columns found, skipping encoding")
            state["technique_metadata"] = state.get("technique_metadata", {})
            state["technique_metadata"]["encode_features"] = {
                "technique": "none",
                "parameters": {},
                "bedrock_reasoning": "No categorical columns to encode",
                "algorithm_context": algorithm_category
            }
            return state

        logger.info(f"Found {len(categorical_columns)} categorical columns")

        # Analyze cardinality
        cardinality_info = []
        high_cardinality_cols = []

        for col in categorical_columns[:10]:
            n_unique = df[col].nunique()
            cardinality_pct = (n_unique / len(df)) * 100 if len(df) > 0 else 0

            if n_unique > 10:
                high_cardinality_cols.append(col)
                cardinality_info.append(f"{col}: {n_unique} unique ({cardinality_pct:.1f}%)")

        # Build prompt for Bedrock
        bedrock_client = BedrockClient()

        prompt = f"""You are an expert ML engineer selecting categorical encoding for UNSUPERVISED LEARNING.

**CRITICAL: NO TARGET ENCODING for unsupervised learning (no target variable!).**

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Categorical columns: {len(categorical_columns)}
- High cardinality (>10 unique): {len(high_cardinality_cols)}

**Algorithm Context:**
- Algorithm category: {algorithm_category}

**Available Techniques:**
1. label_encoding - Assign integer labels (RECOMMENDED for clustering)
2. ordinal_encoding - Custom ordering if meaningful
3. frequency_encoding - Encode by frequency
4. hash_encoding - Hash to fixed dimensions (for high cardinality)

**Task:**
Return optimal parameters for "{user_technique}".

**Required Output (JSON only):**
{{
    "technique": "{user_technique}",
    "parameters": {{"categorical_columns": [...]}},
    "reasoning": "Brief explanation"
}}
"""

        logger.info("Invoking Bedrock for encoding strategy...")
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
            technique_params = bedrock_decision.get("parameters", {"categorical_columns": categorical_columns})
            bedrock_reasoning = bedrock_decision.get("reasoning", "")

            logger.info(f"✓ Bedrock selected: {technique_name}")

        except Exception as parse_error:
            logger.warning(f"Failed to parse Bedrock response: {parse_error}")
            technique_name = user_technique
            technique_params = {"categorical_columns": categorical_columns}
            bedrock_reasoning = "Using default parameters"

        # Execute encoding
        if technique_name not in TECHNIQUES:
            logger.warning(f"Unknown technique '{technique_name}', defaulting to 'label_encoding'")
            technique_name = "label_encoding"

        technique_func = TECHNIQUES[technique_name]
        df_encoded = technique_func(df.copy(), **technique_params)

        new_columns_created = df_encoded.shape[1] - original_shape[1]

        logger.info(f"✓ Encoding complete: {original_shape} → {df_encoded.shape}")

        # Update state
        state["df"] = df_encoded

        # Store metadata
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["encode_features"] = {
            "technique": technique_name,
            "parameters": technique_params,
            "bedrock_reasoning": bedrock_reasoning,
            "algorithm_context": algorithm_category,
            "new_columns_created": new_columns_created,
            "shape_before": original_shape,
            "shape_after": df_encoded.shape
        }
        state["technique_metadata"] = technique_metadata

        logger.info("=" * 80)
        logger.info("UNSUPERVISED ENCODE FEATURES NODE: Complete")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"Error in encode_features_node: {e}", exc_info=True)
        errors = state.get("errors", [])
        errors.append(f"encode_features_node error: {str(e)}")
        state["errors"] = errors
        return state
