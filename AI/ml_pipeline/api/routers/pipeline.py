"""Pipeline API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
from datetime import datetime
import mlflow
import os

from api.models.pipeline import (
    LoadDataRequest,
    LoadDataResponse,
    PipelineStateResponse,
    ErrorResponse,
    DataProfile,
    ReviewAnswersRequest,
    ReviewAnswersResponse,
    AlgorithmSelectionRequest,
    AlgorithmSelectionResponse,
    ContinuePipelineResponse
)
from core.state import create_initial_state, PipelineState
from nodes.preprocessing.load_data import load_data_node
from nodes.preprocessing.review_config import review_config_node
from config.config import EnhancedMLPipelineConfig
from mlflow_utils.experiment_manager import ExperimentManager
from utils.review_storage import create_review_storage_from_env

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active pipeline states (in-memory storage)
active_pipelines: Dict[str, PipelineState] = {}


@router.post("/load-data", response_model=LoadDataResponse)
async def load_data(request: LoadDataRequest):
    """
    Start ML pipeline with natural language prompt OR traditional configuration.

    Two modes supported:
    1. Natural Language: Provide user_prompt + data_path
       - LangGraph starts with analyze_prompt_node (Bedrock extraction)
       - Then flows to load_data_node and continues
    2. Traditional: Provide data_path + target_column + config
       - LangGraph starts directly with load_data_node

    The LangGraph workflow automatically routes to the correct entry point.
    """
    try:
        # Determine mode
        is_natural_language = request.user_prompt and request.user_prompt.strip()

        if is_natural_language:
            logger.info(f"🤖 Natural language mode - User prompt: {request.user_prompt[:100]}...")
        else:
            logger.info(f"📋 Traditional mode - Target column: {request.target_column}")
            if not request.target_column:
                raise HTTPException(
                    status_code=400,
                    detail="target_column is required when user_prompt is not provided"
                )

        logger.info(f"Data path: {request.data_path}")

        # Load configuration
        config = EnhancedMLPipelineConfig.from_env()

        # Set MLflow tracking URI
        mlflow.set_tracking_uri(config.mlflow.tracking_uri)

        # End any active MLflow runs to avoid conflicts
        if mlflow.active_run():
            mlflow.end_run()

        # Create or get MLflow experiment
        experiment_manager = ExperimentManager(
            tracking_uri=config.mlflow.tracking_uri
        )
        experiment = experiment_manager.get_or_create_experiment(
            name=request.experiment_name,
            tags={
                "created_at": datetime.now().isoformat(),
                "source": "streamlit_ui",
                "mode": "natural_language" if is_natural_language else "traditional"
            }
        )

        # Build initial state
        initial_state = {
            "data_path": request.data_path,
            "mlflow_experiment_id": experiment.experiment_id,
            "pipeline_run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "pipeline_status": "running",
            "completed_nodes": [],
            "failed_nodes": [],
            "errors": [],
            "warnings": [],
            "start_time": datetime.now()
        }

        if is_natural_language:
            # Natural language mode - add Bedrock config
            bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
            initial_state["user_prompt"] = request.user_prompt
            initial_state["user_hints"] = request.user_hints or {}
            initial_state["bedrock_model_id"] = bedrock_model_id
            initial_state["bedrock_fallback_model_id"] = os.getenv("BEDROCK_FALLBACK_MODEL_ID")
            initial_state["aws_region"] = os.getenv("AWS_REGION", "us-east-1")
            initial_state["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            initial_state["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
            initial_state["confidence_threshold"] = float(os.getenv("BEDROCK_CONFIDENCE_THRESHOLD", "0.70"))
        else:
            # Traditional mode - use provided config
            initial_state["pipeline_config"] = {
                "data_path": request.data_path,
                "target_column": request.target_column,
                "test_size": request.test_size,
                "random_state": request.random_state,
                "mlflow": {
                    "tracking_uri": config.mlflow.tracking_uri,
                    "enable_logging": config.mlflow.enable_logging
                }
            }

        # Get pipeline_run_id
        pipeline_run_id = initial_state["pipeline_run_id"]

        # Start MLflow run for tracking
        mlflow_run = mlflow.start_run(
            experiment_id=experiment.experiment_id,
            run_name=pipeline_run_id
        )
        initial_state["mlflow_run_id"] = mlflow_run.info.run_id
        logger.info(f"Started MLflow run: {mlflow_run.info.run_id}")

        # Execute pipeline nodes based on mode
        logger.info(f"Executing pipeline for: {pipeline_run_id}")

        if is_natural_language:
            # Natural language mode: analyze_prompt_node → load_data_node
            logger.info("Step 1: Analyzing prompt with Bedrock...")
            from nodes.preprocessing.analyze_prompt import analyze_prompt_node

            # Call analyze_prompt_node to extract config
            updated_state = analyze_prompt_node(initial_state)

            # Check for errors from analyze_prompt
            if updated_state.get("errors"):
                error = updated_state["errors"][0]
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": error.get("error_type", "Config extraction failed"),
                        "message": error.get("error_message", ""),
                        "node": error.get("node_name", "analyze_prompt")
                    }
                )

            # Add data_path from request to extracted config
            if "pipeline_config" in updated_state:
                updated_state["pipeline_config"]["data_path"] = request.data_path
                updated_state["pipeline_config"]["mlflow"] = {
                    "tracking_uri": config.mlflow.tracking_uri,
                    "enable_logging": config.mlflow.enable_logging
                }

            logger.info("Step 2: Loading data with extracted config...")
            # Now call load_data_node with the state that has pipeline_config
            updated_state = load_data_node(updated_state)
        else:
            # Traditional mode: load_data_node directly
            updated_state = load_data_node(initial_state)

        # Check if load_data was successful
        if updated_state.get("errors"):
            error = updated_state["errors"][0]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": error.get("error_type", "Unknown error"),
                    "message": error.get("error_message", ""),
                    "node": error.get("node_name", "load_data")
                }
            )

        # Step 3: Call Agent 1A to predict algorithm category
        logger.info("Step 3: Agent 1A predicting algorithm category...")
        from core.graph import agent_1a_node
        updated_state = agent_1a_node(updated_state)

        # Check for errors
        if updated_state.get("errors"):
            error = updated_state["errors"][0]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": error.get("error_type", "Unknown error"),
                    "message": error.get("error_message", ""),
                    "node": error.get("node_name", "agent_1a")
                }
            )

        # Step 4: Pause for algorithm selection (HITL checkpoint)
        logger.info("Step 4: Pausing for algorithm selection...")
        from core.graph import await_algorithm_selection_node
        updated_state = await_algorithm_selection_node(updated_state)

        # Store state for future operations (in-memory)
        active_pipelines[pipeline_run_id] = updated_state

        # Add experiment name to state for display
        updated_state["experiment_name"] = request.experiment_name

        # Build response
        data_profile_dict = updated_state.get("data_profile")
        data_profile = None
        if data_profile_dict:
            data_profile = DataProfile(
                n_samples=data_profile_dict.get("n_samples", 0),
                n_features=data_profile_dict.get("n_features", 0),
                target_column=data_profile_dict.get("target_column", ""),
                feature_names=data_profile_dict.get("feature_names", []),
                target_distribution=data_profile_dict.get("target_distribution", {})
            )

        # Build response - include extraction details if natural language mode
        response_data = {
            "success": True,
            "message": "Agent 1A completed - please select an algorithm to continue",
            "pipeline_run_id": pipeline_run_id,
            "mlflow_run_id": updated_state.get("mlflow_run_id"),
            "mlflow_experiment_id": experiment.experiment_id,
            "data_profile": data_profile,
            "timestamp": datetime.now()
        }

        # Add extraction details if natural language mode was used
        if is_natural_language:
            # Safely extract reasoning - convert dict to formatted string if needed
            reasoning = updated_state.get("config_reasoning")
            if isinstance(reasoning, dict):
                # Convert reasoning dict to nicely formatted string
                reasoning_parts = []
                for key, value in reasoning.items():
                    reasoning_parts.append(f"• {key.replace('_', ' ').title()}: {value}")
                reasoning = "\n".join(reasoning_parts)
            elif reasoning is None:
                reasoning = None

            response_data.update({
                "extracted_config": updated_state.get("pipeline_config"),
                "confidence": updated_state.get("config_confidence"),
                "reasoning": reasoning,
                "assumptions": updated_state.get("config_assumptions"),
                "config_warnings": updated_state.get("config_warnings"),
                "bedrock_model_id": updated_state.get("bedrock_model_used"),
                "bedrock_tokens_used": updated_state.get("bedrock_tokens_used"),
                "prompt_storage_id": updated_state.get("prompt_storage_id")
            })

        # Add Agent 1A results (Algorithm Category Predictor)
        response_data.update({
            "pipeline_status": updated_state.get("pipeline_status", "awaiting_algorithm_selection"),
            "algorithm_selection_status": updated_state.get("algorithm_selection_status", "pending"),
            "algorithm_category": updated_state.get("algorithm_category"),
            "algorithm_confidence": updated_state.get("agent_1a_confidence"),
            "recommended_algorithms": updated_state.get("recommended_algorithms"),
            "algorithm_requirements": updated_state.get("algorithm_requirements"),
            "preprocessing_priorities": updated_state.get("preprocessing_priorities"),
            "learning_paradigm": updated_state.get("learning_paradigm")
        })

        response = LoadDataResponse(**response_data)

        logger.info(f"Pipeline paused for algorithm selection: {pipeline_run_id}")
        logger.info(f"Recommended algorithms: {updated_state.get('recommended_algorithms', [])}")
        return response

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        # End MLflow run if active
        if mlflow.active_run():
            mlflow.end_run(status="FAILED")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "File not found",
                "message": f"Could not find file: {request.data_path}",
                "detail": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)
        # End MLflow run if active
        if mlflow.active_run():
            mlflow.end_run(status="FAILED")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to load data",
                "detail": str(e)
            }
        )


@router.get("/state/{pipeline_run_id}", response_model=PipelineStateResponse)
async def get_pipeline_state(pipeline_run_id: str):
    """
    Get the current state of a pipeline run.
    """
    try:
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        response = PipelineStateResponse(
            pipeline_run_id=pipeline_run_id,
            pipeline_status=state.get("pipeline_status", "unknown"),
            current_node=state.get("current_node"),
            completed_nodes=state.get("completed_nodes", []),
            failed_nodes=state.get("failed_nodes", []),
            errors=state.get("errors", []),
            warnings=state.get("warnings", []),
            start_time=state.get("start_time", datetime.now()),
            end_time=state.get("end_time")
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pipeline state: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to get pipeline state",
                "detail": str(e)
            }
        )


@router.get("/runs")
async def list_pipeline_runs():
    """
    List all pipeline runs from in-memory storage with detailed information.
    """
    try:
        runs = []
        for pipeline_run_id, state in active_pipelines.items():
            # Convert datetime objects to ISO format strings
            created_at = state.get("start_time")
            start_time = state.get("start_time")
            end_time = state.get("end_time")

            run_data = {
                "pipeline_run_id": pipeline_run_id,
                "status": state.get("pipeline_status", "unknown"),
                "current_node": state.get("current_node"),
                "completed_nodes": state.get("completed_nodes", []),
                "failed_nodes": state.get("failed_nodes", []),
                "created_at": created_at.isoformat() if created_at else None,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "mlflow_run_id": state.get("mlflow_run_id"),
                "mlflow_experiment_id": state.get("mlflow_experiment_id"),
                "experiment_name": state.get("experiment_name"),
                "user_prompt": state.get("user_prompt"),
                "data_path": state.get("data_path"),
                "errors": state.get("errors", []),
                "warnings": state.get("warnings", []),
                "extracted_config": state.get("pipeline_config"),
                "confidence": state.get("config_confidence"),
                "reasoning": state.get("config_reasoning"),
                "assumptions": state.get("config_assumptions"),
                "config_warnings": state.get("config_warnings"),
                "bedrock_model_id": state.get("bedrock_model_used"),
                "bedrock_tokens_used": state.get("bedrock_tokens_used"),
                "data_profile": state.get("data_profile"),
                "node_outputs": state.get("node_outputs", {}),
                # Review workflow fields
                "review_status": state.get("review_status"),
                "review_questions": state.get("review_questions", []),
                "review_summary": state.get("review_summary"),
                "review_recommendation": state.get("review_recommendation"),
                # Algorithm-aware HITL fields (Agent 1A and Agent 1B)
                "algorithm_category": state.get("algorithm_category"),
                "algorithm_confidence": state.get("algorithm_confidence"),
                "recommended_algorithms": state.get("recommended_algorithms", []),
                "algorithm_requirements": state.get("algorithm_requirements", {}),
                "preprocessing_priorities": state.get("preprocessing_priorities", {}),
                "question_count_by_step": state.get("question_count_by_step", {}),
                "preprocessing_recommendations": state.get("preprocessing_recommendations", {})
            }
            runs.append(run_data)

        # Sort by start_time (newest first)
        runs.sort(key=lambda x: x.get("start_time") or "", reverse=True)

        return {
            "runs": runs,
            "total": len(runs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing pipeline runs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to list pipeline runs",
                "detail": str(e)
            }
        )


@router.post("/stop/{pipeline_run_id}")
async def stop_pipeline(pipeline_run_id: str):
    """
    Stop/cancel a running pipeline.

    This endpoint stops a pipeline execution and ends the associated MLflow run.
    """
    try:
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # End MLflow run if active
        mlflow_run_id = state.get("mlflow_run_id")
        if mlflow_run_id:
            try:
                # End the run with KILLED status
                mlflow.end_run(status="KILLED")
                logger.info(f"Ended MLflow run: {mlflow_run_id}")
            except Exception as e:
                logger.warning(f"Failed to end MLflow run {mlflow_run_id}: {e}")

        # Update pipeline status
        state["pipeline_status"] = "stopped"
        state["end_time"] = datetime.now()

        logger.info(f"Stopped pipeline: {pipeline_run_id}")

        return {
            "success": True,
            "message": f"Pipeline {pipeline_run_id} stopped successfully",
            "pipeline_run_id": pipeline_run_id,
            "status": "stopped",
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to stop pipeline",
                "detail": str(e)
            }
        )


@router.delete("/delete/{pipeline_run_id}")
async def delete_pipeline(pipeline_run_id: str, delete_experiment: bool = False):
    """
    Delete a pipeline run and optionally its MLflow experiment.

    Args:
        pipeline_run_id: ID of the pipeline to delete
        delete_experiment: If True, also deletes the associated MLflow experiment
    """
    try:
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]
        mlflow_run_id = state.get("mlflow_run_id")
        mlflow_experiment_id = state.get("mlflow_experiment_id")

        # End MLflow run if still active
        if mlflow_run_id:
            try:
                if mlflow.active_run() and mlflow.active_run().info.run_id == mlflow_run_id:
                    mlflow.end_run(status="KILLED")
                logger.info(f"Ended MLflow run: {mlflow_run_id}")
            except Exception as e:
                logger.warning(f"Failed to end MLflow run {mlflow_run_id}: {e}")

        # Delete MLflow run
        if mlflow_run_id:
            try:
                mlflow.delete_run(mlflow_run_id)
                logger.info(f"Deleted MLflow run: {mlflow_run_id}")
            except Exception as e:
                logger.warning(f"Failed to delete MLflow run {mlflow_run_id}: {e}")

        # Delete MLflow experiment if requested
        experiment_deleted = False
        if delete_experiment and mlflow_experiment_id:
            try:
                experiment_manager = ExperimentManager(
                    tracking_uri=mlflow.get_tracking_uri()
                )
                experiment_manager.delete_experiment(mlflow_experiment_id)
                experiment_deleted = True
                logger.info(f"Deleted MLflow experiment: {mlflow_experiment_id}")
            except Exception as e:
                logger.warning(f"Failed to delete MLflow experiment {mlflow_experiment_id}: {e}")

        # Remove from active pipelines (in-memory)
        if pipeline_run_id in active_pipelines:
            del active_pipelines[pipeline_run_id]

        logger.info(f"Deleted pipeline: {pipeline_run_id}")

        return {
            "success": True,
            "message": f"Pipeline {pipeline_run_id} deleted successfully",
            "pipeline_run_id": pipeline_run_id,
            "mlflow_run_deleted": mlflow_run_id is not None,
            "mlflow_experiment_deleted": experiment_deleted,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to delete pipeline",
                "detail": str(e)
            }
        )


@router.post("/review/{pipeline_run_id}/submit", response_model=ReviewAnswersResponse)
async def submit_review_answers(pipeline_run_id: str, request: ReviewAnswersRequest):
    """
    Submit user's answers to review questions and update review status.

    This endpoint:
    1. Validates that the pipeline run exists and is awaiting review
    2. Saves user's answers to PostgreSQL
    3. Updates review status (approved/rejected)
    4. Updates pipeline state
    5. If approved, pipeline can be continued via /continue endpoint
    6. If rejected, pipeline stops

    Args:
        pipeline_run_id: ID of the pipeline run
        request: User's answers and approval decision

    Returns:
        ReviewAnswersResponse with success status
    """
    try:
        # Check if pipeline exists
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # Verify pipeline is in review state
        review_status = state.get("review_status")
        if review_status != "awaiting_review":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid state",
                    "message": f"Pipeline is not awaiting review. Current status: {review_status}"
                }
            )

        # Convert answers to dict format
        answers_dict = {answer.question_id: answer.answer for answer in request.answers}

        logger.info(f"Submitting review answers for pipeline: {pipeline_run_id}")
        logger.info(f"Approved: {request.approved}")
        logger.info(f"Answers: {answers_dict}")

        # Save answers to PostgreSQL
        try:
            review_storage = create_review_storage_from_env()

            # Determine review status based on approval
            new_review_status = "approved" if request.approved else "rejected"

            # Update review with answers
            success = review_storage.update_review_answers(
                pipeline_run_id=pipeline_run_id,
                answers=answers_dict,
                review_status=new_review_status,
                approved=request.approved,
                user_feedback=request.user_feedback
            )

            review_storage.close()

            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save review answers to database"
                )

            logger.info(f"✓ Review answers saved to PostgreSQL (status: {new_review_status})")

        except Exception as storage_error:
            logger.error(f"Failed to save review answers: {storage_error}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Storage error",
                    "message": "Failed to save review answers",
                    "detail": str(storage_error)
                }
            )

        # Update pipeline state
        state["review_status"] = new_review_status
        state["review_answers"] = answers_dict
        state["review_user_feedback"] = request.user_feedback
        state["review_approved"] = request.approved

        if request.approved:
            state["pipeline_status"] = "review_approved"
            message = "Review approved - pipeline ready to continue"
            logger.info(f"✓ Review approved for pipeline: {pipeline_run_id}")
        else:
            # User rejected - save feedback and ask user what to do next
            state["pipeline_status"] = "review_rejected_awaiting_decision"
            logger.info(f"✗ Review rejected for pipeline: {pipeline_run_id}")
            logger.info(f"User feedback: {request.user_feedback or 'None provided'}")

            # Build user hints from rejection feedback for future retry
            user_hints = state.get("user_hints", {})
            if request.user_feedback:
                user_hints["rejection_feedback"] = request.user_feedback

            # Add specific hints based on which questions were answered "no"
            rejection_reasons = []
            questions = state.get("review_questions", [])
            for question in questions:
                q_id = question.get("question_id")
                answer = answers_dict.get(q_id)
                if answer == "no" or answer == False:
                    rejection_reasons.append(f"{question.get('question_text')} - User answered NO")

            if rejection_reasons:
                user_hints["rejected_aspects"] = "; ".join(rejection_reasons)

            state["user_hints"] = user_hints
            state["review_rejection_feedback"] = request.user_feedback
            state["review_rejection_answers"] = answers_dict

            message = "Configuration rejected. You can retry analysis with Agent 0 or cancel the pipeline."
            logger.info(f"Rejection feedback saved. Awaiting user decision (retry or cancel).")

        # Log to MLflow
        try:
            mlflow_run_id = state.get("mlflow_run_id")
            if mlflow_run_id and request.approved:
                mlflow.log_param("review_approved", True)
                mlflow.log_param("review_feedback", request.user_feedback or "")
        except Exception as mlflow_error:
            logger.warning(f"Failed to log review to MLflow: {mlflow_error}")

        # Save updated state
        active_pipelines[pipeline_run_id] = state

        return ReviewAnswersResponse(
            success=True,
            message=message,
            pipeline_run_id=pipeline_run_id,
            review_status=new_review_status,
            approved=request.approved,
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting review answers: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to submit review answers",
                "detail": str(e)
            }
        )


@router.post("/algorithm-selection/{pipeline_run_id}/submit", response_model=AlgorithmSelectionResponse)
async def submit_algorithm_selection(pipeline_run_id: str, request: AlgorithmSelectionRequest):
    """
    Submit user's algorithm selection after Agent 1A recommends algorithms.

    This endpoint:
    1. Validates that the pipeline run exists and is awaiting algorithm selection
    2. Validates that the selected algorithm is in the recommended list
    3. Updates pipeline state with selected algorithm
    4. If approved: Pipeline continues to Agent 1B with selected algorithm
    5. If rejected: Pipeline restarts from Agent 0

    Args:
        pipeline_run_id: ID of the pipeline run
        request: User's selected algorithm and approval decision

    Returns:
        AlgorithmSelectionResponse with success status
    """
    try:
        # Check if pipeline exists
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # Verify pipeline is in algorithm selection state
        pipeline_status = state.get("pipeline_status")
        if pipeline_status != "awaiting_algorithm_selection":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid state",
                    "message": f"Pipeline is not awaiting algorithm selection. Current status: {pipeline_status}"
                }
            )

        # Validate selected algorithm is in recommended list
        recommended_algorithms = state.get("recommended_algorithms", [])
        if request.approved and request.selected_algorithm not in recommended_algorithms:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid algorithm",
                    "message": f"Selected algorithm '{request.selected_algorithm}' not in recommended list: {recommended_algorithms}"
                }
            )

        logger.info(f"Submitting algorithm selection for pipeline: {pipeline_run_id}")
        logger.info(f"Approved: {request.approved}")
        logger.info(f"Selected algorithm: {request.selected_algorithm if request.approved else 'None (rejected)'}")

        if request.approved:
            # User approved - store selected algorithm
            state["selected_algorithm"] = request.selected_algorithm
            state["algorithm_selection_status"] = "approved"
            state["pipeline_status"] = "algorithm_selected"
            message = f"Algorithm '{request.selected_algorithm}' selected - pipeline will continue to Agent 1B"
            logger.info(f"✓ Algorithm selection approved: {request.selected_algorithm}")

            # Log to MLflow
            try:
                mlflow_run_id = state.get("mlflow_run_id")
                if mlflow_run_id:
                    mlflow.log_param("selected_algorithm", request.selected_algorithm)
                    mlflow.log_param("algorithm_selection_approved", True)
                    if request.user_feedback:
                        mlflow.log_param("algorithm_selection_feedback", request.user_feedback)
            except Exception as mlflow_error:
                logger.warning(f"Failed to log algorithm selection to MLflow: {mlflow_error}")

        else:
            # User rejected - restart from Agent 0
            state["algorithm_selection_status"] = "rejected"
            state["pipeline_status"] = "algorithm_selection_rejected_awaiting_decision"

            # Store rejection feedback for retry
            if request.user_feedback:
                user_hints = state.get("user_hints", {})
                user_hints["algorithm_selection_rejection_feedback"] = request.user_feedback
                state["user_hints"] = user_hints

            message = "Algorithm selection rejected. Pipeline will restart from Agent 0."
            logger.info(f"✗ Algorithm selection rejected")
            logger.info(f"Feedback: {request.user_feedback or 'None provided'}")

        # Save updated state
        active_pipelines[pipeline_run_id] = state

        return AlgorithmSelectionResponse(
            success=True,
            message=message,
            pipeline_run_id=pipeline_run_id,
            selected_algorithm=request.selected_algorithm if request.approved else None,
            algorithm_selection_status=state["algorithm_selection_status"],
            approved=request.approved,
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting algorithm selection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to submit algorithm selection",
                "detail": str(e)
            }
        )


@router.post("/algorithm-selection/{pipeline_run_id}/continue")
async def continue_after_algorithm_selection(pipeline_run_id: str):
    """
    Continue pipeline after algorithm selection is approved.

    This endpoint:
    1. Verifies algorithm selection is approved
    2. Calls Agent 1B to generate preprocessing questions for selected algorithm
    3. Returns review questions for user approval

    Args:
        pipeline_run_id: ID of the pipeline run

    Returns:
        Response with review questions
    """
    try:
        # Check if pipeline exists
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # Verify algorithm selection is approved
        pipeline_status = state.get("pipeline_status")
        if pipeline_status != "algorithm_selected":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid state",
                    "message": f"Pipeline is not ready to continue. Current status: {pipeline_status}"
                }
            )

        selected_algorithm = state.get("selected_algorithm")
        if not selected_algorithm:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "No algorithm selected",
                    "message": "Please select an algorithm first"
                }
            )

        logger.info(f"Continuing pipeline after algorithm selection: {pipeline_run_id}")
        logger.info(f"Selected algorithm: {selected_algorithm}")

        # Call Agent 1B to generate preprocessing questions
        logger.info("Calling Agent 1B to generate preprocessing questions...")
        from core.graph import agent_1b_node, await_review_approval_node

        # Call Agent 1B
        updated_state = agent_1b_node(state)

        # Check for errors
        if updated_state.get("errors"):
            error = updated_state["errors"][0]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": error.get("error_type", "Unknown error"),
                    "message": error.get("error_message", ""),
                    "node": error.get("node_name", "agent_1b")
                }
            )

        # Call await_review_approval_node to pause for review
        updated_state = await_review_approval_node(updated_state)

        # Save updated state
        active_pipelines[pipeline_run_id] = updated_state

        # Build response
        response_data = {
            "success": True,
            "message": "Agent 1B completed - please review preprocessing questions",
            "pipeline_run_id": pipeline_run_id,
            "pipeline_status": updated_state.get("pipeline_status"),
            "review_status": updated_state.get("review_status", "awaiting_review"),
            "review_questions": updated_state.get("review_questions", []),
            "review_summary": updated_state.get("review_summary", ""),
            "review_recommendation": updated_state.get("review_recommendation", ""),
            "question_count_by_step": updated_state.get("question_count_by_step"),
            "preprocessing_recommendations": updated_state.get("preprocessing_recommendations"),
            "selected_algorithm": selected_algorithm,
            "timestamp": datetime.now()
        }

        logger.info(f"✓ Agent 1B generated {len(updated_state.get('review_questions', []))} questions")
        logger.info(f"Pipeline now awaiting review approval: {pipeline_run_id}")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error continuing after algorithm selection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to continue pipeline",
                "detail": str(e)
            }
        )


@router.post("/preprocessing-review/{pipeline_run_id}/submit")
async def submit_preprocessing_review(
    pipeline_run_id: str,
    approved: bool = True,
    user_feedback: str = None
):
    """
    Submit preprocessing review decision (approve or reject).

    This endpoint handles the second HITL checkpoint after preprocessing:
    1. Validates pipeline is awaiting preprocessing review
    2. Updates preprocessing review status
    3. If approved: Pipeline continues to feature engineering (split_data)
    4. If rejected: Pipeline loops back to appropriate preprocessing path
       - Supervised: clean_data_supervised
       - Unsupervised: clean_outliers_unsupervised

    Args:
        pipeline_run_id: ID of the pipeline run
        approved: Whether user approved preprocessing results
        user_feedback: Optional feedback if rejected

    Returns:
        Success response with updated status
    """
    try:
        # Check if pipeline exists
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # Verify pipeline is in preprocessing review state
        pipeline_status = state.get("pipeline_status")
        if pipeline_status != "awaiting_preprocessing_review":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid state",
                    "message": f"Pipeline is not awaiting preprocessing review. Current status: {pipeline_status}"
                }
            )

        logger.info(f"Submitting preprocessing review for pipeline: {pipeline_run_id}")
        logger.info(f"Approved: {approved}")
        logger.info(f"Feedback: {user_feedback or 'None'}")

        # Update pipeline state
        if approved:
            state["preprocessing_review_status"] = "approved"
            state["pipeline_status"] = "preprocessing_approved"
            message = "Preprocessing approved - pipeline will continue to feature engineering"
            logger.info(f"✓ Preprocessing approved for pipeline: {pipeline_run_id}")

            # Log to MLflow
            try:
                mlflow_run_id = state.get("mlflow_run_id")
                if mlflow_run_id:
                    mlflow.log_param("preprocessing_review_approved", True)
            except Exception as mlflow_error:
                logger.warning(f"Failed to log preprocessing review to MLflow: {mlflow_error}")

        else:
            state["preprocessing_review_status"] = "rejected"
            state["pipeline_status"] = "preprocessing_rejected"
            state["preprocessing_rejection_feedback"] = user_feedback
            message = "Preprocessing rejected - will retry with new MLflow experiment"
            logger.info(f"✗ Preprocessing rejected for pipeline: {pipeline_run_id}")
            logger.info(f"Feedback: {user_feedback or 'None provided'}")

            # Log rejection to MLflow before ending run
            try:
                mlflow_run_id = state.get("mlflow_run_id")
                if mlflow_run_id:
                    mlflow.log_param("preprocessing_review_rejected", True)
                    mlflow.log_param("preprocessing_rejection_reason", user_feedback or "No feedback")
                    # End current MLflow run
                    if mlflow.active_run():
                        mlflow.end_run()
                    logger.info("Current MLflow run ended - new run will be created on retry")
            except Exception as mlflow_error:
                logger.warning(f"Failed to log preprocessing rejection to MLflow: {mlflow_error}")

        # Save updated state
        active_pipelines[pipeline_run_id] = state

        return {
            "success": True,
            "message": message,
            "pipeline_run_id": pipeline_run_id,
            "preprocessing_review_status": state["preprocessing_review_status"],
            "approved": approved,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting preprocessing review: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to submit preprocessing review",
                "detail": str(e)
            }
        )


@router.post("/{pipeline_run_id}/retry-agent0")
async def retry_agent0(pipeline_run_id: str):
    """
    Retry Agent 0 configuration extraction after rejection.

    This endpoint:
    1. Retrieves saved rejection feedback from state
    2. Re-invokes Agent 0 with the feedback
    3. If successful, generates new review questions
    4. If fails, returns error details for user to decide next action

    Args:
        pipeline_run_id: ID of the pipeline run

    Returns:
        Success response with new review questions OR error details
    """
    try:
        # Check if pipeline exists
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # Verify pipeline is in awaiting decision state
        pipeline_status = state.get("pipeline_status")
        if pipeline_status != "review_rejected_awaiting_decision":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid state",
                    "message": f"Pipeline is not awaiting retry decision. Current status: {pipeline_status}"
                }
            )

        logger.info(f"Retrying Agent 0 for pipeline: {pipeline_run_id}")

        # Import nodes
        from nodes.preprocessing.analyze_prompt import analyze_prompt_node
        from nodes.preprocessing.load_data import load_data_node
        from nodes.preprocessing.review_config import review_config_node

        try:
            # Update status
            state["pipeline_status"] = "review_rejected_reworking"

            logger.info("Step 1: Re-analyzing prompt with rejection feedback...")
            updated_state = analyze_prompt_node(state)

            # Check for errors
            if updated_state.get("errors"):
                error = updated_state["errors"][0]
                error_msg = error.get('error_message', str(error))
                raise Exception(f"Re-analysis failed: {error_msg}")

            logger.info("Step 2: Re-loading data with new config...")
            updated_state = load_data_node(updated_state)

            if updated_state.get("errors"):
                error = updated_state["errors"][0]
                error_msg = error.get('error_message', str(error))
                raise Exception(f"Data loading failed: {error_msg}")

            logger.info("Step 3: Re-generating review questions...")
            updated_state = review_config_node(updated_state)

            if updated_state.get("errors"):
                error = updated_state["errors"][0]
                error_msg = error.get('error_message', str(error))
                raise Exception(f"Review generation failed: {error_msg}")

            # Update state with new configuration
            state.update(updated_state)
            state["pipeline_status"] = "awaiting_review"
            state["review_iteration"] = state.get("review_iteration", 0) + 1

            # Save updated state
            active_pipelines[pipeline_run_id] = state

            message = f"Configuration re-analyzed successfully. Please review the updated configuration (iteration {state['review_iteration']})."
            logger.info(f"✓ Successfully re-analyzed configuration (iteration {state['review_iteration']})")

            return {
                "success": True,
                "message": message,
                "pipeline_run_id": pipeline_run_id,
                "review_status": "awaiting_review",
                "review_questions": state.get("review_questions", []),
                "review_summary": state.get("review_summary"),
                "review_recommendation": state.get("review_recommendation"),
                "extracted_config": state.get("extracted_config"),
                "confidence": state.get("confidence"),
                "reasoning": state.get("reasoning"),
                "review_iteration": state.get("review_iteration", 1)
            }

        except Exception as retry_error:
            logger.error(f"Failed to retry Agent 0: {retry_error}", exc_info=True)

            # Keep state as awaiting decision so user can try again
            state["pipeline_status"] = "review_rejected_awaiting_decision"
            state["last_retry_error"] = str(retry_error)
            active_pipelines[pipeline_run_id] = state

            # Return error details without ending the pipeline
            return {
                "success": False,
                "message": "Agent 0 re-analysis failed. You can try again or cancel the pipeline.",
                "error": str(retry_error),
                "pipeline_run_id": pipeline_run_id,
                "review_status": "review_rejected_awaiting_decision"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying Agent 0: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to retry Agent 0",
                "detail": str(e)
            }
        )


@router.post("/{pipeline_run_id}/cancel-after-rejection")
async def cancel_after_rejection(pipeline_run_id: str):
    """
    Cancel pipeline after review rejection.

    This endpoint:
    1. Ends the MLflow run with CANCELLED status
    2. Sets pipeline status to "cancelled_by_user"
    3. Cleans up resources

    Args:
        pipeline_run_id: ID of the pipeline run

    Returns:
        Success response confirming cancellation
    """
    try:
        # Check if pipeline exists
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # Verify pipeline is in awaiting decision state
        pipeline_status = state.get("pipeline_status")
        if pipeline_status != "review_rejected_awaiting_decision":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid state",
                    "message": f"Pipeline is not awaiting cancellation decision. Current status: {pipeline_status}"
                }
            )

        logger.info(f"Cancelling pipeline after rejection: {pipeline_run_id}")

        # Update state
        state["pipeline_status"] = "cancelled_by_user"
        state["end_time"] = datetime.now()

        # End MLflow run
        try:
            if mlflow.active_run():
                mlflow.log_param("cancelled_by_user", True)
                mlflow.log_param("cancellation_reason", "User cancelled after review rejection")
                mlflow.end_run(status="KILLED")
                logger.info(f"MLflow run ended with KILLED status for pipeline: {pipeline_run_id}")
        except Exception as mlflow_error:
            logger.warning(f"Failed to end MLflow run: {mlflow_error}")

        # Save updated state
        active_pipelines[pipeline_run_id] = state

        return {
            "success": True,
            "message": "Pipeline cancelled successfully",
            "pipeline_run_id": pipeline_run_id,
            "status": "cancelled_by_user"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to cancel pipeline",
                "detail": str(e)
            }
        )


@router.post("/{pipeline_run_id}/continue", response_model=ContinuePipelineResponse)
async def continue_pipeline(pipeline_run_id: str):
    """
    Continue pipeline execution after review approval.

    This endpoint:
    1. Verifies review is approved
    2. Continues pipeline to next nodes (preprocessing, training, etc.)
    3. Updates pipeline status to "running"

    NOTE: This is a placeholder endpoint. Full pipeline continuation with
    preprocessing and training nodes will be implemented in next iteration.

    Args:
        pipeline_run_id: ID of the pipeline run

    Returns:
        ContinuePipelineResponse with continuation status
    """
    import mlflow

    try:
        # Check if pipeline exists
        if pipeline_run_id not in active_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run not found: {pipeline_run_id}"
            )

        state = active_pipelines[pipeline_run_id]

        # Verify pipeline is approved (either initial review or preprocessing review)
        pipeline_status = state.get("pipeline_status")
        review_approved = state.get("review_approved", False)
        preprocessing_approved = state.get("preprocessing_review_status") == "approved"

        # Handle two cases:
        # 1. Initial review approved → run preprocessing
        # 2. Preprocessing review approved → continue to feature engineering
        # 3. Preprocessing rejected → retry preprocessing with new MLflow run

        if pipeline_status == "review_approved" and review_approved:
            # Case 1: Initial review approved, run preprocessing
            logger.info(f"Continuing pipeline execution (preprocessing): {pipeline_run_id}")
            is_preprocessing_phase = True
        elif pipeline_status == "preprocessing_approved" and preprocessing_approved:
            # Case 2: Preprocessing review approved, continue to feature engineering
            logger.info(f"Continuing pipeline execution (feature engineering): {pipeline_run_id}")
            is_preprocessing_phase = False
        elif pipeline_status == "preprocessing_rejected":
            # Case 3: Preprocessing rejected, retry with new MLflow run
            logger.info(f"Retrying preprocessing with new MLflow run: {pipeline_run_id}")
            is_preprocessing_phase = True

            # Start NEW MLflow run for retry
            old_mlflow_run_id = state.get("mlflow_run_id")
            logger.info(f"Previous MLflow run: {old_mlflow_run_id} (ended on rejection)")

            # Create new MLflow run
            experiment_name = state.get("experiment_name", "ml_pipeline")
            try:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if experiment is None:
                    experiment_id = mlflow.create_experiment(experiment_name)
                else:
                    experiment_id = experiment.experiment_id

                new_run = mlflow.start_run(experiment_id=experiment_id)
                new_mlflow_run_id = new_run.info.run_id
                state["mlflow_run_id"] = new_mlflow_run_id
                state["mlflow_experiment_id"] = experiment_id

                # Log that this is a preprocessing retry
                mlflow.log_param("preprocessing_retry", True)
                mlflow.log_param("previous_mlflow_run_id", old_mlflow_run_id)
                mlflow.log_param("retry_reason", state.get("preprocessing_rejection_feedback", "User requested retry"))

                logger.info(f"✓ Started new MLflow run: {new_mlflow_run_id}")
            except Exception as mlflow_error:
                logger.warning(f"Failed to create new MLflow run: {mlflow_error}")
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid state",
                    "message": f"Pipeline is not approved to continue. Status: {pipeline_status}"
                }
            )

        logger.info(f"Continuing pipeline execution: {pipeline_run_id}")

        # Determine learning paradigm and import appropriate preprocessing nodes
        learning_paradigm = state.get("learning_paradigm", "supervised")
        logger.info(f"Learning paradigm: {learning_paradigm}")

        if learning_paradigm == "unsupervised":
            # Import unsupervised preprocessing nodes
            from nodes.preprocessing.unsupervised import (
                clean_outliers_node,
                handle_missing_node,
                encode_features_node,
                scale_features_node
            )
            first_node_name = "clean_outliers"
            first_node_func = clean_outliers_node
        else:
            # Import supervised preprocessing nodes
            from nodes.preprocessing.supervised import (
                clean_data_node,
                handle_missing_node,
                encode_features_node,
                scale_features_node
            )
            first_node_name = "clean_data"
            first_node_func = clean_data_node

        state["pipeline_status"] = "running"
        state["current_node"] = "preprocessing"

        # Add review_approved to completed nodes
        completed_nodes = state.get("completed_nodes", [])
        if "review_approved" not in completed_nodes:
            completed_nodes.append("review_approved")
        state["completed_nodes"] = completed_nodes

        # Resume MLflow run for artifact logging (only if not already active)
        mlflow_run_id = state.get("mlflow_run_id")
        if mlflow_run_id:
            # Check if this run is already active
            active_run = mlflow.active_run()
            if active_run and active_run.info.run_id == mlflow_run_id:
                logger.info(f"MLflow run already active: {mlflow_run_id}")
            else:
                # End any other active run first
                if active_run:
                    mlflow.end_run()
                    logger.info(f"Ended different active MLflow run: {active_run.info.run_id}")
                # Resume the pipeline's MLflow run
                mlflow.start_run(run_id=mlflow_run_id)
                logger.info(f"Resumed MLflow run: {mlflow_run_id}")

        try:
            # Step 1: Clean data/outliers (based on learning paradigm)
            if learning_paradigm == "unsupervised":
                logger.info("Step 1: Cleaning outliers (unsupervised)...")
            else:
                logger.info("Step 1: Cleaning data (supervised)...")

            state["current_node"] = first_node_name
            active_pipelines[pipeline_run_id] = state  # Save state for frontend polling
            state = first_node_func(state)

            # Check for errors
            errors = state.get("errors", [])
            if errors:
                error_msg = errors[-1] if errors else "Unknown error"
                logger.error(f"{first_node_name}_node failed: {error_msg}")
                raise Exception(f"{first_node_name}_node failed: {error_msg}")

            active_pipelines[pipeline_run_id] = state  # Save after completion

            # Step 2: Handle missing values
            logger.info("Step 2: Handling missing values...")
            state["current_node"] = "handle_missing"
            active_pipelines[pipeline_run_id] = state
            state = handle_missing_node(state)

            if state.get("errors"):
                raise Exception(f"handle_missing_node failed: {state['errors'][-1]}")

            active_pipelines[pipeline_run_id] = state

            # Step 3: Encode categorical features
            logger.info("Step 3: Encoding features...")
            state["current_node"] = "encode_features"
            active_pipelines[pipeline_run_id] = state
            state = encode_features_node(state)

            if state.get("errors"):
                raise Exception(f"encode_features_node failed: {state['errors'][-1]}")

            active_pipelines[pipeline_run_id] = state

            # Step 4: Scale numerical features
            logger.info("Step 4: Scaling features...")
            state["current_node"] = "scale_features"
            active_pipelines[pipeline_run_id] = state
            state = scale_features_node(state)

            if state.get("errors"):
                raise Exception(f"scale_features_node failed: {state['errors'][-1]}")

            # Update pipeline status
            state["pipeline_status"] = "preprocessing_completed"
            state["current_node"] = "preprocessing_completed"

            # ============ Save Preprocessed Data ============
            logger.info("Step 5: Saving preprocessed dataset...")

            # Get the preprocessed dataframe from state
            df_preprocessed = state.get("cleaned_data")
            if df_preprocessed is not None:
                import os
                import pandas as pd

                # Create output directory
                os.makedirs("data/processed", exist_ok=True)

                # Save to CSV with pipeline_run_id in filename
                preprocessed_path = f"data/processed/{pipeline_run_id}_preprocessed.csv"
                df_preprocessed.to_csv(preprocessed_path, index=False)
                logger.info(f"✓ Saved preprocessed data to: {preprocessed_path}")

                # Update state with file path
                state["preprocessed_data_path"] = preprocessed_path

                # Log to MLflow as artifact
                if mlflow_run_id and mlflow.active_run():
                    try:
                        mlflow.log_artifact(preprocessed_path, artifact_path="preprocessed_data")
                        logger.info(f"✓ Logged preprocessed data to MLflow: {preprocessed_path}")

                        # Log dataset statistics
                        mlflow.log_metric("preprocessed_rows", len(df_preprocessed))
                        mlflow.log_metric("preprocessed_columns", len(df_preprocessed.columns))
                        mlflow.log_param("preprocessed_shape", str(df_preprocessed.shape))

                        # Log column names
                        mlflow.log_param("preprocessed_columns", ",".join(df_preprocessed.columns.tolist()[:50]))  # First 50 cols

                        logger.info("✓ Logged preprocessed dataset statistics to MLflow")
                    except Exception as artifact_error:
                        logger.warning(f"Failed to log artifact to MLflow: {artifact_error}")
            else:
                logger.warning("No preprocessed dataframe found in state - skipping save")

            # Save updated state
            active_pipelines[pipeline_run_id] = state

            logger.info(f"✓ Preprocessing completed: {pipeline_run_id}")

            # End MLflow run
            if mlflow_run_id and mlflow.active_run():
                mlflow.end_run()
                logger.info(f"Ended MLflow run: {mlflow_run_id}")

            # Build success message with file path
            success_message = "Preprocessing completed successfully."
            if state.get("preprocessed_data_path"):
                success_message += f" Preprocessed data saved to: {state['preprocessed_data_path']}"
                if mlflow_run_id:
                    success_message += f" | MLflow Run: {mlflow_run_id}"

            return ContinuePipelineResponse(
                success=True,
                message=success_message,
                pipeline_run_id=pipeline_run_id,
                pipeline_status=state["pipeline_status"],
                next_node="model_training (pending implementation)",
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error during preprocessing: {e}", exc_info=True)
            state["pipeline_status"] = "preprocessing_failed"
            state["errors"] = state.get("errors", []) + [{
                "node_name": state.get("current_node", "unknown"),
                "error_type": type(e).__name__,
                "error_message": str(e)
            }]
            active_pipelines[pipeline_run_id] = state

            # End MLflow run on error
            if mlflow_run_id and mlflow.active_run():
                mlflow.end_run(status="FAILED")
                logger.info(f"Ended MLflow run with FAILED status: {mlflow_run_id}")

            return ContinuePipelineResponse(
                success=False,
                message=f"Preprocessing failed at {state.get('current_node', 'unknown')}: {str(e)}",
                pipeline_run_id=pipeline_run_id,
                pipeline_status="preprocessing_failed",
                next_node=None,
                timestamp=datetime.now()
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error continuing pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to continue pipeline",
                "detail": str(e)
            }
        )


@router.get("/graph-visualization")
async def get_graph_visualization():
    """
    Generate and return the LangGraph state visualization as Mermaid diagram text.
    Frontend will render this using mermaid.js library.

    Returns:
        JSON with mermaid diagram syntax
    """
    try:
        from core.graph import create_pipeline_graph

        # Create the pipeline graph
        workflow = create_pipeline_graph()
        compiled_graph = workflow.compile()

        # Get the mermaid diagram as text
        mermaid_syntax = compiled_graph.get_graph().draw_mermaid()

        # Return as JSON for frontend rendering
        return {
            "mermaid": mermaid_syntax,
            "format": "mermaid"
        }

    except Exception as e:
        logger.error(f"Error generating graph visualization: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Graph generation failed",
                "message": str(e)
            }
        )
