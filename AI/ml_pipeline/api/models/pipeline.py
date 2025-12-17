"""Pydantic models for pipeline API requests and responses."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LoadDataRequest(BaseModel):
    """
    Request model for loading data and starting pipeline.

    Supports two modes:
    1. Natural Language: Provide user_prompt + data_path (extracts config with Bedrock)
    2. Traditional: Provide data_path + target_column + other config params
    """

    data_path: str = Field(..., description="Path to the data file (CSV, Parquet, Excel)")

    # Natural language mode
    user_prompt: Optional[str] = Field(default=None, description="Natural language description of ML task (triggers Bedrock extraction)")
    user_hints: Optional[Dict[str, Any]] = Field(default=None, description="Optional hints for Bedrock extraction")

    # Traditional mode (required if user_prompt not provided)
    target_column: Optional[str] = Field(default=None, description="Name of the target column")
    experiment_name: str = Field(default="ml_pipeline_experiment", description="MLflow experiment name")
    test_size: float = Field(default=0.2, ge=0.0, le=1.0, description="Test set size ratio")
    random_state: int = Field(default=42, description="Random state for reproducibility")

    class Config:
        schema_extra = {
            "examples": [
                {
                    "title": "Natural Language Mode",
                    "value": {
                        "data_path": "data/iris.csv",
                        "user_prompt": "Classify iris species with high accuracy using all available algorithms"
                    }
                },
                {
                    "title": "Traditional Mode",
                    "value": {
                        "data_path": "data/raw/train.csv",
                        "target_column": "target",
                        "experiment_name": "my_experiment",
                        "test_size": 0.2,
                        "random_state": 42
                    }
                }
            ]
        }


class DataProfile(BaseModel):
    """Data profile information."""

    n_samples: int
    n_features: int
    target_column: Optional[str]  # None for unsupervised tasks (clustering, etc.)
    feature_names: List[str]
    target_distribution: Dict[str, int]


class LoadDataResponse(BaseModel):
    """Response model for load data operation."""

    success: bool
    message: str
    pipeline_run_id: str
    mlflow_run_id: Optional[str]
    mlflow_experiment_id: Optional[str]
    data_profile: Optional[DataProfile]

    # Natural language mode extraction details (optional)
    extracted_config: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    assumptions: Optional[List[str]] = None
    config_warnings: Optional[List[str]] = None
    bedrock_model_id: Optional[str] = None
    bedrock_tokens_used: Optional[int] = None
    prompt_storage_id: Optional[int] = None

    # Review workflow fields (added after Agent 1 review node)
    review_status: Optional[str] = None
    review_questions: Optional[List[Dict[str, Any]]] = None
    review_summary: Optional[str] = None
    review_recommendation: Optional[str] = None

    # Algorithm-aware HITL fields (Agent 1A and Agent 1B)
    algorithm_category: Optional[str] = None  # linear_models, tree_models, neural_networks, ensemble, time_series
    algorithm_confidence: Optional[float] = None  # Agent 1A confidence score
    recommended_algorithms: Optional[List[str]] = None  # Recommended algorithm names
    algorithm_requirements: Optional[Dict[str, Any]] = None  # Algorithm requirements dict
    preprocessing_priorities: Optional[Dict[str, str]] = None  # Preprocessing step priorities
    question_count_by_step: Optional[Dict[str, int]] = None  # Question count per preprocessing step
    preprocessing_recommendations: Optional[Dict[str, Any]] = None  # Agent 1B recommendations

    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Data loaded successfully",
                "pipeline_run_id": "run_20250101_120000",
                "mlflow_run_id": "abc123def456",
                "mlflow_experiment_id": "1",
                "data_profile": {
                    "n_samples": 1000,
                    "n_features": 15,
                    "target_column": "target",
                    "feature_names": ["feature1", "feature2"],
                    "target_distribution": {"0": 500, "1": 500}
                },
                "timestamp": "2025-01-01T12:00:00"
            }
        }


class PipelineStateResponse(BaseModel):
    """Response model for pipeline state."""

    pipeline_run_id: str
    pipeline_status: str
    current_node: Optional[str]
    completed_nodes: List[str]
    failed_nodes: List[str]
    errors: List[Dict[str, Any]]
    warnings: List[str]
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        schema_extra = {
            "example": {
                "pipeline_run_id": "run_20250101_120000",
                "pipeline_status": "running",
                "current_node": "load_data",
                "completed_nodes": [],
                "failed_nodes": [],
                "errors": [],
                "warnings": [],
                "start_time": "2025-01-01T12:00:00",
                "end_time": None
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "Data validation failed",
                "detail": "File not found: data/raw/train.csv",
                "timestamp": "2025-01-01T12:00:00"
            }
        }


class ReviewAnswer(BaseModel):
    """Single answer to a review question."""

    question_id: str = Field(..., description="ID of the question being answered")
    answer: Any = Field(..., description="User's answer (string, bool, or list for multiple choice)")

    class Config:
        schema_extra = {
            "example": {
                "question_id": "q1",
                "answer": "yes"
            }
        }


class ReviewAnswersRequest(BaseModel):
    """Request model for submitting review answers."""

    answers: List[ReviewAnswer] = Field(..., description="List of answers to review questions")
    user_feedback: Optional[str] = Field(default=None, description="Optional user feedback/comments")
    approved: bool = Field(..., description="Whether user approves to continue with pipeline")

    class Config:
        schema_extra = {
            "example": {
                "answers": [
                    {"question_id": "q1", "answer": "yes"},
                    {"question_id": "q2", "answer": "yes"},
                    {"question_id": "q3", "answer": "yes"}
                ],
                "user_feedback": "Looks good, proceed with training",
                "approved": True
            }
        }


class ReviewAnswersResponse(BaseModel):
    """Response model for review answers submission."""

    success: bool
    message: str
    pipeline_run_id: str
    review_status: str
    approved: bool
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Review answers submitted successfully",
                "pipeline_run_id": "run_20250101_120000",
                "review_status": "approved",
                "approved": True,
                "timestamp": "2025-01-01T12:00:00"
            }
        }


class AlgorithmSelectionRequest(BaseModel):
    """Request model for algorithm selection (after Agent 1A)."""

    selected_algorithm: str = Field(..., description="User-selected algorithm from recommended list")
    user_feedback: Optional[str] = Field(default=None, description="Optional user feedback/comments")
    approved: bool = Field(..., description="Whether user approves to continue with selected algorithm")

    class Config:
        schema_extra = {
            "example": {
                "selected_algorithm": "XGBRegressor",
                "user_feedback": "XGBoost is best for this dataset",
                "approved": True
            }
        }


class AlgorithmSelectionResponse(BaseModel):
    """Response model for algorithm selection submission."""

    success: bool
    message: str
    pipeline_run_id: str
    selected_algorithm: Optional[str]
    algorithm_selection_status: str
    approved: bool
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Algorithm selection submitted successfully",
                "pipeline_run_id": "run_20250101_120000",
                "selected_algorithm": "XGBRegressor",
                "algorithm_selection_status": "approved",
                "approved": True,
                "timestamp": "2025-01-01T12:00:00"
            }
        }


class ContinuePipelineResponse(BaseModel):
    """Response model for pipeline continuation."""

    success: bool
    message: str
    pipeline_run_id: str
    pipeline_status: str
    next_node: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Pipeline continued successfully",
                "pipeline_run_id": "run_20250101_120000",
                "pipeline_status": "running",
                "next_node": "preprocess_data",
                "timestamp": "2025-01-01T12:00:00"
            }
        }
