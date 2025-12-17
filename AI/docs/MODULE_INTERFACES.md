# Module Interface Specifications - Enhanced ML Pipeline

## Overview

This document defines the precise interfaces for each module in the enhanced ML pipeline system, including **AI decision agents**, **MLflow integration**, **individual algorithm nodes**, and **monitoring modules**.

## Core Interfaces

### 1. Enhanced State Schema (core/state.py)

```python
from typing import TypedDict, List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

class PipelineState(TypedDict, total=False):
    """
    Enhanced state schema for ML pipeline with MLflow and AI agents.

    All fields are optional (total=False) to allow progressive population.
    """

    # ============== Data Fields ==============
    raw_data: pd.DataFrame
    cleaned_data: pd.DataFrame
    train_data: pd.DataFrame
    test_data: pd.DataFrame
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series

    # ============== Feature Information ==============
    selected_features: List[str]
    dropped_features: List[str]
    feature_importance: Dict[str, float]
    feature_metadata: Dict[str, Any]
    feature_statistics: Dict[str, Dict[str, float]]  # NEW: For agent analysis

    # ============== MLflow Integration ==============
    mlflow_experiment_id: str                        # NEW
    mlflow_run_id: str                              # NEW
    mlflow_tracking_uri: str                        # NEW
    mlflow_artifacts: Dict[str, str]                # NEW
    mlflow_parent_run_id: Optional[str]            # NEW

    # ============== AI Decision Agents ==============
    algorithm_selection_decision: Dict[str, Any]    # NEW: Agent 1 output
    model_selection_decision: Dict[str, Any]        # NEW: Agent 2 output
    retraining_decision: Dict[str, Any]            # NEW: Agent 3 output
    agent_prompts: Dict[str, str]                  # NEW: Agent prompt history
    agent_responses: Dict[str, str]                # NEW: Full agent responses

    # ============== Algorithm-Specific Results ==============
    algorithm_results: Dict[str, Dict[str, Any]]    # NEW: Per-algorithm results
    # Structure: {
    #   "logistic_regression": {
    #       "model": trained_model,
    #       "cv_scores": [0.85, 0.87, ...],
    #       "best_params": {...},
    #       "training_time": 12.5,
    #       "mlflow_run_id": "...",
    #       "metrics": {...}
    #   }
    # }

    # ============== Hyperparameter Tuning ==============
    grid_search_results: Dict[str, Any]            # NEW
    best_hyperparameters: Dict[str, Dict[str, Any]] # NEW
    tuning_time: Dict[str, float]                  # NEW

    # ============== Model Artifacts ==============
    trained_models: Dict[str, Any]
    best_model_name: str
    best_model: Any                                # NEW: Best model object
    model_predictions: Dict[str, Any]
    cross_validation_scores: Dict[str, List[float]]

    # ============== Evaluation & Monitoring ==============
    evaluation_results: Dict[str, Dict[str, float]]
    baseline_performance: Dict[str, float]         # NEW
    performance_comparison: Dict[str, Any]         # NEW
    drift_detected: bool                           # NEW
    drift_score: float                            # NEW
    performance_drop: float                       # NEW

    # ============== Retraining Control ==============
    retraining_triggered: bool                     # NEW
    retraining_reason: str                        # NEW
    previous_model_path: Optional[str]            # NEW

    # ============== Configuration ==============
    pipeline_config: Dict[str, Any]
    model_type: str  # "classification" or "regression"
    bedrock_model_id: str                         # NEW
    aws_region: str                               # NEW
    selected_algorithms: List[str]                # NEW
    algorithms_to_skip: List[str]                 # NEW

    # ============== Metadata ==============
    execution_timestamp: str
    pipeline_version: str
    current_stage: str
    next_stage: str

    # ============== Error Handling ==============
    errors: List[Dict[str, Any]]
    warnings: List[str]
    validation_status: Dict[str, bool]

    # ============== Output ==============
    output_paths: Dict[str, str]


class AlgorithmResult(TypedDict):
    """Schema for individual algorithm training results"""
    model: Any                      # Trained sklearn model
    best_params: Dict[str, Any]    # Best hyperparameters from GridSearch
    cv_scores: List[float]         # Cross-validation scores
    cv_mean: float                 # Mean CV score
    cv_std: float                  # Std CV score
    test_accuracy: float           # Test set accuracy (or RMSE for regression)
    test_f1: float                 # Test set F1 (classification only)
    training_time: float           # Training time in seconds
    mlflow_run_id: str            # MLflow child run ID
    predictions: Any               # Test predictions


class AgentDecision(TypedDict):
    """Base schema for AI agent decisions"""
    decision_type: str             # "algorithm_selection", "model_selection", "retraining"
    timestamp: str
    confidence: float              # 0.0 to 1.0
    reasoning: str


class AlgorithmSelectionDecision(AgentDecision):
    """Schema for Agent 1: Algorithm Selection"""
    selected_algorithms: List[str]
    reasoning_per_algorithm: Dict[str, str]
    hyperparameter_suggestions: Dict[str, Dict[str, List]]
    estimated_times: Dict[str, float]
    skip_algorithms: List[str]
    skip_reasons: Dict[str, str]


class ModelSelectionDecision(AgentDecision):
    """Schema for Agent 2: Model Selection"""
    selected_model: str
    confidence: float
    trade_offs: Dict[str, str]
    risks: List[str]
    alternative_model: str


class RetrainingDecision(AgentDecision):
    """Schema for Agent 3: Retraining Decision"""
    retrain: bool
    urgency: str  # "low", "medium", "high", "critical"
    contributing_factors: List[str]
    recommended_actions: List[str]
    estimated_improvement: str
```

---

## AI Decision Agent Interfaces

### 2. BaseDecisionAgent (agents/base_agent.py)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import boto3
import json

class BaseDecisionAgent(ABC):
    """
    Abstract base class for all AI decision agents.

    All agents use AWS Bedrock Claude for decision-making with
    retry logic and fallback strategies.
    """

    def __init__(
        self,
        bedrock_model_id: str,
        aws_region: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ):
        """
        Initialize agent with AWS Bedrock configuration.

        Args:
            bedrock_model_id: Claude model ID (e.g., "anthropic.claude-3-sonnet-20240229-v1:0")
            aws_region: AWS region (e.g., "us-east-1")
            temperature: Sampling temperature (0.0 for deterministic)
            max_tokens: Maximum tokens in response
        """
        self.bedrock_model_id = bedrock_model_id
        self.aws_region = aws_region
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = boto3.client('bedrock-runtime', region_name=aws_region)

    @abstractmethod
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build prompt for the agent based on context.

        Args:
            context: Context data for decision-making

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse agent response into structured decision.

        Args:
            response: Raw text response from Claude

        Returns:
            Structured decision dictionary
        """
        pass

    @abstractmethod
    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return fallback decision if agent fails.

        Args:
            context: Context data

        Returns:
            Default safe decision
        """
        pass

    def invoke(self, context: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Invoke the agent with retry logic.

        Args:
            context: Context data for decision
            max_retries: Maximum number of retry attempts

        Returns:
            Structured decision dictionary

        Raises:
            Exception: If all retries fail
        """
        prompt = self.build_prompt(context)

        for attempt in range(max_retries):
            try:
                response = self._call_bedrock(prompt)
                decision = self.parse_response(response)
                return {
                    "decision": decision,
                    "prompt": prompt,
                    "response": response,
                    "attempt": attempt + 1
                }
            except Exception as e:
                if attempt == max_retries - 1:
                    # All retries failed, use default
                    return {
                        "decision": self.get_default_decision(context),
                        "prompt": prompt,
                        "response": None,
                        "error": str(e),
                        "fallback": True
                    }
                time.sleep(2 ** attempt)  # Exponential backoff

    def _call_bedrock(self, prompt: str) -> str:
        """
        Call AWS Bedrock API.

        Args:
            prompt: Prompt string

        Returns:
            Response text
        """
        response = self.client.invoke_model(
            modelId=self.bedrock_model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            })
        )
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
```

---

### 3. AlgorithmSelectionAgent (agents/algorithm_selection.py)

```python
from .base_agent import BaseDecisionAgent
from typing import Dict, Any
import json

class AlgorithmSelectionAgent(BaseDecisionAgent):
    """
    Agent 1: Selects which ML algorithms to train based on data characteristics.
    """

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build algorithm selection prompt.

        Args:
            context: {
                "n_samples": int,
                "n_features": int,
                "target_type": str,
                "class_distribution": dict,
                "feature_correlations": dict,
                "computational_budget": dict
            }

        Returns:
            Formatted prompt
        """
        return f"""You are an expert ML algorithm selection agent. Analyze the following data
characteristics and recommend which algorithms to train:

**Data Profile:**
- Samples: {context['n_samples']}
- Features: {context['n_features']}
- Target type: {context['target_type']}
- Class distribution: {context.get('class_distribution', 'N/A')}
- Feature correlations: {context.get('feature_correlations', 'N/A')}

**Available Algorithms:**
Classification: [logistic_regression, random_forest, gradient_boosting, svm, knn]
Regression: [linear_regression, ridge, lasso, random_forest, gradient_boosting]

**Constraints:**
- Max training time: {context['computational_budget'].get('max_time_minutes', 60)} minutes
- Max parallel algorithms: {context['computational_budget'].get('max_parallel', 3)}

**Task:**
1. Recommend 3-5 algorithms to train (ordered by priority)
2. Explain reasoning for each selection
3. Suggest hyperparameter ranges for GridSearch
4. Estimate training time for each

**Output Format (JSON):**
{{
  "selected_algorithms": ["algo1", "algo2", "algo3"],
  "reasoning": {{"algo1": "Reason...", "algo2": "Reason..."}},
  "hyperparameter_suggestions": {{"algo1": {{}}, "algo2": {{}}}},
  "estimated_times": {{"algo1": 5.0, "algo2": 12.0}},
  "skip_algorithms": ["algo_x"],
  "skip_reasons": {{"algo_x": "Reason..."}}
}}
"""

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from Claude.

        Args:
            response: JSON string

        Returns:
            Parsed decision dictionary
        """
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()

        decision = json.loads(json_str)

        # Validate required fields
        assert "selected_algorithms" in decision
        assert isinstance(decision["selected_algorithms"], list)
        assert len(decision["selected_algorithms"]) > 0

        return decision

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return default algorithm selection if agent fails.

        Args:
            context: Context data

        Returns:
            Default safe selection
        """
        model_type = context.get("target_type", "classification")

        if "classification" in model_type:
            return {
                "selected_algorithms": ["random_forest", "gradient_boosting", "logistic_regression"],
                "reasoning": {
                    "random_forest": "Robust baseline, handles non-linearity",
                    "gradient_boosting": "Often highest accuracy",
                    "logistic_regression": "Fast, interpretable baseline"
                },
                "hyperparameter_suggestions": {},
                "estimated_times": {"random_forest": 30.0, "gradient_boosting": 45.0, "logistic_regression": 5.0},
                "skip_algorithms": [],
                "skip_reasons": {},
                "fallback": True
            }
        else:
            return {
                "selected_algorithms": ["random_forest", "gradient_boosting", "ridge"],
                "reasoning": {
                    "random_forest": "Robust baseline",
                    "gradient_boosting": "Often best performance",
                    "ridge": "Fast, regularized linear model"
                },
                "hyperparameter_suggestions": {},
                "estimated_times": {"random_forest": 30.0, "gradient_boosting": 45.0, "ridge": 5.0},
                "skip_algorithms": [],
                "skip_reasons": {},
                "fallback": True
            }


def algorithm_selection_agent_node(state: PipelineState) -> PipelineState:
    """
    LangGraph node for algorithm selection.

    Args:
        state: Pipeline state with feature_statistics, cleaned_data

    Returns:
        Updated state with algorithm_selection_decision, selected_algorithms
    """
    pass
```

---

### 4. ModelSelectionAgent (agents/model_selection.py)

```python
from .base_agent import BaseDecisionAgent
from typing import Dict, Any

class ModelSelectionAgent(BaseDecisionAgent):
    """
    Agent 2: Selects best model from trained algorithms.
    """

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build model selection prompt.

        Args:
            context: {
                "trained_models": [
                    {
                        "algorithm": str,
                        "cv_mean": float,
                        "test_accuracy": float,
                        "training_time": float,
                        "complexity": str
                    }
                ],
                "business_requirements": dict
            }

        Returns:
            Formatted prompt
        """
        pass

    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse model selection decision"""
        pass

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Return model with highest test accuracy"""
        models = context.get("trained_models", [])
        if not models:
            return {"selected_model": "random_forest", "fallback": True}

        best = max(models, key=lambda m: m.get("test_accuracy", 0))
        return {
            "selected_model": best["algorithm"],
            "reasoning": "Selected based on highest test accuracy (fallback decision)",
            "confidence": 0.7,
            "fallback": True
        }


def model_selection_agent_node(state: PipelineState) -> PipelineState:
    """
    LangGraph node for model selection.

    Args:
        state: Pipeline state with algorithm_results

    Returns:
        Updated state with model_selection_decision, best_model_name
    """
    pass
```

---

### 5. RetrainingDecisionAgent (agents/retraining_decision.py)

```python
from .base_agent import BaseDecisionAgent
from typing import Dict, Any

class RetrainingDecisionAgent(BaseDecisionAgent):
    """
    Agent 3: Decides if model retraining is needed.
    """

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build retraining decision prompt.

        Args:
            context: {
                "performance_analysis": {
                    "current_accuracy": float,
                    "baseline_accuracy": float,
                    "performance_drop": float
                },
                "drift_analysis": {
                    "drift_detected": bool,
                    "drift_score": float,
                    "affected_features": list
                },
                "business_context": dict
            }

        Returns:
            Formatted prompt
        """
        pass

    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse retraining decision"""
        pass

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conservative fallback: retrain if performance drop > 10% or significant drift
        """
        perf = context.get("performance_analysis", {})
        drift = context.get("drift_analysis", {})

        performance_drop = perf.get("performance_drop_pct", 0)
        drift_detected = drift.get("drift_detected", False)

        should_retrain = (performance_drop > 10.0) or (drift_detected and performance_drop > 5.0)

        return {
            "retrain": should_retrain,
            "reasoning": f"Fallback decision: performance drop {performance_drop}%, drift: {drift_detected}",
            "urgency": "high" if should_retrain else "low",
            "confidence": 0.6,
            "fallback": True
        }


def retraining_decision_agent_node(state: PipelineState) -> PipelineState:
    """
    LangGraph node for retraining decision.

    Args:
        state: Pipeline state with performance_comparison, drift_detected

    Returns:
        Updated state with retraining_decision, retraining_triggered
    """
    pass
```

---

## Algorithm Node Interfaces

### 6. BaseClassifierNode (nodes/classification/base.py)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import pandas as pd
from sklearn.model_selection import GridSearchCV
import mlflow
import time

class BaseClassifierNode(ABC):
    """
    Abstract base class for all classification algorithm nodes.

    Each algorithm (Logistic Regression, Random Forest, etc.) inherits from this
    and implements get_default_param_grid() and get_estimator().
    """

    def __init__(self, algorithm_name: str):
        """
        Initialize classifier node.

        Args:
            algorithm_name: Name of algorithm (e.g., "logistic_regression")
        """
        self.algorithm_name = algorithm_name

    @abstractmethod
    def get_default_param_grid(self) -> Dict[str, List]:
        """
        Return default hyperparameter grid for GridSearchCV.

        Returns:
            Dictionary mapping parameter names to lists of values

        Example:
            {
                "C": [0.1, 1.0, 10.0],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "saga"]
            }
        """
        pass

    @abstractmethod
    def get_estimator(self):
        """
        Return sklearn estimator instance.

        Returns:
            Sklearn classifier object

        Example:
            return LogisticRegression(random_state=42)
        """
        pass

    def train_with_gridsearch(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        param_grid: Dict[str, List],
        cv_folds: int = 5,
        scoring: str = 'f1_weighted'
    ) -> AlgorithmResult:
        """
        Train model with GridSearchCV and log to MLflow.

        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            param_grid: Hyperparameter grid
            cv_folds: Number of CV folds
            scoring: Scoring metric

        Returns:
            AlgorithmResult with model, metrics, and MLflow run ID

        Example:
            >>> node = LogisticRegressionNode()
            >>> result = node.train_with_gridsearch(X_train, y_train, X_test, y_test, param_grid)
            >>> assert "model" in result
            >>> assert "cv_mean" in result
            >>> assert "mlflow_run_id" in result
        """
        start_time = time.time()

        # Start MLflow child run
        with mlflow.start_run(run_name=self.algorithm_name, nested=True) as run:
            # Initialize GridSearchCV
            grid_search = GridSearchCV(
                estimator=self.get_estimator(),
                param_grid=param_grid,
                cv=cv_folds,
                scoring=scoring,
                n_jobs=-1,
                verbose=1,
                return_train_score=True
            )

            # Fit
            grid_search.fit(X_train, y_train)

            # Extract results
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            cv_scores = grid_search.cv_results_['mean_test_score']

            training_time = time.time() - start_time

            # Evaluate on test set
            from sklearn.metrics import accuracy_score, f1_score
            y_pred = best_model.predict(X_test)
            test_accuracy = accuracy_score(y_test, y_pred)
            test_f1 = f1_score(y_test, y_pred, average='weighted')

            # Log to MLflow
            mlflow.log_params(best_params)
            mlflow.log_params({"cv_folds": cv_folds, "scoring": scoring})
            mlflow.log_metrics({
                "train_accuracy": grid_search.best_score_,
                "test_accuracy": test_accuracy,
                "test_f1": test_f1,
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
                "training_time": training_time
            })
            mlflow.sklearn.log_model(best_model, "model")
            mlflow.log_dict(grid_search.cv_results_, "cv_results.json")

            return AlgorithmResult(
                model=best_model,
                best_params=best_params,
                cv_scores=cv_scores.tolist(),
                cv_mean=float(cv_scores.mean()),
                cv_std=float(cv_scores.std()),
                test_accuracy=float(test_accuracy),
                test_f1=float(test_f1),
                training_time=training_time,
                mlflow_run_id=run.info.run_id,
                predictions=y_pred
            )
```

---

### 7. Concrete Algorithm Nodes

#### LogisticRegressionNode (nodes/classification/logistic_regression.py)

```python
from .base import BaseClassifierNode
from sklearn.linear_model import LogisticRegression
from typing import Dict, List

class LogisticRegressionNode(BaseClassifierNode):
    """Logistic Regression algorithm node"""

    def __init__(self):
        super().__init__("logistic_regression")

    def get_default_param_grid(self) -> Dict[str, List]:
        return {
            "C": [0.01, 0.1, 1.0, 10.0],
            "penalty": ['l1', 'l2', 'elasticnet'],
            "solver": ['liblinear', 'saga'],
            "max_iter": [100, 500, 1000],
            "class_weight": ['balanced', None]
        }

    def get_estimator(self):
        return LogisticRegression(random_state=42)


def logistic_regression_node(state: PipelineState) -> PipelineState:
    """
    LangGraph node for Logistic Regression.

    Args:
        state: Pipeline state with X_train, y_train, X_test, y_test

    Returns:
        Updated state with algorithm_results["logistic_regression"]
    """
    pass
```

#### RandomForestClassifierNode

```python
from .base import BaseClassifierNode
from sklearn.ensemble import RandomForestClassifier

class RandomForestClassifierNode(BaseClassifierNode):
    def __init__(self):
        super().__init__("random_forest")

    def get_default_param_grid(self) -> Dict[str, List]:
        return {
            "n_estimators": [50, 100, 200],
            "max_depth": [None, 10, 20, 30],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ['sqrt', 'log2', None]
        }

    def get_estimator(self):
        return RandomForestClassifier(random_state=42)
```

---

### 8. BaseRegressorNode (nodes/regression/base.py)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import pandas as pd

class BaseRegressorNode(ABC):
    """
    Abstract base class for all regression algorithm nodes.

    Similar to BaseClassifierNode but with regression-specific metrics.
    """

    def __init__(self, algorithm_name: str):
        self.algorithm_name = algorithm_name

    @abstractmethod
    def get_default_param_grid(self) -> Dict[str, List]:
        pass

    @abstractmethod
    def get_estimator(self):
        pass

    def train_with_gridsearch(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        param_grid: Dict[str, List],
        cv_folds: int = 5,
        scoring: str = 'neg_root_mean_squared_error'
    ) -> AlgorithmResult:
        """
        Train regressor with GridSearchCV.

        Uses regression-specific metrics: RMSE, MAE, R²
        """
        # Similar to BaseClassifierNode but with regression metrics
        pass
```

---

## MLflow Utility Interfaces

### 9. MLflowLogger (mlflow_utils/logger.py)

```python
from typing import Dict, Any
import pandas as pd
import mlflow

class MLflowLogger:
    """
    Centralized MLflow logging utility.

    Provides consistent logging across all pipeline components.
    """

    @staticmethod
    def log_data_profile(data: pd.DataFrame, prefix: str = "data") -> None:
        """
        Log data profile to MLflow.

        Args:
            data: DataFrame to profile
            prefix: Prefix for parameter names

        Example:
            >>> MLflowLogger.log_data_profile(df, prefix="train")
            # Logs: train_rows, train_cols, train_memory_mb
        """
        mlflow.log_params({
            f"{prefix}_rows": data.shape[0],
            f"{prefix}_cols": data.shape[1],
            f"{prefix}_memory_mb": data.memory_usage().sum() / 1024**2
        })

    @staticmethod
    def log_preprocessing(metadata: Dict[str, Any]) -> None:
        """
        Log preprocessing metadata.

        Args:
            metadata: Preprocessing artifacts
        """
        mlflow.log_dict(metadata, "preprocessing/metadata.json")

    @staticmethod
    def log_agent_decision(
        agent_name: str,
        decision: Dict[str, Any],
        prompt: str,
        response: str
    ) -> None:
        """
        Log AI agent decision to MLflow.

        Args:
            agent_name: Name of agent (e.g., "algorithm_selection")
            decision: Structured decision dictionary
            prompt: Prompt sent to agent
            response: Raw agent response

        Example:
            >>> MLflowLogger.log_agent_decision(
            ...     "algorithm_selection",
            ...     decision_dict,
            ...     prompt_str,
            ...     response_str
            ... )
        """
        mlflow.log_dict(decision, f"agents/{agent_name}_decision.json")
        mlflow.log_text(prompt, f"agents/{agent_name}_prompt.txt")
        mlflow.log_text(response, f"agents/{agent_name}_response.txt")

    @staticmethod
    def log_feature_importance(importance: Dict[str, float]) -> None:
        """Log feature importance scores"""
        mlflow.log_dict(importance, "features/importance.json")

    @staticmethod
    def log_algorithm_result(
        algorithm_name: str,
        result: AlgorithmResult
    ) -> None:
        """Log algorithm training results"""
        mlflow.log_metrics({
            f"{algorithm_name}_cv_mean": result["cv_mean"],
            f"{algorithm_name}_test_acc": result["test_accuracy"],
            f"{algorithm_name}_training_time": result["training_time"]
        })
```

---

## Monitoring Module Interfaces

### 10. DriftDetector (monitoring/drift_detector.py)

```python
from typing import Dict, Any, List
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency
import numpy as np

class DriftDetector:
    """
    Detect data drift between training and test distributions.
    """

    def __init__(
        self,
        drift_threshold: float = 0.1,
        psi_threshold: float = 0.25
    ):
        """
        Initialize drift detector.

        Args:
            drift_threshold: KS test p-value threshold
            psi_threshold: PSI threshold for significance
        """
        self.drift_threshold = drift_threshold
        self.psi_threshold = psi_threshold

    def detect_drift(
        self,
        train_data: pd.DataFrame,
        test_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Detect drift across all features.

        Args:
            train_data: Training data distribution
            test_data: Test/production data distribution

        Returns:
            {
                "drift_detected": bool,
                "overall_drift_score": float,
                "feature_drift_scores": Dict[str, float],
                "drifted_features": List[str],
                "drift_details": Dict[str, Any]
            }

        Example:
            >>> detector = DriftDetector()
            >>> result = detector.detect_drift(train_df, test_df)
            >>> if result["drift_detected"]:
            ...     print(f"Drift in features: {result['drifted_features']}")
        """
        pass

    def calculate_ks_statistic(
        self,
        train_feature: pd.Series,
        test_feature: pd.Series
    ) -> float:
        """
        Calculate Kolmogorov-Smirnov statistic for numerical feature.

        Args:
            train_feature: Training feature values
            test_feature: Test feature values

        Returns:
            KS statistic (0 = identical, 1 = completely different)
        """
        statistic, pvalue = ks_2samp(train_feature, test_feature)
        return statistic

    def calculate_psi(
        self,
        expected: pd.Series,
        actual: pd.Series,
        bins: int = 10
    ) -> float:
        """
        Calculate Population Stability Index (PSI).

        PSI < 0.1: No significant drift
        0.1 <= PSI < 0.25: Moderate drift
        PSI >= 0.25: Significant drift

        Args:
            expected: Expected (training) distribution
            actual: Actual (test) distribution
            bins: Number of bins for discretization

        Returns:
            PSI value
        """
        pass


def evaluate_drift_node(state: PipelineState) -> PipelineState:
    """
    LangGraph node for drift detection.

    Args:
        state: Pipeline state with train_data, test_data

    Returns:
        Updated state with drift_detected, drift_score, drift_details
    """
    pass
```

---

### 11. PerformanceMonitor (monitoring/performance_monitor.py)

```python
from typing import Dict, Any
import pandas as pd

class PerformanceMonitor:
    """
    Monitor model performance against baseline.
    """

    def __init__(self, threshold: float = 0.05):
        """
        Initialize performance monitor.

        Args:
            threshold: Performance drop threshold (e.g., 0.05 = 5%)
        """
        self.threshold = threshold

    def compare_performance(
        self,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compare current performance against baseline.

        Args:
            current_metrics: Current model metrics
            baseline_metrics: Baseline (previous) metrics

        Returns:
            {
                "performance_drop": float,
                "performance_drop_pct": float,
                "threshold_exceeded": bool,
                "metric_comparison": Dict[str, Dict]
            }

        Example:
            >>> monitor = PerformanceMonitor(threshold=0.05)
            >>> result = monitor.compare_performance(
            ...     {"accuracy": 0.82},
            ...     {"accuracy": 0.90}
            ... )
            >>> print(result["performance_drop_pct"])  # 8.89
            >>> print(result["threshold_exceeded"])     # True
        """
        pass


def monitor_performance_node(state: PipelineState) -> PipelineState:
    """
    LangGraph node for performance monitoring.

    Args:
        state: Pipeline state with evaluation_results, baseline_performance

    Returns:
        Updated state with performance_comparison, performance_drop
    """
    pass
```

---

## Utility Interfaces

### 12. BedrockClient (utils/bedrock_client.py)

```python
import boto3
import json
import time
from typing import Optional

class BedrockClient:
    """
    AWS Bedrock client wrapper with retry logic and error handling.
    """

    def __init__(
        self,
        model_id: str,
        region: str,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ):
        """
        Initialize Bedrock client.

        Args:
            model_id: Claude model ID
            region: AWS region
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
        """
        self.model_id = model_id
        self.region = region
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = boto3.client('bedrock-runtime', region_name=region)

    def invoke_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        timeout: Optional[int] = None
    ) -> str:
        """
        Invoke Bedrock model with exponential backoff retry.

        Args:
            prompt: Prompt string
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds

        Returns:
            Response text from Claude

        Raises:
            Exception: If all retries fail

        Example:
            >>> client = BedrockClient("anthropic.claude-3-sonnet", "us-east-1")
            >>> response = client.invoke_with_retry("Analyze this data: ...")
        """
        for attempt in range(max_retries):
            try:
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    })
                )
                result = json.loads(response['body'].read())
                return result['content'][0]['text']
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                time.sleep(wait_time)

        raise Exception(f"Failed after {max_retries} retries")
```

---

## Configuration Interfaces

### 13. Enhanced Configuration (config/config.py)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class MLflowConfig:
    """MLflow configuration"""
    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "ml_pipeline_experiment"
    enable_logging: bool = True


@dataclass
class BedrockConfig:
    """AWS Bedrock configuration"""
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    region: str = "us-east-1"
    temperature: float = 0.0
    max_tokens: int = 4096
    enable_agents: bool = True


@dataclass
class TuningConfig:
    """Hyperparameter tuning configuration"""
    enable_tuning: bool = True
    tuning_method: str = "grid"  # grid, random
    cv_folds: int = 5
    n_jobs: int = -1


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    enable_monitoring: bool = True
    drift_threshold: float = 0.1
    psi_threshold: float = 0.25
    performance_drop_threshold: float = 0.05


@dataclass
class RetrainingConfig:
    """Retraining configuration"""
    enable_auto_retrain: bool = False
    retraining_threshold: float = 0.05


@dataclass
class EnhancedMLPipelineConfig:
    """Complete enhanced pipeline configuration"""
    # Data
    data_path: str
    target_column: str

    # Core configs (existing)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    feature_selection: FeatureSelectionConfig = field(default_factory=FeatureSelectionConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    # New configs
    mlflow: MLflowConfig = field(default_factory=MLflowConfig)
    bedrock: BedrockConfig = field(default_factory=BedrockConfig)
    tuning: TuningConfig = field(default_factory=TuningConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    retraining: RetrainingConfig = field(default_factory=RetrainingConfig)

    # Pipeline metadata
    pipeline_version: str = "2.0.0"
```

---

## Summary

This enhanced module interface specification provides:

✅ **Enhanced State Schema** with MLflow and agent fields
✅ **AI Decision Agent Interfaces** with retry logic and fallbacks
✅ **Base Algorithm Node Classes** for standardized training
✅ **MLflow Utility Interfaces** for consistent logging
✅ **Monitoring Module Interfaces** for drift and performance tracking
✅ **Bedrock Client Interface** with robust error handling
✅ **Enhanced Configuration** for all new components

All interfaces are designed for:
- Type safety with TypedDict and dataclasses
- Clear documentation with docstrings and examples
- Extensibility through abstract base classes
- Production-ready error handling
- Full MLflow integration
