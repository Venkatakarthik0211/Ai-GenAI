"""Encode features node for ML Pipeline - LLM-Based Parameter Selection."""

import pandas as pd
import numpy as np
import mlflow
import logging
import json
import re
from typing import Dict, Any

from core.state import PipelineState, update_state, mark_node_completed
from .techniques.encode_features import TECHNIQUES
from utils.bedrock_client import BedrockClient

logger = logging.getLogger(__name__)


def encode_features_node(state: PipelineState) -> PipelineState:
    """
    Encode categorical features using LLM-based parameter selection.

    NEW ARCHITECTURE:
    1. Read user's answer from review_answers (which technique they chose)
    2. Analyze categorical columns (cardinality, unique values, etc.)
    3. Send to Bedrock LLM: "User chose X, columns have Y cardinality, what parameters?"
    4. Bedrock returns optimal parameters + high-cardinality strategy
    5. Execute Python encoding function with those parameters
    6. Update state with encoded data

    Available Techniques (7):
    - one_hot: One-hot encoding (binary columns)
    - label_encoding: Label encoding (ordinal integers)
    - target_encoding: Target/mean encoding
    - frequency_encoding: Frequency-based encoding
    - binary_encoding: Binary encoding
    - hash_encoding: Hash encoding
    - embeddings: Learned embeddings (for neural networks)

    Args:
        state: Current pipeline state with cleaned_data, review_answers, data_profile

    Returns:
        Updated pipeline state with encoded features
    """
    node_name = "encode_features"

    try:
        # Get cleaned data from previous node
        df = state.get("cleaned_data")
        if df is None:
            raise ValueError("cleaned_data not found in state. Ensure handle_missing_node ran successfully.")

        df = df.copy()
        original_shape = df.shape

        # Identify categorical columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        logger.info(f"Encoding features for data shape: {original_shape}, categorical columns: {len(categorical_columns)}")

        # ============ Step 1: Get User's Choice ============
        review_answers = state.get("review_answers", {})

        # Look for encode_features answer
        user_technique = None
        for key, value in review_answers.items():
            if "encode" in key.lower():
                user_technique = value
                logger.info(f"Found user's encoding choice in '{key}': {value}")
                break

        if not user_technique:
            user_technique = "one_hot"  # Safe default
            logger.warning(f"No encode_features answer found, using default: {user_technique}")

        # ============ Step 2: Analyze Categorical Columns ============
        data_profile = state.get("data_profile", {})
        algorithm_category = state.get("algorithm_category", "unknown")
        target_column = state.get("target_column")

        n_samples = data_profile.get("n_samples", original_shape[0])
        n_features = data_profile.get("n_features", original_shape[1])

        # Analyze cardinality of categorical columns
        cardinality_info = []
        high_cardinality_cols = []
        low_cardinality_cols = []

        for col in categorical_columns[:10]:  # Sample first 10 categorical columns
            n_unique = df[col].nunique()
            cardinality_pct = (n_unique / len(df)) * 100 if len(df) > 0 else 0

            if n_unique > 10:  # High cardinality threshold
                high_cardinality_cols.append(col)
                cardinality_info.append(f"{col}: {n_unique} unique ({cardinality_pct:.1f}%)")
            else:
                low_cardinality_cols.append(col)
                cardinality_info.append(f"{col}: {n_unique} unique")

        logger.info(f"Cardinality analysis: {len(high_cardinality_cols)} high-cardinality, {len(low_cardinality_cols)} low-cardinality")
        logger.info(f"Columns: {', '.join(cardinality_info) if cardinality_info else 'None'}")

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
            prompt = f"""You are an expert ML engineer selecting optimal categorical encoding parameters.

**User's Choice:**
- Technique selected: {user_technique}

**Data Characteristics:**
- Samples: {n_samples}
- Features: {n_features}
- Categorical columns: {len(categorical_columns)}
- Low-cardinality (<10 unique): {len(low_cardinality_cols)} columns
- High-cardinality (>10 unique): {len(high_cardinality_cols)} columns
- Cardinality details: {', '.join(cardinality_info) if cardinality_info else 'No categorical columns'}
- Target column: {target_column if target_column else 'None (clustering task)'}

**Algorithm Context:**
- Predicted algorithm category: {algorithm_category}

**Available Technique Signatures:**
1. one_hot(df, categorical_columns=[], drop_first=True) - One-hot encoding
2. label_encoding(df, categorical_columns=[]) - Label encoding (ordinal integers)
3. target_encoding(df, target_column="target", categorical_columns=[], smoothing=1.0) - Target encoding
4. frequency_encoding(df, categorical_columns=[]) - Frequency-based encoding
5. binary_encoding(df, categorical_columns=[]) - Binary encoding (compact)
6. hash_encoding(df, categorical_columns=[], n_components=8) - Hash encoding
7. embeddings(df, categorical_columns=[], embedding_dim=10) - Learned embeddings

**Task:**
Based on the user's choice "{user_technique}" and the cardinality analysis, return the OPTIMAL parameters.

**IMPORTANT - High-Cardinality Handling:**
If there are high-cardinality columns (>10 unique values), you MUST specify which columns to encode differently:
- Low-cardinality columns: Apply user's chosen technique
- High-cardinality columns: Use frequency_encoding, hash_encoding, or target_encoding to avoid dimension explosion

**Guidelines:**
- For one_hot: drop_first=True to avoid multicollinearity (for linear models)
- For target_encoding: smoothing=1.0-10.0 based on sample size, requires target_column
- For hash_encoding: n_components=8-32 based on cardinality
- For embeddings: embedding_dim=min(50, unique_values//2) for neural networks
- If user chose one_hot but there are high-cardinality columns, recommend alternative for those columns

**Required Output (JSON only, no other text):**
{{
    "technique": "{user_technique}",
    "parameters": {{
        "categorical_columns": ["list", "of", "columns"],
        "drop_first": true,
        "other_param": value
    }},
    "high_cardinality_strategy": {{
        "technique": "frequency_encoding",
        "columns": ["high_card_col1", "high_card_col2"],
        "reasoning": "Explanation"
    }},
    "reasoning": "Brief explanation of why these parameters are optimal"
}}

If no high-cardinality columns or user's technique handles them, set high_cardinality_strategy to null.

Return ONLY the JSON object, no additional text."""

            logger.info("Sending request to Bedrock for parameter selection...")
            bedrock_response = bedrock_client.invoke(
                prompt=prompt,
                temperature=0.2,
                max_tokens=1500
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
            high_card_strategy = bedrock_decision.get("high_cardinality_strategy")
            reasoning = bedrock_decision.get("reasoning", "No reasoning provided")

            logger.info(f"✓ Bedrock selected parameters: {technique_params}")
            if high_card_strategy:
                logger.info(f"✓ High-cardinality strategy: {high_card_strategy['technique']} for {len(high_card_strategy.get('columns', []))} columns")
            logger.info(f"✓ Reasoning: {reasoning}")

        except Exception as bedrock_error:
            logger.warning(f"Bedrock parameter selection failed: {bedrock_error}")
            logger.warning("Falling back to default parameters")
            technique_name = user_technique
            technique_params = {"categorical_columns": categorical_columns}
            high_card_strategy = None
            reasoning = "Default parameters used due to Bedrock failure"

        # ============ Step 4: Execute Encoding Technique with Bedrock Parameters ============
        if not categorical_columns:
            logger.info("No categorical columns to encode, skipping")
            technique_name = "none (no categorical columns)"
        else:
            # Add categorical_columns to params if not specified
            if "categorical_columns" not in technique_params:
                technique_params["categorical_columns"] = categorical_columns

            # Handle high-cardinality columns separately if strategy provided
            if high_card_strategy and high_card_strategy.get("columns"):
                high_card_cols = high_card_strategy.get("columns", [])
                high_card_technique = high_card_strategy.get("technique", "frequency_encoding")

                # Encode high-cardinality columns first
                if high_card_technique in TECHNIQUES:
                    logger.info(f"Encoding {len(high_card_cols)} high-cardinality columns with {high_card_technique}")
                    high_card_func = TECHNIQUES[high_card_technique]
                    df = high_card_func(df, categorical_columns=high_card_cols)

                # Remove high-cardinality columns from main encoding
                remaining_cols = [c for c in categorical_columns if c not in high_card_cols]
                technique_params["categorical_columns"] = remaining_cols
                logger.info(f"Encoding {len(remaining_cols)} remaining columns with {technique_name}")

            # Add target_column for target_encoding
            if technique_name == "target_encoding":
                if target_column:
                    technique_params["target_column"] = target_column
                else:
                    logger.warning("target_encoding requires target_column, falling back to one_hot")
                    technique_name = "one_hot"

            # Execute main encoding technique
            if technique_name in TECHNIQUES and technique_params.get("categorical_columns"):
                technique_func = TECHNIQUES[technique_name]
                logger.info(f"Executing {technique_name} with Bedrock-selected parameters: {technique_params}")
                df = technique_func(df, **technique_params)
            elif technique_name == "none (no categorical columns)":
                pass  # Already handled
            else:
                logger.warning(f"Unknown technique '{technique_name}' or no columns to encode, falling back to one_hot")
                if categorical_columns:
                    df = TECHNIQUES["one_hot"](df, categorical_columns=categorical_columns)
                    technique_name = "one_hot (fallback)"

        final_shape = df.shape
        new_columns_created = final_shape[1] - original_shape[1]

        logger.info(f"Feature encoding complete: {original_shape} → {final_shape}, new columns: {new_columns_created}")

        # ============ Step 5: MLflow Logging ============
        try:
            if mlflow.active_run():
                mlflow.log_param("algorithm_category", algorithm_category)
                mlflow.log_param("encode_features_technique", technique_name)
                mlflow.log_param("encode_features_user_choice", user_technique)
                mlflow.log_param("encode_features_bedrock_reasoning", reasoning)
                if high_card_strategy:
                    mlflow.log_param("high_cardinality_technique", high_card_strategy.get("technique"))
                    mlflow.log_param("high_cardinality_columns", len(high_card_strategy.get("columns", [])))

                mlflow.log_metric("categorical_columns_count", len(categorical_columns))
                mlflow.log_metric("new_columns_created", new_columns_created)
                mlflow.log_metric("final_column_count", final_shape[1])

                logger.info("Logged feature encoding metrics to MLflow")
        except Exception as mlflow_error:
            logger.warning(f"Failed to log to MLflow: {mlflow_error}")

        # ============ Step 6: Update State ============
        technique_metadata = state.get("technique_metadata", {})
        technique_metadata["encode_features"] = {
            "technique": technique_name,
            "parameters": {k: v for k, v in technique_params.items() if k != "categorical_columns"},
            "high_cardinality_strategy": high_card_strategy,
            "bedrock_reasoning": reasoning,
            "algorithm_context": algorithm_category,
            "new_columns_created": new_columns_created
        }

        updated_state = update_state(
            state,
            cleaned_data=df,
            categorical_columns_encoded=len(categorical_columns),
            technique_metadata=technique_metadata,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        logger.error(f"Error in encode_features_node: {e}", exc_info=True)
        from core.state import add_error
        return add_error(state, node_name, e)
