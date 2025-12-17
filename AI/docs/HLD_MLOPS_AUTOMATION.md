# High-Level Design (HLD) - MLOps Pipeline Automation with LangGraph

## Document Information
- **Version**: 1.0
- **Date**: 2025-11-30
- **Author**: AI System Design Team
- **Status**: Design Phase

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Design Goals and Principles](#design-goals-and-principles)
4. [System Architecture](#system-architecture)
5. [Component Design](#component-design)
6. [Data Design](#data-design)
7. [Interface Design](#interface-design)
8. [Security Design](#security-design)
9. [Deployment Architecture](#deployment-architecture)
10. [Non-Functional Requirements](#non-functional-requirements)

---

## 1. Executive Summary

### 1.1 Purpose
This document presents the High-Level Design for an intelligent MLOps pipeline automation system that leverages LangGraph for workflow orchestration, AWS Bedrock for AI-powered decision making, and MLflow for comprehensive experiment tracking and model management.

### 1.2 Scope
The system automates the complete machine learning lifecycle including:
- Automated data preprocessing and feature engineering
- AI-powered algorithm selection
- Hyperparameter tuning with GridSearchCV
- Model training and evaluation
- Performance monitoring and drift detection
- Intelligent retraining decisions
- Model deployment and versioning

### 1.3 Key Innovations
- **AI Decision Agents**: Five specialized agents using AWS Bedrock Claude for intelligent optimization
  - **Agent 0**: Configuration extraction from natural language prompts
  - **Agent 1 (NEW)**: Human-in-the-Loop review question generation for preprocessing approval
  - **Agent 2**: Algorithm selection based on data characteristics
  - **Agent 3**: Model selection based on performance metrics
  - **Agent 4**: Retraining decision based on drift and performance
- **Human-in-the-Loop (HITL)**: Intelligent review system with LangGraph interruption for human approval before preprocessing
- **Graph-Based Orchestration**: LangGraph provides state management and dynamic workflow routing
- **Comprehensive Tracking**: MLflow integration for complete experiment lineage
- **Automated Monitoring**: Real-time performance tracking with automated retraining triggers
- **Interactive UI**: React-based interface for visualization and control

---

## 2. System Overview

### 2.1 System Context

```
┌─────────────────────────────────────────────────────────────────────┐
│                          External Systems                            │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ AWS Bedrock  │  │   MLflow     │  │  Data Sources│             │
│  │   Claude     │  │   Server     │  │  (S3, DBs)   │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                     │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                      │
┌─────────▼──────────────────────────────────────▼─────────────────┐
│                MLOps Pipeline Automation System                   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              React UI Layer                                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │          LangGraph Orchestration Engine                     │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  State Management │ Node Execution │ Edge Routing    │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              AI Decision Layer (5 Agents)                   │  │
│  │  • Config Extraction • Review Generation (HITL)            │  │
│  │  • Algorithm Selection • Model Selection • Retraining      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           ML Processing Layer                               │  │
│  │  • Data Preprocessing  • Feature Engineering                │  │
│  │  • Model Training      • Hyperparameter Tuning              │  │
│  │  • Model Evaluation    • Drift Detection                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              MLflow Integration Layer                       │  │
│  │  • Experiment Tracking  • Model Registry  • Artifacts       │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Storage Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ PostgreSQL   │  │   S3/MinIO   │  │  Local FS    │         │
│  │  (MLflow)    │  │  (Artifacts) │  │  (Temp Data) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Stakeholders
- **Data Scientists**: Primary users who configure and monitor pipelines
- **ML Engineers**: Deploy and maintain the system
- **Business Users**: Consume model predictions and insights
- **DevOps Team**: Manage infrastructure and deployments

---

## 3. Design Goals and Principles

### 3.1 Design Goals

#### G1: Automation
- Minimize manual intervention in ML pipeline execution
- Automated hyperparameter tuning
- Automated model selection and deployment
- Self-healing capabilities through intelligent retraining

#### G2: Intelligent Optimization
- AI-powered algorithm selection to reduce computational waste
- Smart hyperparameter search space definition
- Cost-aware decision making

#### G3: Reproducibility
- Complete experiment tracking with MLflow
- Version control for data, code, and models
- Deterministic pipeline execution with seed management

#### G4: Scalability
- Support for parallel algorithm training
- Horizontal scaling for large datasets
- Resource-efficient execution

#### G5: Observability
- Real-time pipeline monitoring
- Comprehensive logging at all stages
- Visual feedback through React UI

#### G6: Production-Ready
- Automated monitoring and drift detection
- Intelligent retraining triggers
- Safe deployment with rollback capabilities

### 3.2 Design Principles

#### P1: Modularity
- Each component is independently testable
- Clear separation of concerns
- Plugin architecture for algorithms

#### P2: State Management
- Centralized state through LangGraph
- Immutable state transitions
- Checkpoint and resume capability

#### P3: Fail-Safe
- Graceful error handling at all levels
- Rollback mechanisms for failed deployments
- Audit trails for all operations

#### P4: Extensibility
- Easy addition of new algorithms
- Pluggable agent implementations
- Configurable monitoring metrics

---

## 4. System Architecture

### 4.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    React UI                                    │  │
│  │  • Dashboard  • Visualizations  • Controls  • Monitoring       │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTP/WebSocket
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                  LangGraph Workflow Engine                     │  │
│  │  • State Graph  • Node Executor  • Edge Router                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
┌───────────────────▼─────┐   ┌───▼──────┐   ┌─▼─────────────────────┐
│  DECISION LAYER          │   │  ML      │   │  TRACKING LAYER       │
│  ┌────────────────────┐  │   │  LAYER   │   │  ┌─────────────────┐  │
│  │ AWS Bedrock Agents │  │   │          │   │  │ MLflow Manager  │  │
│  │ • Agent 1          │◄─┼───┤          ├───┼──│ • Experiments   │  │
│  │ • Agent 2          │  │   │          │   │  │ • Runs          │  │
│  │ • Agent 3          │  │   │          │   │  │ • Models        │  │
│  └────────────────────┘  │   │          │   │  │ • Artifacts     │  │
└──────────────────────────┘   └──────────┘   │  └─────────────────┘  │
                                               └───────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                   ML PROCESSING LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Preprocessing│  │   Training   │  │  Monitoring  │              │
│  │   Module     │  │   Module     │  │   Module     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PostgreSQL  │  │   S3/MinIO   │  │   File System│              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 LangGraph Workflow Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LangGraph State Machine                         │
│                                                                      │
│                          [START]                                     │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────┐                              │
│                    │  load_data      │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────────┐                          │
│                    │ 🤖 review_config    │ ◄─── NEW: HITL          │
│                    │ (Generate Review Qs)│                          │
│                    └────────┬────────────┘                          │
│                             │                                        │
│                    [LangGraph Interruption]                          │
│                    Pipeline pauses for human approval                │
│                             │                                        │
│                    ┌────────┴────────┐                              │
│                    │                 │                              │
│              (Approved)         (Rejected)                           │
│                    │                 │                              │
│                    ▼                 └──> (Re-analyze)               │
│                    │                                                 │
│                    ▼                                                 │
│           ┌─────────────────┐                                       │
│           │  clean_data     │                                       │
│           └────────┬────────┘                                       │
│                    │                                                 │
│                    ▼                                                 │
│           ┌─────────────────┐                                       │
│           │ handle_missing  │                                       │
│           └────────┬────────┘                                       │
│                    │                                                 │
│                    ▼                                                 │
│           ┌─────────────────┐                                       │
│           │ encode_features │                                       │
│           └────────┬────────┘                                       │
│                    │                                                 │
│                    ▼                                                 │
│           ┌─────────────────┐                                       │
│           │ scale_features  │                                       │
│           └────────┬────────┘                                       │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────┐                              │
│                    │  train_test_split│                             │
│                    └────────┬────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────┐                              │
│                    │ feature_selection│                             │
│                    └────────┬────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────────┐                          │
│                    │ 🤖 agent_2_select   │                          │
│                    │ (Algorithm Selection)│                          │
│                    └────────┬────────────┘                          │
│                             │                                        │
│              ┌──────────────┼──────────────┐                        │
│              │              │              │                        │
│              ▼              ▼              ▼                        │
│      ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│      │train_algo_1│  │train_algo_2│  │train_algo_3│               │
│      │(RF + GridCV)│  │(GB + GridCV)│  │(LR + GridCV)│               │
│      └──────┬─────┘  └──────┬─────┘  └──────┬─────┘               │
│             │                │                │                     │
│             └────────────────┼────────────────┘                     │
│                              │                                      │
│                              ▼                                      │
│                    ┌─────────────────────┐                          │
│                    │ 🤖 agent_3_select   │                          │
│                    │  (Model Selection)  │                          │
│                    └────────┬────────────┘                          │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────┐                              │
│                    │  evaluate_model │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────┐                              │
│                    │  detect_drift   │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────┐                              │
│                    │ monitor_performance│                            │
│                    └────────┬────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌─────────────────────┐                          │
│                    │ 🤖 agent_4_decide   │                          │
│                    │ (Retrain Decision)  │                          │
│                    └────────┬────────────┘                          │
│                             │                                        │
│                     ┌───────┴───────┐                               │
│                     │               │                               │
│            (retrain=True)    (retrain=False)                        │
│                     │               │                               │
│                     ▼               ▼                               │
│            ┌─────────────┐   ┌─────────────┐                       │
│            │trigger_retrain│ │save_artifacts│                       │
│            │(loop to start)│ └──────┬──────┘                       │
│            └───────────────┘        │                               │
│                                     ▼                               │
│                            ┌─────────────────┐                      │
│                            │  generate_report│                      │
│                            └────────┬────────┘                      │
│                                     │                               │
│                                     ▼                               │
│                                  [END]                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Component Design

### 5.1 React UI Component

#### 5.1.1 Component Responsibilities
- User input collection and validation
- Real-time pipeline status visualization
- Interactive graph visualization
- MLflow metrics display
- Agent decision explanations

#### 5.1.2 Sub-Components

**A. Configuration Manager**
```
Inputs:
- Data file upload
- Pipeline parameters (test_size, cv_folds, etc.)
- Algorithm preferences
- Performance thresholds

Outputs:
- Validated configuration dictionary
- Pipeline initialization trigger
```

**B. Monitoring Dashboard**
```
Displays:
- Current pipeline stage
- Progress bars
- Resource utilization
- Live metrics
- Error/warning alerts

Updates:
- Real-time WebSocket connection
- 1-second refresh rate
```

**C. Graph Visualizer**
```
Features:
- Network graph of LangGraph nodes
- Node status coloring (pending, running, completed, failed)
- Interactive node inspection
- Edge transition animation
```

**D. MLflow Integration Panel**
```
Features:
- Experiment browser
- Run comparison table
- Metric visualization (line charts, parallel coordinates)
- Artifact viewer
- Model registry interface
```

### 5.2 LangGraph Orchestration Component

#### 5.2.1 State Schema

```python
class PipelineState(TypedDict):
    # Data
    raw_data: pd.DataFrame
    cleaned_data: pd.DataFrame
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series

    # Features
    selected_features: List[str]
    feature_importance: Dict[str, float]
    feature_statistics: Dict[str, Any]

    # MLflow
    mlflow_experiment_id: str
    mlflow_run_id: str
    mlflow_tracking_uri: str

    # Agent Decisions
    algorithm_selection_decision: Dict[str, Any]
    model_selection_decision: Dict[str, Any]
    retraining_decision: Dict[str, Any]

    # Models
    algorithm_results: Dict[str, AlgorithmResult]
    best_model_name: str
    best_model: Any

    # Monitoring
    drift_detected: bool
    drift_score: float
    drift_details: Dict[str, Any]
    performance_comparison: Dict[str, Any]

    # Control
    retraining_triggered: bool
    pipeline_status: str
    error_messages: List[str]
```

#### 5.2.2 Node Functions

Each node is a pure function: `State → State`

**Example: Feature Selection Node**
```python
def feature_selection_node(state: PipelineState) -> PipelineState:
    """
    Select top-k features using feature importance

    Inputs from state:
    - X_train, y_train
    - feature selection config

    Processing:
    1. Calculate feature importance (RF-based)
    2. Select top-k features
    3. Filter X_train, X_test
    4. Log to MLflow

    Outputs to state:
    - selected_features
    - feature_importance
    - updated X_train, X_test

    Returns:
    - Updated state dictionary
    """
```

#### 5.2.3 Edge Routing Logic

```python
# Conditional routing based on agent decisions
def route_after_algorithm_selection(state: PipelineState) -> List[str]:
    """
    Route to selected algorithm nodes only

    Returns list of node names to execute
    """
    selected = state["algorithm_selection_decision"]["selected_algorithms"]
    return [f"train_{algo}" for algo in selected]

def route_after_retraining_decision(state: PipelineState) -> str:
    """
    Route to retraining or finalization
    """
    if state["retraining_decision"]["retrain"]:
        return "trigger_retrain"
    else:
        return "save_artifacts"
```

### 5.3 Human-in-the-Loop (HITL) Component - Algorithm-Aware Preprocessing Review

#### 5.3.1 Purpose and Design Goals

**Primary Purpose**: Enable intelligent, algorithm-aware human oversight of preprocessing decisions before pipeline execution.

**Design Goals**:
1. **Intelligence**: Predict likely algorithm category and generate context-specific preprocessing questions
2. **Flexibility**: Support 1-5 questions per preprocessing step (4-20 total) based on data and algorithm needs
3. **Multiple Techniques**: Offer ranked preprocessing technique options with explanations
4. **Transparency**: Provide clear reasoning for recommendations based on algorithm requirements
5. **User Experience**: Non-technical users understand trade-offs between preprocessing techniques
6. **Audit Trail**: Store all human decisions with algorithm context for compliance
7. **Minimal Interruption**: Quick review process (target: <3 minutes even with 15+ questions)

**When HITL Triggers**:
- After `load_data_node` completes successfully
- After algorithm category prediction (Agent 1A)
- Before any preprocessing operations execute (clean_data, handle_missing, encode_features, scale_features)
- Only triggers once per pipeline run (unless rejected)

**Key Innovation**: The system predicts the likely algorithm category (linear models, tree models, neural networks, ensemble, time series) and generates preprocessing questions tailored to that algorithm's requirements.

#### 5.3.2 Enhanced Component Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│            Enhanced HITL Preprocessing Review System                   │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  1. Data Loading (load_data_node)                                │ │
│  │     Output:                                                       │ │
│  │     - raw_data (DataFrame)                                        │ │
│  │     - data_profile: {shape, dtypes, statistics}                  │ │
│  │     - missing_values_summary, duplicate_count                    │ │
│  └────────────────┬─────────────────────────────────────────────────┘ │
│                   │                                                    │
│                   ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  2. Agent 1A - Algorithm Category Predictor (NEW)                │ │
│  │     Input:                                                        │ │
│  │     - n_samples, n_features, target_type                         │ │
│  │     - feature_types (numeric_count, categorical_count)           │ │
│  │     - class_distribution (for classification)                    │ │
│  │     - dataset_size_mb                                            │ │
│  │                                                                   │ │
│  │     Bedrock Prompt:                                               │ │
│  │     "Analyze dataset characteristics and predict the most        │ │
│  │      likely algorithm category that will achieve best            │ │
│  │      performance. Consider data size, feature types, and         │ │
│  │      target characteristics."                                     │ │
│  │                                                                   │ │
│  │     Output:                                                       │ │
│  │     - algorithm_category: "linear_models" | "tree_models" |      │ │
│  │       "neural_networks" | "ensemble" | "time_series"             │ │
│  │     - confidence: 0.0-1.0                                         │ │
│  │     - reasoning: str (why this category)                         │ │
│  │     - recommended_algorithms: List[str] (3-5 specific algos)     │ │
│  │     - preprocessing_priorities: Dict[step, "critical|required|   │ │
│  │       optional"]                                                  │ │
│  └────────────────┬─────────────────────────────────────────────────┘ │
│                   │                                                    │
│                   ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  3. Agent 1B - Preprocessing Question Generator (Enhanced)       │ │
│  │     Input:                                                        │ │
│  │     - data_profile (from step 1)                                 │ │
│  │     - algorithm_category (from step 2)                           │ │
│  │     - preprocessing_steps: ["clean_data", "handle_missing",      │ │
│  │       "encode_features", "scale_features"]                       │ │
│  │                                                                   │ │
│  │     Processing:                                                   │ │
│  │     For each preprocessing step:                                 │ │
│  │       1. Analyze data requirements (missing%, outliers, etc.)    │ │
│  │       2. Check algorithm category requirements                   │ │
│  │          - Linear models need scaling, outlier handling          │ │
│  │          - Tree models can skip scaling, robust to outliers      │ │
│  │          - Neural networks need scaling, complex imputation      │ │
│  │       3. Generate 1-5 questions with multiple technique options  │ │
│  │       4. Rank techniques by suitability for algorithm            │ │
│  │       5. Assign priority (HIGH if critical, MEDIUM/LOW if not)   │ │
│  │                                                                   │ │
│  │     Output:                                                       │ │
│  │     - questions: List[Dict] (4-20 questions total)               │ │
│  │       Grouped by preprocessing step:                             │ │
│  │       • clean_data_questions (1-5 questions)                     │ │
│  │         Example: "Outlier handling method for linear model?"     │ │
│  │         Options: Winsorization (RECOMMENDED), Z-score, IQR, None │ │
│  │       • handle_missing_questions (1-5 questions)                 │ │
│  │         Example: "Imputation strategy for 15% missing values?"   │ │
│  │         Options: KNN (RECOMMENDED), Mean, Median, Drop rows      │ │
│  │       • encode_features_questions (1-5 questions)                │ │
│  │         Example: "Encoding for 50 categories (high cardinality)?"│ │
│  │         Options: Target (RECOMMENDED), Frequency, Hash, OneHot   │ │
│  │       • scale_features_questions (1-5 questions)                 │ │
│  │         Example: "Scaling method for linear model (REQUIRED)?"   │ │
│  │         Options: StandardScaler (RECOMMENDED), MinMax, Robust    │ │
│  │     - preprocessing_recommendations: Dict[step, technique]       │ │
│  │     - algorithm_context: str (explains why these questions)      │ │
│  └────────────────┬─────────────────────────────────────────────────┘ │
│                   │                                                    │
│                   ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  4. Storage Layer (PostgreSQL)                                   │ │
│  │     Table: review_questions                                      │ │
│  │     - pipeline_run_id (UNIQUE key)                               │ │
│  │     - algorithm_category (VARCHAR) - NEW                         │ │
│  │     - algorithm_confidence (FLOAT) - NEW                         │ │
│  │     - questions (JSONB) - Enhanced schema with technique options │ │
│  │     - answers (JSONB) - Includes selected techniques and params  │ │
│  │     - approved (BOOLEAN)                                         │ │
│  │     - bedrock_prompt_1a, bedrock_response_1a - NEW              │ │
│  │     - bedrock_prompt_1b, bedrock_response_1b - NEW              │ │
│  │     - bedrock_tokens_used (INTEGER)                              │ │
│  │     - created_at, updated_at (TIMESTAMP)                         │ │
│  │                                                                   │ │
│  │     Purpose:                                                      │ │
│  │     - Audit trail with algorithm context for compliance          │ │
│  │     - Analytics on preprocessing technique effectiveness         │ │
│  │     - Training data for improving algorithm prediction           │ │
│  └────────────────┬─────────────────────────────────────────────────┘ │
│                   │                                                    │
│                   ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  5. LangGraph Interruption Mechanism                             │ │
│  │     Implementation:                                               │ │
│  │     - workflow.interrupt_after(["review_config"])                │ │
│  │     - Pipeline status: "awaiting_review"                         │ │
│  │     - State preserved in memory (active_pipelines dict)          │ │
│  │     - State includes algorithm_category for context              │ │
│  │                                                                   │ │
│  │     User Action:                                                  │ │
│  │     - Frontend polls /api/pipeline/state/{run_id} every 2s      │ │
│  │     - Detects status="awaiting_review"                           │ │
│  │     - Fetches algorithm_category and questions from database     │ │
│  │     - Displays ReviewForm.jsx component with algorithm banner    │ │
│  └────────────────┬─────────────────────────────────────────────────┘ │
│                   │                                                    │
│                   ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  6. Frontend Review UI (ReviewForm.jsx) - Enhanced               │ │
│  │     Features:                                                     │ │
│  │     - Algorithm category banner (top of form)                    │ │
│  │       "🎯 Predicted Category: Linear Models (confidence 92%)"    │ │
│  │       "Recommended: Logistic Regression, Linear SVM, Ridge"      │ │
│  │     - Tabbed interface (one tab per preprocessing step)          │ │
│  │       [Clean Data] [Handle Missing] [Encode] [Scale] tabs       │ │
│  │     - Questions grouped by preprocessing step                    │ │
│  │     - Each question shows:                                        │ │
│  │       • Question text                                             │ │
│  │       • Multiple technique options (radio buttons)               │ │
│  │       • Recommended option (green checkmark + badge)             │ │
│  │       • Context tooltip (why this matters for this algorithm)    │ │
│  │       • Priority badge (HIGH/MEDIUM/LOW with color)              │ │
│  │       • Technique comparison (pros/cons for each option)         │ │
│  │     - Technique parameters (sliders/inputs for selected option)  │ │
│  │       Example: KNN imputation → k neighbors slider (3-10)        │ │
│  │     - Progress indicator (e.g., "Step 2 of 4: Handle Missing")  │ │
│  │     - Summary panel showing all selected techniques              │ │
│  │     - Optional feedback text area                                │ │
│  │                                                                   │ │
│  │     Submission Options:                                           │ │
│  │     - "✓ Approve & Continue Pipeline" (green button)            │ │
│  │     - "🔄 Request Re-Analysis" (orange button)                   │ │
│  └────────────────┬─────────────────────────────────────────────────┘ │
│                   │                                                    │
│                   ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  7. Backend Decision Processing                                  │ │
│  │     Approval Path:                                                │ │
│  │     - POST /api/pipeline/submit-review-answers                   │ │
│  │       Body: {                                                     │ │
│  │         "answers": {                                              │ │
│  │           "clean_data_technique": "winsorization",               │ │
│  │           "winsorization_lower_pct": 1,                          │ │
│  │           "winsorization_upper_pct": 99,                         │ │
│  │           "handle_missing_technique": "knn_imputation",          │ │
│  │           "knn_neighbors": 5,                                    │ │
│  │           "encode_technique": "one_hot",                         │ │
│  │           "scale_technique": "standard_scaler"                   │ │
│  │         },                                                        │ │
│  │         "approved": true                                          │ │
│  │       }                                                           │ │
│  │     - Store answers in PostgreSQL (review_questions.answers)     │ │
│  │     - Update state["review_answers"] with approved techniques    │ │
│  │     - POST /api/pipeline/continue/{pipeline_run_id}              │ │
│  │     - Resume MLflow run (mlflow.start_run(run_id=...))           │ │
│  │     - Execute preprocessing nodes with approved techniques:      │ │
│  │       • clean_data_node(technique="winsorization", params={...}) │ │
│  │       • handle_missing_node(technique="knn_imputation", k=5)     │ │
│  │       • encode_features_node(technique="one_hot")                │ │
│  │       • scale_features_node(technique="standard_scaler")         │ │
│  │     - Log selected techniques to MLflow                          │ │
│  │     - Log artifacts (feature_statistics.json)                    │ │
│  │     - End MLflow run                                             │ │
│  │                                                                   │ │
│  │     Rejection Path:                                               │ │
│  │     - Store rejection feedback in PostgreSQL                     │ │
│  │     - Re-invoke Agent 0 (ConfigExtraction) with feedback        │ │
│  │     - Re-invoke Agent 1A (Algorithm Category Predictor)          │ │
│  │     - Re-invoke Agent 1B (Preprocessing Question Generator)      │ │
│  │     - Generate new questions based on new algorithm prediction   │ │
│  │     - Increment review_iteration counter                         │ │
│  │     - Display new ReviewForm with iteration badge               │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

#### 5.3.3 Agent 1A: Algorithm Category Predictor

**Agent Type**: AlgorithmCategoryPredictor (inherits from BaseDecisionAgent)

**File**: `agents/algorithm_category_predictor.py`

**Input Context Schema**:
```python
{
    "n_samples": int,  # Number of rows in dataset
    "n_features": int,  # Number of columns (excluding target)
    "target_type": str,  # "classification" or "regression"
    "feature_types": {
        "numeric_count": int,  # Number of numeric features
        "categorical_count": int,  # Number of categorical features
        "high_cardinality_count": int  # Categories with >50 unique values
    },
    "class_distribution": Dict[str, int],  # For classification: {"class_0": 1500, "class_1": 1200}
    "dataset_size_mb": float,  # Memory footprint
    "data_characteristics": {
        "missing_percentage": float,  # Overall missing data percentage
        "duplicate_percentage": float,  # Duplicate rows percentage
        "outlier_percentage": float,  # Estimated outlier percentage (IQR method)
        "feature_correlation_max": float  # Maximum feature correlation (multicollinearity check)
    }
}
```

**Output Schema**:
```python
{
    "algorithm_category": str,  # "linear_models" | "tree_models" | "neural_networks" | "ensemble" | "time_series"
    "confidence": float,  # 0.0-1.0 confidence in prediction
    "reasoning": str,  # Detailed reasoning for category selection
    "recommended_algorithms": List[str],  # 3-5 specific algorithms (e.g., ["RandomForest", "XGBoost", "GradientBoosting"])
    "preprocessing_priorities": {
        "clean_data": str,  # "critical" | "required" | "optional"
        "handle_missing": str,
        "encode_features": str,
        "scale_features": str
    },
    "algorithm_requirements": {
        "scaling_required": bool,
        "outlier_sensitive": bool,
        "handles_missing": bool,
        "categorical_encoding_preference": str  # "one_hot" | "label" | "target"
    }
}
```

**Prediction Logic**:

The agent uses Bedrock Claude to analyze dataset characteristics and predict the most suitable algorithm category:

- **Tree Models** (RandomForest, XGBoost, GradientBoosting):
  - Small to medium datasets (< 100k rows)
  - Mixed feature types (numeric + categorical)
  - Non-linear relationships expected
  - Interpretability important

- **Linear Models** (LogisticRegression, LinearSVM, Ridge):
  - Small datasets (< 10k rows)
  - Mostly numeric features
  - Fast training required
  - Interpretability critical

- **Neural Networks** (MLPClassifier, Deep Learning):
  - Large datasets (> 100k rows)
  - High-dimensional data (> 100 features)
  - Complex non-linear patterns
  - Computational resources available

- **Ensemble Methods** (Stacking, Voting):
  - Medium to large datasets
  - Performance is top priority
  - Computational resources available

- **Time Series Models** (ARIMA, Prophet, LSTM):
  - Temporal dependencies detected
  - Sequential data
  - Time-based features present

**Bedrock Model**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`

**Temperature**: 0.2 (low temperature for consistent predictions)

**Fallback**: If agent fails, default to "tree_models" (most versatile category)

#### 5.3.4 Agent 1B: Enhanced Preprocessing Question Generator

**Agent Type**: PreprocessingQuestionGenerator (inherits from BaseDecisionAgent)

**File**: `agents/preprocessing_question_generator.py` (renamed from `review_question_generator.py`)

**Input Context Schema**:
```python
{
    "algorithm_category": str,  # Output from Agent 1A
    "algorithm_confidence": float,  # Confidence from Agent 1A
    "algorithm_requirements": Dict[str, Any],  # Requirements from Agent 1A
    "data_profile": {
        "n_samples": int,
        "n_features": int,
        "missing_values": Dict[str, int],  # {column: missing_count}
        "duplicate_rows": int,
        "categorical_columns": List[str],
        "numeric_columns": List[str],
        "high_cardinality_columns": List[str],  # >50 unique values
        "outlier_summary": Dict[str, Dict]  # {column: {count, Q1, Q3, IQR}}
    },
    "preprocessing_config": {
        "target_column": str,
        "test_size": float,
        "analysis_type": str
    }
}
```

**Output Schema** (Enhanced):
```python
{
    "questions": [
        {
            "question_id": str,  # "clean_q1", "missing_q1", "encode_q1", "scale_q1"
            "preprocessing_step": str,  # "clean_data" | "handle_missing" | "encode_features" | "scale_features"
            "question_text": str,  # "How should we handle outliers for linear models?"
            "question_type": str,  # "multiple_choice" | "yes_no" | "numeric_input"
            "priority": str,  # "high" | "medium" | "low"
            "context": str,  # Algorithm-specific explanation
            "options": [
                {
                    "value": str,  # Internal identifier (e.g., "winsorization")
                    "label": str,  # Display text (e.g., "Percentile Capping (Winsorization)")
                    "recommended": bool,  # True if recommended for this algorithm
                    "reasoning": str,  # Why recommended/not recommended
                    "algorithm_suitability": str  # "excellent" | "good" | "acceptable" | "poor"
                },
                # ... more options
            ],
            "parameters": [  # Optional technique-specific parameters
                {
                    "param_name": str,  # e.g., "winsorization_lower_pct"
                    "param_type": str,  # "int" | "float" | "string"
                    "default": Any,  # Default value
                    "range": List[Any],  # Valid range (for numeric) or options (for string)
                    "description": str  # Parameter explanation
                }
            ]
        },
        # 4-20 questions total (1-5 per preprocessing step)
    ],
    "preprocessing_recommendations": {
        "clean_data_technique": str,  # Recommended technique for this step
        "handle_missing_technique": str,
        "encode_technique": str,
        "scale_technique": str
    },
    "algorithm_context": str,  # High-level explanation of why these questions matter
    "question_count_by_step": {
        "clean_data": int,  # Number of questions for this step
        "handle_missing": int,
        "encode_features": int,
        "scale_features": int
    }
}
```

**Question Generation Strategy by Algorithm Category**:

**For Linear Models**:
- **clean_data**: 2-3 questions (HIGH priority)
  - Outlier method: Winsorization (RECOMMENDED), Z-score, IQR, None
  - Outlier threshold: If Z-score selected, threshold parameter
  - Duplicate handling: Remove duplicates (RECOMMENDED)
- **handle_missing**: 2-3 questions (HIGH priority)
  - Imputation method: Mean/Median (RECOMMENDED), KNN, MICE, Drop
  - Missing threshold: Drop features with >30% missing
- **encode_features**: 1-2 questions (MEDIUM priority)
  - Encoding: One-hot (RECOMMENDED), Binary, Label
- **scale_features**: 2-3 questions (CRITICAL priority)
  - Scaling method: StandardScaler (RECOMMENDED), MinMaxScaler, RobustScaler
  - Scaling parameters: Feature range, centering options

**For Tree Models**:
- **clean_data**: 1-2 questions (LOW priority)
  - Outlier method: None (RECOMMENDED), IQR for extreme cases
  - Duplicate handling: Remove duplicates (RECOMMENDED)
- **handle_missing**: 1-2 questions (LOW priority)
  - Imputation method: Simple (RECOMMENDED), KNN, Native handling
- **encode_features**: 2-3 questions (MEDIUM priority)
  - Encoding: Target (RECOMMENDED for high cardinality), Label, One-hot
  - High cardinality strategy: Target encoding, Frequency encoding
- **scale_features**: 1 question (LOW priority)
  - Skip scaling: Yes (RECOMMENDED) - "Tree models are scale-invariant"

**For Neural Networks**:
- **clean_data**: 2-3 questions (HIGH priority)
  - Outlier method: Z-score (RECOMMENDED), Percentile capping, Robust scaler
  - Outlier threshold: 3.0 standard deviations
- **handle_missing**: 3-4 questions (CRITICAL priority)
  - Imputation method: KNN (RECOMMENDED), MICE, Mean/Median
  - KNN neighbors: 5 (default), range 3-10
  - Imputation features: All features or subset
- **encode_features**: 2-3 questions (HIGH priority)
  - Encoding: One-hot (RECOMMENDED), Embeddings, Binary
  - Embedding dimensions: For high cardinality
- **scale_features**: 2-3 questions (CRITICAL priority)
  - Scaling method: StandardScaler (RECOMMENDED), MinMaxScaler
  - Normalization: Layer normalization, Batch normalization

**Dynamic Question Count Logic**:

```python
def determine_question_count(step, data_profile, algorithm_category, algorithm_requirements):
    """Determine number of questions (1-5) for a preprocessing step."""

    if step == "clean_data":
        count = 1  # Always at least 1 (duplicate handling)
        if data_profile["outlier_percentage"] > 5:
            count += 1  # Outlier method
        if algorithm_requirements["outlier_sensitive"]:
            count += 1  # Additional outlier parameters
        return min(count, 5)

    elif step == "handle_missing":
        missing_pct = data_profile["missing_percentage"]
        count = 0
        if missing_pct > 0:
            count += 1  # Imputation method
        if missing_pct > 20:
            count += 1  # High missing strategy
        if algorithm_category == "neural_networks":
            count += 1  # Advanced imputation options
        return min(count, 5)

    elif step == "encode_features":
        count = 0
        if len(data_profile["categorical_columns"]) > 0:
            count += 1  # Basic encoding method
        if len(data_profile["high_cardinality_columns"]) > 0:
            count += 1  # High cardinality strategy
        return min(count, 5)

    elif step == "scale_features":
        if algorithm_requirements["scaling_required"]:
            return 2  # Method + parameters
        else:
            return 1  # Skip or apply (tree models)
```

**Bedrock Model**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`

**Temperature**: 0.3 (slightly higher for natural question phrasing)

**Fallback**: If agent fails, generate basic questions (5 total, 1-2 per step)

#### 5.3.5 State Management (Enhanced)

**PipelineState Extensions for Algorithm-Aware HITL**:
```python
class PipelineState(TypedDict):
    # ... existing fields ...

    # Algorithm Prediction (Agent 1A)
    algorithm_category: str  # "linear_models" | "tree_models" | "neural_networks" | "ensemble" | "time_series"
    algorithm_confidence: float  # 0.0-1.0
    algorithm_reasoning: str  # Why this category was predicted
    recommended_algorithms: List[str]  # Specific algorithms (e.g., ["RandomForest", "XGBoost"])
    algorithm_requirements: Dict[str, Any]  # Preprocessing requirements from Agent 1A

    # Preprocessing Questions (Agent 1B)
    review_questions: List[Dict[str, Any]]  # 4-20 questions grouped by preprocessing step
    question_count_by_step: Dict[str, int]  # Number of questions per step
    preprocessing_recommendations: Dict[str, str]  # Recommended techniques per step

    # User Answers
    review_answers: Dict[str, Any]  # Selected techniques and parameters
    # Example:
    # {
    #   "clean_data_technique": "winsorization",
    #   "winsorization_lower_pct": 1,
    #   "winsorization_upper_pct": 99,
    #   "handle_missing_technique": "knn_imputation",
    #   "knn_neighbors": 5,
    #   "encode_technique": "one_hot",
    #   "scale_technique": "standard_scaler"
    # }

    # Review Status
    review_approved: bool  # True if approved
    review_iteration: int  # Number of review cycles
    review_status: str  # "awaiting_review" | "approved" | "rejected"
    review_feedback: str  # User feedback text (for rejection)
    pipeline_status: str  # "awaiting_review" during HITL pause

    # Agent Metadata
    agent_1a_execution_time: float  # Seconds
    agent_1b_execution_time: float  # Seconds
    agent_1a_tokens_used: int  # Bedrock tokens
    agent_1b_tokens_used: int  # Bedrock tokens
```

**State Transitions**:
1. `load_data_node` completes → `pipeline_status = "predicting_algorithm"`
2. Agent 1A completes → `pipeline_status = "generating_questions"`
3. Agent 1B completes → `pipeline_status = "awaiting_review"`, `review_status = "awaiting_review"`
4. User approves → `review_approved = True`, `review_status = "approved"`, `pipeline_status = "preprocessing"`
5. User rejects → `review_approved = False`, `review_status = "rejected"`, `review_iteration += 1`

#### 5.3.6 Preprocessing Technique Execution

**Enhanced Preprocessing Nodes**:

Each preprocessing node (`clean_data_node`, `handle_missing_node`, `encode_features_node`, `scale_features_node`) must:

1. **Read approved technique** from `state["review_answers"]`
2. **Execute technique** with user-specified parameters
3. **Log technique selection** to MLflow
4. **Handle missing technique** gracefully (use defaults or skip)

**Example**: `ml_pipeline/nodes/preprocessing/clean_data.py`

```python
def clean_data_node(state: PipelineState) -> PipelineState:
    """Enhanced clean_data node with multiple technique support."""

    # Get approved technique from review answers
    approved_technique = state.get("review_answers", {}).get("clean_data_technique", "iqr_method")

    # Execute technique based on user selection
    if approved_technique == "iqr_method":
        multiplier = state["review_answers"].get("iqr_multiplier", 1.5)
        df = apply_iqr_outlier_removal(df, multiplier=multiplier)

    elif approved_technique == "z_score_filtering":
        threshold = state["review_answers"].get("z_score_threshold", 3.0)
        df = apply_z_score_filtering(df, threshold=threshold)

    elif approved_technique == "winsorization":
        lower_pct = state["review_answers"].get("winsorization_lower_pct", 1)
        upper_pct = state["review_answers"].get("winsorization_upper_pct", 99)
        df = apply_winsorization(df, lower_pct=lower_pct, upper_pct=upper_pct)

    elif approved_technique == "isolation_forest":
        contamination = state["review_answers"].get("contamination", 0.1)
        df = apply_isolation_forest(df, contamination=contamination)

    elif approved_technique == "none":
        logger.info("Skipping outlier removal (user approved)")
        # No outlier removal

    # Log technique to MLflow
    mlflow.log_param("clean_data_technique", approved_technique)
    mlflow.log_param("algorithm_category", state["algorithm_category"])

    # ... rest of node logic (duplicates, etc.)
```

**Technique Implementation Matrix**:

| Technique | Parameters | Implementation Function |
|-----------|------------|------------------------|
| **Outlier Handling** |||
| IQR Method | `iqr_multiplier` (default: 1.5) | `apply_iqr_outlier_removal()` |
| Z-Score Filtering | `z_score_threshold` (default: 3.0) | `apply_z_score_filtering()` |
| Winsorization | `lower_pct`, `upper_pct` (default: 1, 99) | `apply_winsorization()` |
| Isolation Forest | `contamination` (default: 0.1) | `apply_isolation_forest()` |
| None | - | Skip outlier removal |
| **Missing Value Handling** |||
| Mean Imputation | `strategy="mean"` | `apply_simple_imputation()` |
| Median Imputation | `strategy="median"` | `apply_simple_imputation()` |
| Mode Imputation | `strategy="mode"` | `apply_simple_imputation()` |
| KNN Imputation | `knn_neighbors` (default: 5) | `apply_knn_imputation()` |
| MICE Imputation | `max_iter` (default: 10) | `apply_mice_imputation()` |
| Drop Rows | `threshold` (default: 0%) | `drop_missing_rows()` |
| **Categorical Encoding** |||
| One-Hot Encoding | `drop_first` (default: False) | `apply_one_hot_encoding()` |
| Label Encoding | - | `apply_label_encoding()` |
| Target Encoding | `smoothing` (default: 1.0) | `apply_target_encoding()` |
| Frequency Encoding | - | `apply_frequency_encoding()` |
| Binary Encoding | - | `apply_binary_encoding()` |
| **Feature Scaling** |||
| StandardScaler | `with_mean`, `with_std` (default: True, True) | `apply_standard_scaling()` |
| MinMaxScaler | `feature_range` (default: (0,1)) | `apply_minmax_scaling()` |
| RobustScaler | `with_centering`, `with_scaling` | `apply_robust_scaling()` |
| None | - | Skip scaling |

#### 5.3.7 Security Considerations

1. **Authentication**: Review submission requires authenticated user session
2. **Authorization**: Only pipeline creator can approve/reject reviews
3. **Data Privacy**:
   - Only store anonymized data previews in review table (max 100 rows)
   - Full datasets not persisted in PostgreSQL
   - Sensitive columns (PII) detected and masked in data preview
   - Algorithm prediction based on metadata only (no raw data in prompts)
4. **Audit Trail**:
   - All decisions logged with user ID, timestamp, and algorithm context
   - Store both Agent 1A and 1B prompts and responses
   - Immutable audit log (INSERT-only, no DELETE)
   - Track technique selections for compliance
5. **Token Management**:
   - Track Bedrock API token usage per agent (1A and 1B separately)
   - Set budget alerts for excessive token consumption (>10k tokens per review)
   - Monitor cumulative token usage across review iterations
6. **Input Validation**:
   - Validate technique parameters (e.g., `knn_neighbors` must be 3-10)
   - Sanitize user feedback text (prevent injection attacks)
   - Verify technique values against allowed list

#### 5.3.8 Performance Requirements

**Agent Execution Times**:
- **Agent 1A (Algorithm Prediction)**: Target < 3 seconds, Max 5 seconds
- **Agent 1B (Question Generation)**: Target < 5 seconds, Max 10 seconds
- **Total Question Generation**: Target < 8 seconds, Max 15 seconds

**System Performance**:
- **Review Session Creation**: Target < 2 seconds (includes database writes)
- **Pipeline Interruption Overhead**: Target < 500ms
- **Frontend Polling Frequency**: Every 2 seconds (configurable)
- **Database Query Performance**: < 100ms for session retrieval
- **Technique Execution Overhead**: < 5% compared to fixed preprocessing

**Scalability**:
- Support concurrent review sessions for up to 100 users
- Handle datasets up to 1GB without performance degradation in Agent 1A
- Cache algorithm category predictions for similar datasets (reduce redundant API calls)

**Optimization Strategies**:
- Cache Agent 1A predictions based on data profile hash (validity: 24 hours)
- Pre-generate common question templates to reduce Agent 1B latency
- Implement progressive question loading in frontend (load by tab)
- Use connection pooling for PostgreSQL (max 50 connections)

#### 5.3.9 Error Handling (Enhanced)

**Failure Scenarios**:

1. **Agent 1A (Algorithm Prediction) Fails**:
   - Fallback: Default to "tree_models" category (most versatile)
   - Reasoning: "Algorithm prediction failed, defaulting to tree-based models"
   - Log error to MLflow and PostgreSQL with full context
   - Continue to Agent 1B with fallback category

2. **Agent 1B (Question Generation) Fails**:
   - Fallback: Generate basic questions (5 total, 1-2 per step)
   - Use algorithm_category from Agent 1A (or fallback if both failed)
   - Basic questions:
     - clean_data: "Remove outliers using IQR method?" (yes/no)
     - handle_missing: "Imputation method?" (mean/median/drop)
     - encode_features: "Encoding method?" (one-hot/label)
     - scale_features: "Apply StandardScaler?" (yes/no)
   - Log error to MLflow and PostgreSQL

3. **PostgreSQL Connection Failed**:
   - Store review session in MLflow artifacts as fallback
   - Filename: `review_session_{run_id}.json`
   - Display warning in frontend: "Audit logging unavailable"
   - Continue with in-memory state
   - Retry PostgreSQL connection on next pipeline run

4. **Frontend Timeout (user takes >30 minutes)**:
   - Auto-reject and save partial answers to database
   - Send notification to user (email/Slack)
   - Mark pipeline status as "timed_out"
   - Allow user to resume review within 24 hours

5. **Interruption Mechanism Fails**:
   - Graceful degradation: Skip HITL and continue pipeline with defaults
   - Use algorithm_category prediction if Agent 1A succeeded
   - Apply default preprocessing techniques based on algorithm category
   - Log warning to MLflow: "HITL bypassed due to interruption failure"
   - Notify user via email/Slack

6. **Invalid Technique Parameter**:
   - Validate parameters before execution
   - If invalid, use default parameter value
   - Log warning: "Invalid parameter {param_name}={value}, using default {default}"
   - Continue preprocessing

7. **Technique Execution Fails**:
   - Catch exception during technique application
   - Fall back to default technique for that step (e.g., IQR for outliers)
   - Log error with full stack trace to MLflow
   - Update state with fallback technique used
   - Continue pipeline (don't fail entire run)

#### 5.3.10 Future Enhancements

1. **Adaptive Algorithm Prediction**:
   - Learn from historical pipeline results
   - Track algorithm accuracy: predicted category vs. best performing algorithm
   - Adjust prediction logic based on feedback loop
   - Confidence threshold: Only auto-select if confidence > 95%

2. **Smart Technique Recommendation**:
   - Analyze historical technique selections and their impact on model performance
   - Recommend techniques that historically improved accuracy for similar datasets
   - A/B testing framework for comparing preprocessing strategies

3. **Interactive Technique Preview**:
   - Show sample data transformation in real-time
   - Display before/after statistics (e.g., outlier count, missing values)
   - Visualize impact of parameters (slider for `knn_neighbors` shows imputation quality)

4. **Multi-User Approval Workflow**:
   - Require approval from multiple stakeholders (data scientist + domain expert)
   - Approval workflow with escalation rules
   - Role-based technique restrictions (junior users limited to recommended options)

5. **Domain-Specific Preprocessing Profiles**:
   - Pre-configured profiles for common domains (finance, healthcare, retail)
   - Domain-specific technique preferences (e.g., healthcare: preserve outliers for anomaly detection)
   - Compliance-aware preprocessing (GDPR, HIPAA)

6. **Technique Performance Analytics**:
   - Dashboard showing technique effectiveness by dataset type
   - Track: Technique → Model Accuracy correlation
   - Recommendations: "Datasets with X% missing values benefit from KNN over mean imputation"

7. **Automated Hyperparameter Tuning for Preprocessing**:
   - Optimize technique parameters (e.g., best `knn_neighbors` value)
   - Use Optuna or Hyperopt to search parameter space
   - Balance preprocessing time vs. model performance improvement

8. **Explainable Preprocessing**:
   - Generate human-readable explanations for why each technique was recommended
   - Show impact: "Winsorization reduced outlier impact by 37%, improving linear model coefficient stability"
   - Technique comparison: Side-by-side metric comparison (IQR vs. Z-score vs. Winsorization)

### 5.4 AI Decision Agent Component

#### 5.4.1 Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Base Architecture                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Context Preparation                                     │ │
│  │     - Extract relevant state information                    │ │
│  │     - Format into structured JSON                           │ │
│  │     - Add business constraints                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  2. Prompt Construction                                     │ │
│  │     - Load prompt template                                  │ │
│  │     - Inject context data                                   │ │
│  │     - Add output format specification                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  3. AWS Bedrock API Call                                    │ │
│  │     - Initialize Bedrock client                             │ │
│  │     - Invoke Claude model                                   │ │
│  │     - Handle rate limiting & retries                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  4. Response Parsing                                        │ │
│  │     - Extract JSON from response                            │ │
│  │     - Validate against schema                               │ │
│  │     - Handle parsing errors                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  5. Decision Logging                                        │ │
│  │     - Log to MLflow (prompt, response, decision)            │ │
│  │     - Update pipeline state                                 │ │
│  │     - Store for audit trail                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.4.2 Agent 0: Configuration Extraction

**Purpose**: Extract ML pipeline configuration from natural language user prompts

**Input Schema:**
```python
{
    "user_prompt": str,  # "I want to analyze how liveness relates to track_genre"
    "data_path": str,
    "available_columns": List[str],
    "dataset_preview": {
        "n_rows": int,
        "n_columns": int,
        "dtypes": Dict[str, str]
    },
    "user_hints": Optional[Dict[str, str]]  # User can provide hints before extraction
}
```

**Output Schema:**
```python
{
    "target_column": str,
    "experiment_name": str,  # Generated from prompt (snake_case)
    "test_size": float,  # 0.1-0.5, default 0.2
    "random_state": int,  # Default 42
    "analysis_type": str,  # "classification" | "regression"
    "confidence": float,  # 0.0-1.0 (requires >= 0.70 to proceed)
    "reasoning": str,
    "assumptions": List[str],
    "warnings": List[str]
}
```

**Bedrock Model**:
- Primary: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Fallback: `anthropic.claude-3-7-sonnet-20250219-v1:0`

**Confidence Threshold**: Minimum 70% confidence required. If confidence < 0.70, system returns error and asks user for manual configuration or to refine prompt.

**Fallback Strategy**: If Bedrock fails, return error suggesting to try fallback model. No automatic heuristics to avoid incorrect assumptions.

**Storage**: User prompts and extracted configurations stored in triple storage:
- MLflow artifacts (experiment lineage)
- PostgreSQL database (querying/analytics)
- MinIO/S3 (long-term archival)

#### 5.4.3 Agent 1: Review Question Generation (HITL)

**Purpose**: Generate intelligent review questions for human approval of preprocessing decisions

**Note**: This agent is comprehensively documented in Section 5.3: Human-in-the-Loop (HITL) Component. See Section 5.3.3 for complete input/output schemas, question generation strategy, and implementation details.

**Key Responsibilities**:
- Analyze dataset preview and preprocessing configuration
- Generate 5 contextual yes/no questions covering:
  - Duplicate row handling
  - Missing value imputation strategy
  - Outlier removal approach
  - Categorical encoding methods
  - Numerical feature scaling
- Prioritize questions by importance (HIGH/MEDIUM/LOW)
- Provide context explanations for each question
- Trigger LangGraph interruption for human review

**Integration**: This agent executes after `load_data_node` and before preprocessing operations, creating a review session that pauses the pipeline until human approval is received.

#### 5.4.4 Agent 2: Algorithm Selection

**Input Schema:**
```python
{
    "n_samples": int,
    "n_features": int,
    "target_type": str,  # "classification" | "regression"
    "class_distribution": Dict[int, int],
    "feature_correlations": Dict[str, float],
    "computational_budget": {
        "max_time_minutes": int,
        "max_parallel": int
    }
}
```

**Output Schema:**
```python
{
    "selected_algorithms": List[str],
    "reasoning": Dict[str, str],
    "hyperparameter_suggestions": Dict[str, Dict],
    "estimated_times": Dict[str, float],
    "skip_algorithms": List[str],
    "skip_reasons": Dict[str, str]
}
```

#### 5.4.5 Agent 3: Model Selection

**Input Schema:**
```python
{
    "trained_models": List[{
        "algorithm": str,
        "cv_mean": float,
        "cv_std": float,
        "test_accuracy": float,
        "test_f1": float,
        "training_time": float,
        "model_complexity": str
    }],
    "business_requirements": {
        "max_prediction_latency_ms": int,
        "interpretability_importance": str
    }
}
```

**Output Schema:**
```python
{
    "selected_model": str,
    "reasoning": str,
    "confidence": float,
    "trade_offs": Dict[str, str],
    "risks": List[str],
    "alternative_model": str
}
```

#### 5.4.6 Agent 4: Retraining Decision

**Input Schema:**
```python
{
    "performance_analysis": {
        "current_accuracy": float,
        "baseline_accuracy": float,
        "performance_drop": float,
        "threshold": float
    },
    "drift_analysis": {
        "drift_detected": bool,
        "drift_score": float,
        "affected_features": List[str]
    },
    "business_context": {
        "model_age_days": int,
        "predictions_per_day": int
    }
}
```

**Output Schema:**
```python
{
    "retrain": bool,
    "reasoning": str,
    "urgency": str,  # "low" | "medium" | "high"
    "confidence": float,
    "contributing_factors": List[str],
    "recommended_actions": List[str]
}
```

### 5.5 ML Processing Component

#### 5.5.1 Preprocessing Module

```
┌─────────────────────────────────────────────────────────────┐
│                  Preprocessing Pipeline                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Data Quality Check                                  │ │
│  │     - Null value analysis                               │ │
│  │     - Data type validation                              │ │
│  │     - Duplicate detection                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  2. Missing Value Handling                              │ │
│  │     - Imputation strategy selection                     │ │
│  │     - Mean/Median/Mode imputation                       │ │
│  │     - KNN imputation                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  3. Outlier Detection & Treatment                       │ │
│  │     - IQR method                                        │ │
│  │     - Z-score method                                    │ │
│  │     - Capping/Removal                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  4. Feature Encoding                                    │ │
│  │     - One-hot encoding (categorical)                    │ │
│  │     - Label encoding (ordinal)                          │ │
│  │     - Target encoding                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  5. Feature Scaling                                     │ │
│  │     - StandardScaler (z-score normalization)            │ │
│  │     - MinMaxScaler (0-1 scaling)                        │ │
│  │     - RobustScaler (outlier-resistant)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 5.5.2 Training Module

**Algorithm Training Node Design:**

```python
class AlgorithmTrainingNode:
    """
    Generic algorithm training node with GridSearchCV
    """

    def __init__(self, algorithm_name: str, estimator_class, param_grid: Dict):
        self.algorithm_name = algorithm_name
        self.estimator = estimator_class
        self.param_grid = param_grid

    def execute(self, state: PipelineState) -> PipelineState:
        """
        Execute training with hyperparameter tuning

        Steps:
        1. Start MLflow child run
        2. Initialize GridSearchCV
        3. Fit on training data
        4. Extract best model and parameters
        5. Evaluate on test set
        6. Log everything to MLflow
        7. Update state with results
        """
```

**Hyperparameter Tuning Configuration:**

```python
# Example: Random Forest
param_grid_rf = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2'],
    'bootstrap': [True, False]
}

# GridSearchCV configuration
grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid_rf,
    cv=5,  # 5-fold cross-validation
    scoring='f1_weighted',
    n_jobs=-1,  # Use all CPU cores
    verbose=2,
    return_train_score=True
)
```

#### 5.5.3 Monitoring Module

**Drift Detection:**

```python
class DriftDetector:
    """
    Detect data drift using statistical tests
    """

    def detect_drift(self,
                     reference_data: pd.DataFrame,
                     current_data: pd.DataFrame) -> DriftReport:
        """
        Steps:
        1. For each feature:
           a. Numerical: Kolmogorov-Smirnov test
           b. Categorical: Chi-squared test
        2. Calculate PSI (Population Stability Index)
        3. Aggregate drift scores
        4. Flag drifted features
        """

        drift_results = {}

        for column in reference_data.columns:
            if is_numerical(column):
                # KS test
                ks_stat, p_value = ks_2samp(
                    reference_data[column],
                    current_data[column]
                )
                drift_results[column] = {
                    "test": "ks",
                    "statistic": ks_stat,
                    "p_value": p_value,
                    "drift_detected": p_value < 0.05
                }
            else:
                # Chi-squared test
                chi2, p_value = chi2_test(
                    reference_data[column],
                    current_data[column]
                )
                drift_results[column] = {
                    "test": "chi2",
                    "statistic": chi2,
                    "p_value": p_value,
                    "drift_detected": p_value < 0.05
                }

            # Calculate PSI
            psi = calculate_psi(reference_data[column], current_data[column])
            drift_results[column]["psi"] = psi

        return DriftReport(drift_results)
```

**Performance Monitoring:**

```python
class PerformanceMonitor:
    """
    Monitor model performance against baseline
    """

    def compare_performance(self,
                           current_metrics: Dict[str, float],
                           baseline_metrics: Dict[str, float],
                           threshold: float = 0.05) -> PerformanceReport:
        """
        Compare current performance with baseline

        Returns:
        - performance_drop: absolute difference
        - performance_drop_pct: percentage drop
        - threshold_exceeded: bool
        - detailed_comparison: per-metric breakdown
        """
```

### 5.6 MLflow Integration Component

#### 5.6.1 Experiment Manager

```python
class MLflowExperimentManager:
    """
    Manage MLflow experiments and runs
    """

    def __init__(self, tracking_uri: str):
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()

    def create_experiment(self, name: str, tags: Dict = None) -> str:
        """Create or get existing experiment"""

    def start_run(self, run_name: str, nested: bool = False) -> str:
        """Start a new MLflow run"""

    def end_run(self):
        """End current MLflow run"""

    def log_params(self, params: Dict):
        """Log parameters"""

    def log_metrics(self, metrics: Dict, step: int = None):
        """Log metrics"""

    def log_artifact(self, file_path: str):
        """Log artifact file"""

    def log_model(self, model, artifact_path: str, signature=None):
        """Log trained model"""
```

#### 5.6.2 Model Registry Manager

```python
class MLflowModelRegistry:
    """
    Manage model registration and versioning
    """

    def register_model(self,
                      model_uri: str,
                      model_name: str,
                      tags: Dict = None) -> ModelVersion:
        """Register model in registry"""

    def transition_model_stage(self,
                              model_name: str,
                              version: int,
                              stage: str):  # "Staging" | "Production"
        """Transition model to different stage"""

    def get_latest_model(self, model_name: str, stage: str = "Production"):
        """Get latest model version for given stage"""
```

---

## 6. Data Design

### 6.1 State Data Model

The complete state object flows through the LangGraph pipeline:

```python
# Initial State (after data loading)
{
    "raw_data": DataFrame(10000 rows × 25 columns),
    "mlflow_experiment_id": "5",
    "mlflow_run_id": "abc123",
    "pipeline_status": "data_loaded"
}

# After Preprocessing
{
    ...previous state,
    "cleaned_data": DataFrame(9800 rows × 35 columns),
    "feature_statistics": {...},
    "pipeline_status": "preprocessed"
}

# After Feature Selection
{
    ...previous state,
    "selected_features": ["feature_1", "feature_3", ...],
    "feature_importance": {"feature_1": 0.25, ...},
    "X_train": DataFrame(7840 rows × 15 columns),
    "X_test": DataFrame(1960 rows × 15 columns),
    "pipeline_status": "features_selected"
}

# After Agent 2 Decision (Algorithm Selection)
{
    ...previous state,
    "algorithm_selection_decision": {
        "selected_algorithms": ["random_forest", "gradient_boosting"],
        "reasoning": {...},
        ...
    },
    "pipeline_status": "algorithms_selected"
}

# After Training
{
    ...previous state,
    "algorithm_results": {
        "random_forest": {
            "model": <RandomForestClassifier>,
            "cv_mean": 0.87,
            "test_accuracy": 0.88,
            ...
        },
        "gradient_boosting": {...}
    },
    "pipeline_status": "models_trained"
}

# Final State
{
    ...all previous state,
    "best_model_name": "gradient_boosting",
    "best_model": <GradientBoostingClassifier>,
    "drift_detected": True,
    "performance_comparison": {...},
    "retraining_decision": {...},
    "pipeline_status": "completed"
}
```

### 6.2 MLflow Data Model

**Experiment Hierarchy:**
```
Experiment: "mlops_pipeline_v1"
├── Run 1: "2025-11-30_run_001"
│   ├── Parameters:
│   │   ├── data_path: "data/train.csv"
│   │   ├── test_size: 0.2
│   │   ├── cv_folds: 5
│   │   └── ...
│   ├── Metrics:
│   │   ├── best_model_accuracy: 0.90
│   │   ├── drift_score: 0.15
│   │   └── ...
│   ├── Artifacts:
│   │   ├── models/
│   │   │   ├── random_forest/
│   │   │   └── gradient_boosting/
│   │   ├── plots/
│   │   ├── reports/
│   │   └── agents/
│   │       ├── algorithm_selection_decision.json
│   │       ├── model_selection_decision.json
│   │       └── retraining_decision.json
│   └── Nested Runs:
│       ├── Run 1.1: "random_forest"
│       │   ├── Parameters: {n_estimators: 200, max_depth: 20, ...}
│       │   ├── Metrics: {cv_mean: 0.87, test_accuracy: 0.88, ...}
│       │   └── Artifacts: {model, cv_results.json}
│       ├── Run 1.2: "gradient_boosting"
│       └── Run 1.3: "logistic_regression"
└── Run 2: "2025-12-01_run_002"
    └── ...
```

**Model Registry Structure:**
```
Model: "mlops_best_model"
├── Version 1 (Staging)
│   ├── Source: Run 1
│   ├── Created: 2025-11-30
│   ├── Metrics: {accuracy: 0.88}
│   └── Tags: {algorithm: "random_forest"}
├── Version 2 (Production)
│   ├── Source: Run 1
│   ├── Created: 2025-11-30
│   ├── Metrics: {accuracy: 0.90}
│   └── Tags: {algorithm: "gradient_boosting"}
└── Version 3 (Archived)
```

### 6.3 Database Schema (PostgreSQL for MLflow Backend)

```sql
-- MLflow creates these tables automatically
-- Shown here for completeness

-- Experiments table
CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    name VARCHAR(256) NOT NULL UNIQUE,
    artifact_location VARCHAR(256),
    lifecycle_stage VARCHAR(32),
    creation_time BIGINT,
    last_update_time BIGINT
);

-- Runs table
CREATE TABLE runs (
    run_uuid VARCHAR(32) PRIMARY KEY,
    name VARCHAR(250),
    source_type VARCHAR(20),
    source_name VARCHAR(500),
    entry_point_name VARCHAR(50),
    user_id VARCHAR(256),
    status VARCHAR(20),
    start_time BIGINT,
    end_time BIGINT,
    deleted_time BIGINT,
    source_version VARCHAR(50),
    lifecycle_stage VARCHAR(20),
    artifact_uri VARCHAR(200),
    experiment_id INTEGER REFERENCES experiments(experiment_id)
);

-- Metrics table (time-series metrics)
CREATE TABLE metrics (
    key VARCHAR(250) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp BIGINT NOT NULL,
    run_uuid VARCHAR(32) REFERENCES runs(run_uuid),
    step BIGINT DEFAULT 0 NOT NULL,
    is_nan BOOLEAN DEFAULT FALSE NOT NULL,
    PRIMARY KEY (key, timestamp, step, run_uuid, value, is_nan)
);

-- Parameters table
CREATE TABLE params (
    key VARCHAR(250) NOT NULL,
    value VARCHAR(500) NOT NULL,
    run_uuid VARCHAR(32) REFERENCES runs(run_uuid),
    PRIMARY KEY (key, run_uuid)
);

-- Model registry tables
CREATE TABLE registered_models (
    name VARCHAR(256) PRIMARY KEY,
    creation_time BIGINT,
    last_updated_time BIGINT,
    description VARCHAR(5000)
);

CREATE TABLE model_versions (
    name VARCHAR(256) REFERENCES registered_models(name),
    version INTEGER NOT NULL,
    creation_time BIGINT,
    last_updated_time BIGINT,
    description VARCHAR(5000),
    user_id VARCHAR(256),
    current_stage VARCHAR(20),
    source VARCHAR(500),
    run_id VARCHAR(32),
    status VARCHAR(20),
    status_message VARCHAR(500),
    PRIMARY KEY (name, version)
);
```

---

## 7. Interface Design

### 7.1 React UI Mockups

#### 7.1.1 Main Dashboard

```
╔════════════════════════════════════════════════════════════════════╗
║  MLOps Pipeline Automation Dashboard                              ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  📊 Pipeline Status: [●] Running - Stage 4/8: Model Training      ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50% Complete     ║
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  📁 Data Configuration                                        │ ║
║  │  ├── Dataset: train.csv (10,000 rows × 25 features)          │ ║
║  │  ├── Train/Test Split: 80/20                                 │ ║
║  │  └── Selected Features: 15                                   │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  🤖 Agent Decisions                                           │ ║
║  │  ├── [✓] Algorithm Selection: RF, GB, LR (3 selected)        │ ║
║  │  ├── [⏳] Model Selection: In Progress...                     │ ║
║  │  └── [○] Retraining Decision: Pending                        │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  📈 Live Metrics                                              │ ║
║  │  ├── Random Forest:      CV=0.87 (±0.02) | Test=0.88 ✓       │ ║
║  │  ├── Gradient Boosting:  CV=0.89 (±0.01) | Test=0.90 ✓       │ ║
║  │  └── Logistic Regression: Training... 67%                     │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  [⚙️ Configure]  [▶️ Start Pipeline]  [⏸️ Pause]  [🔄 Retrain]  ║
╚════════════════════════════════════════════════════════════════════╝
```

#### 7.1.2 Graph Visualization Panel

```
╔════════════════════════════════════════════════════════════════════╗
║  LangGraph Workflow Visualization                                  ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║                          [load_data] ✓                            ║
║                               │                                    ║
║                               ▼                                    ║
║                         [preprocess] ✓                            ║
║                               │                                    ║
║                               ▼                                    ║
║                      [feature_selection] ✓                        ║
║                               │                                    ║
║                               ▼                                    ║
║                  [🤖 agent_2_algorithm_select] ✓                  ║
║                               │                                    ║
║           ┌───────────────────┼───────────────────┐               ║
║           │                   │                   │               ║
║           ▼                   ▼                   ▼               ║
║    [train_rf] ✓        [train_gb] ●        [train_lr] ○          ║
║           │                   │                   │               ║
║           └───────────────────┼───────────────────┘               ║
║                               │                                    ║
║                               ▼                                    ║
║                  [🤖 agent_3_model_select] ○                      ║
║                               │                                    ║
║                               ▼                                    ║
║                        [evaluate_model] ○                         ║
║                                                                    ║
║  Legend: ✓ Completed | ● Running | ○ Pending | ✗ Failed          ║
║                                                                    ║
║  [🔍 Zoom In]  [🔍 Zoom Out]  [📥 Export PNG]                     ║
╚════════════════════════════════════════════════════════════════════╝
```

### 7.2 API Design (Internal)

#### 7.2.1 Pipeline Control API

```python
class PipelineController:
    """
    API for controlling pipeline execution from React UI
    """

    def start_pipeline(self, config: PipelineConfig) -> str:
        """
        Start a new pipeline run

        Args:
            config: Pipeline configuration

        Returns:
            run_id: Unique identifier for this run
        """

    def pause_pipeline(self, run_id: str):
        """Pause running pipeline"""

    def resume_pipeline(self, run_id: str):
        """Resume paused pipeline"""

    def stop_pipeline(self, run_id: str):
        """Stop pipeline execution"""

    def get_pipeline_status(self, run_id: str) -> PipelineStatus:
        """Get current pipeline status"""

    def trigger_manual_retrain(self, config: RetrainingConfig):
        """Manually trigger retraining"""
```

#### 7.2.2 State Query API

```python
class StateQueryAPI:
    """
    API for querying pipeline state
    """

    def get_current_state(self, run_id: str) -> PipelineState:
        """Get complete current state"""

    def get_node_status(self, run_id: str, node_name: str) -> NodeStatus:
        """Get status of specific node"""

    def get_metrics(self, run_id: str) -> Dict[str, Any]:
        """Get all metrics for run"""

    def get_agent_decisions(self, run_id: str) -> List[AgentDecision]:
        """Get all agent decisions"""
```

### 7.3 External Integrations

#### 7.3.1 AWS Bedrock Integration

```python
# Configuration
AWS_REGION = "us-east-1"
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# Client initialization
import boto3
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)

# Invoke model
response = bedrock_runtime.invoke_model(
    modelId=BEDROCK_MODEL_ID,
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
)
```

#### 7.3.2 MLflow Server Integration

```python
# MLflow server configuration
MLFLOW_TRACKING_URI = "http://mlflow-server:5000"
MLFLOW_ARTIFACT_ROOT = "s3://mlflow-artifacts"
MLFLOW_BACKEND_STORE_URI = "postgresql://user:pass@postgres:5432/mlflow"

# Initialize
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("mlops_pipeline_v1")
```

---

## 8. Security Design

### 8.1 Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Layer 1: React UI Authentication                      ││
│  │  - User login with credentials                         ││
│  │  - Role-based access control                           ││
│  │  - Session management                                  ││
│  └────────────────────────────────────────────────────────┘│
│                          │                                  │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Layer 2: AWS IAM                                      ││
│  │  - Service role for Bedrock access                    ││
│  │  - Least privilege permissions                        ││
│  │  - Access logging via CloudTrail                      ││
│  └────────────────────────────────────────────────────────┘│
│                          │                                  │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Layer 3: MLflow Authentication                        ││
│  │  - Basic auth or OAuth 2.0                            ││
│  │  - Experiment-level permissions                       ││
│  │  - Model registry access control                      ││
│  └────────────────────────────────────────────────────────┘│
│                          │                                  │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Layer 4: Data Encryption                              ││
│  │  - TLS for data in transit                            ││
│  │  - AES-256 for data at rest                           ││
│  │  - Key management via AWS KMS                         ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Data Privacy

**PII Detection & Masking:**
```python
class PIIDetector:
    """
    Detect and mask PII in datasets
    """

    PII_PATTERNS = {
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'phone': r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}',
        'ssn': r'\d{3}-\d{2}-\d{4}',
        'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}'
    }

    def detect_pii(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detect PII columns"""

    def mask_pii(self, df: pd.DataFrame, method='hash') -> pd.DataFrame:
        """Mask PII with hashing or redaction"""
```

### 8.3 Audit Logging

```python
class AuditLogger:
    """
    Comprehensive audit logging
    """

    def log_pipeline_start(self, user: str, config: Dict):
        """Log pipeline initiation"""

    def log_agent_decision(self, agent: str, decision: Dict, reasoning: str):
        """Log AI agent decisions"""

    def log_model_deployment(self, model_name: str, version: int, user: str):
        """Log model deployment"""

    def log_data_access(self, user: str, dataset: str, action: str):
        """Log data access"""
```

---

## 9. Deployment Architecture

### 9.1 Production Deployment

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AWS Cloud Environment                         │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Load Balancer (ALB)                          │ │
│  └────────────────────┬───────────────────────────────────────────┘ │
│                       │                                              │
│       ┌───────────────┼───────────────┐                             │
│       │               │               │                             │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐                        │
│  │React UI │    │React UI │    │React UI │                        │
│  │ Pod 1   │    │ Pod 2   │    │ Pod 3   │                        │
│  └────┬────┘    └────┬────┘    └────┬────┘                        │
│       └───────────────┼───────────────┘                             │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐ │
│  │              LangGraph Execution Pods                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │ │
│  │  │Pipeline  │  │Pipeline  │  │Pipeline  │  │Pipeline  │      │ │
│  │  │Worker 1  │  │Worker 2  │  │Worker 3  │  │Worker 4  │      │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                       │               │                              │
│       ┌───────────────┼───────────────┼─────────────┐               │
│       │               │               │             │               │
│  ┌────▼─────┐   ┌────▼─────┐   ┌────▼─────┐  ┌───▼──────┐        │
│  │  AWS     │   │ MLflow   │   │PostgreSQL│  │   S3     │        │
│  │ Bedrock  │   │  Server  │   │  (RDS)   │  │(Artifacts)│        │
│  └──────────┘   └──────────┘   └──────────┘  └──────────┘        │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Monitoring Stack                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │ │
│  │  │CloudWatch│  │ Grafana  │  │Prometheus│                     │ │
│  │  └──────────┘  └──────────┘  └──────────┘                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Container Architecture

**Docker Compose Configuration:**

```yaml
version: '3.8'

services:
  # React UI
  react-ui:
    image: mlops-pipeline-ui:latest
    ports:
      - "3000:80"
    environment:
      - BACKEND_URL=http://pipeline-backend:8000
      - MLFLOW_TRACKING_URI=http://mlflow-server:5000
    depends_on:
      - pipeline-backend
      - mlflow-server

  # LangGraph Pipeline Backend
  pipeline-backend:
    image: mlops-pipeline-backend:latest
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=us-east-1
      - MLFLOW_TRACKING_URI=http://mlflow-server:5000
      - POSTGRES_URI=postgresql://mlflow:mlflow@postgres:5432/mlflow
    depends_on:
      - postgres
      - mlflow-server
    volumes:
      - ./data:/app/data
      - ./models:/app/models

  # MLflow Tracking Server
  mlflow-server:
    image: mlflow-server:latest
    ports:
      - "5000:5000"
    command: >
      mlflow server
      --backend-store-uri postgresql://mlflow:mlflow@postgres:5432/mlflow
      --default-artifact-root s3://mlflow-artifacts
      --host 0.0.0.0
      --port 5000
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - postgres

  # PostgreSQL for MLflow
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=mlflow
      - POSTGRES_PASSWORD=mlflow
      - POSTGRES_DB=mlflow
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # MinIO (S3-compatible storage)
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio-data:/data

volumes:
  postgres-data:
  minio-data:
```

### 9.3 Kubernetes Deployment

```yaml
# React UI Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: react-ui
spec:
  replicas: 3
  selector:
    matchLabels:
      app: react-ui
  template:
    metadata:
      labels:
        app: react-ui
    spec:
      containers:
      - name: react-ui
        image: mlops-pipeline-ui:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: BACKEND_URL
          value: "http://pipeline-backend-service:8000"
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow-service:5000"

---

# Pipeline Backend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pipeline-backend
spec:
  replicas: 4
  selector:
    matchLabels:
      app: pipeline-backend
  template:
    metadata:
      labels:
        app: pipeline-backend
    spec:
      containers:
      - name: backend
        image: mlops-pipeline-backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
        env:
        - name: AWS_REGION
          value: "us-east-1"
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow-service:5000"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: pipeline-data-pvc

---

# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pipeline-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pipeline-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 10. Non-Functional Requirements

### 10.1 Performance Requirements

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Pipeline Execution Time | < 60 minutes for dataset up to 100K rows | End-to-end timing |
| UI Response Time | < 200ms for dashboard refresh | Browser performance API |
| MLflow Metric Logging | < 50ms per metric | Timing decorator |
| Agent Decision Time | < 30 seconds per decision | Bedrock API latency |
| Model Training (GridSearchCV) | Parallel execution on all cores | Resource utilization |
| Concurrent Pipeline Runs | Support 10+ simultaneous runs | Load testing |

### 10.2 Scalability Requirements

| Dimension | Requirement |
|-----------|-------------|
| Dataset Size | Support up to 10M rows, 1000 features |
| Algorithm Training | Parallel training of up to 10 algorithms |
| Concurrent Users | Support 50+ concurrent UI users |
| Model Versions | Manage 1000+ model versions per model |
| Experiment History | Retain 10,000+ experiment runs |
| Horizontal Scaling | Auto-scale from 2 to 20 backend pods |

### 10.3 Availability Requirements

| Component | Target Uptime | Recovery Time Objective (RTO) |
|-----------|---------------|-------------------------------|
| React UI | 99.5% | 5 minutes |
| Pipeline Backend | 99.9% | 2 minutes |
| MLflow Server | 99.9% | 2 minutes |
| PostgreSQL | 99.99% | 1 minute |
| AWS Bedrock | 99.9% (AWS SLA) | N/A |

### 10.4 Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| Data Encryption (Transit) | TLS 1.3 |
| Data Encryption (Rest) | AES-256 |
| Authentication | OAuth 2.0 + MFA |
| Authorization | RBAC with 3 roles: Viewer, Data Scientist, Admin |
| Audit Logging | All actions logged with retention period of 1 year |
| PII Protection | Automated detection and masking |
| Secrets Management | AWS Secrets Manager / HashiCorp Vault |

### 10.5 Maintainability Requirements

| Aspect | Requirement |
|--------|-------------|
| Code Coverage | > 80% test coverage |
| Documentation | Comprehensive API docs + architecture diagrams |
| Logging | Structured logging (JSON format) |
| Monitoring | Full observability with metrics, traces, logs |
| Deployment | GitOps with automated CI/CD |
| Configuration | Externalized config with version control |

### 10.6 Compliance Requirements

| Standard | Compliance Measures |
|----------|---------------------|
| GDPR | Data privacy controls, right to deletion |
| HIPAA (if applicable) | PHI encryption, access controls, audit trails |
| SOC 2 | Security controls, monitoring, incident response |
| Model Governance | Model approval workflows, change tracking |

---

## 11. Design Validation

### 11.1 Design Review Checklist

- [✓] All functional requirements addressed
- [✓] Non-functional requirements defined
- [✓] Component boundaries clearly defined
- [✓] Data flow documented
- [✓] Security design reviewed
- [✓] Scalability considerations addressed
- [✓] Deployment architecture defined
- [✓] Monitoring and observability planned

### 11.2 Known Limitations

1. **AWS Bedrock Dependency**: System requires active AWS account with Bedrock access
2. **Compute Resources**: Large datasets require significant CPU/memory resources
3. **GridSearchCV Time**: Exhaustive grid search can be time-consuming
4. **Drift Detection**: Requires historical baseline data for comparison
5. **Real-time Predictions**: Current design focuses on batch training, not real-time inference

### 11.3 Future Enhancements

1. **Real-time Inference API**: Add FastAPI endpoints for model serving
2. **AutoML Integration**: Integrate with Optuna or Ray Tune for advanced hyperparameter optimization
3. **Ensemble Methods**: Automated ensemble model creation
4. **A/B Testing Framework**: Built-in A/B testing for model comparison in production
5. **Edge Deployment**: Support for deploying models to edge devices
6. **Multi-cloud Support**: Azure ML and GCP Vertex AI integration

---

## 12. Conclusion

This High-Level Design document presents a comprehensive architecture for an intelligent MLOps pipeline automation system. The design leverages:

- **LangGraph** for flexible, state-driven workflow orchestration
- **AWS Bedrock Claude** for intelligent decision-making
- **MLflow** for comprehensive experiment tracking and model management
- **GridSearchCV** for systematic hyperparameter tuning
- **React** for interactive user interface

The architecture is designed to be:
- **Scalable**: Horizontal scaling for increased load
- **Maintainable**: Modular design with clear separation of concerns
- **Observable**: Comprehensive logging and monitoring
- **Secure**: Multiple layers of security controls
- **Production-ready**: Automated monitoring and retraining capabilities

This design serves as the foundation for the detailed design and implementation phases.

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| System Architect | | | |
| ML Lead | | | |
| Security Lead | | | |
| DevOps Lead | | | |

---

**End of High-Level Design Document**
