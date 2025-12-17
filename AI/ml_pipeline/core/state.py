"""Enhanced PipelineState schema for LangGraph workflow."""

from typing import TypedDict, Dict, Any, List, Optional
from typing_extensions import NotRequired
import pandas as pd
import numpy as np
from datetime import datetime


class AlgorithmResult(TypedDict):
    """Result structure for a single algorithm's training."""

    algorithm_name: str
    best_params: Dict[str, Any]
    cv_mean_score: float
    cv_std_score: float
    test_score: float
    train_time: float
    model: Any  # Trained model object
    feature_importance: Optional[Dict[str, float]]
    confusion_matrix: Optional[np.ndarray]
    classification_report: Optional[Dict[str, Any]]


class PipelineState(TypedDict, total=False):
    """
    Enhanced state schema for ML Pipeline with LangGraph.

    This TypedDict defines all possible state keys used throughout the pipeline.
    Fields are marked as NotRequired since they are populated progressively.
    """

    # ==================== Configuration ====================
    pipeline_config: Dict[str, Any]  # Configuration parameters
    pipeline_run_id: str  # Unique identifier for this pipeline run
    start_time: datetime
    end_time: NotRequired[datetime]

    # ==================== Data ====================
    # Raw and processed data
    raw_data: NotRequired[pd.DataFrame]
    cleaned_data: NotRequired[pd.DataFrame]
    encoded_data: NotRequired[pd.DataFrame]
    scaled_data: NotRequired[pd.DataFrame]

    # Train/test splits
    X_train: NotRequired[pd.DataFrame]
    X_test: NotRequired[pd.DataFrame]
    y_train: NotRequired[pd.Series]
    y_test: NotRequired[pd.Series]

    # Data statistics
    data_profile: NotRequired[Dict[str, Any]]
    missing_value_stats: NotRequired[Dict[str, Any]]
    feature_types: NotRequired[Dict[str, str]]

    # ==================== MLflow ====================
    mlflow_experiment_id: NotRequired[str]
    mlflow_run_id: NotRequired[str]
    mlflow_tracking_uri: NotRequired[str]

    # ==================== AWS Bedrock ====================
    bedrock_model_id: NotRequired[str]
    aws_region: NotRequired[str]

    # ==================== AI Agent Decisions ====================
    # Agent 1A: Algorithm Category Predictor
    learning_paradigm: NotRequired[str]  # supervised or unsupervised
    algorithm_category: NotRequired[str]  # linear_models, tree_models, clustering, etc.
    agent_1a_confidence: NotRequired[float]  # Agent 1A's confidence score
    recommended_algorithms: NotRequired[List[str]]  # Recommended algorithms from Agent 1A
    algorithm_requirements: NotRequired[Dict[str, Any]]  # Algorithm-specific requirements
    preprocessing_priorities: NotRequired[Dict[str, str]]  # Preprocessing step priorities

    # Algorithm Selection (HITL after Agent 1A)
    selected_algorithm: NotRequired[str]  # User-selected algorithm from recommended list
    algorithm_selection_status: NotRequired[str]  # pending, approved, rejected

    # Agent 1B: Preprocessing Question Generator
    review_questions: NotRequired[List[Dict[str, Any]]]  # Generated preprocessing questions
    question_count_by_step: NotRequired[Dict[str, int]]  # Number of questions per preprocessing step
    preprocessing_recommendations: NotRequired[Dict[str, str]]  # Recommended preprocessing techniques
    review_summary: NotRequired[str]  # Summary of preprocessing recommendations
    review_recommendation: NotRequired[str]  # Overall recommendation from Agent 1B

    # Agent 1 (deprecated): Algorithm Selection
    algorithm_selection_decision: NotRequired[Dict[str, Any]]
    selected_algorithms: NotRequired[List[str]]
    algorithm_selection_reasoning: NotRequired[str]

    # Agent 2: Model Selection
    model_selection_decision: NotRequired[Dict[str, Any]]
    best_model_name: NotRequired[str]
    model_selection_reasoning: NotRequired[str]

    # Agent 3: Retraining Decision
    retraining_decision: NotRequired[Dict[str, Any]]
    should_retrain: NotRequired[bool]
    retraining_reasoning: NotRequired[str]

    # ==================== Algorithm Training Results ====================
    algorithm_results: NotRequired[Dict[str, AlgorithmResult]]
    best_model: NotRequired[Any]  # Best trained model object
    best_model_score: NotRequired[float]

    # ==================== Hyperparameter Tuning ====================
    param_grids: NotRequired[Dict[str, Dict[str, List[Any]]]]
    best_hyperparameters: NotRequired[Dict[str, Dict[str, Any]]]

    # ==================== Evaluation Metrics ====================
    evaluation_metrics: NotRequired[Dict[str, float]]
    classification_report: NotRequired[Dict[str, Any]]
    confusion_matrix: NotRequired[np.ndarray]
    feature_importance: NotRequired[Dict[str, float]]
    roc_auc_scores: NotRequired[Dict[str, float]]

    # ==================== Monitoring ====================
    # Drift detection
    drift_detection_results: NotRequired[Dict[str, Any]]
    drifted_features: NotRequired[List[str]]
    drift_detected: NotRequired[bool]

    # Performance monitoring
    performance_comparison: NotRequired[Dict[str, Any]]
    performance_degradation: NotRequired[float]
    baseline_metrics: NotRequired[Dict[str, float]]
    current_metrics: NotRequired[Dict[str, float]]

    # ==================== Artifacts ====================
    plots: NotRequired[Dict[str, str]]  # Plot file paths
    reports: NotRequired[Dict[str, str]]  # Report file paths
    model_artifacts: NotRequired[Dict[str, str]]  # Model artifact paths

    # ==================== Error Handling ====================
    errors: NotRequired[List[Dict[str, Any]]]
    warnings: NotRequired[List[str]]

    # ==================== Pipeline Status ====================
    current_node: NotRequired[str]
    completed_nodes: NotRequired[List[str]]
    failed_nodes: NotRequired[List[str]]
    pipeline_status: NotRequired[str]  # Options: running, completed, failed

    # ==================== Preprocessing Metadata ====================
    preprocessing_steps: NotRequired[List[str]]
    preprocessing_summary: NotRequired[Dict[str, Any]]  # Summary of preprocessing results
    preprocessing_review_status: NotRequired[str]  # pending, approved, rejected
    technique_metadata: NotRequired[Dict[str, Dict[str, Any]]]  # Metadata for each preprocessing technique
    encoders: NotRequired[Dict[str, Any]]  # Fitted encoders
    scalers: NotRequired[Dict[str, Any]]  # Fitted scalers
    scaler: NotRequired[Any]  # Fitted scaler (for inference)
    imputers: NotRequired[Dict[str, Any]]  # Fitted imputers
    df: NotRequired[pd.DataFrame]  # Current DataFrame being processed

    # ==================== Feature Engineering ====================
    feature_selection_method: NotRequired[str]
    selected_features: NotRequired[List[str]]
    feature_engineering_steps: NotRequired[List[str]]

    # ==================== Model Registry ====================
    registered_model_name: NotRequired[str]
    registered_model_version: NotRequired[str]
    model_stage: NotRequired[str]  # None, Staging, Production, Archived

    # ==================== Human Review (HITL) ====================
    review_session_id: NotRequired[str]  # UUID for review session
    review_status: NotRequired[str]  # pending, approved, rejected
    review_answers: NotRequired[Dict[str, Any]]  # User's answers to review questions
    review_feedback: NotRequired[str]  # User's rejection feedback
    retry_requested: NotRequired[bool]  # True if user wants to retry Agent 0
    agent_1a_result: NotRequired[Dict[str, Any]]  # Agent 1A algorithm prediction
    agent_1b_result: NotRequired[Dict[str, Any]]  # Agent 1B generated questions
    user_prompt: NotRequired[str]  # Original user prompt for natural language config


def create_initial_state(config: Dict[str, Any]) -> PipelineState:
    """
    Create initial pipeline state with configuration.

    Args:
        config: Pipeline configuration dictionary

    Returns:
        Initial PipelineState with required fields
    """
    return PipelineState(
        pipeline_config=config,
        pipeline_run_id=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        start_time=datetime.now(),
        completed_nodes=[],
        failed_nodes=[],
        errors=[],
        warnings=[],
        pipeline_status="running",
        algorithm_results={},
    )


def update_state(state: PipelineState, **updates: Any) -> PipelineState:
    """
    Update pipeline state with new values.

    Args:
        state: Current pipeline state
        **updates: Key-value pairs to update

    Returns:
        Updated pipeline state
    """
    return {**state, **updates}


def add_error(state: PipelineState, node_name: str, error: Exception) -> PipelineState:
    """
    Add error to pipeline state.

    Args:
        state: Current pipeline state
        node_name: Name of node where error occurred
        error: Exception that was raised

    Returns:
        Updated pipeline state with error logged
    """
    errors = state.get("errors", [])
    errors.append({
        "node": node_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
    })

    failed_nodes = state.get("failed_nodes", [])
    if node_name not in failed_nodes:
        failed_nodes.append(node_name)

    return update_state(
        state,
        errors=errors,
        failed_nodes=failed_nodes,
        pipeline_status="failed"
    )


def add_warning(state: PipelineState, warning_message: str) -> PipelineState:
    """
    Add warning to pipeline state.

    Args:
        state: Current pipeline state
        warning_message: Warning message

    Returns:
        Updated pipeline state with warning logged
    """
    warnings = state.get("warnings", [])
    warnings.append(f"[{datetime.now().isoformat()}] {warning_message}")
    return update_state(state, warnings=warnings)


def mark_node_completed(state: PipelineState, node_name: str) -> PipelineState:
    """
    Mark a node as completed in the pipeline state.

    Args:
        state: Current pipeline state
        node_name: Name of completed node

    Returns:
        Updated pipeline state
    """
    completed_nodes = state.get("completed_nodes", [])
    if node_name not in completed_nodes:
        completed_nodes.append(node_name)

    return update_state(state, completed_nodes=completed_nodes)


def is_classification_task(state: PipelineState) -> bool:
    """
    Determine if the task is classification based on target variable.

    Args:
        state: Current pipeline state

    Returns:
        True if classification, False if regression
    """
    if "y_train" in state:
        # Check if target has few unique values (classification)
        n_unique = state["y_train"].nunique()
        n_samples = len(state["y_train"])
        return n_unique < 50 and n_unique / n_samples < 0.05

    # Default to classification
    return True


def get_algorithm_result(state: PipelineState, algorithm_name: str) -> Optional[AlgorithmResult]:
    """
    Get result for a specific algorithm.

    Args:
        state: Current pipeline state
        algorithm_name: Name of algorithm

    Returns:
        AlgorithmResult if available, None otherwise
    """
    return state.get("algorithm_results", {}).get(algorithm_name)
