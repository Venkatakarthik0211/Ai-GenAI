"""LangGraph workflow construction for Enhanced ML Pipeline."""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from .state import PipelineState, is_classification_task
import logging

logger = logging.getLogger(__name__)


def create_pipeline_graph() -> StateGraph:
    """
    Create the complete LangGraph workflow for ML pipeline.

    Architecture with visible agent nodes and dual preprocessing paths:

    Entry → analyze_prompt (Agent 0) → load_data → agent_1a → agent_1b → await_review_approval
            ↑                                                                      ↓
            └─────────────────────── (if rejected) ←──────────────────────────────┴─────┐
                                                                                          ↓
                                                                               (if approved, route by learning_paradigm)
                                                                                          ↓
                                    ┌─────────────────────────────────────────────────────┴────────────────────────────────────┐
                                    ↓                                                                                          ↓
                            SUPERVISED PATH:                                                                          UNSUPERVISED PATH:
                            clean_data_supervised                                                                     clean_outliers_unsupervised
                                    ↓                                                                                          ↓
                            handle_missing_supervised                                                                 handle_missing_unsupervised
                                    ↓                                                                                          ↓
                            encode_features_supervised                                                                encode_features_unsupervised
                                    ↓                                                                                          ↓
                            scale_features_supervised                                                                 scale_features_unsupervised
                                    ↓                                                                                          ↓
                                    └─────────────────────────────────────────────────────┬────────────────────────────────────┘
                                                                                          ↓
                                                                            await_preprocessing_review → ...

    Key Features:
    - Agent 1A detects supervised vs unsupervised learning paradigm
    - Agent 1B generates paradigm-specific preprocessing questions
    - Two separate preprocessing subtrees (supervised/unsupervised)
    - Conditional routing based on learning_paradigm in state
    - Both paths converge at await_preprocessing_review checkpoint

    Returns:
        StateGraph configured with all nodes and edges
    """
    # Import node functions
    from nodes.preprocessing import (
        analyze_prompt_node,
        load_data_node,
    )
    # Import supervised preprocessing nodes
    from nodes.preprocessing.supervised import (
        clean_data_node as clean_data_supervised_node,
        handle_missing_node as handle_missing_supervised_node,
        encode_features_node as encode_features_supervised_node,
        scale_features_node as scale_features_supervised_node,
    )
    # Import unsupervised preprocessing nodes
    from nodes.preprocessing.unsupervised import (
        clean_outliers_node as clean_outliers_unsupervised_node,
        handle_missing_node as handle_missing_unsupervised_node,
        encode_features_node as encode_features_unsupervised_node,
        scale_features_node as scale_features_unsupervised_node,
    )
    from nodes.feature_engineering import (
        split_data_node,
        select_features_node,
    )
    from nodes.evaluation import evaluate_models_node
    from nodes.reporting import (
        generate_report_node,
        save_artifacts_node,
    )

    # Initialize state graph
    workflow = StateGraph(PipelineState)

    # ==================== Add Nodes ====================

    # Agent 0: Natural language config extraction (visible in graph)
    workflow.add_node("analyze_prompt", analyze_prompt_node)

    # Data loading
    workflow.add_node("load_data", load_data_node)

    # Agent 1A: Algorithm Category Predictor (visible as separate node)
    workflow.add_node("agent_1a", agent_1a_node)

    # Algorithm selection checkpoint (pause point for HITL - user selects ONE algorithm)
    workflow.add_node("await_algorithm_selection", await_algorithm_selection_node)

    # Agent 1B: Preprocessing Question Generator (visible as separate node)
    workflow.add_node("agent_1b", agent_1b_node)

    # Human review approval checkpoint (pause point for HITL)
    workflow.add_node("await_review_approval", await_review_approval_node)

    # Supervised preprocessing nodes
    workflow.add_node("clean_data_supervised", clean_data_supervised_node)
    workflow.add_node("handle_missing_supervised", handle_missing_supervised_node)
    workflow.add_node("encode_features_supervised", encode_features_supervised_node)
    workflow.add_node("scale_features_supervised", scale_features_supervised_node)

    # Unsupervised preprocessing nodes
    workflow.add_node("clean_outliers_unsupervised", clean_outliers_unsupervised_node)
    workflow.add_node("handle_missing_unsupervised", handle_missing_unsupervised_node)
    workflow.add_node("encode_features_unsupervised", encode_features_unsupervised_node)
    workflow.add_node("scale_features_unsupervised", scale_features_unsupervised_node)

    # Preprocessing review checkpoint (second HITL pause point)
    workflow.add_node("await_preprocessing_review", await_preprocessing_review_node)

    # Feature engineering nodes
    workflow.add_node("split_data", split_data_node)
    workflow.add_node("select_features", select_features_node)

    # AI Agent nodes (will be implemented in agents/ directory)
    workflow.add_node("algorithm_selection_agent", algorithm_selection_agent_node)

    # Algorithm nodes - these will be added conditionally based on task type
    # Classification nodes
    workflow.add_node("logistic_regression", logistic_regression_node)
    workflow.add_node("random_forest_classifier", random_forest_classifier_node)
    workflow.add_node("gradient_boosting_classifier", gradient_boosting_classifier_node)

    # Regression nodes
    workflow.add_node("linear_regression", linear_regression_node)
    workflow.add_node("ridge_regression", ridge_regression_node)
    workflow.add_node("random_forest_regressor", random_forest_regressor_node)

    # Model selection agent
    workflow.add_node("model_selection_agent", model_selection_agent_node)

    # Evaluation and reporting
    workflow.add_node("evaluate_models", evaluate_models_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("save_artifacts", save_artifacts_node)

    # ==================== Define Edges ====================

    # Agent flow: analyze_prompt → load_data → agent_1a → await_algorithm_selection → agent_1b → await_review
    workflow.add_edge("analyze_prompt", "load_data")
    workflow.add_edge("load_data", "agent_1a")
    workflow.add_edge("agent_1a", "await_algorithm_selection")

    # Conditional routing after algorithm selection (NEW HITL)
    # If rejected: loop back to Agent 0 with user feedback
    # If approved: continue to Agent 1B with selected algorithm
    workflow.add_conditional_edges(
        "await_algorithm_selection",
        route_after_algorithm_selection,
        {
            "retry_agent0": "analyze_prompt",  # Rejected - retry from Agent 0
            "continue_to_agent_1b": "agent_1b"  # Approved - continue with selected algorithm
        }
    )

    workflow.add_edge("agent_1b", "await_review_approval")

    # Conditional routing after human review
    # Routes to either supervised or unsupervised preprocessing based on learning_paradigm
    # If rejected: loop back to Agent 0 with user feedback
    workflow.add_conditional_edges(
        "await_review_approval",
        route_after_review_approval,
        {
            "retry_agent0": "analyze_prompt",  # Rejected - retry with feedback
            "supervised_preprocessing": "clean_data_supervised",  # Supervised path
            "unsupervised_preprocessing": "clean_outliers_unsupervised"  # Unsupervised path
        }
    )

    # Supervised preprocessing pipeline
    workflow.add_edge("clean_data_supervised", "handle_missing_supervised")
    workflow.add_edge("handle_missing_supervised", "encode_features_supervised")
    workflow.add_edge("encode_features_supervised", "scale_features_supervised")
    workflow.add_edge("scale_features_supervised", "await_preprocessing_review")

    # Unsupervised preprocessing pipeline
    workflow.add_edge("clean_outliers_unsupervised", "handle_missing_unsupervised")
    workflow.add_edge("handle_missing_unsupervised", "encode_features_unsupervised")
    workflow.add_edge("encode_features_unsupervised", "scale_features_unsupervised")
    workflow.add_edge("scale_features_unsupervised", "await_preprocessing_review")

    # Conditional routing after preprocessing review
    # If approved: continue to feature engineering
    # If rejected: loop back to appropriate preprocessing path based on learning_paradigm
    workflow.add_conditional_edges(
        "await_preprocessing_review",
        route_after_preprocessing_review,
        {
            "retry_supervised": "clean_data_supervised",  # Rejected - retry supervised preprocessing
            "retry_unsupervised": "clean_outliers_unsupervised",  # Rejected - retry unsupervised preprocessing
            "continue_pipeline": "split_data"  # Approved - continue to feature engineering
        }
    )

    workflow.add_edge("split_data", "select_features")

    # Agent-based algorithm selection
    workflow.add_edge("select_features", "algorithm_selection_agent")

    # Conditional routing to algorithm nodes based on agent decision
    workflow.add_conditional_edges(
        "algorithm_selection_agent",
        route_to_algorithms,
        {
            "logistic_regression": "logistic_regression",
            "random_forest": "random_forest_classifier",
            "gradient_boosting": "gradient_boosting_classifier",
            "linear_regression": "linear_regression",
            "ridge": "ridge_regression",
            "random_forest_regressor": "random_forest_regressor",
            "model_selection": "model_selection_agent",  # If no algorithms selected
        }
    )

    # All algorithm nodes converge to model selection agent
    for algo in ["logistic_regression", "random_forest_classifier", "gradient_boosting_classifier",
                 "linear_regression", "ridge_regression", "random_forest_regressor"]:
        workflow.add_edge(algo, "model_selection_agent")

    # After model selection, evaluate
    workflow.add_edge("model_selection_agent", "evaluate_models")
    workflow.add_edge("evaluate_models", "generate_report")
    workflow.add_edge("generate_report", "save_artifacts")

    # End the workflow
    workflow.add_edge("save_artifacts", END)

    # Set entry point - starts at analyze_prompt (Agent 0)
    workflow.set_entry_point("analyze_prompt")

    return workflow


def route_to_algorithms(state: PipelineState) -> str:
    """
    Route to appropriate algorithm nodes based on agent decision.

    Args:
        state: Current pipeline state with agent decisions

    Returns:
        Next node name to execute
    """
    selected_algorithms = state.get("selected_algorithms", [])

    if not selected_algorithms:
        # No algorithms selected, skip to model selection
        return "model_selection"

    # Return first algorithm (in a full implementation, this would handle parallel execution)
    return selected_algorithms[0]


def route_after_algorithm_selection(state: PipelineState) -> str:
    """
    Route after algorithm selection based on user decision.

    This function handles the first HITL decision point (after Agent 1A):
    - If user rejected: Loop back to analyze_prompt (Agent 0) with feedback
    - If user approved: Continue to Agent 1B with selected algorithm

    Args:
        state: Current pipeline state with algorithm selection decision

    Returns:
        "retry_agent0" if user rejected (loop back to Agent 0)
        "continue_to_agent_1b" if approved (continue with selected algorithm)
    """
    algorithm_selection_status = state.get("algorithm_selection_status", "pending")

    # If algorithm selection was rejected, retry from Agent 0 with user feedback
    if algorithm_selection_status == "rejected":
        logger.info("Algorithm selection rejected - restarting from Agent 0")
        return "retry_agent0"

    # Otherwise continue to Agent 1B with selected algorithm
    selected_algorithm = state.get("selected_algorithm")
    logger.info(f"Algorithm selection approved - continuing to Agent 1B with {selected_algorithm}")
    return "continue_to_agent_1b"


def route_after_review_approval(state: PipelineState) -> str:
    """
    Route after human review approval based on user decision and learning paradigm.

    This function handles the second HITL decision point (after Agent 1B):
    - If user rejected: Loop back to analyze_prompt (Agent 0) with feedback
    - If user approved: Route to supervised or unsupervised preprocessing based on learning_paradigm

    Args:
        state: Current pipeline state with review decision and learning_paradigm

    Returns:
        "retry_agent0" if user rejected (loop back to Agent 0)
        "supervised_preprocessing" if approved with supervised learning
        "unsupervised_preprocessing" if approved with unsupervised learning
    """
    review_status = state.get("review_status", "pending")
    learning_paradigm = state.get("learning_paradigm", "supervised")

    # If review was rejected, retry from Agent 0 with user feedback
    if review_status == "rejected":
        logger.info("Review rejected - restarting from Agent 0")
        return "retry_agent0"

    # Route to appropriate preprocessing path based on learning paradigm
    if learning_paradigm == "unsupervised":
        logger.info("Routing to unsupervised preprocessing path")
        return "unsupervised_preprocessing"
    else:
        logger.info("Routing to supervised preprocessing path")
        return "supervised_preprocessing"


def route_after_preprocessing_review(state: PipelineState) -> str:
    """
    Route after preprocessing review based on user decision and learning paradigm.

    This function handles the second HITL decision point:
    - If user rejected: Loop back to appropriate preprocessing path (supervised or unsupervised)
    - If user approved: Continue to split_data (feature engineering)

    Args:
        state: Current pipeline state with preprocessing review decision and learning_paradigm

    Returns:
        "retry_supervised" if user rejected supervised preprocessing
        "retry_unsupervised" if user rejected unsupervised preprocessing
        "continue_pipeline" if user approved (continue forward)
    """
    preprocessing_review_status = state.get("preprocessing_review_status", "pending")
    learning_paradigm = state.get("learning_paradigm", "supervised")

    # If preprocessing review was rejected, retry from appropriate path
    if preprocessing_review_status == "rejected":
        if learning_paradigm == "unsupervised":
            logger.info("Preprocessing rejected - looping back to unsupervised preprocessing with new MLflow run")
            return "retry_unsupervised"
        else:
            logger.info("Preprocessing rejected - looping back to supervised preprocessing with new MLflow run")
            return "retry_supervised"

    # Otherwise continue with feature engineering (approved or default)
    return "continue_pipeline"


def should_retrain_model(state: PipelineState) -> Literal["retrain", "end"]:
    """
    Conditional edge function to decide if model should be retrained.

    Args:
        state: Current pipeline state

    Returns:
        "retrain" if retraining needed, "end" otherwise
    """
    if state.get("should_retrain", False):
        return "retrain"
    return "end"


def compile_pipeline(checkpointer=None) -> Any:
    """
    Compile the pipeline graph into an executable workflow.

    Args:
        checkpointer: Optional checkpointer for persisting state and enabling interrupts

    Returns:
        Compiled pipeline ready for execution
    """
    workflow = create_pipeline_graph()

    # Compile with interruption after all review nodes
    # This allows the workflow to pause and wait for user approval/rejection
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_after=[
            "await_algorithm_selection",  # Pause after Agent 1A for algorithm selection
            "await_review_approval",  # Pause after Agent 1B generates questions
            "await_preprocessing_review"  # Pause after preprocessing completes
        ]
    )


# ==================== Agent Node Functions ====================

def agent_1a_node(state: PipelineState) -> PipelineState:
    """
    Agent 1A: Algorithm Category Predictor

    Analyzes data characteristics and predicts optimal algorithm category.
    This is a visible node in the graph for transparency.
    """
    from agents import AlgorithmCategoryPredictorAgent
    import os

    logger.info("🤖 Agent 1A: Predicting algorithm category...")

    # Extract data profile
    data_profile = state.get("data_profile", {})

    # Initialize Agent 1A
    bedrock_model_id = state.get("bedrock_model_id", os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"))
    aws_region = state.get("aws_region", os.getenv("AWS_REGION", "us-east-1"))

    agent_1a = AlgorithmCategoryPredictorAgent(
        bedrock_model_id=bedrock_model_id,
        aws_region=aws_region,
        temperature=0.2,
        max_tokens=2000
    )

    # Predict algorithm category
    result = agent_1a.predict_category(
        n_samples=data_profile.get("n_samples", 0),
        n_features=data_profile.get("n_features", 0),
        target_type=data_profile.get("target_type", "unknown"),
        feature_types=data_profile.get("feature_types", {}),
        class_distribution=data_profile.get("class_distribution", {}),
        dataset_size_mb=data_profile.get("dataset_size_mb", 0),
        data_characteristics=data_profile.get("data_characteristics", {})
    )

    # Update state with Agent 1A results
    state["learning_paradigm"] = result.get("learning_paradigm", "supervised")
    state["algorithm_category"] = result.get("algorithm_category", "tree_models")
    state["agent_1a_confidence"] = result.get("confidence", 0.0)
    state["recommended_algorithms"] = result.get("recommended_algorithms", [])
    state["algorithm_requirements"] = result.get("algorithm_requirements", {})
    state["preprocessing_priorities"] = result.get("preprocessing_priorities", {})

    logger.info(
        f"✅ Agent 1A predicted: {state['learning_paradigm']} learning, "
        f"{state['algorithm_category']} (confidence: {state['agent_1a_confidence']:.2f})"
    )

    return state


def agent_1b_node(state: PipelineState) -> PipelineState:
    """
    Agent 1B: Preprocessing Question Generator

    Generates preprocessing questions tailored to the user-selected algorithm.
    This is a visible node in the graph for transparency.
    """
    from agents import PreprocessingQuestionGeneratorAgent
    import os

    logger.info("🤖 Agent 1B: Generating preprocessing questions...")

    # Get user-selected algorithm and other context
    selected_algorithm = state.get("selected_algorithm")
    if not selected_algorithm:
        # Fallback to algorithm category if no algorithm selected (shouldn't happen)
        logger.warning("No algorithm selected! Falling back to algorithm_category")
        selected_algorithm = state.get("algorithm_category", "tree_models")

    learning_paradigm = state.get("learning_paradigm", "supervised")
    data_profile = state.get("data_profile", {})

    logger.info(f"Generating questions for selected algorithm: {selected_algorithm}")

    # Initialize Agent 1B
    bedrock_model_id = state.get("bedrock_model_id", os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"))
    aws_region = state.get("aws_region", os.getenv("AWS_REGION", "us-east-1"))

    agent_1b = PreprocessingQuestionGeneratorAgent(
        bedrock_model_id=bedrock_model_id,
        aws_region=aws_region,
        temperature=0.3,
        max_tokens=4096
    )

    # Generate questions using selected algorithm
    result = agent_1b.generate_questions(
        algorithm_category=selected_algorithm,  # Now using selected_algorithm instead of category
        algorithm_confidence=state.get("agent_1a_confidence", 0.0),
        algorithm_requirements=state.get("algorithm_requirements", {}),
        preprocessing_priorities=state.get("preprocessing_priorities", {}),
        data_profile=data_profile,
        n_samples=data_profile.get("n_samples", 0),
        n_features=data_profile.get("n_features", 0),
        target_type=data_profile.get("target_type", "unknown"),
        learning_paradigm=learning_paradigm
    )

    # Update state with Agent 1B results
    state["review_questions"] = result.get("questions", [])
    state["question_count_by_step"] = result.get("question_count_by_step", {})
    state["preprocessing_recommendations"] = result.get("preprocessing_recommendations", {})
    state["review_summary"] = result.get("review_summary", "")
    state["review_recommendation"] = result.get("review_recommendation", "")

    logger.info(f"✅ Agent 1B generated {len(state['review_questions'])} questions for {selected_algorithm} ({learning_paradigm} learning)")

    return state


def await_algorithm_selection_node(state: PipelineState) -> PipelineState:
    """
    Algorithm Selection Checkpoint (HITL after Agent 1A)

    This node pauses the workflow after Agent 1A recommends algorithms.
    User must select ONE specific algorithm from the recommended list.

    The workflow will interrupt here and wait for user to:
    - Review Agent 1A's recommended algorithms (3-5 options)
    - Select ONE algorithm to use for preprocessing and training
    - Either approve selection (continue to Agent 1B) or reject (retry from Agent 0)
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("⏸️  Pausing for algorithm selection...")

    # Update pipeline status
    state["pipeline_status"] = "awaiting_algorithm_selection"
    state["algorithm_selection_status"] = "pending"

    logger.info(f"📊 Agent 1A recommended {len(state.get('recommended_algorithms', []))} algorithms:")
    for algo in state.get("recommended_algorithms", []):
        logger.info(f"  - {algo}")
    logger.info("✅ Awaiting user algorithm selection")

    # LangGraph will interrupt here (configured in compile_pipeline)
    return state


def await_review_approval_node(state: PipelineState) -> PipelineState:
    """
    Human Review Approval Checkpoint (After Agent 1B)

    This node marks the point where the workflow pauses for human approval.
    It stores the review session in the database and updates the pipeline status.

    The workflow will interrupt here and wait for user to:
    - Answer questions via frontend
    - Either approve (continue) or reject (retry from Agent 0)
    """
    from utils.review_storage import create_review_storage_from_env
    import logging

    logger = logging.getLogger(__name__)
    logger.info("⏸️  Pausing for human review...")

    # Store review session in database
    try:
        review_storage = create_review_storage_from_env()
        review_storage.store_review_session(
            pipeline_run_id=state.get("pipeline_run_id"),
            questions=state.get("review_questions", []),
            algorithm_category=state.get("algorithm_category"),
            agent_1a_confidence=state.get("agent_1a_confidence"),
            recommended_algorithms=state.get("recommended_algorithms", [])
        )
    except Exception as e:
        logger.warning(f"Failed to store review session: {e}")

    # Update pipeline status
    state["pipeline_status"] = "awaiting_review"
    state["review_status"] = "pending"

    logger.info("✅ Review session stored - awaiting user response")

    # LangGraph will interrupt here (configured in compile_pipeline)
    return state


def await_preprocessing_review_node(state: PipelineState) -> PipelineState:
    """
    Preprocessing Review Checkpoint (Second HITL)

    This node pauses after preprocessing completes to show the user:
    - Summary of all preprocessing steps executed
    - Data shape changes (original → final)
    - Techniques used and Bedrock's reasoning for each step
    - Missing values handled, outliers removed, encoding results, scaling applied
    - Option to approve (continue) or reject (retry preprocessing with new MLflow run)
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("⏸️  Pausing for preprocessing review...")

    # Generate preprocessing summary
    technique_metadata = state.get("technique_metadata", {})
    data_profile = state.get("data_profile", {})
    cleaned_data = state.get("cleaned_data")

    # Original data shape
    original_shape = (
        data_profile.get("n_samples", 0),
        data_profile.get("n_features", 0)
    )

    # Final data shape
    final_shape = cleaned_data.shape if cleaned_data is not None else (0, 0)

    # Build summary
    preprocessing_summary = {
        "original_shape": {
            "rows": original_shape[0],
            "columns": original_shape[1]
        },
        "final_shape": {
            "rows": final_shape[0],
            "columns": final_shape[1]
        },
        "rows_removed": original_shape[0] - final_shape[0],
        "columns_added": final_shape[1] - original_shape[1],
        "steps_completed": []
    }

    # Add details for each preprocessing step (handle both supervised and unsupervised step names)
    learning_paradigm = state.get("learning_paradigm", "supervised")

    # Determine which step names to look for based on learning paradigm
    if learning_paradigm == "unsupervised":
        step_names = ["clean_outliers", "handle_missing", "encode_features", "scale_features"]
    else:
        step_names = ["clean_data", "handle_missing", "encode_features", "scale_features"]

    for step_name in step_names:
        if step_name in technique_metadata:
            step_meta = technique_metadata[step_name]
            preprocessing_summary["steps_completed"].append({
                "step": step_name,
                "technique": step_meta.get("technique", "unknown"),
                "parameters": step_meta.get("parameters", {}),
                "bedrock_reasoning": step_meta.get("bedrock_reasoning", ""),
                "algorithm_context": step_meta.get("algorithm_context", ""),
                "learning_paradigm": learning_paradigm,
                # Step-specific metrics
                "rows_removed": step_meta.get("rows_removed", 0) if step_name in ["clean_data", "clean_outliers"] else None,
                "missing_handled": step_meta.get("missing_handled", 0) if step_name == "handle_missing" else None,
                "new_columns_created": step_meta.get("new_columns_created", 0) if step_name == "encode_features" else None,
                "high_cardinality_strategy": step_meta.get("high_cardinality_strategy") if step_name == "encode_features" else None,
                "scaler_fitted": step_meta.get("scaler_fitted", False) if step_name == "scale_features" else None
            })

    # Update state with preprocessing summary
    state["preprocessing_summary"] = preprocessing_summary
    state["pipeline_status"] = "awaiting_preprocessing_review"
    state["preprocessing_review_status"] = "pending"

    logger.info("="*80)
    logger.info("PREPROCESSING COMPLETE - Summary:")
    logger.info(f"  Original: {original_shape[0]} rows × {original_shape[1]} columns")
    logger.info(f"  Final: {final_shape[0]} rows × {final_shape[1]} columns")
    logger.info(f"  Rows removed: {preprocessing_summary['rows_removed']}")
    logger.info(f"  Columns added: {preprocessing_summary['columns_added']}")
    logger.info(f"  Steps completed: {len(preprocessing_summary['steps_completed'])}")
    logger.info("="*80)
    logger.info("✅ Preprocessing review ready - awaiting user approval")

    # LangGraph will interrupt here (configured in compile_pipeline)
    return state


# Placeholder node functions for later pipeline stages
# These will be implemented in their respective modules

def algorithm_selection_agent_node(state: PipelineState) -> PipelineState:
    """Placeholder for algorithm selection agent node."""
    # Will be implemented in agents/algorithm_selection.py
    return state


def model_selection_agent_node(state: PipelineState) -> PipelineState:
    """Placeholder for model selection agent node."""
    # Will be implemented in agents/model_selection.py
    return state


# Algorithm node placeholders
def logistic_regression_node(state: PipelineState) -> PipelineState:
    """Placeholder for logistic regression node."""
    return state


def random_forest_classifier_node(state: PipelineState) -> PipelineState:
    """Placeholder for random forest classifier node."""
    return state


def gradient_boosting_classifier_node(state: PipelineState) -> PipelineState:
    """Placeholder for gradient boosting classifier node."""
    return state


def linear_regression_node(state: PipelineState) -> PipelineState:
    """Placeholder for linear regression node."""
    return state


def ridge_regression_node(state: PipelineState) -> PipelineState:
    """Placeholder for ridge regression node."""
    return state


def random_forest_regressor_node(state: PipelineState) -> PipelineState:
    """Placeholder for random forest regressor node."""
    return state
