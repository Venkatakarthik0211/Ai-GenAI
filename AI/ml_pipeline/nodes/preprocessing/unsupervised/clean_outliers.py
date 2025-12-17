"""
Clean Outliers Node (Unsupervised Learning)

For unsupervised learning, outliers are often MEANINGFUL data points (e.g., separate clusters,
anomalies to detect). This node focuses on data quality validation rather than outlier removal.

Key Differences from Supervised:
- KEEP outliers (they could be valid clusters or anomalies!)
- Only remove duplicates and invalid values
- Focus on data validation, not statistical outlier removal
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
import json

from utils.bedrock_client import BedrockClient

logger = logging.getLogger(__name__)

# Available techniques (limited to data quality checks for unsupervised)
TECHNIQUES = {
    "keep_all": lambda df: df,  # Keep all data including outliers
    "remove_duplicates": lambda df: df.drop_duplicates(),
    "remove_invalid": lambda df: df.replace([np.inf, -np.inf], np.nan).dropna()
}


def clean_outliers_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean Outliers Node for Unsupervised Learning.

    Uses Bedrock LLM to intelligently select data cleaning approach.
    For unsupervised learning, we preserve outliers as they may represent:
    - Separate clusters
    - Anomalies we want to detect
    - Valid edge cases in the data

    Args:
        state: Pipeline state containing:
            - df: Input DataFrame
            - review_answers: User's choices from review form
            - algorithm_category: Clustering/dimensionality_reduction/etc.

    Returns:
        Updated state with:
            - df: Cleaned DataFrame (outliers preserved!)
            - technique_metadata: Cleaning technique and Bedrock reasoning
    """
    logger.info("=" * 80)
    logger.info("UNSUPERVISED CLEAN OUTLIERS NODE: Starting data quality validation")
    logger.info("=" * 80)

    try:
        df = state.get("df")
        if df is None or df.empty:
            raise ValueError("DataFrame is empty or missing")

        original_shape = df.shape
        logger.info(f"Original shape: {original_shape}")

        # Get user's technique choice from review answers
        review_answers = state.get("review_answers", [])
        user_technique = None

        for answer in review_answers:
            if answer.get("question_id", "").startswith("clean_"):
                user_technique = answer.get("technique_name") or answer.get("answer")
                logger.info(f"User selected technique: {user_technique}")
                break

        if not user_technique:
            logger.warning("No cleaning technique specified, defaulting to 'keep_all'")
            user_technique = "keep_all"

        # Get algorithm context
        algorithm_category = state.get("algorithm_category", "clustering")

        # Analyze data characteristics
        n_samples, n_features = df.shape
        duplicate_count = df.duplicated().sum()
        invalid_count = df.replace([np.inf, -np.inf], np.nan).isnull().sum().sum()

        # Build prompt for Bedrock LLM
        bedrock_client = BedrockClient()

        prompt = f"""You are an expert ML engineer selecting optimal data cleaning parameters for UNSUPERVISED LEARNING.

**CRITICAL: For unsupervised learning, outliers are often MEANINGFUL:**
- Outliers could be separate clusters to discover
- Outliers could be anomalies we want to detect
- Outliers could be valid edge cases in the data

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Samples: {n_samples}
- Features: {n_features}
- Duplicates: {duplicate_count} rows ({duplicate_count/n_samples*100:.2f}%)
- Invalid values (inf, -inf, NaN): {invalid_count} values

**Algorithm Context:**
- Algorithm category: {algorithm_category}
- Learning paradigm: UNSUPERVISED (no target variable)

**Available Technique Signatures:**
1. keep_all() - Keep all data including outliers (RECOMMENDED for unsupervised)
2. remove_duplicates() - Only remove exact duplicate rows
3. remove_invalid() - Only remove inf/-inf/NaN values (may lose important data)

**Guidelines for Unsupervised Learning:**
- **PRESERVE OUTLIERS**: They could be:
  - Separate clusters (e.g., in customer segmentation, outliers = VIP customers)
  - Anomalies to detect (the whole point of anomaly detection!)
  - Valid edge cases that define cluster boundaries
- Only remove true data quality issues (duplicates, invalid values)
- Err on the side of keeping data rather than removing it

**Task:**
Based on the user's choice "{user_technique}" and the data characteristics, return the OPTIMAL parameters.

**Required Output (JSON only, no other text):**
{{
    "technique": "{user_technique}",
    "parameters": {{}},
    "reasoning": "Brief explanation of why these parameters are optimal for UNSUPERVISED learning"
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
            logger.info(f"✓ Reasoning: {bedrock_reasoning}")

        except Exception as parse_error:
            logger.warning(f"Failed to parse Bedrock response: {parse_error}")
            technique_name = user_technique
            technique_params = {}
            bedrock_reasoning = "Using user's choice (Bedrock parse failed)"

        # Execute cleaning technique
        if technique_name not in TECHNIQUES:
            logger.warning(f"Unknown technique '{technique_name}', defaulting to 'keep_all'")
            technique_name = "keep_all"

        technique_func = TECHNIQUES[technique_name]
        df_cleaned = technique_func(df.copy())

        rows_removed = original_shape[0] - df_cleaned.shape[0]
        logger.info(f"✓ Cleaning complete: {original_shape} → {df_cleaned.shape}")
        logger.info(f"  Rows removed: {rows_removed}")

        # Update state
        state["df"] = df_cleaned

        # Store metadata for preprocessing review
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["clean_outliers"] = {
            "technique": technique_name,
            "parameters": technique_params,
            "bedrock_reasoning": bedrock_reasoning,
            "algorithm_context": algorithm_category,
            "rows_removed": rows_removed,
            "shape_before": original_shape,
            "shape_after": df_cleaned.shape,
            "duplicates_removed": duplicate_count if technique_name == "remove_duplicates" else 0
        }
        state["technique_metadata"] = technique_metadata

        logger.info("=" * 80)
        logger.info("UNSUPERVISED CLEAN OUTLIERS NODE: Complete")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"Error in clean_outliers_node: {e}", exc_info=True)
        errors = state.get("errors", [])
        errors.append(f"clean_outliers_node error: {str(e)}")
        state["errors"] = errors
        return state
