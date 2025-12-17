# Project Structure - Enhanced ML Pipeline

## Overview

This document defines the complete project structure for the enhanced ML pipeline system with **natural language configuration extraction**, **MLflow experiment tracking**, **AWS Bedrock AI decision agents** (5 agents including algorithm-aware preprocessing), **individual algorithm nodes**, **hyperparameter tuning**, **performance monitoring**, **technique-based preprocessing**, and **triple prompt storage**.

---

## Complete Directory Structure

```
ml_pipeline/
│
├── README.md                          # Project overview and quick start
├── PROMPT.md                         # Implementation guide and methodology
├── DOCKER_README.md                  # Docker deployment guide
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package installation
├── .gitignore                        # Git ignore rules
├── .dockerignore                     # Docker ignore rules
├── .env.example                      # Environment variables template
├── Dockerfile.backend                # Backend Docker image
├── Dockerfile.frontend               # Frontend Docker image
├── docker-compose.yml                # Docker Compose orchestration
│
├── config/                           # Configuration files
│   ├── __init__.py
│   ├── config.py                     # Main configuration dataclasses
│   ├── default_config.yaml           # Default pipeline configuration
│   ├── mlflow_config.yaml            # MLflow-specific configuration
│   └── bedrock_config.yaml           # AWS Bedrock configuration
│
├── core/                             # Core pipeline components
│   ├── __init__.py
│   ├── state.py                      # Enhanced PipelineState schema
│   ├── graph.py                      # LangGraph workflow construction
│   ├── validators.py                 # State and data validators
│   └── exceptions.py                 # Custom exceptions
│
├── nodes/                            # LangGraph node implementations
│   ├── __init__.py
│   │
│   ├── preprocessing/                # Data preprocessing nodes
│   │   ├── __init__.py
│   │   ├── analyze_prompt.py        # Prompt analysis node (Agent 0)
│   │   ├── load_data.py             # Data loading node
│   │   ├── clean_data.py            # Data cleaning node
│   │   ├── handle_missing.py        # Missing value imputation
│   │   ├── encode_features.py       # Categorical encoding
│   │   ├── scale_features.py        # Feature scaling
│   │   └── techniques/              # Preprocessing technique registry
│   │       ├── __init__.py
│   │       ├── clean_data.py        # Outlier handling techniques (8 methods)
│   │       ├── handle_missing.py    # Missing value techniques (7 methods)
│   │       ├── encode_features.py   # Categorical encoding techniques (7 methods)
│   │       └── scale_features.py    # Feature scaling techniques (7 methods)
│   │
│   ├── feature_engineering/          # Feature engineering nodes
│   │   ├── __init__.py
│   │   ├── split_data.py            # Train/test split node
│   │   ├── select_features.py       # Feature selection node
│   │   └── transform_features.py    # Feature transformations
│   │
│   ├── classification/               # Classification algorithm nodes
│   │   ├── __init__.py
│   │   ├── base.py                  # BaseClassifierNode abstract class
│   │   ├── logistic_regression.py   # Logistic Regression node
│   │   ├── random_forest.py         # Random Forest node
│   │   ├── gradient_boosting.py     # Gradient Boosting node
│   │   ├── svm.py                   # SVM node
│   │   ├── knn.py                   # KNN node
│   │   └── xgboost_classifier.py    # XGBoost node (optional)
│   │
│   ├── regression/                   # Regression algorithm nodes
│   │   ├── __init__.py
│   │   ├── base.py                  # BaseRegressorNode abstract class
│   │   ├── linear_regression.py     # Linear Regression node
│   │   ├── ridge.py                 # Ridge Regression node
│   │   ├── lasso.py                 # Lasso Regression node
│   │   ├── random_forest.py         # Random Forest Regressor node
│   │   ├── gradient_boosting.py     # Gradient Boosting Regressor node
│   │   └── xgboost_regressor.py     # XGBoost Regressor node (optional)
│   │
│   ├── evaluation/                   # Evaluation nodes
│   │   ├── __init__.py
│   │   ├── evaluate_models.py       # Model evaluation node
│   │   └── generate_metrics.py      # Metric generation
│   │
│   └── reporting/                    # Reporting nodes
│       ├── __init__.py
│       ├── generate_report.py       # Report generation node
│       ├── create_visualizations.py # Visualization creation
│       └── save_artifacts.py        # Artifact saving node
│
├── agents/                           # AI Decision Agent implementations
│   ├── __init__.py
│   ├── base_agent.py                # BaseDecisionAgent abstract class
│   ├── config_extraction.py         # Agent 0: Configuration Extraction
│   ├── algorithm_category_predictor.py  # Agent 1A: Algorithm Category Prediction (NEW)
│   ├── preprocessing_question_generator.py  # Agent 1B: Preprocessing Questions (NEW)
│   ├── algorithm_selection.py       # Agent 2: Algorithm Selection
│   ├── model_selection.py           # Agent 3: Model Selection
│   ├── retraining_decision.py       # Agent 4: Retraining Decision
│   └── prompts/                     # Agent prompt templates
│       ├── __init__.py
│       ├── config_extraction_prompt.txt
│       ├── algorithm_category_prompt.txt    # Agent 1A prompt (NEW)
│       ├── preprocessing_questions_prompt.txt  # Agent 1B prompt (NEW)
│       ├── algorithm_selection_prompt.txt
│       ├── model_selection_prompt.txt
│       └── retraining_decision_prompt.txt
│
├── tuning/                           # Hyperparameter tuning modules
│   ├── __init__.py
│   ├── grid_search.py               # GridSearchCV wrapper
│   ├── random_search.py             # RandomizedSearchCV wrapper
│   ├── param_grids.py               # Default parameter grids
│   └── tuner.py                     # Unified tuning interface
│
├── monitoring/                       # Performance monitoring modules
│   ├── __init__.py
│   ├── drift_detector.py            # Data drift detection
│   ├── performance_monitor.py       # Performance comparison
│   ├── metrics_calculator.py        # Metric calculations
│   └── alerting.py                  # Alert generation
│
├── retraining/                       # Retraining modules
│   ├── __init__.py
│   ├── trigger.py                   # Retraining trigger logic
│   ├── scheduler.py                 # Retraining scheduler
│   └── pipeline_executor.py         # Automated pipeline execution
│
├── mlflow_utils/                     # MLflow integration utilities
│   ├── __init__.py
│   ├── logger.py                    # MLflowLogger class
│   ├── experiment_manager.py        # Experiment management
│   ├── model_registry.py            # Model registry operations
│   └── run_context.py               # Run context management
│
├── utils/                            # General utilities
│   ├── __init__.py
│   ├── bedrock_client.py            # AWS Bedrock client wrapper
│   ├── prompt_storage.py            # Triple prompt storage (DB + MLflow + S3)
│   ├── data_utils.py                # Data manipulation utilities
│   ├── file_utils.py                # File I/O utilities
│   ├── logging_utils.py             # Python logging configuration
│   └── metrics_utils.py             # Metric calculation helpers
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   │
│   ├── unit/                        # Unit tests
│   │   ├── test_state.py
│   │   ├── test_preprocessing.py
│   │   ├── test_analyze_prompt_node.py
│   │   ├── test_agents.py
│   │   ├── test_config_extraction_agent.py
│   │   ├── test_algorithm_nodes.py
│   │   ├── test_monitoring.py
│   │   └── test_mlflow_utils.py
│   │
│   ├── integration/                 # Integration tests
│   │   ├── test_graph_execution.py
│   │   ├── test_mlflow_integration.py
│   │   └── test_bedrock_integration.py
│   │
│   └── e2e/                         # End-to-end tests
│       └── test_full_pipeline.py
│
├── api/                              # FastAPI backend
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── models/                      # Pydantic models
│   │   ├── __init__.py
│   │   └── pipeline.py             # Pipeline request/response models
│   └── routers/                     # API routers
│       ├── __init__.py
│       └── pipeline.py              # Pipeline endpoints
│
├── frontend/                         # Vue.js 3 UI (ChatGPT-like interface)
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js              # Vite build configuration
│   ├── index.html                  # HTML entry point
│   ├── Dockerfile                  # Frontend Docker image
│   ├── nginx.conf                  # Nginx production server config
│   ├── .env.example                # Environment variables template
│   ├── public/                     # Static assets
│   │   └── favicon.ico
│   └── src/                        # Vue.js source code
│       ├── main.js                 # Application entry point
│       ├── App.vue                 # Root component
│       ├── router/                 # Vue Router configuration
│       │   └── index.js
│       ├── stores/                 # Pinia state management
│       │   ├── pipeline.js         # Pipeline state store
│       │   └── runs.js             # Run history store
│       ├── services/               # Backend communication
│       │   ├── api.js              # API client (Axios)
│       │   └── websocket.js        # Real-time updates (WebSocket/SSE)
│       ├── components/             # Vue components
│       │   ├── layout/
│       │   │   ├── Sidebar.vue     # Left sidebar (run history)
│       │   │   ├── MainContent.vue # Right content area
│       │   │   └── Header.vue      # Top header
│       │   ├── pipeline/
│       │   │   ├── PromptInput.vue        # Natural language input
│       │   │   ├── PipelineConfig.vue     # Config display
│       │   │   ├── StateChart.vue         # LangGraph diagram (Mermaid)
│       │   │   ├── MetricsPanel.vue       # Pipeline metrics
│       │   │   └── ReviewForm.jsx         # Human-in-the-loop review UI (NEW)
│       │   ├── history/
│       │   │   ├── RunList.vue            # List of runs
│       │   │   ├── RunItem.vue            # Single run item
│       │   │   └── RunDetails.vue         # Run details modal
│       │   └── common/
│       │       ├── Button.vue
│       │       ├── Input.vue
│       │       ├── Card.vue
│       │       └── Loading.vue
│       ├── views/                  # Page-level components
│       │   ├── Home.vue            # Main pipeline view
│       │   └── RunDetail.vue       # Detailed run view
│       ├── composables/            # Vue composables
│       │   ├── usePipeline.js      # Pipeline logic
│       │   └── useRealtime.js      # Realtime updates
│       ├── utils/                  # Utility functions
│       │   ├── format.js           # Formatting utilities
│       │   └── constants.js        # Constants
│       └── assets/                 # Assets
│           └── styles/
│               ├── main.css         # Global styles
│               └── variables.css    # CSS variables
│
├── scripts/                          # Utility scripts
│   ├── setup_mlflow.sh              # MLflow server setup script
│   ├── run_pipeline.py              # Pipeline execution script
│   ├── evaluate_model.py            # Model evaluation script
│   └── deploy_model.py              # Model deployment script
│
├── data/                             # Data directory (gitignored)
│   ├── raw/                         # Raw input data
│   ├── processed/                   # Processed data
│   └── external/                    # External data sources
│
├── outputs/                          # Pipeline outputs (gitignored)
│   ├── models/                      # Trained model artifacts
│   ├── metrics/                     # Evaluation metrics
│   ├── plots/                       # Generated plots
│   ├── reports/                     # Generated reports
│   └── logs/                        # Pipeline execution logs
│
├── mlruns/                          # MLflow tracking directory (gitignored)
│
├── notebooks/                        # Jupyter notebooks
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_comparison.ipynb
│   └── 04_drift_analysis.ipynb
│
└── docs/                            # Documentation
    ├── README.md
    ├── LANGGRAPH_DESIGN.md          # LangGraph architecture design
    ├── COMPONENT_SPECIFICATIONS.md   # Component specifications
    ├── MODULE_INTERFACES.md          # Module interface definitions
    ├── DATA_FLOW_ARCHITECTURE.md     # Data flow documentation
    ├── PROJECT_STRUCTURE.md          # This file
    ├── BEDROCK_SETUP.md              # AWS Bedrock configuration guide
    ├── API_REFERENCE.md              # API documentation
    ├── DEPLOYMENT_GUIDE.md           # Deployment instructions
    └── TROUBLESHOOTING.md            # Common issues and solutions
```

---

## Key Directory Descriptions

### `/config/` - Configuration Management

**Purpose**: Centralized configuration for all pipeline components

**Key Files**:
- `config.py`: Main configuration dataclasses (EnhancedMLPipelineConfig, MLflowConfig, BedrockConfig, etc.)
- `default_config.yaml`: Default pipeline parameters
- `mlflow_config.yaml`: MLflow tracking URI, experiment names, registry settings
- `bedrock_config.yaml`: AWS region, model IDs, temperature settings

**Example `config.py` Structure**:
```python
@dataclass
class MLflowConfig:
    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "ml_pipeline_experiment"
    enable_logging: bool = True

@dataclass
class BedrockConfig:
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    region: str = "us-east-1"
    temperature: float = 0.0
    enable_agents: bool = True
```

---

### `/core/` - Core Pipeline Components

**Purpose**: Fundamental pipeline infrastructure

**Key Files**:
- `state.py`: Enhanced PipelineState TypedDict with all MLflow and agent fields
- `graph.py`: LangGraph StateGraph construction with all nodes and conditional edges
- `validators.py`: State validation logic
- `exceptions.py`: Custom exception classes (AgentFailureException, DriftDetectedException, etc.)

**Example `state.py` Structure**:
```python
class PipelineState(TypedDict, total=False):
    # Data
    raw_data: pd.DataFrame
    X_train: pd.DataFrame
    y_train: pd.Series

    # MLflow
    mlflow_experiment_id: str
    mlflow_run_id: str

    # Agents
    algorithm_selection_decision: Dict[str, Any]
    model_selection_decision: Dict[str, Any]
    retraining_decision: Dict[str, Any]

    # Results
    algorithm_results: Dict[str, Dict[str, Any]]
    best_model_name: str
```

---

### `/nodes/` - LangGraph Node Implementations

**Purpose**: All LangGraph node functions organized by category

#### `/nodes/preprocessing/`
**Contains**: Data loading, cleaning, imputation, encoding, scaling nodes

**Example Node**:
```python
# nodes/preprocessing/load_data.py
def load_data_node(state: PipelineState) -> PipelineState:
    """Load data and initialize MLflow run"""
    data_path = state["pipeline_config"]["data_path"]

    # Start MLflow run
    mlflow.start_run(experiment_id=state["mlflow_experiment_id"])

    # Load data
    raw_data = pd.read_csv(data_path)

    # Log to MLflow
    mlflow.log_params({
        "data_path": data_path,
        "n_rows": raw_data.shape[0],
        "n_cols": raw_data.shape[1]
    })

    return {
        **state,
        "raw_data": raw_data,
        "mlflow_run_id": mlflow.active_run().info.run_id
    }
```

#### `/nodes/classification/`
**Contains**: Individual classification algorithm nodes (Logistic Regression, Random Forest, etc.)

**Example Structure**:
```python
# nodes/classification/random_forest.py
from .base import BaseClassifierNode
from sklearn.ensemble import RandomForestClassifier

class RandomForestNode(BaseClassifierNode):
    def __init__(self):
        super().__init__("random_forest")

    def get_default_param_grid(self):
        return {
            "n_estimators": [100, 200],
            "max_depth": [10, 20, None],
            "min_samples_split": [2, 5]
        }

    def get_estimator(self):
        return RandomForestClassifier(random_state=42)

def random_forest_node(state: PipelineState) -> PipelineState:
    """LangGraph node for Random Forest training"""
    if "random_forest" not in state.get("selected_algorithms", []):
        return state  # Skip if not selected by agent

    node = RandomForestNode()
    result = node.train_with_gridsearch(
        X_train=state["X_train"],
        y_train=state["y_train"],
        X_test=state["X_test"],
        y_test=state["y_test"],
        param_grid=node.get_default_param_grid()
    )

    algorithm_results = state.get("algorithm_results", {})
    algorithm_results["random_forest"] = result

    return {**state, "algorithm_results": algorithm_results}
```

#### `/nodes/regression/`
**Contains**: Individual regression algorithm nodes (Linear, Ridge, Lasso, etc.)

Similar structure to classification nodes but with regression-specific metrics (RMSE, MAE, R²).

---

### `/agents/` - AI Decision Agent Implementations

**Purpose**: AWS Bedrock Claude agents for intelligent decision-making

**Key Files**:
- `base_agent.py`: BaseDecisionAgent abstract class with retry logic
- `config_extraction.py`: Agent 0 - Extracts pipeline config from natural language
- `algorithm_category_predictor.py`: Agent 1A - Predicts optimal algorithm category
- `preprocessing_question_generator.py`: Agent 1B - Generates algorithm-aware preprocessing questions
- `algorithm_selection.py`: Agent 2 - Selects which algorithms to train
- `model_selection.py`: Agent 3 - Selects best model from trained algorithms
- `retraining_decision.py`: Agent 4 - Decides if retraining is needed

**Example Agent Structure**:
```python
# agents/algorithm_selection.py
class AlgorithmSelectionAgent(BaseDecisionAgent):
    def build_prompt(self, context: Dict[str, Any]) -> str:
        return f"""You are an ML algorithm selection expert...

        Data Profile:
        - Samples: {context['n_samples']}
        - Features: {context['n_features']}
        - Target type: {context['target_type']}

        Task: Select 3-5 algorithms to train based on data characteristics.
        Output JSON with: selected_algorithms, reasoning, hyperparameter_suggestions
        """

    def parse_response(self, response: str) -> Dict[str, Any]:
        # Extract JSON from response
        json_str = extract_json(response)
        return json.loads(json_str)

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Fallback if agent fails
        return {
            "selected_algorithms": ["random_forest", "gradient_boosting", "logistic_regression"],
            "reasoning": "Default safe selection",
            "fallback": True
        }

def algorithm_selection_agent_node(state: PipelineState) -> PipelineState:
    """LangGraph node wrapper for agent"""
    agent = AlgorithmSelectionAgent(
        bedrock_model_id=state["bedrock_model_id"],
        aws_region=state["aws_region"]
    )

    context = build_context_from_state(state)
    result = agent.invoke(context)

    # Log to MLflow
    MLflowLogger.log_agent_decision(
        "algorithm_selection",
        result["decision"],
        result["prompt"],
        result["response"]
    )

    return {
        **state,
        "algorithm_selection_decision": result["decision"],
        "selected_algorithms": result["decision"]["selected_algorithms"]
    }
```

---

### `/tuning/` - Hyperparameter Tuning

**Purpose**: Unified hyperparameter tuning interface

**Key Files**:
- `grid_search.py`: GridSearchCV implementation
- `param_grids.py`: Default parameter grids for all algorithms
- `tuner.py`: Abstract tuning interface

**Example `param_grids.py`**:
```python
CLASSIFICATION_PARAM_GRIDS = {
    "logistic_regression": {
        "C": [0.01, 0.1, 1.0, 10.0],
        "penalty": ["l1", "l2"],
        "solver": ["liblinear", "saga"]
    },
    "random_forest": {
        "n_estimators": [50, 100, 200],
        "max_depth": [None, 10, 20, 30],
        "min_samples_split": [2, 5, 10]
    }
}
```

---

### `/monitoring/` - Performance Monitoring

**Purpose**: Data drift detection and performance comparison

**Key Files**:
- `drift_detector.py`: DriftDetector class with KS test, Chi², PSI
- `performance_monitor.py`: PerformanceMonitor class for baseline comparison
- `metrics_calculator.py`: Standard metric calculations
- `alerting.py`: Alert generation when thresholds exceeded

**Example `drift_detector.py`**:
```python
class DriftDetector:
    def detect_drift(
        self,
        train_data: pd.DataFrame,
        test_data: pd.DataFrame
    ) -> Dict[str, Any]:
        drifted_features = []
        feature_scores = {}

        for col in train_data.columns:
            if is_numerical(col):
                ks_stat, p_value = ks_2samp(train_data[col], test_data[col])
                if p_value < 0.05:
                    drifted_features.append(col)
                feature_scores[col] = ks_stat

        return {
            "drift_detected": len(drifted_features) > 0,
            "drifted_features": drifted_features,
            "feature_drift_scores": feature_scores
        }
```

---

### `/mlflow_utils/` - MLflow Integration

**Purpose**: Centralized MLflow logging and management

**Key Files**:
- `logger.py`: MLflowLogger class with standard logging methods
- `experiment_manager.py`: Experiment creation and management
- `model_registry.py`: Model registration and versioning
- `run_context.py`: MLflow run context helpers

**Example `logger.py`**:
```python
class MLflowLogger:
    @staticmethod
    def log_agent_decision(
        agent_name: str,
        decision: Dict[str, Any],
        prompt: str,
        response: str
    ):
        mlflow.log_dict(decision, f"agents/{agent_name}_decision.json")
        mlflow.log_text(prompt, f"agents/{agent_name}_prompt.txt")
        mlflow.log_text(response, f"agents/{agent_name}_response.txt")

    @staticmethod
    def log_algorithm_result(algorithm_name: str, result: AlgorithmResult):
        mlflow.log_metrics({
            f"{algorithm_name}_cv_mean": result["cv_mean"],
            f"{algorithm_name}_test_acc": result["test_accuracy"]
        })
```

---

### `/utils/` - General Utilities

**Purpose**: Reusable utility functions

**Key Files**:
- `bedrock_client.py`: BedrockClient wrapper with retry logic
- `data_utils.py`: Data manipulation helpers
- `file_utils.py`: File I/O operations
- `metrics_utils.py`: Metric calculation helpers

---

### `/tests/` - Test Suite

**Purpose**: Comprehensive test coverage

**Structure**:
- `unit/`: Test individual functions and classes
- `integration/`: Test component interactions
- `e2e/`: Test full pipeline execution

**Example Unit Test**:
```python
# tests/unit/test_agents.py
def test_algorithm_selection_agent():
    agent = AlgorithmSelectionAgent(
        bedrock_model_id="anthropic.claude-3-sonnet",
        aws_region="us-east-1"
    )

    context = {
        "n_samples": 1000,
        "n_features": 15,
        "target_type": "binary_classification"
    }

    result = agent.invoke(context)

    assert "decision" in result
    assert "selected_algorithms" in result["decision"]
    assert len(result["decision"]["selected_algorithms"]) >= 3
```

---

## Implementation Order

When implementing the enhanced ML pipeline, follow this recommended order:

### Phase 1: Foundation (Week 1)
1. ✅ Set up project structure
2. ✅ Create `core/state.py` with enhanced PipelineState
3. ✅ Implement basic preprocessing nodes
4. ✅ Set up MLflow tracking server
5. ✅ Create `mlflow_utils/logger.py`

### Phase 2: Algorithm Nodes (Week 2)
6. ✅ Implement `nodes/classification/base.py` (BaseClassifierNode)
7. ✅ Implement individual classification nodes (Logistic Regression, Random Forest, etc.)
8. ✅ Implement `nodes/regression/base.py` (BaseRegressorNode)
9. ✅ Implement individual regression nodes
10. ✅ Add hyperparameter tuning with GridSearchCV

### Phase 3: AI Agents (Week 3)
11. ✅ Implement `agents/base_agent.py` (BaseDecisionAgent)
12. ✅ Implement `utils/bedrock_client.py`
13. ✅ Implement Agent 0: Configuration Extraction
14. ✅ Implement Agent 1A: Algorithm Category Prediction
15. ✅ Implement Agent 1B: Preprocessing Question Generation
16. ✅ Implement Agent 2: Algorithm Selection
17. ✅ Implement Agent 3: Model Selection
18. ✅ Test agent integration with MLflow

### Phase 4: Monitoring (Week 4)
19. ✅ Implement `monitoring/drift_detector.py`
20. ✅ Implement `monitoring/performance_monitor.py`
21. ✅ Implement Agent 4: Retraining Decision
22. ✅ Add monitoring nodes to graph

### Phase 5: Integration (Week 5)
23. ✅ Construct complete LangGraph in `core/graph.py`
24. ✅ Add conditional routing based on agent decisions
25. ✅ Implement end-to-end pipeline execution
26. ✅ Add comprehensive MLflow logging at all stages

### Phase 6: Testing & Deployment (Week 6)
27. ✅ Write unit tests for all components
28. ✅ Write integration tests
29. ✅ Write end-to-end tests
30. ✅ Create deployment scripts
31. ✅ Document API and usage

---

## Dependencies

### Core Dependencies
```
# requirements.txt
langgraph>=0.0.30
langchain>=0.1.0
langchain-aws>=0.1.0
mlflow>=2.10.0
boto3>=1.34.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.4.0
scipy>=1.11.0
```

### Optional Dependencies
```
# requirements-dev.txt
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.1.0
mypy>=1.7.0
jupyter>=1.0.0
xgboost>=2.0.0  # Optional algorithm
```

---

## Environment Setup

### Required Environment Variables
```bash
# .env.example

# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_TEMPERATURE=0.0
BEDROCK_MAX_TOKENS=4096

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=ml_pipeline_experiment

# Pipeline Configuration
DEFAULT_DATA_PATH=data/raw/train.csv
DEFAULT_TARGET_COLUMN=target
OUTPUT_DIR=outputs
```

---

## File Size Estimates

- **Total Python Files**: ~50 files
- **Core Logic**: ~3,000 lines
- **Agent Implementations**: ~1,500 lines
- **Algorithm Nodes**: ~2,000 lines
- **Monitoring**: ~800 lines
- **Tests**: ~2,500 lines
- **Total**: ~10,000 lines of production code

---

## Git Structure

### Important `.gitignore` Entries
```
# Data
data/raw/*
data/processed/*
!data/.gitkeep

# Outputs
outputs/*
!outputs/.gitkeep

# MLflow
mlruns/
mlartifacts/

# Environment
.env
.venv/
venv/

# IDE
.vscode/
.idea/

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
```

---

## Detailed File Descriptions

### Root Level Files

#### `README.md`
**Purpose**: Project overview and quick start guide
**Description**: Comprehensive documentation including:
- Project features and architecture overview
- Quick start installation instructions
- Configuration guide
- Usage examples
- Links to detailed documentation
- Contributing guidelines

#### `requirements.txt`
**Purpose**: Python package dependencies
**Description**: Lists all required Python packages with version constraints:
- Core: langgraph, langchain, langchain-aws, mlflow, boto3
- Data Science: pandas, numpy, scikit-learn, scipy
- Visualization: matplotlib, seaborn, plotly
- Configuration: pyyaml, python-dotenv
- Optional: xgboost, lightgbm, catboost

#### `setup.py`
**Purpose**: Package installation and distribution configuration
**Description**: Defines:
- Package metadata (name, version, author, description)
- Dependencies and extras_require
- Entry points for console scripts
- Package data and classifiers
- Installation requirements

#### `.gitignore`
**Purpose**: Git version control ignore patterns
**Description**: Specifies files to exclude from version control:
- Python artifacts (__pycache__, *.pyc)
- Virtual environments (venv/, .venv/)
- Data directories (data/raw/, data/processed/)
- Output directories (outputs/, mlruns/)
- IDE files (.vscode/, .idea/)
- Environment files (.env)
- Model binaries (*.pkl, *.h5)

#### `.env.example`
**Purpose**: Environment variables template
**Description**: Template for .env file with all configurable parameters:
- AWS credentials and region
- Bedrock model configuration
- MLflow tracking URI and settings
- Pipeline parameters (data paths, thresholds)
- Tuning configuration
- Monitoring settings
- Logging configuration

#### `PROMPT.md`
**Purpose**: Master implementation guide and methodology
**Description**: Comprehensive implementation guide that:
- Defines core implementation principle: "bits and bits" (incremental, step-by-step development)
- Documents implementation workflow: Check Documentation → Plan → Execute → Update → Verify
- Lists all documentation files with descriptions and when to use each
- Provides 6-step implementation guidelines
- Includes common implementation scenarios with examples
- Defines testing, MLflow logging, and configuration requirements
- Provides documentation update checklist
- Includes version control guidelines with commit message format
- Contains complete walkthrough example (Adding XGBoost classifier)
- Establishes mandatory documentation-first approach
- Serves as contract for all future implementations

#### `DOCKER_README.md`
**Purpose**: Docker deployment comprehensive guide
**Description**: Complete Docker deployment documentation:
- Architecture overview (3 services: MLflow, FastAPI, Streamlit)
- Prerequisites and requirements
- Quick start instructions
- Service access URLs and ports
- Streamlit dashboard usage guide
- API usage examples with curl commands
- Docker Compose command reference (start, stop, logs, restart)
- Volume management and data persistence
- Backup and restore procedures
- Comprehensive troubleshooting section
- Development mode instructions
- Production deployment considerations
- Horizontal and vertical scaling strategies
- Monitoring and cleanup procedures
- Links to additional resources

#### `.dockerignore`
**Purpose**: Docker build ignore patterns
**Description**: Optimizes Docker builds by excluding:
- Git files and repositories
- Python bytecode and caches
- Virtual environments
- Large data files (data/raw/*, data/processed/*)
- Output directories (outputs/*, mlruns/, mlartifacts/)
- IDE configuration files
- Jupyter notebooks and checkpoints
- Documentation files
- Test files and pytest cache
- Temporary and log files
- OS-specific files

#### `Dockerfile.backend`
**Purpose**: Backend Docker image definition
**Description**: Multi-stage Docker build for FastAPI backend:
- Based on python:3.10-slim
- Installs system dependencies (gcc, g++, git, curl)
- Installs Python dependencies from requirements.txt
- Copies application code (config/, core/, nodes/, api/, etc.)
- Creates necessary directories (data/, outputs/, mlruns/)
- Sets environment variables (PYTHONUNBUFFERED, PYTHONPATH)
- Exposes port 8000
- Includes health check endpoint
- Runs uvicorn server with hot reload enabled
- ~500MB final image size

#### `Dockerfile.frontend`
**Purpose**: Frontend Docker image definition
**Description**: Streamlit UI Docker image:
- Based on python:3.10-slim
- Installs curl for health checks
- Installs frontend dependencies (streamlit, requests, pandas)
- Copies Streamlit application code
- Sets Streamlit environment variables
- Exposes port 8501
- Includes health check for Streamlit core
- Runs Streamlit server on all interfaces
- ~300MB final image size

#### `docker-compose.yml`
**Purpose**: Multi-service orchestration
**Description**: Defines complete ML pipeline stack:
- **mlflow service**:
  - Official MLflow image (v2.10.0)
  - Port 5000
  - SQLite backend store
  - Local artifact storage
  - Health check enabled
- **backend service**:
  - FastAPI application
  - Port 8000
  - Depends on MLflow
  - Volume mounts for data, outputs, config
  - Environment variables for MLflow and AWS
  - Health check enabled
  - Auto-restart policy
- **frontend service**:
  - Streamlit UI
  - Port 8501
  - Depends on backend
  - Health check enabled
  - Auto-restart policy
- Defines ml-pipeline-network bridge network
- Declares named volumes for persistence
- Service dependencies with health conditions

---

### `/config/` - Configuration Files

#### `config/__init__.py`
**Purpose**: Configuration module exports
**Description**: Exports all configuration classes and functions:
- EnhancedMLPipelineConfig
- MLflowConfig, BedrockConfig
- TuningConfig, MonitoringConfig
- load_config(), get_default_config()

#### `config/config.py`
**Purpose**: Configuration dataclasses and loaders
**Description**: Defines configuration dataclasses with:
- **MLflowConfig**: tracking_uri, experiment_name, enable_logging
- **BedrockConfig**: model_id, region, temperature, max_retries
- **TuningConfig**: enable_tuning, method, cv_folds, scoring
- **MonitoringConfig**: drift thresholds, performance thresholds
- **RetrainingConfig**: auto retraining settings, schedules
- **DataConfig**: data paths, validation parameters
- **AlgorithmConfig**: available algorithms, optional libraries
- **OutputConfig**: output directory paths
- Methods: from_env(), from_yaml(), to_dict(), save_to_yaml()

#### `config/default_config.yaml`
**Purpose**: Default pipeline configuration
**Description**: YAML file with default values for:
- Data configuration (paths, target column, test size)
- MLflow settings (tracking URI, experiment name)
- Bedrock settings (model ID, temperature)
- Tuning parameters (CV folds, n_jobs)
- Monitoring thresholds
- Algorithm selections

#### `config/mlflow_config.yaml`
**Purpose**: MLflow-specific configuration
**Description**: Comprehensive MLflow settings:
- Tracking server configuration (URI, backend store)
- Artifact storage (local, S3, Azure, GCS)
- Experiment definitions
- Model registry configuration
- Logging settings (params, metrics, artifacts)
- Auto-logging configuration
- UI settings
- Cleanup policies

#### `config/bedrock_config.yaml`
**Purpose**: AWS Bedrock configuration
**Description**: Bedrock-specific settings:
- AWS region and credentials
- Model selection (Claude-3 variants)
- Model parameters (temperature, max_tokens, top_p)
- Agent-specific configurations (5 agents: Agent 0, 1A, 1B, 2, 3, 4)
- Retry and error handling
- Timeout configuration
- Cost tracking and budgets
- Guardrails and validation

---

### `/core/` - Core Pipeline Components

#### `core/__init__.py`
**Purpose**: Core module exports
**Description**: Exports core classes and functions:
- PipelineState, AlgorithmResult
- create_pipeline_graph(), compile_pipeline()
- validate_state(), validate_data()
- All exception classes

#### `core/state.py`
**Purpose**: Pipeline state schema definition
**Description**: Defines the complete pipeline state using TypedDict:
- **PipelineState**: 50+ state fields organized by category
  - Configuration fields (pipeline_config, pipeline_run_id)
  - Data fields (raw_data, cleaned_data, X_train, y_train, etc.)
  - MLflow fields (experiment_id, run_id, tracking_uri)
  - Agent decision fields (5 agents: config extraction, algorithm category, preprocessing questions, algorithm selection, model selection, retraining)
  - Algorithm results
  - Monitoring results (drift, performance)
  - Artifacts and metadata
- **AlgorithmResult**: Standard result structure for trained models
- Helper functions: create_initial_state(), update_state(), add_error(), mark_node_completed()

#### `core/graph.py`
**Purpose**: LangGraph workflow construction
**Description**: Creates the complete DAG workflow:
- Defines StateGraph with PipelineState
- Adds all preprocessing nodes
- Adds feature engineering nodes
- Adds AI agent nodes
- Adds algorithm training nodes (classification & regression)
- Adds evaluation and reporting nodes
- Defines edges (sequential and conditional)
- Implements routing logic (route_to_algorithms, should_retrain_model)
- compile_pipeline() function to create executable workflow

#### `core/validators.py`
**Purpose**: State and data validation
**Description**: Validation functions:
- **validate_state()**: Checks required state keys present
- **validate_data()**: Validates input data quality
  - Minimum samples check
  - Missing value ratio validation
  - Duplicate detection
  - Constant feature detection
- **validate_train_test_split()**: Validates split consistency
- **validate_model_input()**: Validates model-ready data
- **validate_algorithm_results()**: Validates training outputs

#### `core/exceptions.py`
**Purpose**: Custom exception definitions
**Description**: Defines 15+ exception classes:
- **PipelineException**: Base exception
- **StateValidationError**: State validation failures
- **DataValidationError**: Data validation failures
- **AgentFailureException**: AI agent errors
- **DriftDetectedException**: Drift detection alerts
- **ModelTrainingError**: Training failures
- **HyperparameterTuningError**: Tuning failures
- **MLflowError**: MLflow operation errors
- **BedrockError**: Bedrock API errors
- Additional specialized exceptions

---

### `/nodes/preprocessing/` - Data Preprocessing Nodes

#### `nodes/preprocessing/__init__.py`
**Purpose**: Preprocessing module exports
**Description**: Exports all preprocessing node functions

#### `nodes/preprocessing/analyze_prompt.py`
**Purpose**: Natural language configuration extraction (NEW)
**Description**: LangGraph node that executes BEFORE load_data node:
- Receives user_prompt and data_path from user
- Performs quick data peek (first 100 rows) to get column names and dtypes
- Invokes ConfigExtraction Agent (Agent 0) with context
- Extracts configuration from natural language:
  - target_column
  - experiment_name
  - test_size
  - random_state
  - analysis_type (classification/regression)
- Validates confidence threshold (>= 70%)
- Stores prompt in triple storage (MLflow + PostgreSQL + MinIO/S3)
- Updates pipeline_config in state with extracted values
- Logs extraction metadata to MLflow

**Example Node Function**:
```python
def analyze_prompt_node(state: PipelineState) -> PipelineState:
    """Analyze user prompt and extract pipeline configuration using Bedrock"""
    user_prompt = state["user_prompt"]
    data_path = state["data_path"]

    # Quick data peek for column names
    data_preview = pd.read_csv(data_path, nrows=100)

    # Invoke Agent 0
    agent = ConfigExtractionAgent(
        bedrock_model_id=state["bedrock_model_id"],
        aws_region=state["aws_region"]
    )

    context = {
        "user_prompt": user_prompt,
        "data_path": data_path,
        "available_columns": data_preview.columns.tolist(),
        "dataset_preview": {
            "n_rows": len(data_preview),
            "n_columns": len(data_preview.columns),
            "dtypes": data_preview.dtypes.to_dict()
        }
    }

    result = agent.invoke(context)

    # Validate confidence
    if result["decision"]["confidence"] < 0.70:
        raise ValueError(f"Confidence {result['decision']['confidence']} below threshold")

    # Store prompt
    prompt_storage.save_prompt(
        user_prompt=user_prompt,
        extracted_config=result["decision"],
        pipeline_run_id=state["pipeline_run_id"]
    )

    # Update state
    return {
        **state,
        "pipeline_config": result["decision"],
        "config_confidence": result["decision"]["confidence"],
        "config_reasoning": result["decision"]["reasoning"]
    }
```

#### `nodes/preprocessing/load_data.py`
**Purpose**: Data loading and initialization
**Description**: LangGraph node that:
- Loads data from CSV/Parquet/Excel
- Starts MLflow run
- Validates data quality
- Creates data profile
- Logs data statistics to MLflow
- Updates state with raw_data and mlflow_run_id

#### `nodes/preprocessing/review_config.py`
**Purpose**: Human-in-the-loop review workflow (NEW)
**Description**: LangGraph node that:
- **Executes after `load_data_node` and before preprocessing**
- Triggers LangGraph interruption for human approval
- Invokes ReviewQuestionGenerator Agent (Agent 1) to generate 5 contextual questions
- Questions cover preprocessing decisions:
  - Duplicate row handling
  - Missing value imputation strategy
  - Outlier removal approach
  - Categorical encoding methods
  - Numerical feature scaling
- Stores review session in PostgreSQL (`review_questions` table)
- Updates state with:
  - review_questions: List[str] (5 questions)
  - pipeline_status: "awaiting_review"
- Logs review data to MLflow artifacts
- Pipeline pauses here until user submits approval via frontend
- After approval: `continue_pipeline` endpoint executes preprocessing nodes

**Example Node Function**:
```python
def review_config_node(state: PipelineState) -> PipelineState:
    """Generate review questions and pause for human approval"""
    # Invoke Agent 1
    agent = ReviewQuestionGenerator(
        bedrock_model_id=state["bedrock_model_id"],
        aws_region=state["aws_region"]
    )

    context = {
        "dataset_preview": state["dataset_preview"],
        "preprocessing_config": state["pipeline_config"],
        "data_statistics": {
            "missing_values": state["missing_value_summary"],
            "duplicate_rows": state["duplicate_count"],
            "categorical_columns": len(state["categorical_columns"]),
            "numeric_columns": len(state["numeric_columns"])
        }
    }

    result = agent.invoke(context)
    questions = result["decision"]["questions"]

    # Store in PostgreSQL
    review_storage.create_review_session(
        pipeline_run_id=state["pipeline_run_id"],
        questions=questions,
        bedrock_prompt=result["prompt"],
        bedrock_response=result["response"]
    )

    # Update state (triggers interruption)
    return {
        **state,
        "review_questions": questions,
        "pipeline_status": "awaiting_review",
        "current_node": "review_config"
    }
```

#### `nodes/preprocessing/clean_data.py`
**Purpose**: Technique-based data cleaning operations
**Description**: LangGraph node that executes user-selected outlier handling technique:
- **Reads technique selection** from state["review_answers"]["clean_data_technique"]
- **Loads technique from registry**: `from techniques.clean_data import TECHNIQUES`
- **Executes selected technique** with user-specified parameters:
  - **none**: Skip outlier removal (recommended for tree_models)
  - **iqr_method**: Remove outliers using IQR (Q1 - 1.5*IQR, Q3 + 1.5*IQR) with configurable multiplier
  - **z_score**: Remove outliers using Z-score threshold (default 3.0)
  - **winsorization**: Cap outliers at percentiles
  - **isolation_forest**: Detect outliers using Isolation Forest algorithm
  - **dbscan**: Identify outliers using DBSCAN clustering
  - **robust_scalers**: Apply RobustScaler to reduce outlier impact
  - **domain_clipping**: Clip values to domain-specific ranges
- Removes duplicate rows if requested
- Drops rows with all NaN values
- **Logs technique selection with algorithm context** to MLflow:
  - clean_data_technique, technique_parameters (e.g., iqr_multiplier=1.5)
  - algorithm_category from Agent 1A (for traceability)
  - outliers_removed, duplicates_removed
- Logs outlier report per column (Q1, Q3, IQR, bounds, outlier_count)
- Updates state with cleaned_data, outlier_report, outliers_removed, technique_applied

#### `nodes/preprocessing/handle_missing.py`
**Purpose**: Technique-based missing value imputation
**Description**: LangGraph node that executes user-selected imputation technique:
- **Reads technique selection** from state["review_answers"]["handle_missing_technique"]
- **Loads technique from registry**: `from techniques.handle_missing import TECHNIQUES`
- **Analyzes missing values** per column (null_count / total_rows)
- **Executes selected technique** with user-specified parameters:
  - **drop_rows**: Remove rows with any missing values
  - **simple_imputation**: Use SimpleImputer with strategy (mean/median/mode/constant)
  - **knn_imputation**: Use KNNImputer with configurable n_neighbors (default 5)
  - **mice**: Use IterativeImputer (MICE algorithm) for multivariate imputation
  - **domain_specific**: Apply domain-specific imputation rules
  - **forward_fill**: Forward-fill missing values (time-series data)
  - **interpolation**: Interpolate missing values (linear, polynomial, spline)
- **Drop columns** with missing percentage above threshold (default 70%)
- **Logs technique selection with algorithm context** to MLflow:
  - handle_missing_technique, technique_parameters (e.g., imputation_strategy="median", knn_neighbors=5)
  - algorithm_category from Agent 1A
  - columns_dropped, columns_imputed, remaining_nulls, missing_values_before, missing_values_after
- Logs imputation report per column (missing_pct, technique_used, parameters)
- Updates state with cleaned_data, dropped_columns, imputation_applied, missing_value_report, technique_metadata

#### `nodes/preprocessing/encode_features.py`
**Purpose**: Technique-based categorical feature encoding
**Description**: LangGraph node that executes user-selected encoding technique:
- **Reads technique selection** from state["review_answers"]["encode_technique"]
- **Loads technique from registry**: `from techniques.encode_features import TECHNIQUES`
- **Identifies categorical columns** (object, category dtypes)
- **Executes selected technique** with user-specified parameters:
  - **one_hot**: One-hot encoding using pd.get_dummies() (recommended for linear_models, neural_networks)
  - **label_encoding**: Label encoding (0, 1, 2, ...) using LabelEncoder
  - **target_encoding**: Target encoding with configurable smoothing (recommended for tree_models)
  - **frequency_encoding**: Map to value frequencies (value_counts / total_count)
  - **binary_encoding**: Binary representation of categories
  - **hash_encoding**: Hash categories to fixed number of features
  - **embeddings**: Learn embeddings for high-cardinality categorical features (neural_networks)
- **Applies technique to columns** based on cardinality and algorithm requirements
- Stores fitted encoders and mappings in state for inverse transform
- **Logs technique selection with algorithm context** to MLflow:
  - encode_technique, technique_parameters (e.g., target_smoothing=1.0)
  - algorithm_category from Agent 1A (e.g., "tree_models prefer target_encoding")
  - encoding_methods per column, features_added, features_removed
- Logs encoding report per column (original_cardinality, technique_used, new_features)
- Updates state with cleaned_data, encoding_mappings, encoded_columns, encoding_methods, feature_names, technique_metadata

#### `nodes/preprocessing/scale_features.py`
**Purpose**: Technique-based numerical feature scaling
**Description**: LangGraph node that executes user-selected scaling technique:
- **Reads technique selection** from state["review_answers"]["scale_technique"]
- **Loads technique from registry**: `from techniques.scale_features import TECHNIQUES`
- **Identifies numerical columns**
- **Executes selected technique** with user-specified parameters:
  - **none**: Skip scaling (recommended for tree_models which are scale-invariant)
  - **standard_scaler**: StandardScaler - z-score normalization ((value - mean) / std)
  - **minmax_scaler**: MinMaxScaler - scale to [0, 1] range
  - **robust_scaler**: RobustScaler - uses median and IQR (robust to outliers)
  - **maxabs_scaler**: MaxAbsScaler - scale by maximum absolute value
  - **normalizer**: Normalizer - normalize samples individually to unit norm
  - **quantile_transformer**: QuantileTransformer - transform to uniform or normal distribution
- **Algorithm-aware scaling decision**:
  - If algorithm_category = "tree_models" and scale_technique = "none": Log reason "Tree models scale-invariant"
  - If algorithm_category = "linear_models" or "neural_networks": Recommend scaling
- Calculates comprehensive feature statistics (mean, std, min, max, median, q1, q3) before and after scaling
- **Performs data validation**:
  - Asserts no null values remain
  - Asserts no infinite values in numeric columns
  - Checks for duplicate rows
- Builds consolidated feature_metadata from all preprocessing steps
- **Logs technique selection with algorithm context** to MLflow:
  - scale_technique, technique_parameters
  - algorithm_category from Agent 1A
  - scale_skipped_reason (if technique = "none")
  - final_features, validation_passed
- Logs feature_statistics.json artifact (comprehensive stats for all features before/after scaling)
- Stores fitted scaler in state for transform phase (or None if skipped)
- Updates state with cleaned_data, scaler, scaled_columns, feature_statistics, feature_metadata, technique_metadata

---

### `/nodes/feature_engineering/` - Feature Engineering Nodes

#### `nodes/feature_engineering/__init__.py`
**Purpose**: Feature engineering module exports
**Description**: Exports feature engineering node functions

#### `nodes/feature_engineering/split_data.py`
**Purpose**: Train/test split
**Description**: LangGraph node that:
- Splits data into training and test sets
- Uses stratified split for classification
- Respects random_state for reproducibility
- Validates split consistency
- Updates state with X_train, X_test, y_train, y_test

#### `nodes/feature_engineering/select_features.py`
**Purpose**: Feature selection
**Description**: LangGraph node that:
- Implements feature selection methods:
  - Variance threshold
  - Correlation-based
  - Tree-based importance
  - Recursive feature elimination
- Logs selected features
- Updates state with reduced feature set

#### `nodes/feature_engineering/transform_features.py`
**Purpose**: Feature transformations
**Description**: LangGraph node that:
- Applies feature transformations:
  - Log/sqrt for skewed distributions
  - Polynomial features
  - Interaction terms
- Creates new derived features
- Updates state with transformed features

---

### `/nodes/classification/` - Classification Algorithm Nodes

#### `nodes/classification/__init__.py`
**Purpose**: Classification module exports
**Description**: Exports all classification algorithm node functions

#### `nodes/classification/logistic_regression.py`
**Purpose**: Logistic Regression training
**Description**: LangGraph node that:
- Checks if algorithm was selected by agent
- Defines parameter grid (C, penalty, solver)
- Trains with GridSearchCV
- Evaluates on test set
- Logs metrics and parameters to MLflow
- Stores AlgorithmResult in state

#### `nodes/classification/random_forest.py`
**Purpose**: Random Forest Classifier training
**Description**: LangGraph node that:
- Parameter grid: n_estimators, max_depth, min_samples_split
- Trains Random Forest with hyperparameter tuning
- Extracts feature importance
- Generates confusion matrix
- Logs all artifacts to MLflow

#### `nodes/classification/gradient_boosting.py`
**Purpose**: Gradient Boosting Classifier training
**Description**: LangGraph node that:
- Parameter grid: n_estimators, learning_rate, max_depth, subsample
- Trains Gradient Boosting model
- Monitors training progress
- Logs learning curves

#### `nodes/classification/svm.py`
**Purpose**: Support Vector Machine training
**Description**: LangGraph node that:
- Parameter grid: C, kernel, gamma
- Trains SVM classifier
- Handles multi-class classification
- Logs decision boundaries

#### `nodes/classification/knn.py`
**Purpose**: K-Nearest Neighbors training
**Description**: LangGraph node that:
- Parameter grid: n_neighbors, weights, metric
- Trains KNN classifier
- Analyzes optimal k value
- Logs distance metrics

---

### `/nodes/regression/` - Regression Algorithm Nodes

#### `nodes/regression/__init__.py`
**Purpose**: Regression module exports
**Description**: Exports all regression algorithm node functions

#### `nodes/regression/linear_regression.py`
**Purpose**: Linear Regression training
**Description**: LangGraph node that:
- Trains Linear Regression model
- Calculates RMSE, MAE, R² score
- Analyzes residuals
- Logs coefficient values

#### `nodes/regression/ridge.py`
**Purpose**: Ridge Regression training
**Description**: LangGraph node that:
- Parameter grid: alpha values
- Trains Ridge regression with L2 regularization
- Analyzes regularization effect
- Compares coefficients with Linear Regression

#### `nodes/regression/lasso.py`
**Purpose**: Lasso Regression training
**Description**: LangGraph node that:
- Parameter grid: alpha values
- Trains Lasso regression with L1 regularization
- Performs automatic feature selection
- Identifies zero-coefficient features

#### `nodes/regression/random_forest.py`
**Purpose**: Random Forest Regressor training
**Description**: LangGraph node that:
- Parameter grid: n_estimators, max_depth, min_samples_split
- Trains Random Forest regression
- Extracts feature importance
- Analyzes prediction variance

#### `nodes/regression/gradient_boosting.py`
**Purpose**: Gradient Boosting Regressor training
**Description**: LangGraph node that:
- Parameter grid: n_estimators, learning_rate, max_depth
- Trains Gradient Boosting regression
- Monitors training loss
- Logs partial dependence plots

---

### `/nodes/evaluation/` - Evaluation Nodes

#### `nodes/evaluation/__init__.py`
**Purpose**: Evaluation module exports
**Description**: Exports evaluation node functions

#### `nodes/evaluation/evaluate_models.py`
**Purpose**: Model evaluation and comparison
**Description**: LangGraph node that:
- Evaluates all trained models
- Calculates comprehensive metrics
- Compares model performance
- Generates comparison tables
- Identifies best model
- Logs all metrics to MLflow

#### `nodes/evaluation/generate_metrics.py`
**Purpose**: Metric calculation
**Description**: LangGraph node that:
- Calculates task-specific metrics:
  - Classification: accuracy, precision, recall, F1, ROC-AUC
  - Regression: RMSE, MAE, R², MAPE
- Generates confusion matrices
- Creates ROC curves
- Logs all metrics

---

### `/nodes/reporting/` - Reporting Nodes

#### `nodes/reporting/__init__.py`
**Purpose**: Reporting module exports
**Description**: Exports reporting node functions

#### `nodes/reporting/generate_report.py`
**Purpose**: Report generation
**Description**: LangGraph node that:
- Generates comprehensive evaluation report
- Includes model comparisons
- Adds agent decision summaries
- Creates executive summary
- Exports to HTML/PDF
- Logs report to MLflow

#### `nodes/reporting/create_visualizations.py`
**Purpose**: Visualization creation
**Description**: LangGraph node that:
- Creates visualizations:
  - Feature importance plots
  - Confusion matrices
  - ROC curves
  - Residual plots
  - Learning curves
- Saves plots to outputs/plots/
- Logs plots to MLflow

#### `nodes/reporting/save_artifacts.py`
**Purpose**: Artifact saving
**Description**: LangGraph node that:
- Saves all pipeline artifacts:
  - Trained models
  - Encoders and scalers
  - Evaluation metrics
  - Agent decisions
  - Plots and reports
- Organizes artifacts by category
- Logs all artifacts to MLflow

---

### `/agents/` - AI Decision Agent Implementations

#### `agents/__init__.py`
**Purpose**: Agents module exports
**Description**: Exports all agent classes and node functions

#### `agents/base_agent.py`
**Purpose**: Base class for AI agents
**Description**: Abstract base class defining:
- **BaseDecisionAgent** interface:
  - build_prompt(): Creates context-aware prompts
  - parse_response(): Extracts structured decisions
  - get_default_decision(): Fallback logic
  - invoke(): Main execution with retry logic
- Retry mechanism with exponential backoff
- Error handling and fallback strategies
- MLflow logging integration

#### `agents/config_extraction.py`
**Purpose**: Configuration extraction agent (Agent 0) - NEW
**Description**: Inherits from BaseDecisionAgent:
- **First agent in pipeline** - executes before all others
- Analyzes natural language user prompts to extract ML pipeline configuration
- Inputs analyzed:
  - User prompt (natural language description)
  - Available column names from data preview
  - Dataset preview (dtypes, shape)
  - Optional user hints
- Extracts configuration:
  - target_column: Column name to predict
  - experiment_name: Descriptive MLflow experiment name
  - test_size: Train/test split ratio (default 0.2)
  - random_state: Random seed for reproducibility
  - analysis_type: "classification" or "regression"
- Returns structured JSON with:
  - Extracted configuration values
  - Confidence score (0.0-1.0, must be >= 0.70)
  - Reasoning for each extracted value
  - Assumptions made during extraction
  - Warnings if any ambiguity detected
- Fallback strategy:
  - If confidence < 70%: Return error and suggest trying fallback model
  - If Bedrock unavailable: Return error (NO heuristics fallback)
- Uses AWS Bedrock Claude Sonnet 4.5 (primary) or Claude 3.7 Sonnet (fallback)

**Example Agent Class**:
```python
class ConfigExtractionAgent(BaseDecisionAgent):
    def build_prompt(self, context: Dict[str, Any]) -> str:
        return f"""You are an ML pipeline configuration expert...

        User Prompt: {context['user_prompt']}
        Available Columns: {context['available_columns']}

        Extract JSON with: target_column, experiment_name, test_size, random_state"""

    def parse_response(self, response: str) -> Dict[str, Any]:
        json_str = extract_json(response)
        config = json.loads(json_str)

        # Validate confidence
        if config.get("confidence", 0) < 0.70:
            raise ValueError(f"Confidence {config['confidence']} below 70% threshold")

        return config

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # NO DEFAULT - return error if agent fails
        raise AgentFailureException("ConfigExtraction agent failed, please try fallback model")
```

#### `agents/algorithm_category_predictor.py`
**Purpose**: Algorithm category prediction agent (Agent 1A) - NEW
**Description**: Inherits from BaseDecisionAgent:
- **First HITL agent** - analyzes dataset and predicts optimal algorithm category
- Executes after `load_data_node` and before preprocessing
- Analyzes data profile to predict algorithm category
- Inputs analyzed:
  - Dataset shape (n_samples, n_features)
  - Target type (binary_classification, multiclass_classification, regression)
  - Feature types (numeric_count, categorical_count, high_cardinality_count)
  - Class distribution (for classification tasks)
  - Dataset size in MB
  - Data characteristics (missing_percentage, duplicate_percentage, outlier_percentage, feature_correlation_max)
- Predicts algorithm category from:
  - linear_models (LogisticRegression, LinearRegression, Ridge, Lasso)
  - tree_models (RandomForest, XGBoost, GradientBoosting)
  - neural_networks (MLP, Deep Learning models)
  - ensemble (Stacking, Voting, Blending)
  - time_series (ARIMA, LSTM, Prophet)
- Returns structured JSON with:
  - algorithm_category: str (predicted category)
  - confidence: float (0.0-1.0, must be >= 0.70)
  - reasoning: str (explanation for prediction)
  - recommended_algorithms: List[str] (specific algorithms within category)
  - preprocessing_priorities: Dict[str, str] (required/optional for each step)
  - algorithm_requirements: Dict (scaling_required, outlier_sensitive, handles_missing, categorical_encoding_preference)
- Uses AWS Bedrock Claude Sonnet 4.5 with temperature=0.2 (low for consistent predictions)
- Stores prediction in PostgreSQL review_questions table
- Logs to MLflow: algorithm_category, confidence, agent_1a_prediction.json

**Example Agent Class**:
```python
class AlgorithmCategoryPredictor(BaseDecisionAgent):
    def build_prompt(self, context: Dict[str, Any]) -> str:
        return f"""You are an ML algorithm expert. Analyze this dataset profile
        and predict the optimal algorithm category.

        Dataset Profile:
        {json.dumps(context['data_profile'], indent=2)}

        Predict category: linear_models, tree_models, neural_networks,
        ensemble, or time_series.

        Return JSON with algorithm_category, confidence, reasoning,
        recommended_algorithms, preprocessing_priorities, algorithm_requirements."""

    def parse_response(self, response: str) -> Dict[str, Any]:
        json_str = extract_json(response)
        prediction = json.loads(json_str)

        # Validate confidence
        if prediction.get("confidence", 0) < 0.70:
            raise ValueError(f"Confidence {prediction['confidence']} below 70% threshold")

        return prediction

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # NO DEFAULT - return error if agent fails
        raise AgentFailureException("AlgorithmCategoryPredictor agent failed")
```

#### `agents/preprocessing_question_generator.py`
**Purpose**: Preprocessing question generation agent (Agent 1B) - NEW
**Description**: Inherits from BaseDecisionAgent:
- **Algorithm-aware HITL agent** - generates 4-20 dynamic preprocessing questions tailored to predicted algorithm category
- Executes after Agent 1A (algorithm category prediction) and before preprocessing
- Uses algorithm_category from Agent 1A to tailor questions and technique options
- Inputs analyzed:
  - Algorithm context (algorithm_category, algorithm_confidence, algorithm_requirements from Agent 1A)
  - Enhanced data profile (missing_values dict, outlier_summary, categorical_columns, high_cardinality_columns)
  - Preprocessing steps: clean_data, handle_missing, encode_features, scale_features
- Generates 4-20 questions dynamically (1-5 per preprocessing step):
  - Question count determined by algorithm requirements and data characteristics
  - Each question includes technique options ranked by algorithm suitability
  - Options rated as: excellent, good, acceptable, poor
- Returns structured JSON with:
  - questions: List[Question] (4-20 questions with question_id, preprocessing_step, question_text, question_type, priority, options, parameters)
  - preprocessing_recommendations: Dict (summary of recommendations)
  - algorithm_context: Dict (algorithm_category and requirements from Agent 1A)
  - question_count_by_step: Dict (number of questions per preprocessing step)
- Each technique option includes:
  - value: str (technique identifier)
  - label: str (human-readable name)
  - recommended: bool (whether this is the recommended choice)
  - reasoning: str (why this technique is recommended/not recommended)
  - algorithm_suitability: str (excellent/good/acceptable/poor for predicted algorithm)
- Parameters for each technique (e.g., iqr_multiplier, imputation_strategy, target_smoothing)
- Uses AWS Bedrock Claude Sonnet 4.5 with temperature=0.3 (slightly higher for natural phrasing)
- Stores questions in PostgreSQL review_questions table
- Logs to MLflow: question_count, question_count_by_step, agent_1b_questions.json
- Triggers LangGraph interruption for human review

**Example Agent Class**:
```python
class PreprocessingQuestionGenerator(BaseDecisionAgent):
    def build_prompt(self, context: Dict[str, Any]) -> str:
        return f"""You are a preprocessing expert. Generate algorithm-aware
        preprocessing questions based on the predicted algorithm category.

        Algorithm Context:
        {json.dumps(context['algorithm_context'], indent=2)}

        Data Profile:
        {json.dumps(context['data_profile'], indent=2)}

        Generate 1-5 questions per preprocessing step (4-20 total).
        Rank technique options by algorithm suitability for {context['algorithm_category']}.

        Return JSON with questions, preprocessing_recommendations,
        algorithm_context, question_count_by_step."""

    def parse_response(self, response: str) -> Dict[str, Any]:
        json_str = extract_json(response)
        result = json.loads(json_str)

        # Validate 4-20 questions
        if not (4 <= len(result.get("questions", [])) <= 20):
            raise ValueError(f"Must generate 4-20 questions, got {len(result['questions'])}")

        # Validate each question has algorithm_suitability ratings
        for q in result["questions"]:
            for option in q["options"]:
                assert "algorithm_suitability" in option

        return result

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise AgentFailureException("PreprocessingQuestionGenerator agent failed")
```

#### `agents/algorithm_selection.py`
**Purpose**: Algorithm selection agent (Agent 2)
**Description**: Inherits from BaseDecisionAgent:
- Analyzes data characteristics (samples, features, target type)
- Selects 3-5 optimal algorithms based on:
  - Dataset size
  - Feature types
  - Target distribution
  - Computational constraints
- Returns: selected_algorithms list with reasoning
- Includes fallback to safe default algorithms

#### `agents/model_selection.py`
**Purpose**: Model selection agent (Agent 3)
**Description**: Inherits from BaseDecisionAgent:
- Reviews all trained algorithm results
- Analyzes metrics:
  - Cross-validation scores
  - Test set performance
  - Training time
  - Model complexity
- Selects best model with detailed reasoning
- Considers trade-offs (accuracy vs. speed)
- Returns: best_model_name with justification

#### `agents/retraining_decision.py`
**Purpose**: Retraining decision agent (Agent 4)
**Description**: Inherits from BaseDecisionAgent:
- Analyzes current model performance
- Reviews drift detection results
- Evaluates performance degradation
- Considers time since last training
- Decides whether to retrain
- Returns: should_retrain (bool) with reasoning
- Provides recommendations for retraining strategy

#### `agents/prompts/` - Agent Prompt Templates

#### `agents/prompts/config_extraction_prompt.txt`
**Purpose**: Prompt template for configuration extraction (Agent 0) - NEW
**Description**: Structured prompt for extracting pipeline configuration from natural language:
- **Role definition**: ML pipeline configuration extraction expert
- **Input context**:
  - User's natural language prompt
  - Available column names from dataset
  - Dataset preview (shape, dtypes)
  - Optional user hints
- **Task specification**:
  - Extract target_column (which column to predict)
  - Generate descriptive experiment_name
  - Determine test_size (default 0.2)
  - Set random_state (default 42)
  - Infer analysis_type (classification or regression)
- **Output format**: JSON schema with required fields
- **Confidence scoring**: Must provide 0.0-1.0 confidence score
- **Reasoning requirement**: Explain each extracted value
- **Assumptions tracking**: List all assumptions made
- **Warning generation**: Flag any ambiguities or uncertainties
- **Examples**: Few-shot examples for common prompt patterns
- **Validation rules**: Column name must exist in available_columns

**Example Prompt Template Structure**:
```xml
<role>
You are an expert at extracting ML pipeline configuration from natural language descriptions.
</role>

<task>
Analyze the user's prompt and extract the following configuration:
1. target_column: The column name to predict
2. experiment_name: Descriptive name for MLflow experiment
3. test_size: Train/test split ratio (0.0-1.0, default 0.2)
4. random_state: Random seed for reproducibility (default 42)
5. analysis_type: "classification" or "regression"
</task>

<context>
User Prompt: {{user_prompt}}
Available Columns: {{available_columns}}
Dataset Info: {{dataset_preview}}
User Hints: {{user_hints}}
</context>

<output_format>
Return JSON:
{
  "target_column": "column_name",
  "experiment_name": "descriptive_name",
  "test_size": 0.2,
  "random_state": 42,
  "analysis_type": "classification",
  "confidence": 0.95,
  "reasoning": {
    "target_column": "User mentioned 'predict price'...",
    ...
  },
  "assumptions": ["Assumed classification because..."],
  "warnings": ["Column name might be ambiguous..."]
}
</output_format>

<examples>
Example 1:
User: "Analyze customer churn using the status column"
Output: {"target_column": "status", "analysis_type": "classification", ...}
</examples>
```

#### `agents/prompts/algorithm_selection_prompt.txt`
**Purpose**: Prompt template for algorithm selection
**Description**: Structured prompt with:
- Role definition (ML algorithm expert)
- Data profile context
- Task requirements
- Output format specification (JSON)
- Example outputs
- Reasoning guidelines

#### `agents/prompts/model_selection_prompt.txt`
**Purpose**: Prompt template for model selection
**Description**: Structured prompt with:
- Role definition (Model evaluation expert)
- Algorithm results context
- Selection criteria
- Output format (JSON)
- Trade-off considerations

#### `agents/prompts/retraining_decision_prompt.txt`
**Purpose**: Prompt template for retraining decision
**Description**: Structured prompt with:
- Role definition (MLOps decision expert)
- Performance metrics context
- Drift detection results
- Decision criteria
- Output format (JSON)
- Risk assessment guidelines

---

### `/tuning/` - Hyperparameter Tuning

#### `tuning/__init__.py`
**Purpose**: Tuning module exports
**Description**: Exports tuning classes and parameter grids

#### `tuning/grid_search.py`
**Purpose**: GridSearchCV wrapper
**Description**: GridSearchWrapper class that:
- Wraps sklearn GridSearchCV
- Integrates with MLflow logging
- Logs all hyperparameters tried
- Logs best parameters and scores
- Records training time
- Provides standardized result format
- fit_predict() method for training and evaluation

#### `tuning/param_grids.py`
**Purpose**: Default parameter grids
**Description**: Defines parameter grids for all algorithms:
- **CLASSIFICATION_PARAM_GRIDS**: Dictionary with grids for:
  - logistic_regression: C, penalty, solver
  - random_forest: n_estimators, max_depth, min_samples_split
  - gradient_boosting: n_estimators, learning_rate, max_depth
  - svm: C, kernel, gamma
  - knn: n_neighbors, weights, metric
- **REGRESSION_PARAM_GRIDS**: Dictionary with grids for:
  - linear_regression: fit_intercept
  - ridge: alpha
  - lasso: alpha
  - random_forest_regressor: n_estimators, max_depth
  - gradient_boosting_regressor: n_estimators, learning_rate

---

### `/monitoring/` - Performance Monitoring

#### `monitoring/__init__.py`
**Purpose**: Monitoring module exports
**Description**: Exports monitoring classes

#### `monitoring/drift_detector.py`
**Purpose**: Data drift detection
**Description**: DriftDetector class that:
- Implements multiple drift detection methods:
  - **Kolmogorov-Smirnov test**: For numerical features
  - **Chi-squared test**: For categorical features
  - **Population Stability Index (PSI)**: For distribution shifts
- Compares training vs. new data distributions
- Identifies drifted features
- Calculates drift scores
- Returns: drift_detected flag and drifted_features list

#### `monitoring/performance_monitor.py`
**Purpose**: Performance comparison
**Description**: PerformanceMonitor class that:
- Compares current model vs. baseline performance
- Calculates performance degradation percentage
- Tracks metrics over time
- Detects significant performance drops
- Generates performance reports
- Triggers alerts when thresholds exceeded

#### `monitoring/metrics_calculator.py`
**Purpose**: Metric calculations
**Description**: Utility functions for calculating:
- Classification metrics: accuracy, precision, recall, F1, ROC-AUC
- Regression metrics: RMSE, MAE, R², MAPE
- Custom business metrics
- Confusion matrix generation
- ROC curve calculation

#### `monitoring/alerting.py`
**Purpose**: Alert generation
**Description**: Alerting class that:
- Monitors metrics against thresholds
- Generates alerts for:
  - Performance degradation
  - Data drift detection
  - Training failures
  - Resource utilization
- Sends notifications (email, Slack, etc.)
- Logs all alerts to MLflow

---

### `/retraining/` - Retraining Modules

#### `retraining/__init__.py`
**Purpose**: Retraining module exports
**Description**: Exports retraining classes

#### `retraining/trigger.py`
**Purpose**: Retraining trigger logic
**Description**: RetrainingTrigger class that:
- Monitors conditions that require retraining:
  - Performance degradation below threshold
  - Significant data drift detected
  - Time-based triggers
  - Manual triggers
- Evaluates trigger conditions
- Logs trigger events
- Initiates retraining pipeline

#### `retraining/scheduler.py`
**Purpose**: Retraining scheduler
**Description**: RetrainingScheduler class that:
- Implements scheduled retraining (cron-like)
- Manages retraining queue
- Prevents concurrent retraining jobs
- Handles retry logic
- Logs scheduling events

#### `retraining/pipeline_executor.py`
**Purpose**: Automated pipeline execution
**Description**: Executes complete retraining pipeline:
- Loads new data
- Runs full pipeline
- Compares new model vs. current
- Deploys if performance improved
- Rolls back if performance degraded
- Logs all execution steps

---

### `/mlflow_utils/` - MLflow Integration

#### `mlflow_utils/__init__.py`
**Purpose**: MLflow utilities module exports
**Description**: Exports MLflow utility classes

#### `mlflow_utils/logger.py`
**Purpose**: Centralized MLflow logging
**Description**: MLflowLogger class with static methods:
- **log_agent_decision()**: Logs AI agent decisions (prompt, response, decision)
- **log_algorithm_result()**: Logs training results (metrics, params, model)
- **log_preprocessing_step()**: Logs preprocessing operations
- **log_evaluation_metrics()**: Logs comprehensive evaluation metrics
- **log_artifacts()**: Logs files and plots
- Provides consistent logging interface across pipeline

#### `mlflow_utils/experiment_manager.py`
**Purpose**: Experiment management with automatic restoration
**Description**: ExperimentManager class that:
- Creates and manages MLflow experiments
- **Automatically restores deleted experiments** when reused (prevents "experiment must be active" errors)
- `get_or_create_experiment()`: Gets existing experiment or creates new one
  - Checks if experiment exists by name
  - If experiment is deleted (lifecycle_stage="deleted"), automatically restores it using MLflowClient
  - If experiment doesn't exist, creates new one with optional tags and artifact location
- `list_experiments()`: Lists experiments with optional filtering (ACTIVE_ONLY, DELETED_ONLY, ALL)
- `delete_experiment()`: Deletes (archives) an experiment by ID
- `set_experiment_tag()`: Sets tags on experiments
- `get_experiment_by_name()`: Retrieves experiment by name
- `get_experiment_by_id()`: Retrieves experiment by ID
- Sets tracking URI on initialization
- Comprehensive logging for all operations

#### `mlflow_utils/model_registry.py`
**Purpose**: Model registry operations
**Description**: ModelRegistry class that:
- Registers trained models
- Manages model versions
- Transitions model stages (None → Staging → Production)
- Archives old models
- Retrieves models by name/version/stage
- Compares model versions

#### `mlflow_utils/run_context.py`
**Purpose**: MLflow run context management
**Description**: Utility functions for:
- Managing active MLflow runs
- Nested run creation
- Run tagging and organization
- Run cleanup
- Context managers for safe run handling

---

### `/utils/` - General Utilities

#### `utils/__init__.py`
**Purpose**: Utils module exports
**Description**: Exports utility functions and classes

#### `utils/bedrock_client.py`
**Purpose**: AWS Bedrock client wrapper
**Description**: BedrockClient class that:
- Wraps boto3 bedrock-runtime client
- Handles authentication
- Implements retry logic
- Parses Bedrock responses
- Tracks token usage
- Calculates costs
- Provides clean API for model invocation

#### `utils/prompt_storage.py`
**Purpose**: Triple prompt storage system (NEW)
**Description**: PromptStorage class implementing centralized prompt storage across three backends:

**Triple Storage Architecture**:
1. **MLflow Artifacts** (for experiment lineage)
   - Stores: user_prompt.txt, extracted_config.json, agent_response.txt
   - Tied to MLflow run for traceability
   - Enables experiment-level prompt tracking

2. **PostgreSQL Database** (for querying and analytics)
   - Table: `prompts` with JSONB columns for config/metadata
   - Indexed fields: timestamp, pipeline_run_id, confidence, target_column
   - Enables: SQL queries, full-text search, aggregations, analytics
   - Schema includes: user_prompt, extracted_config, confidence, reasoning, assumptions, warnings

3. **MinIO/S3 Object Storage** (for long-term archival)
   - Path structure: `s3://ml-pipeline-prompts/{year}/{month}/{pipeline_run_id}/`
   - Lifecycle: Automatic transition to cold storage after 90 days
   - Purpose: Cost-effective long-term storage, compliance, backups

**Key Features**:
- **Automatic synchronization**: All 3 backends updated atomically
- **Prompt similarity search**: Find similar historical prompts
- **Prompt reuse suggestions**: Recommend configs based on past prompts
- **Analytics dashboard data**: Aggregate prompt patterns and success rates
- **Bulk export**: For compliance and auditing
- **Data retention policies**: Configurable (default: 2 years)

**Class Interface**:
```python
class PromptStorage:
    def __init__(self, mlflow_client, db_connection, s3_client):
        self.mlflow = mlflow_client
        self.db = db_connection
        self.s3 = s3_client

    def save_prompt(
        self,
        user_prompt: str,
        extracted_config: Dict[str, Any],
        pipeline_run_id: str,
        mlflow_run_id: str,
        confidence: float,
        reasoning: str,
        assumptions: List[str],
        warnings: List[str]
    ) -> str:
        """Save prompt to all 3 storage backends atomically"""
        # 1. Save to MLflow artifacts
        self._save_to_mlflow(mlflow_run_id, user_prompt, extracted_config)

        # 2. Save to PostgreSQL
        prompt_id = self._save_to_database(
            user_prompt, extracted_config, pipeline_run_id,
            confidence, reasoning, assumptions, warnings
        )

        # 3. Archive to S3
        self._archive_to_s3(pipeline_run_id, user_prompt, extracted_config)

        return prompt_id

    def search_similar_prompts(
        self,
        prompt: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar historical prompts using keyword matching"""
        # PostgreSQL full-text search
        return self.db.query(
            "SELECT * FROM prompts WHERE to_tsvector(user_prompt) @@ plainto_tsquery(%s)",
            (prompt,)
        ).limit(limit)

    def get_prompt_by_run(self, pipeline_run_id: str) -> Dict[str, Any]:
        """Retrieve prompt data by pipeline run ID"""
        return self.db.query(
            "SELECT * FROM prompts WHERE pipeline_run_id = %s",
            (pipeline_run_id,)
        ).one()

    def get_analytics(self) -> Dict[str, Any]:
        """Get prompt usage analytics"""
        return {
            "total_prompts": self.db.count("prompts"),
            "avg_confidence": self.db.avg("prompts", "confidence"),
            "common_targets": self.db.top_values("extracted_config->>'target_column'", limit=10),
            "success_rate": self.db.ratio("extraction_success = true")
        }
```

**Database Schema**:
```sql
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    pipeline_run_id VARCHAR(64) NOT NULL,
    mlflow_run_id VARCHAR(64),
    user_prompt TEXT NOT NULL,
    extracted_config JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    reasoning TEXT,
    assumptions JSONB,
    warnings JSONB,
    extraction_success BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_prompts_timestamp ON prompts(timestamp DESC);
CREATE INDEX idx_prompts_pipeline_run ON prompts(pipeline_run_id);
CREATE INDEX idx_prompts_confidence ON prompts(confidence);
CREATE INDEX idx_prompts_target ON prompts((extracted_config->>'target_column'));
```

#### `utils/review_storage.py`
**Purpose**: Review session storage system (NEW)
**Description**: ReviewStorage class implementing persistent storage for human-in-the-loop review sessions:

**Storage Backend**: PostgreSQL only (audit trail and compliance)

**Key Functionality**:
- `create_review_session()`: Create new review session with questions
- `update_review_answers()`: Update session with user answers and approval status
- `get_review_by_pipeline()`: Retrieve review session by pipeline_run_id
- `store_bedrock_decision()`: Store AI agent prompt and response

**Database Table**: `review_questions`
```sql
CREATE TABLE review_questions (
    id SERIAL PRIMARY KEY,
    pipeline_run_id VARCHAR(255) NOT NULL UNIQUE,
    questions JSONB NOT NULL,
    answers JSONB,
    approved BOOLEAN,
    decision_reasoning TEXT,
    bedrock_prompt TEXT,
    bedrock_response TEXT,
    bedrock_tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Connection Management**:
- Uses psycopg2 connection pooling
- Environment variables: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- Automatic connection cleanup
- Transaction support for atomic operations

**Type Handling**:
- Extracts `total_tokens` from bedrock_tokens_used dictionary before insert
- Handles JSONB serialization for questions and answers
- Proper NULL handling for optional fields

**Usage Example**:
```python
storage = ReviewStorage()

# Create review session
storage.create_review_session(
    pipeline_run_id="run_20251206_170927",
    questions=["Q1?", "Q2?", "Q3?", "Q4?", "Q5?"],
    bedrock_prompt="...",
    bedrock_response="...",
    bedrock_tokens_used={"total_tokens": 3044}
)

# Update with user answers
storage.update_review_answers(
    pipeline_run_id="run_20251206_170927",
    answers={"q1": "yes", "q2": "no", ...},
    approved=True
)
```

#### `utils/data_utils.py`
**Purpose**: Data manipulation utilities
**Description**: Utility functions for:
- Data loading from multiple formats
- Data saving with compression
- DataFrame operations
- Type conversions
- Memory optimization
- Data profiling

#### `utils/file_utils.py`
**Purpose**: File I/O operations
**Description**: Utility functions for:
- File reading/writing
- Directory management
- Path resolution
- File compression/decompression
- Temporary file handling
- Safe file operations with cleanup

#### `utils/logging_utils.py`
**Purpose**: Python logging configuration
**Description**: Configures Python logging:
- Sets up log formatters
- Configures console handlers
- Configures file handlers
- Sets log levels by module
- Provides structured logging
- Integrates with MLflow logging

#### `utils/metrics_utils.py`
**Purpose**: Metric calculation helpers
**Description**: Utility functions for:
- Calculating classification metrics
- Calculating regression metrics
- Generating confusion matrices
- Computing ROC curves
- Custom metric implementations
- Metric aggregation and reporting

---

### `/tests/` - Test Suite

#### `tests/__init__.py`
**Purpose**: Test package initialization
**Description**: Empty init file for test discovery

#### `tests/conftest.py`
**Purpose**: Pytest fixtures and configuration
**Description**: Defines shared pytest fixtures:
- Sample datasets (classification, regression)
- Mock MLflow client
- Mock Bedrock client
- Test configuration objects
- Temporary directories
- Common test utilities

#### `tests/unit/` - Unit Tests

#### `tests/unit/test_state.py`
**Purpose**: Test state management
**Description**: Tests for core/state.py:
- PipelineState creation
- State updates
- State validation
- Helper functions (add_error, mark_node_completed)

#### `tests/unit/test_preprocessing.py`
**Purpose**: Test preprocessing nodes
**Description**: Tests for preprocessing nodes:
- Data loading
- Data cleaning
- Missing value handling
- Encoding and scaling

#### `tests/unit/test_analyze_prompt_node.py`
**Purpose**: Test analyze_prompt node (NEW)
**Description**: Unit tests for the analyze_prompt LangGraph node:
- **Test prompt analysis flow**: Verify node correctly invokes ConfigExtraction Agent
- **Test data preview**: Ensure quick data peek loads first 100 rows correctly
- **Test context building**: Validate context dict passed to agent contains all required fields
- **Test configuration extraction**: Verify extracted config updates pipeline_config in state
- **Test confidence validation**: Ensure < 70% confidence raises error
- **Test prompt storage**: Verify prompt saved to triple storage (MLflow + DB + S3)
- **Test error handling**: Invalid data path, missing columns, Bedrock failures
- **Test state updates**: Confirm state correctly updated with extracted values
- **Mock Agent 0**: Use mocked ConfigExtraction Agent for isolated testing

**Example Test**:
```python
def test_analyze_prompt_node_success(mock_agent, mock_prompt_storage):
    """Test successful prompt analysis and config extraction"""
    # Setup
    state = {
        "user_prompt": "Predict house prices using price column",
        "data_path": "test_data.csv",
        "bedrock_model_id": "claude-sonnet-4-5",
        "pipeline_run_id": "test123"
    }

    # Mock agent response
    mock_agent.invoke.return_value = {
        "decision": {
            "target_column": "price",
            "experiment_name": "house_price_prediction",
            "test_size": 0.2,
            "random_state": 42,
            "analysis_type": "regression",
            "confidence": 0.95
        }
    }

    # Execute
    result = analyze_prompt_node(state)

    # Assert
    assert result["pipeline_config"]["target_column"] == "price"
    assert result["config_confidence"] == 0.95
    mock_prompt_storage.save_prompt.assert_called_once()
```

#### `tests/unit/test_config_extraction_agent.py`
**Purpose**: Test ConfigExtraction Agent (Agent 0) - NEW
**Description**: Unit tests for ConfigExtraction Agent class:
- **Test agent initialization**: Verify Bedrock client setup with correct model ID
- **Test prompt building**: Ensure build_prompt() creates valid structured prompt with XML tags
- **Test response parsing**: Verify parse_response() extracts JSON correctly
- **Test confidence validation**: Ensure parser rejects confidence < 70%
- **Test field extraction**: Verify all required fields extracted (target_column, experiment_name, etc.)
- **Test column validation**: Ensure target_column exists in available_columns
- **Test fallback behavior**: Verify agent raises error (no heuristics) when Bedrock fails
- **Test retry mechanism**: Ensure exponential backoff retry logic works
- **Test with user hints**: Verify agent incorporates user hints in extraction
- **Test edge cases**: Missing fields in response, malformed JSON, invalid dtypes

**Example Test**:
```python
def test_config_extraction_agent_valid_response():
    """Test agent successfully extracts config from valid Bedrock response"""
    # Setup
    agent = ConfigExtractionAgent(
        bedrock_model_id="claude-sonnet-4-5",
        aws_region="us-east-1"
    )

    context = {
        "user_prompt": "Analyze customer churn with status column",
        "available_columns": ["customer_id", "status", "age", "income"],
        "dataset_preview": {"n_rows": 100, "n_columns": 4}
    }

    # Mock Bedrock response
    mock_response = """
    {
        "target_column": "status",
        "experiment_name": "customer_churn_analysis",
        "test_size": 0.2,
        "random_state": 42,
        "analysis_type": "classification",
        "confidence": 0.92,
        "reasoning": {"target_column": "User mentioned 'churn' and 'status'"}
    }
    """

    # Test
    result = agent.parse_response(mock_response)

    # Assert
    assert result["target_column"] == "status"
    assert result["confidence"] >= 0.70
    assert result["analysis_type"] == "classification"


def test_config_extraction_agent_low_confidence():
    """Test agent rejects extraction with confidence < 70%"""
    agent = ConfigExtractionAgent(...)

    mock_response = '{"target_column": "price", "confidence": 0.65}'

    # Should raise error
    with pytest.raises(ValueError, match="below 70% threshold"):
        agent.parse_response(mock_response)
```

#### `tests/unit/test_agents.py`
**Purpose**: Test AI agents
**Description**: Tests for agent classes:
- Agent initialization
- Prompt building
- Response parsing
- Fallback logic
- Retry mechanism

#### `tests/integration/` - Integration Tests

#### `tests/integration/test_graph_execution.py`
**Purpose**: Test LangGraph workflow
**Description**: Tests complete workflow execution:
- Node sequencing
- State passing between nodes
- Conditional routing
- Error handling in workflow

#### `tests/integration/test_mlflow_integration.py`
**Purpose**: Test MLflow integration
**Description**: Tests MLflow logging:
- Experiment creation
- Run management
- Metric logging
- Artifact logging
- Model registration

#### `tests/integration/test_bedrock_integration.py`
**Purpose**: Test Bedrock integration
**Description**: Tests Bedrock API calls:
- Model invocation
- Response parsing
- Error handling
- Retry logic

#### `tests/e2e/` - End-to-End Tests

#### `tests/e2e/test_full_pipeline.py`
**Purpose**: Test complete pipeline execution
**Description**: End-to-end tests:
- Full pipeline execution from data loading to model deployment
- Integration of all components
- Performance validation
- Output verification

---

### `/api/` - FastAPI Backend

#### `api/__init__.py`
**Purpose**: API package initialization
**Description**: Exports API version and package metadata.

#### `api/main.py`
**Purpose**: FastAPI application entry point
**Description**: Main FastAPI application that:
- Configures CORS middleware for cross-origin requests
- Registers API routers (pipeline endpoints)
- Provides root and health check endpoints
- Implements global exception handling
- Serves OpenAPI documentation at /api/docs
- Runs uvicorn server on port 8000
- Integrates with backend LangGraph nodes

#### `api/models/` - Pydantic Models

#### `api/models/__init__.py`
**Purpose**: API models exports
**Description**: Exports all Pydantic request/response models for API endpoints.

#### `api/models/pipeline.py`
**Purpose**: Pipeline API request and response schemas
**Description**: Defines Pydantic models for:
- **LoadDataRequest**: Input for data loading (data_path, target_column, experiment_name, test_size, random_state)
- **DataProfile**: Data statistics (n_samples, n_features, feature_names, target_distribution)
- **LoadDataResponse**: Success response with pipeline_run_id, mlflow_run_id, experiment_id, data_profile
- **PipelineStateResponse**: Current pipeline state (status, current_node, completed_nodes, errors, warnings)
- **ErrorResponse**: Error details with timestamp
- All models include validation, examples, and comprehensive field descriptions

#### `api/routers/` - API Routers

#### `api/routers/__init__.py`
**Purpose**: Router exports
**Description**: Exports all API router modules.

#### `api/routers/pipeline.py`
**Purpose**: Pipeline operation endpoints
**Description**: Implements comprehensive REST API endpoints for pipeline lifecycle management:
- **POST /api/pipeline/load-data**: Triggers load_data_node, initializes MLflow experiment, returns data profile
  - Automatically ends any active MLflow runs to prevent conflicts
  - Creates or restores MLflow experiments
  - Returns success response with pipeline_run_id, mlflow_run_id, and data_profile
- **GET /api/pipeline/state/{pipeline_run_id}**: Retrieves current pipeline state
  - Returns detailed state including status, current node, completed/failed nodes, errors, timestamps
- **GET /api/pipeline/runs**: Lists all active pipeline runs with comprehensive details
  - Returns list of all pipelines with status, nodes, timestamps, MLflow IDs, config, errors
  - Includes data_path, target_column, and progress metrics
- **POST /api/pipeline/stop/{pipeline_run_id}**: Stop/cancel a running pipeline
  - Ends associated MLflow run with KILLED status
  - Updates pipeline status to "stopped"
  - Sets end_time timestamp
- **DELETE /api/pipeline/delete/{pipeline_run_id}?delete_experiment=bool**: Delete pipeline and optionally experiment
  - Removes pipeline from active_pipelines dictionary
  - Optionally ends and deletes MLflow run
  - Optionally deletes MLflow experiment if delete_experiment=true
  - Returns deletion status for run and experiment
- Manages active pipeline states in memory (production should use Redis/database)
- Integrates with ExperimentManager for MLflow operations
- Calls LangGraph nodes directly
- Returns structured responses with proper error handling
- Comprehensive logging for all operations

---

### `/frontend/` - Vue.js 3 UI (ChatGPT-like Interface)

**Purpose**: Modern single-page application (SPA) with ChatGPT-inspired interface for ML pipeline management

**Technology Stack**:
- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite (fast development and optimized production builds)
- **State Management**: Pinia (official Vue.js state management)
- **Routing**: Vue Router (client-side routing)
- **HTTP Client**: Axios (REST API communication)
- **Real-time**: WebSocket/Server-Sent Events (live pipeline updates)
- **Styling**: Tailwind CSS (utility-first CSS framework)
- **Charts**: Mermaid.js (LangGraph state diagrams)
- **Deployment**: Docker + Nginx (production-ready)

#### **Architecture Overview**

**ChatGPT-like Layout Design**:
```
┌─────────────────────────────────────────────────────┐
│  Header (Logo, User, Settings)                      │
├──────────┬──────────────────────────────────────────┤
│          │                                           │
│  LEFT    │         MAIN CONTENT AREA                │
│ SIDEBAR  │    (LangGraph Diagram + Metrics)         │
│          │                                           │
│ Run      │  - Natural language prompt input         │
│ History  │  - Pipeline configuration display        │
│          │  - Real-time state diagram               │
│ [+ New]  │  - Metrics and progress                  │
│          │  - Results visualization                 │
│ Today    │                                           │
│ • Run 1  │                                           │
│ • Run 2  │                                           │
│          │                                           │
│ Yester.  │                                           │
│ • Run 3  │                                           │
│          │                                           │
└──────────┴──────────────────────────────────────────┘
```

#### **Core Components**

##### 1. **Layout Components** (`src/components/layout/`)

**Sidebar.vue**:
- Collapsible left sidebar (25-30% width, resizable)
- **"+ New Run"** button at top
- Run history organized by date (Today, Yesterday, Last 7 Days, etc.)
- Each run shows:
  - Run ID (shortened)
  - Status indicator (🟢 Running, ✅ Completed, ❌ Failed)
  - Timestamp
  - Experiment name
- Click to load run details in main area
- Search/filter runs by experiment, status, date
- Hover actions: delete, duplicate, view MLflow
- Responsive: collapses to icon-only on mobile

**MainContent.vue**:
- Dynamic content area (70-75% width)
- **Empty State**: Shows welcome + prompt input when no run selected
- **Active Run**: Shows real-time pipeline visualization
  - Natural language prompt display
  - Extracted configuration (confidence, reasoning, assumptions)
  - LangGraph state diagram with current node highlighting
  - Metrics panel (data profile, progress, performance)
  - Error/warning alerts
- **Completed Run**: Shows final results
  - Model comparison table
  - Evaluation metrics
  - Visualizations (confusion matrix, ROC curves)
  - MLflow experiment link

**Header.vue**:
- App logo and title
- Current user (if auth enabled)
- Settings menu (theme toggle, preferences)
- Notifications/alerts
- MLflow server status indicator

##### 2. **Pipeline Components** (`src/components/pipeline/`)

**PromptInput.vue**:
- Large textarea for natural language ML task description
- Placeholder with examples
- Character count and AI assist button
- Required fields:
  - Data path input with file browser
  - Experiment name (auto-generated or custom)
- Optional fields (collapsible):
  - Test size, random state, specific algorithms
- **"🚀 Start Pipeline"** button
- Validation feedback

**StateChart.vue**:
- Mermaid.js diagram renderer
- Real-time node status updates:
  - ⏳ Pending (gray)
  - 🔄 In Progress (blue, pulsing)
  - ✅ Completed (green)
  - ❌ Failed (red)
- Click node to see details
- Zoom and pan controls
- Export diagram as PNG/SVG
- Conditional routing visualization (natural language vs traditional mode)

**PipelineConfig.vue**:
- Extracted configuration display (from Bedrock)
- **Confidence Score**: Progress bar with percentage
- **Reasoning**: Bullet-point explanation
- **Assumptions**: Tagged list of assumptions
- **Warnings**: Alert-style warnings if any
- **Edit Mode**: Allow manual config override before pipeline runs
- Bedrock model info (model ID, tokens used)

**MetricsPanel.vue**:
- **Data Profile**: Samples, features, target distribution (chart)
- **Progress**: Node completion percentage, estimated time remaining
- **Performance**: Real-time metrics as models train
- **Resources**: CPU/Memory usage (if available)
- **Links**: Quick links to MLflow UI, logs, artifacts

**ReviewForm.jsx** (NEW - Human-in-the-Loop):
- **Purpose**: Interactive UI for human review and approval of preprocessing configuration
- **When Shown**: Appears when pipeline status is `"awaiting_review"` (after load_data_node)
- **Question Display**:
  - Shows 5 AI-generated review questions one at a time
  - Progress indicator: "Question X of 5" with visual progress bar
  - Priority badges (HIGH/MEDIUM/LOW) for each question
  - Context tooltips (💡) explaining why each question matters
- **Question Types Supported**:
  - Yes/No buttons (most common)
  - Multiple choice options
  - Text input for custom feedback
- **Navigation**:
  - Previous/Next buttons to move between questions
  - Review summary showing all answers before final submission
- **Submission Options**:
  - **"✓ Approve & Continue Pipeline"** (green button):
    - Submits answers to backend
    - Triggers POST `/api/pipeline/submit-review-answers`
    - Then calls POST `/api/pipeline/continue/{pipeline_run_id}`
    - Backend resumes MLflow run and executes preprocessing nodes
  - **"🔄 Request Re-Analysis"** (orange button):
    - Submits rejection feedback
    - Backend re-invokes Agent 0 with user feedback
    - Generates new configuration and review questions
    - Increments `review_iteration` counter
- **Review Iterations**:
  - Shows iteration badge if `review_iteration > 0` ("Iteration 2", "Iteration 3", etc.)
  - Displays previous review summary and AI recommendations
- **State Management**:
  - Tracks current question index
  - Stores all answers in local state: `{ question_id: answer }`
  - Validates all questions answered before allowing submission
- **Error Handling**:
  - Displays backend errors in red alert box
  - Prevents duplicate submissions (disables buttons while submitting)
- **Integration**:
  - Imported by `Home.jsx` and shown conditionally
  - Polls pipeline state every 2 seconds to detect when review is ready
  - Calls `onReviewSubmitted()` callback to refresh pipeline state

**Example Flow**:
```jsx
// User reviews 5 questions
Q1: "Should we remove 150 duplicate rows?" → Answer: Yes
Q2: "Is mean imputation acceptable for 5% missing values?" → Answer: Yes
Q3: "Should we remove outliers using IQR method?" → Answer: No
Q4: "Is frequency encoding suitable for high-cardinality columns?" → Answer: Yes
Q5: "Should we apply StandardScaler to numerical features?" → Answer: Yes

// User adds optional feedback
Feedback: "Don't remove outliers, they might be important for anomaly detection"

// User clicks "Approve & Continue"
→ POST /api/pipeline/submit-review-answers
→ POST /api/pipeline/continue/{pipeline_run_id}
→ Backend executes: clean_data → handle_missing → encode_features → scale_features
→ Frontend polls state and shows preprocessing progress
```

##### 3. **History Components** (`src/components/history/`)

**RunList.vue**:
- Virtualized list for performance (handle 1000+ runs)
- Group by date with collapsible sections
- Each run rendered by RunItem.vue
- Infinite scroll for loading more runs
- Pull-to-refresh on mobile

**RunItem.vue**:
- Compact run card in sidebar
- Shows: status, ID, experiment, timestamp
- Hover: show quick actions (delete, duplicate)
- Active state styling when selected
- Click to load in main content

**RunDetails.vue**:
- Modal/drawer for detailed run information
- Tabs:
  - **Overview**: Status, timestamps, configuration
  - **Nodes**: All node execution details with logs
  - **Metrics**: All logged metrics with history
  - **Artifacts**: Downloadable artifacts (models, plots, reports)
  - **Logs**: Full execution logs with filtering
  - **Bedrock**: AI decision details and prompts
- Export run report as JSON/PDF

##### 4. **Common Components** (`src/components/common/`)

Reusable UI components:
- **Button.vue**: Primary, secondary, danger variants
- **Input.vue**: Text, number, file inputs with validation
- **Card.vue**: Containers for content sections
- **Loading.vue**: Skeleton loaders and spinners
- **Alert.vue**: Success, info, warning, error alerts
- **Modal.vue**: Overlay modals for dialogs
- **Badge.vue**: Status badges (running, completed, failed)
- **Tooltip.vue**: Contextual help tooltips

#### **State Management** (`src/stores/`)

**pipelineStore.js** (Pinia store):
```javascript
{
  // Current Pipeline
  activePipeline: null,
  currentState: {},

  // Actions
  startPipeline(config),
  stopPipeline(runId),
  updateState(state),  // Called by WebSocket

  // Getters
  isRunning,
  currentNode,
  progress
}
```

**runsStore.js** (Pinia store):
```javascript
{
  // Run History
  runs: [],
  selectedRun: null,
  filters: { status, experiment, dateRange },

  // Actions
  fetchRuns(),
  selectRun(runId),
  deleteRun(runId),
  duplicateRun(runId),

  // Getters
  filteredRuns,
  groupedByDate
}
```

#### **Services** (`src/services/`)

**api.js** (Axios client):
- API base URL configuration from environment
- Request/response interceptors
- Error handling
- Endpoints:
  - `POST /api/pipeline/load-data` - Start pipeline
  - `GET /api/pipeline/state/{id}` - Get pipeline state
  - `POST /api/pipeline/stop/{id}` - Stop pipeline
  - `DELETE /api/pipeline/delete/{id}` - Delete pipeline
  - `GET /api/pipeline/runs` - List all runs
  - `GET /api/pipeline/run/{id}` - Get run details

**websocket.js** (Real-time updates):
- WebSocket connection management
- Automatic reconnection on disconnect
- Subscribe to pipeline state updates
- Event handlers:
  - `state_update` - Pipeline state changed
  - `node_started` - Node execution started
  - `node_completed` - Node execution completed
  - `node_failed` - Node execution failed
  - `pipeline_completed` - Pipeline finished

#### **Views** (`src/views/`)

**Home.vue**:
- Main application view
- Composition of Sidebar + MainContent + Header
- Handles routing and state initialization
- WebSocket connection lifecycle
- Responsive layout adjustments

**RunDetail.vue**:
- Dedicated page for detailed run view
- Accessed via route: `/run/:runId`
- Full-screen layout without sidebar
- Comprehensive run analysis
- Comparison with other runs

#### **Composables** (`src/composables/`)

**usePipeline.js**:
```javascript
export function usePipeline() {
  const store = usePipelineStore()

  const startPipeline = async (config) => { ... }
  const stopPipeline = async () => { ... }
  const refreshState = async () => { ... }

  return {
    pipeline: computed(() => store.activePipeline),
    isRunning: computed(() => store.isRunning),
    startPipeline,
    stopPipeline,
    refreshState
  }
}
```

**useRealtime.js**:
```javascript
export function useRealtime(runId) {
  const ws = ref(null)

  const connect = () => { ... }
  const disconnect = () => { ... }
  const onStateUpdate = (callback) => { ... }

  return {
    connected,
    connect,
    disconnect,
    onStateUpdate
  }
}
```

#### **Configuration Files**

**package.json**:
- Vue 3, Vue Router, Pinia
- Vite, Tailwind CSS
- Axios, Mermaid.js
- Development and build scripts

**vite.config.js**:
- Development server (port 3000)
- Proxy API requests to backend (port 8000)
- Build optimization
- Environment variable handling

**Dockerfile**:
- Multi-stage build:
  1. Build stage: Install deps, build production assets
  2. Production stage: Nginx to serve static files
- Nginx configured to:
  - Serve Vue.js SPA
  - Proxy `/api/*` to backend
  - Handle client-side routing (SPA fallback)
  - Enable gzip compression

**nginx.conf**:
```nginx
server {
  listen 80;
  root /usr/share/nginx/html;

  location / {
    try_files $uri $uri/ /index.html;  # SPA fallback
  }

  location /api/ {
    proxy_pass http://backend:8000;
  }
}
```

#### **Features**

**Real-time Updates**:
- WebSocket connection for live pipeline state
- Auto-reconnect on connection loss
- Optimistic UI updates
- Progress indicators with smooth animations

**Natural Language Integration**:
- Prominent prompt input with examples
- Display Bedrock extraction results
- Show confidence and reasoning
- Allow config override before execution

**Run Management**:
- Sidebar history with search/filter
- Quick actions (stop, delete, duplicate)
- Persistent selection across refreshes
- Export run data

**Responsive Design**:
- Desktop: Full sidebar + main content
- Tablet: Collapsible sidebar
- Mobile: Bottom navigation, full-screen content

**Dark Mode**:
- System preference detection
- Manual toggle
- Smooth transitions
- Consistent color palette

**Performance**:
- Code splitting (lazy-loaded routes)
- Virtual scrolling for long lists
- Debounced search
- Optimized re-renders with Vue reactivity

#### **Docker Deployment**

**Build**:
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**Integration with docker-compose.yml**:
- Service name: `frontend`
- Exposed on port `3000` (maps to internal 80)
- Depends on: `backend`, `mlflow`
- Environment variables:
  - `VITE_API_BASE_URL=http://localhost:8000`
  - `VITE_MLFLOW_URL=http://localhost:5000`
  - `VITE_WS_URL=ws://localhost:8000/ws`

---

### `/scripts/` - Utility Scripts

#### `scripts/setup_mlflow.sh`
**Purpose**: MLflow server setup
**Description**: Bash script that:
- Installs MLflow dependencies
- Creates backend database
- Configures artifact storage
- Starts MLflow tracking server
- Sets up authentication (optional)
- Displays access URL

#### `scripts/run_pipeline.py`
**Purpose**: Main pipeline execution script
**Description**: Python script that:
- Parses command-line arguments
- Loads configuration
- Initializes pipeline state
- Compiles LangGraph workflow
- Executes pipeline
- Displays results
- Handles errors gracefully

#### `scripts/evaluate_model.py`
**Purpose**: Model evaluation script
**Description**: Python script that:
- Loads trained model from registry
- Evaluates on new data
- Generates evaluation report
- Compares against baseline
- Logs results to MLflow

#### `scripts/deploy_model.py`
**Purpose**: Model deployment script
**Description**: Python script that:
- Retrieves model from registry
- Packages model for deployment
- Deploys to target environment
- Performs health checks
- Logs deployment metadata

---

### `/data/` - Data Directories

#### `data/raw/`
**Purpose**: Raw input data storage
**Description**: Stores unprocessed data files (gitignored)

#### `data/processed/`
**Purpose**: Processed data storage
**Description**: Stores cleaned and preprocessed data (gitignored)

#### `data/external/`
**Purpose**: External data sources
**Description**: Stores data from external sources (gitignored)

---

### `/outputs/` - Pipeline Outputs

#### `outputs/models/`
**Purpose**: Trained model artifacts
**Description**: Stores serialized models (gitignored)

#### `outputs/metrics/`
**Purpose**: Evaluation metrics
**Description**: Stores metric JSON/CSV files (gitignored)

#### `outputs/plots/`
**Purpose**: Generated visualizations
**Description**: Stores PNG/SVG plot files (gitignored)

#### `outputs/reports/`
**Purpose**: Generated reports
**Description**: Stores HTML/PDF reports (gitignored)

#### `outputs/logs/`
**Purpose**: Execution logs
**Description**: Stores pipeline execution logs (gitignored)

---

### `/mlruns/` - MLflow Tracking Directory
**Purpose**: MLflow artifact storage
**Description**: Stores MLflow tracking data and artifacts (gitignored)

---

### `/notebooks/` - Jupyter Notebooks

#### `notebooks/01_exploratory_data_analysis.ipynb`
**Purpose**: EDA notebook
**Description**: Jupyter notebook for:
- Initial data exploration
- Statistical analysis
- Data quality assessment
- Visualization

#### `notebooks/02_feature_engineering.ipynb`
**Purpose**: Feature engineering experiments
**Description**: Jupyter notebook for:
- Feature creation experiments
- Feature selection analysis
- Transformation testing

---

### `/docs/` - Documentation

#### `docs/README.md`
**Purpose**: Documentation index
**Description**: Overview of all documentation files

#### `docs/LANGGRAPH_DESIGN.md`
**Purpose**: LangGraph architecture documentation
**Description**: Details about workflow design and node structure

#### `docs/COMPONENT_SPECIFICATIONS.md`
**Purpose**: Component specifications
**Description**: Detailed specifications for all components

#### `docs/MODULE_INTERFACES.md`
**Purpose**: Module interface definitions
**Description**: API contracts between modules

#### `docs/DATA_FLOW_ARCHITECTURE.md`
**Purpose**: Data flow documentation
**Description**: How data flows through the pipeline

#### `docs/PROJECT_STRUCTURE.md`
**Purpose**: Project structure documentation
**Description**: This file - complete project structure reference

#### `docs/BEDROCK_SETUP.md`
**Purpose**: AWS Bedrock configuration and setup guide (NEW)
**Description**: Comprehensive guide for setting up AWS Bedrock for the ML pipeline:

**Sections Covered**:

1. **Prerequisites**:
   - AWS account with appropriate permissions
   - AWS CLI installed and configured
   - Python 3.10+ with boto3 installed
   - Understanding of IAM roles and policies

2. **AWS Bedrock Setup**:
   - **Request Model Access**: Step-by-step guide to request access to Claude models in AWS console
     - Navigate to AWS Bedrock → Model access
     - Request access to:
       - `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (primary)
       - `anthropic.claude-3-7-sonnet-20250219-v1:0` (fallback)
     - Wait for approval (typically 1-2 business days)
   - **Verify Model Access**: AWS CLI commands to confirm model availability
   - **Model Pricing**: Cost breakdown for Claude Sonnet 4.5 and 3.7 Sonnet

3. **IAM Configuration**:
   - **User Mode (Development)**: IAM user with programmatic access
     - Create IAM user with `AmazonBedrockFullAccess` policy
     - Generate access keys (Access Key ID + Secret Access Key)
     - Configure AWS CLI: `aws configure`
     - Set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
   - **Service Mode (Production)**: IAM role for EC2/ECS
     - Create IAM role with `AmazonBedrockFullAccess` policy
     - Attach role to EC2 instance or ECS task
     - No credentials needed (automatic credential resolution)
   - **Least Privilege Policy**: Custom IAM policy example with minimal Bedrock permissions

4. **Environment Configuration**:
   - **.env file setup**: Complete example with all required variables
   ```bash
   # AWS Configuration
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX  # Optional (user mode)
   AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxx  # Optional (user mode)

   # Bedrock Configuration
   BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
   BEDROCK_FALLBACK_MODEL_ID=anthropic.claude-3-7-sonnet-20250219-v1:0
   BEDROCK_TEMPERATURE=0.0
   BEDROCK_MAX_TOKENS=4096
   BEDROCK_CONFIDENCE_THRESHOLD=0.70
   ```

5. **Testing Bedrock Connection**:
   - Python script to verify Bedrock access
   - Test both primary and fallback models
   - Validate response parsing
   - Check token usage and costs

6. **Troubleshooting**:
   - **Model access denied**: Check model access request status
   - **Region not supported**: List of supported Bedrock regions
   - **Throttling errors**: Rate limits and backoff strategies
   - **Authentication failures**: IAM permission debugging
   - **Cost management**: Setting up budget alerts and CloudWatch alarms

7. **Production Considerations**:
   - **High availability**: Multi-region Bedrock setup
   - **Cost optimization**: Caching strategies, batch processing
   - **Security best practices**: Encryption, VPC endpoints, CloudTrail logging
   - **Monitoring**: CloudWatch metrics for Bedrock API calls
   - **Budget alerts**: Setting up cost alerts for Bedrock usage

8. **Local Development Setup**:
   - Using LocalStack for Bedrock simulation (limited functionality)
   - Mocking Bedrock responses for offline development
   - Environment-specific configurations (dev, staging, prod)

**Example IAM Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-sonnet-4-5-*",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-7-sonnet-*"
      ]
    }
  ]
}
```

**Testing Script Example**:
```python
# test_bedrock_connection.py
import boto3
import json

def test_bedrock_connection():
    """Test AWS Bedrock connection and model invocation"""
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )

    prompt = "Extract config from: Predict house prices using price column"

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    })

    try:
        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            body=body
        )
        print("✅ Bedrock connection successful!")
        print(f"Response: {response['body'].read().decode()}")
    except Exception as e:
        print(f"❌ Bedrock connection failed: {e}")

if __name__ == "__main__":
    test_bedrock_connection()
```

#### `docs/API_REFERENCE.md`
**Purpose**: API documentation
**Description**: Reference for all public APIs

#### `docs/DEPLOYMENT_GUIDE.md`
**Purpose**: Deployment instructions
**Description**: Step-by-step deployment guide

#### `docs/TROUBLESHOOTING.md`
**Purpose**: Troubleshooting guide
**Description**: Common issues and solutions

---

## Summary

This project structure provides:

✅ **Clear Separation of Concerns**: Agents, nodes, monitoring, and utilities in separate directories
✅ **Individual Algorithm Nodes**: Each ML algorithm as a separate LangGraph node
✅ **Comprehensive Testing**: Unit, integration, and end-to-end test suites
✅ **MLflow Integration**: Dedicated utilities directory for experiment tracking
✅ **AI Decision Agents**: Separate agents directory with prompt templates
✅ **Monitoring**: Dedicated monitoring directory for drift detection and performance tracking
✅ **Scalability**: Easy to add new algorithms, agents, or monitoring capabilities
✅ **Documentation**: Complete documentation directory with all design files

The structure supports the enhanced ML pipeline with intelligent decision-making, comprehensive logging, and production-ready monitoring.
