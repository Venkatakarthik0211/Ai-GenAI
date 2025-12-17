"""Handle missing values node for ML Pipeline - LLM-Based Parameter Selection."""

import pandas as pd
import numpy as np
import mlflow
import logging
import json
import re
from typing import Dict, Any

from core.state import PipelineState, update_state, mark_node_completed
from .techniques.handle_missing import TECHNIQUES
from utils.bedrock_client import BedrockClient

logger = logging.getLogger(__name__)


def handle_missing_node(state: PipelineState) -> PipelineState:
    """
    Handle missing values using LLM-based parameter selection.

    NEW ARCHITECTURE:
    1. Read user's answer from review_answers (which technique they chose)
    2. Get data characteristics (missing %, distribution, etc.)
    3. Send to Bedrock LLM: "User chose X, data has Y% missing, what parameters?"
    4. Bedrock returns optimal parameters in JSON format
    5. Execute Python imputation function with those parameters
    6. Update state with imputed data

    Available Techniques (7):
    - drop_rows: Drop rows with missing values
    - simple_imputation: Mean/median/mode imputation
    - knn_imputation: KNN-based imputation
    - mice: Multiple Imputation by Chained Equations
    - domain_specific: Domain-specific imputation rules
    - forward_fill: Forward fill (for time series)
    - interpolation: Linear/polynomial interpolation

    Args:
        state: Current pipeline state with cleaned_data, review_answers, data_profile

    Returns:
        Updated pipeline state with imputed data
    """
    node_name = "handle_missing"

    try:
        # Get cleaned data from previous node
        df = state.get("cleaned_data")
        if df is None:
            raise ValueError("cleaned_data not found in state. Ensure clean_data_node ran successfully.")

        df = df.copy()
        original_shape = df.shape
        missing_before = df.isnull().sum().sum()

        logger.info(f"Handling missing values for data shape: {original_shape}, missing values: {missing_before}")

        # ============ Step 1: Get User's Choice ============
        review_answers = state.get("review_answers", {})

        # Look for handle_missing answer
        user_technique = None
        for key, value in review_answers.items():
            if "handle_missing" in key.lower() or "missing" in key.lower():
                user_technique = value
                logger.info(f"Found user's missing value handling choice in '{key}': {value}")
                break

        if not user_technique:
            user_technique = "simple_imputation"  # Safe default
            logger.warning(f"No handle_missing answer found, using default: {user_technique}")

        # ============ Step 2: Get Data Characteristics ============
        data_profile = state.get("data_profile", {})
        algorithm_category = state.get("algorithm_category", "unknown")

        n_samples = data_profile.get("n_samples", original_shape[0])
        n_features = data_profile.get("n_features", original_shape[1])
        missing_percentage = (missing_before / (n_samples * n_features) * 100) if n_samples * n_features > 0 else 0

        # Analyze missing patterns per column
        missing_info = []
        for col in df.columns[:10]:  # Sample first 10 columns
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(df)) * 100
                col_type = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "categorical"
                missing_info.append(f"{col} ({col_type}): {missing_pct:.1f}% missing")

        logger.info(f"Missing value analysis: {missing_percentage:.2f}% overall")
        logger.info(f"Columns with missing: {', '.join(missing_info) if missing_info else 'None'}")

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
            prompt = f"""You are an expert ML engineer selecting optimal missing value imputation parameters.

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Samples: {n_samples}
- Features: {n_features}
- Overall missing: {missing_percentage:.2f}%
- Columns with missing values: {', '.join(missing_info) if missing_info else 'No missing values'}

**Algorithm Context:**
- Predicted algorithm category: {algorithm_category}

**Available Technique Signatures:**
1. drop_rows(df, threshold=0.5) - Drop rows with >threshold fraction of missing values
2. simple_imputation(df, strategy="mean") - Simple imputation (mean/median/most_frequent)
3. knn_imputation(df, n_neighbors=5) - KNN-based imputation
4. mice(df, max_iter=10) - Multiple Imputation by Chained Equations
5. domain_specific(df, rules={{}}) - Domain-specific rules (requires custom rules dict)
6. forward_fill(df) - Forward fill for time series (no parameters)
7. interpolation(df, method="linear") - Interpolation (linear/polynomial/spline)

**Task:**
Based on the user's choice "{user_technique}" and the data characteristics, return the OPTIMAL parameters.

**Important Guidelines:**
- For simple_imputation: Use "mean" for numeric, "most_frequent" for categorical
- For knn_imputation: n_neighbors=3-10 based on data size and missing percentage
- For mice: max_iter=5-20 based on missing percentage (higher for more missing)
- For drop_rows: threshold=0.3-0.7 based on how much missing is acceptable
- For interpolation: "linear" for smooth data, "polynomial" for curves
- Consider algorithm requirements and data type distribution

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
            technique_params = {}
            reasoning = "Default parameters used due to Bedrock failure"

        # ============ Step 4: Execute Imputation Technique with Bedrock Parameters ============
        if missing_before == 0:
            logger.info("No missing values to handle, skipping imputation")
            technique_name = "none (no missing values)"
        elif technique_name in TECHNIQUES:
            technique_func = TECHNIQUES[technique_name]
            logger.info(f"Executing {technique_name} with Bedrock-selected parameters: {technique_params}")
            df = technique_func(df, **technique_params)
        else:
            logger.warning(f"Unknown technique '{technique_name}', falling back to simple_imputation")
            df = TECHNIQUES["simple_imputation"](df, strategy="mean")
            technique_name = "simple_imputation (fallback)"

        missing_after = df.isnull().sum().sum()
        missing_handled = missing_before - missing_after

        logger.info(f"Missing value handling complete: {missing_before} → {missing_after} missing values")
        logger.info(f"Handled {missing_handled} missing values ({missing_handled / missing_before * 100:.1f}%)" if missing_before > 0 else "No missing values")

        # ============ Step 5: MLflow Logging ============
        try:
            if mlflow.active_run():
                mlflow.log_param("algorithm_category", algorithm_category)
                mlflow.log_param("handle_missing_technique", technique_name)
                mlflow.log_param("handle_missing_user_choice", user_technique)
                mlflow.log_param("handle_missing_bedrock_reasoning", reasoning)
                mlflow.log_params({f"handle_missing_{k}": v for k, v in technique_params.items()})

                mlflow.log_metric("missing_values_before", missing_before)
                mlflow.log_metric("missing_values_after", missing_after)
                mlflow.log_metric("missing_values_handled", missing_handled)
                mlflow.log_metric("missing_percentage_before", missing_percentage)

                logger.info("Logged missing value handling metrics to MLflow")
        except Exception as mlflow_error:
            logger.warning(f"Failed to log to MLflow: {mlflow_error}")

        # ============ Step 6: Update State ============
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["handle_missing"] = {
            "technique": technique_name,
            "parameters": technique_params,
            "bedrock_reasoning": reasoning,
            "algorithm_context": algorithm_category,
            "missing_handled": missing_handled
        }

        updated_state = update_state(
            state,
            cleaned_data=df,
            missing_values_handled=missing_handled,
            technique_metadata=technique_metadata,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        logger.error(f"Error in handle_missing_node: {e}", exc_info=True)
        from core.state import add_error
        return add_error(state, node_name, e)
