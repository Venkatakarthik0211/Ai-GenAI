"""
Analyze Prompt Node (Agent 0 Invocation)

LangGraph node that executes BEFORE load_data node.
Extracts ML pipeline configuration from natural language user prompts using AWS Bedrock.

This is the entry point of the pipeline for natural language configuration.
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd

from agents.config_extraction import ConfigExtractionAgent
from utils.prompt_storage import PromptStorage, PromptStorageError

logger = logging.getLogger(__name__)


def analyze_prompt_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze user prompt and extract pipeline configuration using AWS Bedrock.

    This node:
    1. Receives user_prompt and data_path from user
    2. Performs quick data peek (first 100 rows) to get column names and dtypes
    3. Invokes ConfigExtraction Agent (Agent 0) with context
    4. Extracts configuration from natural language
    5. Validates confidence threshold (>= 70%)
    6. Stores prompt in triple storage (MLflow + PostgreSQL + MinIO/S3)
    7. Updates pipeline_config in state with extracted values
    8. Logs extraction metadata to MLflow

    Args:
        state: Pipeline state containing:
            - user_prompt: Natural language description from user
            - data_path: Path to data file
            - bedrock_model_id: Bedrock model ID to use
            - aws_region: AWS region
            - aws_access_key_id: Optional AWS access key
            - aws_secret_access_key: Optional AWS secret key
            - bedrock_fallback_model_id: Optional fallback model ID
            - confidence_threshold: Minimum confidence (default 0.70)
            - user_hints: Optional dict with user-provided hints
            - pipeline_run_id: Unique pipeline run identifier
            - mlflow_run_id: MLflow run ID (if already started)

    Returns:
        Updated state with:
            - pipeline_config: Extracted configuration dict
            - config_confidence: Confidence score
            - config_reasoning: Reasoning for extraction
            - config_assumptions: List of assumptions made
            - config_warnings: List of warnings
            - prompt_storage_id: ID from prompt storage system

    Raises:
        ValueError: If confidence below threshold or validation fails
        FileNotFoundError: If data file not found
        Exception: For other errors (Bedrock access, parsing, etc.)
    """
    logger.info("="*80)
    logger.info("ANALYZE PROMPT NODE: Starting configuration extraction")
    logger.info("="*80)

    # Extract inputs from state
    user_prompt = state.get("user_prompt")
    data_path = state.get("data_path")
    bedrock_model_id = state.get("bedrock_model_id")
    aws_region = state.get("aws_region", "us-east-1")
    aws_access_key_id = state.get("aws_access_key_id")
    aws_secret_access_key = state.get("aws_secret_access_key")
    bedrock_fallback_model_id = state.get("bedrock_fallback_model_id")
    confidence_threshold = state.get("confidence_threshold", 0.70)
    user_hints = state.get("user_hints", {})
    pipeline_run_id = state.get("pipeline_run_id")

    # Validate required inputs
    if not user_prompt:
        raise ValueError("user_prompt is required for configuration extraction")
    if not data_path:
        raise ValueError("data_path is required for configuration extraction")
    if not bedrock_model_id:
        raise ValueError("bedrock_model_id is required for configuration extraction")

    logger.info(f"User prompt: {user_prompt[:100]}...")
    logger.info(f"Data path: {data_path}")
    logger.info(f"Bedrock model: {bedrock_model_id}")
    logger.info(f"Confidence threshold: {confidence_threshold}")

    # Step 1: Quick data peek to get column names and dtypes
    logger.info("Step 1: Performing quick data peek (first 100 rows)...")

    try:
        # Read first 100 rows to get schema
        data_preview = pd.read_csv(data_path, nrows=100)
        logger.info(f"Data preview loaded: {data_preview.shape[0]} rows, {data_preview.shape[1]} columns")

        # Extract metadata
        available_columns = data_preview.columns.tolist()
        dtypes_dict = {col: str(dtype) for col, dtype in data_preview.dtypes.items()}

        dataset_preview = {
            "n_rows": len(data_preview),
            "n_columns": len(data_preview.columns),
            "dtypes": dtypes_dict
        }

        logger.info(f"Available columns ({len(available_columns)}): {', '.join(available_columns[:10])}...")

    except FileNotFoundError:
        logger.error(f"Data file not found: {data_path}")
        raise FileNotFoundError(f"Data file not found: {data_path}")
    except Exception as e:
        logger.error(f"Failed to read data preview: {e}")
        raise Exception(f"Failed to read data preview from {data_path}: {e}")

    # Step 2: Build context for ConfigExtraction Agent
    logger.info("Step 2: Building context for ConfigExtraction Agent...")

    context = {
        "user_prompt": user_prompt,
        "data_path": data_path,
        "available_columns": available_columns,
        "dataset_preview": dataset_preview,
        "user_hints": user_hints
    }

    logger.debug(f"Context keys: {list(context.keys())}")

    # Step 3: Initialize and invoke ConfigExtraction Agent
    logger.info("Step 3: Invoking ConfigExtraction Agent (Agent 0)...")

    try:
        agent = ConfigExtractionAgent(
            bedrock_model_id=bedrock_model_id,
            aws_region=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            fallback_model_id=bedrock_fallback_model_id,
            confidence_threshold=confidence_threshold,
            temperature=0.0,  # Deterministic extraction
            max_tokens=4096
        )

        # Build and log prompt before invocation
        prompt_to_send = agent.build_prompt(context)
        logger.info("="*80)
        logger.info("PROMPT SENT TO BEDROCK:")
        logger.info(prompt_to_send[:2000] + "..." if len(prompt_to_send) > 2000 else prompt_to_send)
        logger.info("="*80)

        # Invoke agent
        result = agent.invoke(context)

        logger.info("Agent invocation successful")
        logger.info(f"Model used: {result.get('model_id', 'unknown')}")
        logger.info(f"Tokens: {result.get('tokens', {}).get('total_tokens', 'unknown')}")

    except ValueError as e:
        # Confidence too low or validation failed
        logger.error(f"ConfigExtraction Agent validation error: {e}")
        raise ValueError(f"Configuration extraction failed: {e}")
    except Exception as e:
        # Bedrock access error, network error, etc.
        logger.error(f"ConfigExtraction Agent invocation error: {e}")
        error_msg = str(e)

        # Detect data mismatch errors (when task doesn't match dataset capabilities)
        data_mismatch_keywords = [
            "CRITICAL:",
            "dataset does NOT contain",
            "MAJOR LIMITATION:",
            "data does not match the stated task",
            "available data only supports",
            "requires time-series",
            "requires sequential"
        ]

        is_data_mismatch = any(keyword.lower() in error_msg.lower() for keyword in data_mismatch_keywords)

        if is_data_mismatch:
            # Extract key warning messages if available
            warnings_section = ""
            if "Warnings:" in error_msg:
                warnings_start = error_msg.find("Warnings:")
                warnings_section = error_msg[warnings_start:warnings_start+500] if warnings_start != -1 else ""

            # Build user-friendly error message
            friendly_error = (
                "⚠️ DATA MISMATCH ERROR\n\n"
                "Agent 0 detected that your task cannot be completed with the provided dataset. "
                "The dataset does not contain the necessary columns or data structure required for your task.\n\n"
                "WHAT WENT WRONG:\n"
                f"{warnings_section[:300] if warnings_section else 'The task requires data that is not present in your dataset.'}\n\n"
                "HOW TO FIX THIS:\n\n"
                "Option 1: Reframe Your Task\n"
                "   → Change your prompt to match what your dataset CAN do\n"
                "   → Example: Instead of 'predict next song in sequence', try:\n"
                "      • 'Predict track genre based on audio features'\n"
                "      • 'Cluster songs by similarity using audio features'\n"
                "      • 'Predict song popularity from audio characteristics'\n\n"
                "Option 2: Use Different Data\n"
                "   → Provide a dataset that includes the columns/structure your task needs\n"
                "   → For sequence prediction, you'd need: user_id, timestamp, listening history\n\n"
                "💡 TIP: Review the available columns in your dataset and choose a task that uses those columns."
            )
            raise Exception(friendly_error)
        else:
            # Generic error for other issues
            raise Exception(f"Failed to invoke ConfigExtraction Agent: {e}")

    # Step 4: Extract decision from result
    decision = result["decision"]
    agent_prompt = result["prompt"]
    agent_response = result["response"]
    model_id = result.get("model_id")
    tokens = result.get("tokens", {})

    # Log Bedrock raw response for debugging
    logger.info("="*80)
    logger.info("BEDROCK RAW RESPONSE:")
    logger.info(agent_response)
    logger.info("="*80)

    # Log extracted configuration
    logger.info("="*80)
    logger.info("CONFIGURATION EXTRACTED:")
    logger.info(f"  target_column: {decision['target_column']}")
    logger.info(f"  experiment_name: {decision['experiment_name']}")
    logger.info(f"  test_size: {decision['test_size']}")
    logger.info(f"  random_state: {decision['random_state']}")
    logger.info(f"  analysis_type: {decision['analysis_type']}")
    logger.info(f"  confidence: {decision['confidence']:.2f}")
    logger.info("="*80)

    # Validate target_column exists in available_columns
    # For unsupervised tasks (clustering, dimensionality_reduction, etc.), target_column can be None
    analysis_type = decision.get("analysis_type", "")
    unsupervised_tasks = ["clustering", "dimensionality_reduction", "association_rules", "anomaly_detection"]

    target_column = decision["target_column"]

    if analysis_type in unsupervised_tasks:
        # Unsupervised tasks: target_column should be None/null
        if target_column is not None and target_column != "null" and target_column != "None":
            logger.warning(
                f"⚠️ Unsupervised task '{analysis_type}' has target_column='{target_column}'. "
                f"Setting to None as unsupervised tasks don't require a target."
            )
            decision["target_column"] = None
    else:
        # Supervised tasks: target_column must exist in dataset
        if target_column is None or target_column == "null" or target_column == "None":
            raise ValueError(
                f"Supervised task '{analysis_type}' requires a target_column, but got: {target_column}"
            )
        if target_column not in available_columns:
            raise ValueError(
                f"Extracted target_column '{target_column}' not found in available columns. "
                f"Available: {available_columns}"
            )

    # Step 5: Store prompt in triple storage
    logger.info("Step 5: Storing prompt in triple storage...")

    prompt_storage_id = None

    # Check if prompt_storage instance is provided in state
    prompt_storage = state.get("prompt_storage")

    if prompt_storage:
        try:
            prompt_storage_id = prompt_storage.save_prompt(
                user_prompt=user_prompt,
                extracted_config=decision,
                pipeline_run_id=pipeline_run_id,
                mlflow_run_id=state.get("mlflow_run_id"),
                mlflow_experiment_id=state.get("mlflow_experiment_id"),
                confidence=decision["confidence"],
                reasoning=decision.get("reasoning"),
                assumptions=decision.get("assumptions", []),
                warnings=decision.get("warnings", []),
                bedrock_model_id=model_id,
                bedrock_tokens_used=tokens.get("total_tokens"),
                user_hints=user_hints,
                data_path=data_path,
                extraction_success=True,
                error_message=None
            )

            logger.info(f"✓ Prompt stored with ID: {prompt_storage_id}")

        except PromptStorageError as e:
            logger.warning(f"Failed to store prompt: {e}")
            # Don't fail the entire pipeline if storage fails
        except Exception as e:
            logger.warning(f"Unexpected error storing prompt: {e}")
    else:
        logger.info("Prompt storage skipped (no prompt_storage instance in state)")

    # Step 6: Log extraction metadata to MLflow (if run already started)
    logger.info("Step 6: Logging extraction metadata to MLflow...")

    if state.get("mlflow_run_id"):
        try:
            import mlflow

            mlflow.log_params({
                "user_prompt": user_prompt[:100],  # Truncate for param limit
                "bedrock_model_id": model_id,
                "config_confidence": decision["confidence"],
                "target_column": decision["target_column"],
                "analysis_type": decision["analysis_type"]
            })

            mlflow.log_metrics({
                "config_confidence": decision["confidence"],
                "config_extraction_input_tokens": tokens.get("input_tokens", 0),
                "config_extraction_output_tokens": tokens.get("output_tokens", 0)
            })

            # Log artifacts
            mlflow.log_text(user_prompt, "agents/user_prompt.txt")
            mlflow.log_text(agent_prompt, "agents/config_extraction_prompt.txt")
            mlflow.log_text(agent_response, "agents/config_extraction_response.txt")
            mlflow.log_dict(decision, "agents/config_extraction_decision.json")

            logger.info("✓ MLflow logging successful")

        except Exception as e:
            logger.warning(f"Failed to log to MLflow: {e}")
    else:
        logger.info("MLflow logging skipped (no mlflow_run_id in state)")

    # Step 7: Build pipeline_config from extracted values
    pipeline_config = {
        "data_path": data_path,
        "target_column": decision["target_column"],
        "experiment_name": decision["experiment_name"],
        "test_size": decision["test_size"],
        "random_state": decision["random_state"],
        "analysis_type": decision["analysis_type"],
        "recommended_algorithms": decision.get("recommended_algorithms", []),
        "algorithm_rationale": decision.get("algorithm_rationale", "")
    }

    # Step 8: Update state with extracted configuration
    logger.info("Step 8: Updating pipeline state with extracted configuration...")

    updated_state = {
        **state,
        "pipeline_config": pipeline_config,
        "config_confidence": decision["confidence"],
        "config_reasoning": decision["reasoning"],
        "config_assumptions": decision.get("assumptions", []),
        "config_warnings": decision.get("warnings", []),
        "prompt_storage_id": prompt_storage_id,
        "bedrock_tokens_used": tokens.get("total_tokens", 0),
        "bedrock_model_used": model_id
    }

    logger.info("="*80)
    logger.info("ANALYZE PROMPT NODE: Configuration extraction completed successfully")
    logger.info("="*80)

    return updated_state


def analyze_prompt_node_with_fallback(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for analyze_prompt_node with automatic fallback model retry.

    If primary model fails, automatically retries with fallback model.

    Args:
        state: Pipeline state (same as analyze_prompt_node)

    Returns:
        Updated state from successful extraction
    """
    try:
        # Try with primary model
        return analyze_prompt_node(state)
    except ValueError as e:
        # Confidence too low or validation error
        logger.warning(f"Primary model failed: {e}")

        # Check if fallback model is configured
        if not state.get("bedrock_fallback_model_id"):
            logger.error("No fallback model configured, cannot retry")
            raise

        logger.info("Retrying with fallback model...")

        # Update state to use fallback model
        fallback_state = {
            **state,
            "bedrock_model_id": state["bedrock_fallback_model_id"],
            "bedrock_fallback_model_id": None  # Prevent infinite fallback
        }

        # Retry with fallback
        return analyze_prompt_node(fallback_state)
