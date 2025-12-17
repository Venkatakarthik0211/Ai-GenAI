"""Scale features node for ML Pipeline - LLM-Based Parameter Selection."""

import pandas as pd
import numpy as np
import mlflow
import logging
import json
import re
from typing import Dict, Any

from core.state import PipelineState, update_state, mark_node_completed
from .techniques.scale_features import TECHNIQUES
from utils.bedrock_client import BedrockClient

logger = logging.getLogger(__name__)


def scale_features_node(state: PipelineState) -> PipelineState:
    """
    Scale numerical features using LLM-based parameter selection.

    NEW ARCHITECTURE:
    1. Read user's answer from review_answers (which technique they chose)
    2. Analyze numeric columns (distribution, range, outliers, etc.)
    3. Send to Bedrock LLM: "User chose X, data has Y distribution, what parameters?"
    4. Bedrock returns optimal parameters in JSON format
    5. Execute Python scaling function with those parameters
    6. Store fitted scaler for transform phase
    7. Update state with scaled data

    Available Techniques (7):
    - none: Skip scaling (for tree models - scale-invariant)
    - standard_scaler: StandardScaler (z-score normalization)
    - minmax_scaler: MinMaxScaler (scale to [0, 1])
    - robust_scaler: RobustScaler (robust to outliers)
    - maxabs_scaler: MaxAbsScaler (scale by max abs value)
    - normalizer: Normalizer (normalize to unit norm)
    - quantile_transformer: QuantileTransformer (uniform/normal distribution)

    Args:
        state: Current pipeline state with cleaned_data, review_answers, data_profile

    Returns:
        Updated pipeline state with scaled features and scaler object
    """
    node_name = "scale_features"

    try:
        # Get cleaned data from previous node
        df = state.get("cleaned_data")
        if df is None:
            raise ValueError("cleaned_data not found in state. Ensure encode_features_node ran successfully.")

        df = df.copy()
        original_shape = df.shape

        # Identify numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        logger.info(f"Scaling features for data shape: {original_shape}, numeric columns: {len(numeric_columns)}")

        # ============ Step 1: Get User's Choice ============
        review_answers = state.get("review_answers", {})

        # Look for scale_features answer
        user_technique = None
        for key, value in review_answers.items():
            if "scale" in key.lower() or "scaling" in key.lower():
                user_technique = value
                logger.info(f"Found user's scaling choice in '{key}': {value}")
                break

        if not user_technique:
            user_technique = "standard_scaler"  # Safe default
            logger.warning(f"No scale_features answer found, using default: {user_technique}")

        # ============ Step 2: Analyze Numeric Columns ============
        data_profile = state.get("data_profile", {})
        algorithm_category = state.get("algorithm_category", "unknown")

        n_samples = data_profile.get("n_samples", original_shape[0])
        n_features = data_profile.get("n_features", original_shape[1])

        # Analyze distribution of numeric columns
        distribution_info = []
        for col in numeric_columns[:10]:  # Sample first 10 numeric columns
            col_min = df[col].min()
            col_max = df[col].max()
            col_mean = df[col].mean()
            col_std = df[col].std()
            col_range = col_max - col_min

            distribution_info.append(
                f"{col}: range=[{col_min:.2f}, {col_max:.2f}], "
                f"mean={col_mean:.2f}, std={col_std:.2f}"
            )

        logger.info(f"Distribution analysis for {len(numeric_columns)} numeric columns")
        logger.info(f"Sample distributions: {', '.join(distribution_info[:3]) if distribution_info else 'None'}")

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
            prompt = f"""You are an expert ML engineer selecting optimal feature scaling parameters.

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Samples: {n_samples}
- Features: {n_features}
- Numeric columns: {len(numeric_columns)}
- Sample distributions: {', '.join(distribution_info[:3]) if distribution_info else 'No numeric columns'}

**Algorithm Context:**
- Predicted algorithm category: {algorithm_category}

**Available Technique Signatures:**
1. none - Skip scaling (for tree models which are scale-invariant)
2. standard_scaler(df, numeric_columns=[]) - Z-score normalization (mean=0, std=1)
3. minmax_scaler(df, numeric_columns=[], feature_range=(0, 1)) - Scale to range
4. robust_scaler(df, numeric_columns=[]) - Robust to outliers (uses median, IQR)
5. maxabs_scaler(df, numeric_columns=[]) - Scale by maximum absolute value
6. normalizer(df, numeric_columns=[], norm="l2") - Normalize to unit norm (l1/l2/max)
7. quantile_transformer(df, numeric_columns=[], output_distribution="uniform", n_quantiles=1000) - Transform to uniform/normal distribution

**Task:**
Based on the user's choice "{user_technique}" and the data characteristics, return the OPTIMAL parameters.

**Important Guidelines:**
- For tree models (random_forest, xgboost, gradient_boosting): Recommend "none" - they're scale-invariant
- For linear models, neural networks: Scaling is CRITICAL - recommend standard_scaler or minmax_scaler
- For clustering: Scaling is CRITICAL - recommend standard_scaler or robust_scaler
- For data with outliers: Use robust_scaler
- For minmax_scaler: feature_range=(0, 1) is standard, but (-1, 1) works for neural networks
- For normalizer: norm="l2" (Euclidean) is standard, "l1" (Manhattan) for sparse data
- For quantile_transformer: output_distribution="uniform" or "normal", n_quantiles=min(1000, n_samples)

**Algorithm-Specific Recommendations:**
- linear_models: standard_scaler (assumes normally distributed)
- tree_models: none (scale-invariant, no scaling needed)
- neural_networks: minmax_scaler or standard_scaler (gradient descent works better with scaled data)
- clustering: standard_scaler or robust_scaler (distance-based, very sensitive to scale)
- ensemble: depends on base models

**Required Output (JSON only, no other text):**
{{
    "technique": "{user_technique}",
    "parameters": {{
        "numeric_columns": ["list", "of", "columns"],
        "feature_range": [0, 1],
        "other_param": value
    }},
    "reasoning": "Brief explanation of why these parameters are optimal"
}}

If user chose a technique that conflicts with algorithm requirements (e.g., scaling for tree models), you may suggest a better alternative.

Return ONLY the JSON object, no additional text."""

            logger.info("Sending request to Bedrock for parameter selection...")
            bedrock_response = bedrock_client.invoke(
                prompt=prompt,
                temperature=0.2,
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
            technique_params = {"numeric_columns": numeric_columns}
            reasoning = "Default parameters used due to Bedrock failure"

        # ============ Step 4: Execute Scaling Technique with Bedrock Parameters ============
        scaler = None

        if not numeric_columns:
            logger.info("No numeric columns to scale, skipping")
            technique_name = "none (no numeric columns)"
        elif technique_name == "none":
            logger.info(f"Skipping scaling (algorithm_category={algorithm_category}, likely scale-invariant)")
        elif technique_name in TECHNIQUES:
            # Add numeric_columns to params if not specified
            if "numeric_columns" not in technique_params:
                technique_params["numeric_columns"] = numeric_columns

            technique_func = TECHNIQUES[technique_name]
            logger.info(f"Executing {technique_name} with Bedrock-selected parameters: {technique_params}")

            # Execute scaling and get scaler object
            result = technique_func(df, **technique_params)

            # Handle return value (could be tuple or just df)
            if isinstance(result, tuple) and len(result) == 2:
                df, scaler = result
                logger.info(f"Scaler fitted and stored: {type(scaler).__name__}")
            else:
                df = result
                logger.info("Scaling applied (no scaler object returned)")

        else:
            logger.warning(f"Unknown technique '{technique_name}', falling back to standard_scaler")
            if numeric_columns:
                result = TECHNIQUES["standard_scaler"](df, numeric_columns=numeric_columns)
                if isinstance(result, tuple) and len(result) == 2:
                    df, scaler = result
                else:
                    df = result
                technique_name = "standard_scaler (fallback)"

        final_shape = df.shape

        logger.info(f"Feature scaling complete: {original_shape} → {final_shape}")

        # ============ Step 5: MLflow Logging ============
        try:
            if mlflow.active_run():
                mlflow.log_param("algorithm_category", algorithm_category)
                mlflow.log_param("scale_features_technique", technique_name)
                mlflow.log_param("scale_features_user_choice", user_technique)
                mlflow.log_param("scale_features_bedrock_reasoning", reasoning)
                mlflow.log_params({
                    f"scale_features_{k}": v
                    for k, v in technique_params.items()
                    if k != "numeric_columns"
                })

                mlflow.log_metric("numeric_columns_count", len(numeric_columns))
                mlflow.log_param("scaler_fitted", scaler is not None)

                logger.info("Logged feature scaling metrics to MLflow")
        except Exception as mlflow_error:
            logger.warning(f"Failed to log to MLflow: {mlflow_error}")

        # ============ Step 6: Update State ============
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["scale_features"] = {
            "technique": technique_name,
            "parameters": {k: v for k, v in technique_params.items() if k != "numeric_columns"},
            "bedrock_reasoning": reasoning,
            "algorithm_context": algorithm_category,
            "scaler_fitted": scaler is not None
        }

        updated_state = update_state(
            state,
            cleaned_data=df,
            scaler=scaler,
            technique_metadata=technique_metadata,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        logger.error(f"Error in scale_features_node: {e}", exc_info=True)
        from core.state import add_error
        return add_error(state, node_name, e)
