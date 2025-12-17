"""
Handle Missing Values Node (Unsupervised Learning)

For unsupervised learning, missing values require careful handling:
- Prefer DROPPING rows/columns with missing values (preserves data integrity)
- Use simple imputation (mean/median) if dropping loses too much data
- AVOID complex imputation (KNN, MICE) that creates artificial patterns

Key Differences from Supervised:
- No target variable to guide imputation
- Complex imputation can create false clusters
- Dropping data is often safer than imputing
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
import json

from utils.bedrock_client import BedrockClient
from ..techniques.handle_missing import (
    drop_rows, drop_columns, simple_imputation
)

logger = logging.getLogger(__name__)

# Available techniques (limited for unsupervised)
TECHNIQUES = {
    "drop_rows": drop_rows,
    "drop_columns": drop_columns,
    "simple_imputation": simple_imputation
    # NOT INCLUDED for unsupervised: knn_imputation, mice, iterative_imputation
    # These create artificial patterns that can mislead clustering
}


def handle_missing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Missing Values Node for Unsupervised Learning.

    Uses Bedrock LLM to select appropriate missing value strategy.
    For unsupervised learning, prioritizes data integrity over completeness.

    Args:
        state: Pipeline state containing:
            - df: Input DataFrame
            - review_answers: User's choices from review form
            - algorithm_category: Clustering/dimensionality_reduction/etc.

    Returns:
        Updated state with:
            - df: DataFrame with missing values handled
            - technique_metadata: Imputation technique and Bedrock reasoning
    """
    logger.info("=" * 80)
    logger.info("UNSUPERVISED HANDLE MISSING NODE: Starting missing value handling")
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
            if answer.get("question_id", "").startswith("handle_missing_"):
                user_technique = answer.get("technique_name") or answer.get("answer")
                logger.info(f"User selected technique: {user_technique}")
                break

        if not user_technique:
            logger.warning("No technique specified, defaulting to 'drop_rows'")
            user_technique = "drop_rows"

        # Get algorithm context
        algorithm_category = state.get("algorithm_category", "clustering")

        # Analyze missing value patterns
        missing_count = df.isnull().sum().sum()
        missing_percentage = (missing_count / (df.shape[0] * df.shape[1])) * 100

        missing_info = []
        for col in df.columns[:10]:  # Sample first 10 columns
            missing_col = df[col].isnull().sum()
            if missing_col > 0:
                missing_pct = (missing_col / len(df)) * 100
                col_type = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "categorical"
                missing_info.append(f"{col} ({col_type}): {missing_pct:.1f}% missing")

        # Build prompt for Bedrock
        bedrock_client = BedrockClient()

        prompt = f"""You are an expert ML engineer selecting missing value handling for UNSUPERVISED LEARNING.

**CRITICAL: For unsupervised learning, missing value handling must preserve data integrity:**
- Complex imputation (KNN, MICE) creates artificial patterns
- These artificial patterns can create FALSE clusters
- It's better to DROP data than to impute incorrectly
- Only use simple imputation (mean/median) when dropping loses too much data

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Samples: {original_shape[0]}
- Features: {original_shape[1]}
- Missing values: {missing_count} ({missing_percentage:.2f}%)
- Columns with missing values: {len([c for c in df.columns if df[c].isnull().any()])}

**Missing Value Patterns (first 10 columns):**
{chr(10).join(missing_info) if missing_info else "No missing values"}

**Algorithm Context:**
- Algorithm category: {algorithm_category}
- Learning paradigm: UNSUPERVISED (no target to guide imputation)

**Available Technique Signatures (UNSUPERVISED ONLY):**
1. drop_rows(df, threshold=0.5) - Drop rows with >threshold fraction missing (PREFERRED)
2. drop_columns(df, threshold=0.5) - Drop columns with >threshold fraction missing (PREFERRED)
3. simple_imputation(df, strategy="mean") - Simple mean/median imputation (use sparingly)

**NOT AVAILABLE for unsupervised:**
- knn_imputation: Creates artificial patterns based on neighbors
- mice: Creates artificial patterns via chained equations
- iterative_imputation: Creates artificial patterns iteratively

**Guidelines:**
- **PREFER DROPPING** over imputing (preserves data integrity)
- Use simple_imputation ONLY if:
  - Dropping would lose >50% of data
  - Missing percentage is low (<10%)
  - Column is numeric (mean/median makes sense)
- For clustering: Missing data can mislead distance calculations
- For dimensionality reduction: Missing data affects variance calculations

**Task:**
Based on "{user_technique}" and the data characteristics, return optimal parameters for UNSUPERVISED learning.

**Required Output (JSON only):**
{{
    "technique": "{user_technique}",
    "parameters": {{"threshold": 0.5, "strategy": "mean"}},
    "reasoning": "Why these parameters are optimal for UNSUPERVISED learning"
}}
"""

        logger.info("Invoking Bedrock for parameter selection...")
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
            technique_params = bedrock_decision.get("parameters", {})
            bedrock_reasoning = bedrock_decision.get("reasoning", "")

            logger.info(f"✓ Bedrock selected: {technique_name}")
            logger.info(f"✓ Parameters: {technique_params}")
            logger.info(f"✓ Reasoning: {bedrock_reasoning}")

        except Exception as parse_error:
            logger.warning(f"Failed to parse Bedrock response: {parse_error}")
            technique_name = user_technique
            technique_params = {"threshold": 0.5} if "drop" in user_technique else {"strategy": "mean"}
            bedrock_reasoning = "Using default parameters (Bedrock parse failed)"

        # Execute technique
        if technique_name not in TECHNIQUES:
            logger.warning(f"Unknown technique '{technique_name}', defaulting to 'drop_rows'")
            technique_name = "drop_rows"
            technique_params = {"threshold": 0.5}

        technique_func = TECHNIQUES[technique_name]
        df_imputed = technique_func(df.copy(), **technique_params)

        rows_removed = original_shape[0] - df_imputed.shape[0]
        cols_removed = original_shape[1] - df_imputed.shape[1]
        missing_handled = missing_count - df_imputed.isnull().sum().sum()

        logger.info(f"✓ Missing value handling complete: {original_shape} → {df_imputed.shape}")
        logger.info(f"  Rows removed: {rows_removed}")
        logger.info(f"  Columns removed: {cols_removed}")
        logger.info(f"  Missing values handled: {missing_handled}")

        # Update state
        state["df"] = df_imputed

        # Store metadata
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["handle_missing"] = {
            "technique": technique_name,
            "parameters": technique_params,
            "bedrock_reasoning": bedrock_reasoning,
            "algorithm_context": algorithm_category,
            "rows_removed": rows_removed,
            "cols_removed": cols_removed,
            "missing_handled": missing_handled,
            "shape_before": original_shape,
            "shape_after": df_imputed.shape
        }
        state["technique_metadata"] = technique_metadata

        logger.info("=" * 80)
        logger.info("UNSUPERVISED HANDLE MISSING NODE: Complete")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"Error in handle_missing_node: {e}", exc_info=True)
        errors = state.get("errors", [])
        errors.append(f"handle_missing_node error: {str(e)}")
        state["errors"] = errors
        return state
