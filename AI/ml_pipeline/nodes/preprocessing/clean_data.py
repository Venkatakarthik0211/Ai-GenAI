"""Data cleaning node for ML Pipeline - LLM-Based Parameter Selection."""

import pandas as pd
import numpy as np
import mlflow
import logging
import json
import re
from typing import Dict, Any

from core.state import PipelineState, update_state, mark_node_completed
from .techniques.clean_data import TECHNIQUES
from utils.bedrock_client import BedrockClient

logger = logging.getLogger(__name__)


def clean_data_node(state: PipelineState) -> PipelineState:
    """
    Clean data using LLM-based parameter selection.

    NEW ARCHITECTURE (per user guidance):
    1. Read user's answer from review_answers (which technique they chose)
    2. Get data characteristics from state (outlier %, distribution, etc.)
    3. Send to Bedrock LLM: "User chose X, data has Y characteristics, what parameters?"
    4. Bedrock returns optimal parameters in JSON format
    5. Execute Python cleaning function with those parameters
    6. Update state with cleaned data

    This allows Bedrock to intelligently select parameters based on:
    - User's technique choice
    - Actual data characteristics
    - Algorithm requirements
    - Best practices

    Available Techniques (8):
    - none: Skip outlier removal
    - iqr_method: IQR-based outlier removal
    - z_score: Z-score threshold filtering
    - winsorization: Cap outliers at percentiles
    - isolation_forest: Isolation Forest detection
    - dbscan: DBSCAN-based detection
    - robust_scalers: Apply RobustScaler
    - domain_clipping: Domain-specific clipping

    Args:
        state: Current pipeline state with raw_data, review_answers, data_profile

    Returns:
        Updated pipeline state with cleaned_data
    """
    node_name = "clean_data"

    try:
        raw_data = state["raw_data"]
        df = raw_data.copy()
        original_shape = df.shape
        logger.info(f"Cleaning data with shape: {original_shape}")

        # ============ Step 1: Get User's Choice ============
        review_answers = state.get("review_answers", {})

        # Look for clean_data answer (could be clean_data_q1, clean_data_technique, etc.)
        user_technique = None
        for key, value in review_answers.items():
            if "clean_data" in key.lower():
                user_technique = value
                logger.info(f"Found user's cleaning choice in '{key}': {value}")
                break

        if not user_technique:
            user_technique = "iqr_method"  # Safe default
            logger.warning(f"No clean_data answer found in review_answers, using default: {user_technique}")

        # ============ Step 2: Get Data Characteristics ============
        data_profile = state.get("data_profile", {})
        algorithm_category = state.get("algorithm_category", "unknown")

        # Extract relevant data characteristics
        n_samples = data_profile.get("n_samples", original_shape[0])
        n_features = data_profile.get("n_features", original_shape[1])
        missing_percentage = data_profile.get("missing_percentage", 0.0)

        # Calculate outlier percentage for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        outlier_info = []
        for col in numeric_cols[:5]:  # Sample first 5 numeric columns
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            outlier_pct = (outliers / len(df)) * 100 if len(df) > 0 else 0
            outlier_info.append(f"{col}: {outlier_pct:.1f}% outliers")

        logger.info(f"Data characteristics: {n_samples} samples, {n_features} features, {len(numeric_cols)} numeric")
        logger.info(f"Outlier analysis: {', '.join(outlier_info)}")

        # ============ Step 3: Ask Bedrock for Optimal Parameters ============
        try:
            # Initialize Bedrock client
            bedrock_model_id = state.get("bedrock_model_id")
            aws_region = state.get("aws_region", "us-east-1")
            aws_access_key_id = state.get("aws_access_key_id")
            aws_secret_access_key = state.get("aws_secret_access_key")

            bedrock_client = BedrockClient(
                model_id=bedrock_model_id,
                aws_region=aws_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

            # Build prompt for Bedrock
            prompt = f"""You are an expert ML engineer selecting optimal data cleaning parameters.

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Samples: {n_samples}
- Features: {n_features}
- Numeric columns: {len(numeric_cols)}
- Missing values: {missing_percentage:.2f}%
- Outlier analysis: {', '.join(outlier_info) if outlier_info else 'No numeric columns'}

**Algorithm Context:**
- Predicted algorithm category: {algorithm_category}

**Available Technique Signatures:**
1. iqr_method(df, multiplier=1.5) - Remove outliers beyond Q1-multiplier*IQR or Q3+multiplier*IQR
2. z_score(df, threshold=3.0) - Remove outliers beyond threshold standard deviations
3. winsorization(df, lower_percentile=0.05, upper_percentile=0.95) - Cap outliers at percentiles
4. isolation_forest(df, contamination=0.1) - Detect outliers using Isolation Forest
5. dbscan(df, eps=0.5, min_samples=5) - Detect outliers using DBSCAN clustering
6. robust_scalers(df) - Apply RobustScaler (no parameters needed)
7. domain_clipping(df, min_val=None, max_val=None) - Clip values to domain-specific range
8. none - Skip outlier removal

**Task:**
Based on the user's choice "{user_technique}" and the data characteristics, return the OPTIMAL parameters for this cleaning technique.

**Important Guidelines:**
- For IQR: Use multiplier=1.5 (standard) to 3.0 (more lenient) based on outlier percentage
- For Z-score: Use threshold=2.5 to 3.5 based on data size and distribution
- For Winsorization: Use 0.01-0.05 for lower, 0.95-0.99 for upper percentile
- For Isolation Forest: contamination should match approximate outlier percentage (0.01-0.2)
- For DBSCAN: eps and min_samples depend on data density and size
- Consider algorithm requirements (tree models are robust to outliers)

**Required Output (JSON only, no other text):**
{{
    "technique": "{user_technique}",
    "parameters": {{"param1": value1, "param2": value2}},
    "reasoning": "Brief explanation of why these parameters are optimal"
}}

Return ONLY the JSON object, no additional text."""

            logger.info("Sending request to Bedrock for parameter selection...")
            bedrock_response = bedrock_client.invoke(
                prompt=prompt,
                temperature=0.2,  # Low for consistent parameter selection
                max_tokens=1000
            )

            logger.info(f"Bedrock response received ({bedrock_response.total_tokens} tokens)")

            # Parse JSON from response
            response_text = bedrock_response.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in Bedrock response")

            bedrock_decision = json.loads(json_match.group(0))
            technique_name = bedrock_decision.get("technique", user_technique)
            technique_params = bedrock_decision.get("parameters", {})
            reasoning = bedrock_decision.get("reasoning", "No reasoning provided")

            logger.info(f"✓ Bedrock selected parameters: {technique_params}")
            logger.info(f"✓ Reasoning: {reasoning}")

        except Exception as bedrock_error:
            logger.warning(f"Bedrock parameter selection failed: {bedrock_error}")
            logger.warning("Falling back to default parameters")
            technique_name = user_technique
            technique_params = {}
            reasoning = "Default parameters used due to Bedrock failure"

        # ============ Step 4: Remove Duplicates and All-NaN Rows ============
        duplicates_count = df.duplicated().sum()
        df = df.drop_duplicates()
        logger.info(f"Removed {duplicates_count} duplicate rows")

        all_nan_count = df.isnull().all(axis=1).sum()
        df = df.dropna(how='all')
        logger.info(f"Removed {all_nan_count} rows with all NaN values")

        # ============ Step 5: Execute Cleaning Technique with Bedrock Parameters ============
        rows_before = len(df)

        if technique_name in TECHNIQUES:
            technique_func = TECHNIQUES[technique_name]
            logger.info(f"Executing {technique_name} with Bedrock-selected parameters: {technique_params}")
            df = technique_func(df, **technique_params)
        elif technique_name == "none":
            logger.info(f"Skipping outlier removal (user choice or algorithm recommendation)")
        else:
            logger.warning(f"Unknown technique '{technique_name}', falling back to iqr_method")
            df = TECHNIQUES["iqr_method"](df, multiplier=1.5)
            technique_name = "iqr_method (fallback)"

        rows_after = len(df)
        outliers_removed = rows_before - rows_after

        # Reset index after row removals
        df = df.reset_index(drop=True)

        final_shape = df.shape
        total_removed = original_shape[0] - final_shape[0]

        logger.info(f"Data cleaning complete: {original_shape} → {final_shape}")
        logger.info(
            f"Total rows removed: {total_removed} "
            f"(duplicates: {duplicates_count}, all-NaN: {all_nan_count}, outliers: {outliers_removed})"
        )

        # ============ Step 6: MLflow Logging ============
        try:
            if mlflow.active_run():
                mlflow.log_param("algorithm_category", algorithm_category)
                mlflow.log_param("clean_data_technique", technique_name)
                mlflow.log_param("clean_data_user_choice", user_technique)
                mlflow.log_param("clean_data_bedrock_reasoning", reasoning)
                mlflow.log_params({f"clean_data_{k}": v for k, v in technique_params.items()})

                mlflow.log_metric("duplicates_removed", duplicates_count)
                mlflow.log_metric("all_nan_removed", all_nan_count)
                mlflow.log_metric("outliers_removed", outliers_removed)
                mlflow.log_metric("total_rows_removed", total_removed)
                mlflow.log_metric("original_rows", original_shape[0])
                mlflow.log_metric("final_rows", final_shape[0])

                logger.info("Logged data cleaning metrics to MLflow")
        except Exception as mlflow_error:
            logger.warning(f"Failed to log to MLflow: {mlflow_error}")

        # ============ Step 7: Update State ============
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["clean_data"] = {
            "technique": technique_name,
            "parameters": technique_params,
            "bedrock_reasoning": reasoning,
            "algorithm_context": algorithm_category,
            "rows_removed": outliers_removed
        }

        updated_state = update_state(
            state,
            cleaned_data=df,
            outliers_removed=outliers_removed,
            technique_metadata=technique_metadata,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        logger.error(f"Error in clean_data_node: {e}", exc_info=True)
        from core.state import add_error
        return add_error(state, node_name, e)
