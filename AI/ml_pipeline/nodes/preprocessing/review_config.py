"""
Review Configuration Node (Two-Agent HITL System)

LangGraph node that executes AFTER load_data node.
Uses two sequential AI agents for algorithm-aware preprocessing review:
- Agent 1A: Predicts optimal algorithm category based on data characteristics
- Agent 1B: Generates algorithm-aware preprocessing questions (4-20 questions)

This node pauses the pipeline and waits for user confirmation before proceeding.

Architecture per PROMPT.md lines 1058-1187.
"""

import logging
from typing import Dict, Any
import mlflow

from agents.algorithm_category_predictor import AlgorithmCategoryPredictorAgent
from agents.preprocessing_question_generator import PreprocessingQuestionGeneratorAgent
from utils.review_storage import ReviewStorage, create_review_storage_from_env

logger = logging.getLogger(__name__)


def review_config_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate algorithm-aware review questions using two-agent system.

    This node implements the enhanced HITL architecture:
    1. Agent 1A predicts optimal algorithm category from data characteristics
    2. Agent 1B generates preprocessing questions tailored to that algorithm
    3. Stores questions in triple storage (MLflow + PostgreSQL + embedding)
    4. Updates pipeline state to "awaiting_review"
    5. Pipeline pauses - waits for user to answer via API

    Args:
        state: Pipeline state containing:
            - pipeline_config: Extracted configuration from Agent 0
            - config_confidence: Agent 0 confidence score
            - data_profile: Data profile from load_data node (REQUIRED)
            - user_prompt: Original user prompt
            - pipeline_run_id: Unique pipeline run identifier
            - mlflow_run_id: MLflow run ID
            - bedrock_model_id: Bedrock model ID to use
            - aws_region: AWS region
            - (optional) aws_access_key_id, aws_secret_access_key

    Returns:
        Updated state with:
            - agent_1a_result: Algorithm category prediction
            - agent_1b_result: Generated questions
            - review_questions: List of generated questions
            - review_status: "awaiting_review"
            - review_session_id: ID from review storage
            - completed_nodes: Updated with "review_config"

    Raises:
        ValueError: If required inputs missing
        Exception: If agent invocation fails
    """
    logger.info("="*80)
    logger.info("REVIEW CONFIG NODE: Starting Two-Agent HITL System")
    logger.info("="*80)

    # Extract inputs from state
    pipeline_config = state.get("pipeline_config", {})
    config_confidence = state.get("config_confidence", 0.0)
    config_reasoning = state.get("config_reasoning", {})
    config_assumptions = state.get("config_assumptions", [])
    config_warnings = state.get("config_warnings", [])
    data_profile = state.get("data_profile", {})
    user_prompt = state.get("user_prompt", "")
    pipeline_run_id = state.get("pipeline_run_id")
    mlflow_run_id = state.get("mlflow_run_id")
    mlflow_experiment_id = state.get("mlflow_experiment_id")

    # Bedrock configuration
    bedrock_model_id = state.get("bedrock_model_id")
    aws_region = state.get("aws_region", "us-east-1")
    aws_access_key_id = state.get("aws_access_key_id")
    aws_secret_access_key = state.get("aws_secret_access_key")
    bedrock_fallback_model_id = state.get("bedrock_fallback_model_id")

    # Validate required inputs
    if not pipeline_config:
        raise ValueError("pipeline_config is required for review generation")
    if not data_profile:
        raise ValueError("data_profile is required for review generation")
    if not bedrock_model_id:
        raise ValueError("bedrock_model_id is required for review generation")

    logger.info(f"Pipeline Run ID: {pipeline_run_id}")
    logger.info(f"Agent 0 Confidence: {config_confidence:.2f}")
    logger.info(f"Config Warnings: {len(config_warnings)}")

    # ============================================================================
    # STEP 1: Agent 1A - Predict Algorithm Category
    # ============================================================================
    logger.info("="*80)
    logger.info("STEP 1: Agent 1A - Algorithm Category Prediction")
    logger.info("="*80)

    try:
        # Initialize Agent 1A
        agent_1a = AlgorithmCategoryPredictorAgent(
            bedrock_model_id=bedrock_model_id,
            aws_region=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            fallback_model_id=bedrock_fallback_model_id,
            temperature=0.2,  # Low for consistent predictions
            max_tokens=2000
        )

        # Build context for Agent 1A from data_profile
        n_samples = data_profile.get("n_samples", 0)
        n_features = data_profile.get("n_features", 0)
        target_type = pipeline_config.get("analysis_type", "classification")

        # Extract feature types
        feature_names = data_profile.get("feature_names", [])
        numeric_features = [f for f in feature_names if data_profile.get("feature_types", {}).get(f) in ["int64", "float64"]]
        categorical_features = [f for f in feature_names if data_profile.get("feature_types", {}).get(f) == "object"]

        feature_types = {
            "numeric_count": len(numeric_features),
            "categorical_count": len(categorical_features),
            "high_cardinality_count": 0  # TODO: Calculate from data_profile
        }

        # Get class distribution if classification
        class_distribution = data_profile.get("target_distribution", {})
        dataset_size_mb = n_samples * n_features * 8 / (1024 * 1024)  # Rough estimate

        # Data characteristics
        data_characteristics = {
            "missing_percentage": data_profile.get("missing_percentage", 0.0),
            "duplicate_percentage": data_profile.get("duplicate_percentage", 0.0),
            "outlier_percentage": 0.0,  # TODO: Calculate
            "feature_correlation_max": 0.0  # TODO: Calculate
        }

        logger.info(f"Invoking Agent 1A with: {n_samples} samples, {n_features} features, type={target_type}")

        # Invoke Agent 1A
        agent_1a_result = agent_1a.predict_category(
            n_samples=n_samples,
            n_features=n_features,
            target_type=target_type,
            feature_types=feature_types,
            class_distribution=class_distribution if target_type == "classification" else None,
            dataset_size_mb=dataset_size_mb,
            data_characteristics=data_characteristics
        )

        algorithm_category = agent_1a_result.get("algorithm_category", "tree_models")
        agent_1a_confidence = agent_1a_result.get("confidence", 0.0)
        recommended_algorithms = agent_1a_result.get("recommended_algorithms", [])

        logger.info(f"✓ Agent 1A Result:")
        logger.info(f"  Algorithm Category: {algorithm_category}")
        logger.info(f"  Confidence: {agent_1a_confidence:.2f}")
        logger.info(f"  Recommended Algorithms: {recommended_algorithms}")

    except Exception as e:
        logger.error(f"Agent 1A failed: {e}", exc_info=True)
        logger.warning("Using default algorithm category: tree_models")

        # Use safe default
        algorithm_category = "tree_models"
        agent_1a_confidence = 0.50
        recommended_algorithms = ["Random Forest", "XGBoost", "Gradient Boosting"]
        agent_1a_result = {
            "algorithm_category": algorithm_category,
            "confidence": agent_1a_confidence,
            "reasoning": "Default fallback due to Agent 1A failure",
            "recommended_algorithms": recommended_algorithms,
            "preprocessing_priorities": {
                "clean_data": "optional",
                "handle_missing": "required",
                "encode_features": "required",
                "scale_features": "optional"
            }
        }

    # ============================================================================
    # STEP 2: Agent 1B - Generate Algorithm-Aware Questions
    # ============================================================================
    logger.info("="*80)
    logger.info("STEP 2: Agent 1B - Algorithm-Aware Question Generation")
    logger.info("="*80)

    try:
        # Initialize Agent 1B
        agent_1b = PreprocessingQuestionGeneratorAgent(
            bedrock_model_id=bedrock_model_id,
            aws_region=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            fallback_model_id=bedrock_fallback_model_id,
            temperature=0.3,  # Slightly creative for question generation
            max_tokens=4096
        )

        # Build context for Agent 1B
        context = {
            "user_prompt": user_prompt,
            "extracted_config": pipeline_config,
            "agent0_confidence": config_confidence,
            "config_reasoning": config_reasoning,
            "config_assumptions": config_assumptions,
            "config_warnings": config_warnings,
            "data_profile": data_profile,
            # NEW: Algorithm category from Agent 1A
            "algorithm_category": algorithm_category,
            "agent_1a_confidence": agent_1a_confidence,
            "recommended_algorithms": recommended_algorithms,
            "preprocessing_priorities": agent_1a_result.get("preprocessing_priorities", {})
        }

        logger.info(f"Invoking Agent 1B with algorithm_category={algorithm_category}")

        # Invoke Agent 1B
        result = agent_1b.invoke(context=context)

        # Extract decision from result
        decision = result.get("decision", {})
        questions = decision.get("questions", [])
        summary = decision.get("summary", "")
        recommendation = decision.get("recommendation", "Review configuration carefully")

        logger.info(f"✓ Agent 1B generated {len(questions)} algorithm-aware questions")
        logger.info(f"Summary: {summary}")
        logger.info(f"Recommendation: {recommendation}")

        # Log questions by preprocessing step
        questions_by_step = {}
        for q in questions:
            step = q.get("preprocessing_step", "general")
            questions_by_step.setdefault(step, []).append(q)

        for step, step_questions in questions_by_step.items():
            logger.info(f"  {step}: {len(step_questions)} questions")

    except Exception as e:
        logger.error(f"Agent 1B failed: {e}", exc_info=True)
        logger.warning("Using fallback questions")

        # Use fallback
        result = agent_1b.get_default_decision(context)
        questions = result.get("questions", [])
        summary = result.get("summary", "")
        recommendation = result.get("recommendation", "Review configuration carefully")

    # ============================================================================
    # STEP 3: Store Review Session in PostgreSQL + MLflow
    # ============================================================================
    logger.info("="*80)
    logger.info("STEP 3: Storing review session to PostgreSQL and MLflow")
    logger.info("="*80)

    try:
        review_storage = create_review_storage_from_env()

        review_session_id = review_storage.save_review_session(
            pipeline_run_id=pipeline_run_id,
            questions=questions,
            user_prompt=user_prompt,
            extracted_config=pipeline_config,
            data_profile=data_profile,
            agent0_confidence=config_confidence,
            mlflow_run_id=mlflow_run_id,
            mlflow_experiment_id=mlflow_experiment_id,
            bedrock_model_id=bedrock_model_id,
            bedrock_tokens_used=result.get("tokens"),
            question_generation_prompt=result.get("prompt"),
            bedrock_response=result.get("response"),
            generation_success=True
        )

        logger.info(f"✓ Review session stored (ID: {review_session_id})")
        review_storage.close()

    except Exception as storage_error:
        logger.error(f"Failed to store review session: {storage_error}")
        review_session_id = None

    # ============================================================================
    # STEP 4: Log to MLflow
    # ============================================================================
    logger.info("STEP 4: Logging to MLflow...")

    try:
        if mlflow.active_run():
            # Log Agent 1A results
            mlflow.log_param("agent_1a_algorithm_category", algorithm_category)
            mlflow.log_metric("agent_1a_confidence", agent_1a_confidence)
            mlflow.log_param("agent_1a_recommended_algorithms", str(recommended_algorithms))

            # Log Agent 1B results
            mlflow.log_param("agent_1b_questions_count", len(questions))
            mlflow.log_param("review_recommendation", recommendation)
            mlflow.log_text(summary, "review/summary.txt")

            # Log questions
            for i, q in enumerate(questions, 1):
                mlflow.log_param(f"review_q{i}_priority", q.get("priority", "unknown"))
                mlflow.log_param(f"review_q{i}_step", q.get("preprocessing_step", "general"))

            logger.info("✓ Logged to MLflow")

    except Exception as mlflow_error:
        logger.warning(f"Failed to log to MLflow: {mlflow_error}")

    # ============================================================================
    # STEP 5: Update Pipeline State
    # ============================================================================
    logger.info("STEP 5: Updating pipeline state...")

    updated_state = state.copy()

    # Add Agent 1A results
    updated_state["agent_1a_result"] = agent_1a_result
    updated_state["algorithm_category"] = algorithm_category
    updated_state["agent_1a_confidence"] = agent_1a_confidence

    # Add Agent 1B results
    updated_state["agent_1b_result"] = {
        "questions": questions,
        "summary": summary,
        "recommendation": recommendation
    }
    updated_state["review_questions"] = questions
    updated_state["review_summary"] = summary
    updated_state["review_recommendation"] = recommendation
    updated_state["review_status"] = "awaiting_review"
    updated_state["review_session_id"] = review_session_id
    updated_state["current_node"] = "review_config"
    updated_state["pipeline_status"] = "awaiting_review"

    # Add to completed nodes
    completed_nodes = state.get("completed_nodes", [])
    if "review_config" not in completed_nodes:
        completed_nodes.append("review_config")
    updated_state["completed_nodes"] = completed_nodes

    logger.info("="*80)
    logger.info("REVIEW CONFIG NODE: Complete - Pipeline paused for user review")
    logger.info(f"Algorithm Category: {algorithm_category} (confidence: {agent_1a_confidence:.2f})")
    logger.info(f"Questions Generated: {len(questions)}")
    logger.info(f"Status: {updated_state['review_status']}")
    logger.info("="*80)

    return updated_state
