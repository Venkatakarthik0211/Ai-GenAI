# ML Pipeline System Architecture (Enhanced with MLflow & AI Decision Making)

## Overview

This document describes the enhanced system architecture for an intelligent Machine Learning pipeline implemented using LangGraph, MLflow for experiment tracking, and AWS Bedrock for AI-powered decision making. The system provides a stateful, graph-based workflow for end-to-end ML model development with intelligent optimization and automated retraining capabilities.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│              Vue.js 3 UI Layer (ChatGPT-like SPA Interface)                   │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  • Natural Language Pipeline Creation (Bedrock-powered)                 │  │
│  │  • Real-time LangGraph State Diagram (WebSocket updates)                │  │
│  │  • Run History Sidebar (ChatGPT-style)                                  │  │
│  │  • Live Pipeline Metrics & Progress                                     │  │
│  │  • AI Agent Decision Explanations (Confidence & Reasoning)              │  │
│  │  • Model Performance Visualization & Comparison                         │  │
│  │  • Responsive Design with Dark Mode                                     │  │
│  │  • MLflow Integration & Artifact Management                             │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │ REST API + WebSocket
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          ML Pipeline Orchestrator                             │
│                         (LangGraph Core + AI Agents)                          │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           State Management Layer                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Pipeline State (TypedDict)                                            │  │
│  │  - raw_data, cleaned_data, train/test data                            │  │
│  │  - selected_features, trained_models                                  │  │
│  │  - mlflow_run_id, experiment_id                                       │  │
│  │  - decision_agent_recommendations                                     │  │
│  │  - performance_metrics, drift_detected                                │  │
│  │  - retraining_triggered                                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      MLflow Experiment Tracking Layer                         │
│  - Experiment Creation                                                        │
│  - Run Management                                                             │
│  - Parameter Logging                                                          │
│  - Metric Tracking                                                            │
│  - Model Registry                                                             │
│  - Artifact Storage                                                           │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Enhanced Pipeline Nodes                                │
│                                                                               │
│  ┌──────────────────┐   ┌─────────────┐   ┌──────────────┐                  │
│  │  🤖 AGENT 0      │──▶│    Data     │──▶│ Preprocessing│                  │
│  │  Prompt Analysis │   │   Loading   │   │   + MLflow   │                  │
│  │  (Config Extract)│   └─────────────┘   └──────────────┘                  │
│  └──────────────────┘                                 │                      │
│   │ Stores to:                                        │                      │
│   │ - MLflow                                          ▼                      │
│   │ - PostgreSQL                              ┌──────────────┐               │
│   │ - MinIO/S3                                │ Train/Test   │               │
│   └────────────────────────────────────────▶  │    Split     │               │
│                                                └──────┬───────┘               │
│                                              │                                │
│                                              ▼                                │
│                                    ┌──────────────────┐                      │
│                                    │  Feature         │                      │
│                                    │  Selection       │                      │
│                                    └────────┬─────────┘                      │
│                                             │                                │
│                                             ▼                                │
│                              ┌──────────────────────────┐                    │
│                              │  🤖 DECISION AGENT 1     │                    │
│                              │  (Algorithm Selection)   │                    │
│                              │  AWS Bedrock Claude      │                    │
│                              │                          │                    │
│                              │  Analyzes:               │                    │
│                              │  - Data characteristics  │                    │
│                              │  - Feature types         │                    │
│                              │  - Class distribution    │                    │
│                              │  - Compute budget        │                    │
│                              │                          │                    │
│                              │  Decides:                │                    │
│                              │  - Which algorithms      │                    │
│                              │  - Hyperparameter ranges │                    │
│                              │  - CV strategy           │                    │
│                              └────────┬─────────────────┘                    │
│                                       │                                      │
│                    ┌──────────────────┴──────────────────┐                  │
│                    │                                      │                  │
│                    ▼                                      ▼                  │
│         ┌──────────────────────┐              ┌──────────────────────┐      │
│         │  Classification      │              │  Regression          │      │
│         │  Algorithm Nodes     │              │  Algorithm Nodes     │      │
│         │  (Dynamic)           │              │  (Dynamic)           │      │
│         │                      │              │                      │      │
│         │  - Logistic Reg Node │              │  - Linear Reg Node   │      │
│         │  - Random Forest Node│              │  - Ridge Reg Node    │      │
│         │  - Gradient Boost    │              │  - Lasso Reg Node    │      │
│         │  - SVM Node          │              │  - RF Regressor      │      │
│         │  - KNN Node          │              │  - GB Regressor      │      │
│         │                      │              │                      │      │
│         │  Each with:          │              │  Each with:          │      │
│         │  - MLflow logging    │              │  - MLflow logging    │      │
│         │  - Hyperparameter    │              │  - Hyperparameter    │      │
│         │    tuning (GridCV)   │              │    tuning (GridCV)   │      │
│         └──────────┬───────────┘              └──────────┬───────────┘      │
│                    └──────────────────┬──────────────────┘                  │
│                                       │                                      │
│                                       ▼                                      │
│                              ┌──────────────────────────┐                    │
│                              │  🤖 DECISION AGENT 2     │                    │
│                              │  (Model Selection)       │                    │
│                              │  AWS Bedrock Claude      │                    │
│                              │                          │                    │
│                              │  Analyzes:               │                    │
│                              │  - CV scores             │                    │
│                              │  - Training time         │                    │
│                              │  - Model complexity      │                    │
│                              │  - Business requirements │                    │
│                              │                          │                    │
│                              │  Decides:                │                    │
│                              │  - Best model            │                    │
│                              │  - Ensemble strategy     │                    │
│                              │  - Further tuning needed │                    │
│                              └────────┬─────────────────┘                    │
│                                       │                                      │
│                                       ▼                                      │
│                              ┌──────────────────┐                            │
│                              │  Model           │                            │
│                              │  Evaluation      │                            │
│                              │  + MLflow Log    │                            │
│                              └────────┬─────────┘                            │
│                                       │                                      │
│                                       ▼                                      │
│                              ┌──────────────────────────┐                    │
│                              │  Performance             │                    │
│                              │  Monitoring              │                    │
│                              │  - Track metrics         │                    │
│                              │  - Detect drift          │                    │
│                              │  - Compare with baseline │                    │
│                              └────────┬─────────────────┘                    │
│                                       │                                      │
│                                       ▼                                      │
│                              ┌──────────────────────────┐                    │
│                              │  🤖 DECISION AGENT 3     │                    │
│                              │  (Retraining Decision)   │                    │
│                              │  AWS Bedrock Claude      │                    │
│                              │                          │                    │
│                              │  Analyzes:               │                    │
│                              │  - Performance metrics   │                    │
│                              │  - Drift indicators      │                    │
│                              │  - Time since training   │                    │
│                              │  - Data volume           │                    │
│                              │                          │                    │
│                              │  Decides:                │                    │
│                              │  - Retrain: YES/NO       │                    │
│                              │  - Full vs incremental   │                    │
│                              │  - Keep current model    │                    │
│                              └────────┬─────────────────┘                    │
│                                       │                                      │
│                    ┌──────────────────┴──────────────────┐                  │
│                    │                                      │                  │
│                    ▼                                      ▼                  │
│         ┌──────────────────┐                  ┌──────────────────┐          │
│         │  Reporting &     │                  │  Trigger         │          │
│         │  Artifacts       │                  │  Retraining      │          │
│         │  + MLflow Log    │                  │  (Loop back)     │          │
│         └──────────────────┘                  └──────────────────┘          │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      MLflow Model Registry                                    │
│  - Model Versioning                                                           │
│  - Stage Transitions (Staging → Production)                                  │
│  - Model Metadata                                                             │
│  - Performance History                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Enhanced Design Principles

### 1. Intelligent Decision Making
- **AI-Powered Optimization**: AWS Bedrock Claude agents make intelligent decisions
- **Context-Aware**: Agents analyze data characteristics, compute resources, and business requirements
- **Adaptive**: Pipeline adapts based on agent recommendations
- **Cost-Efficient**: Reduces unnecessary computation through smart algorithm selection

### 2. Comprehensive Experiment Tracking
- **MLflow Integration**: Every experiment tracked automatically
- **Parameter Logging**: All hyperparameters recorded
- **Metric Tracking**: Real-time metric logging during training
- **Artifact Management**: Models, plots, and data artifacts versioned
- **Reproducibility**: Complete experiment reconstruction capability

### 3. Production-Ready Monitoring
- **Performance Tracking**: Continuous monitoring of model metrics
- **Drift Detection**: Automated detection of data/concept drift
- **Baseline Comparison**: Compare against production baselines
- **Alert System**: Notifications on performance degradation

### 4. Automated Retraining
- **Intelligent Triggers**: AI agent decides when retraining is needed
- **Incremental Learning**: Support for incremental model updates
- **A/B Testing**: Compare new model against production
- **Safe Deployment**: Gradual rollout with monitoring

### 5. Modular Algorithm Nodes
- **Separate Nodes per Algorithm**: Each algorithm is an independent LangGraph node
- **Parallel Execution**: Multiple algorithms can run concurrently
- **Easy Extension**: Add new algorithms by creating new nodes
- **Algorithm-Specific Logic**: Hyperparameter tuning tailored per algorithm

## System Components (Enhanced)

### 1. Vue.js 3 UI Layer (ChatGPT-like Interface)
**Responsibility**: Modern single-page application for pipeline control, monitoring, and visualization with real-time updates

**Technology Stack**:
- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Real-time**: WebSocket/SSE
- **Styling**: Tailwind CSS
- **Diagrams**: Mermaid.js
- **Deployment**: Docker + Nginx

**Architecture Pattern**: Component-based SPA with reactive state management and real-time data streaming

**Key Features**:

#### 1.1 ChatGPT-Inspired Layout
```typescript
Layout Structure:
- Left Sidebar (25-30% width, collapsible, resizable)
  - "New Run" button at top
  - Run history organized by date (Today, Yesterday, Last 7 Days)
  - Each run shows: ID, status icon, timestamp, experiment name
  - Click to load run details
  - Search/filter by experiment, status, date range
  - Hover actions: delete, duplicate, view in MLflow

- Main Content Area (70-75% width)
  - Header: Logo, settings, notifications, MLflow status
  - Dynamic content based on selection:
    * Empty state: Welcome + natural language prompt input
    * Active run: Real-time pipeline visualization
    * Completed run: Final results and analysis

- Responsive Design:
  - Desktop: Full split-view layout
  - Tablet: Collapsible sidebar
  - Mobile: Bottom navigation + full-screen content
```

#### 1.2 Natural Language Pipeline Creation
```typescript
Component: PromptInput.vue

Features:
- Large textarea for ML task description in natural language
- Placeholder examples:
  * "Classify iris species using random forest and SVM"
  * "Predict house prices, optimize for RMSE"
  * "Binary classification with class imbalance handling"
- Character count and AI assist suggestions
- Required fields:
  * Data path input with file browser integration
  * Experiment name (auto-generated timestamp or custom)
- Optional fields (collapsible section):
  * Test size, random state
  * Specific algorithms to include/exclude
  * Performance thresholds
- Validation feedback with inline error messages
- "🚀 Start Pipeline" button with loading state

Backend Integration:
- POST /api/pipeline/load-data with user_prompt
- Displays Bedrock config extraction results:
  * Extracted configuration (target_column, test_size, etc.)
  * Confidence score with progress bar
  * Reasoning as bullet points
  * Assumptions as tags
  * Warnings as alerts
- Edit mode to override config before pipeline execution
```

#### 1.3 Real-time LangGraph State Diagram
```typescript
Component: StateChart.vue

Features:
- Mermaid.js interactive diagram rendering
- Real-time node status updates via WebSocket:
  * ⏳ Pending (gray)
  * 🔄 In Progress (blue, animated pulse)
  * ✅ Completed (green with checkmark)
  * ❌ Failed (red with error icon)
- Conditional routing visualization:
  * Shows decision diamond for natural language vs traditional mode
  * Highlights analyze_prompt node when used
- Interactive features:
  * Click node to view execution details
  * Zoom and pan controls
  * Full-screen mode
  * Export diagram as PNG/SVG
- Node detail modal showing:
  * Start/end timestamps
  * Execution duration
  * Input/output state
  * Logs and errors
  * MLflow metrics logged during node execution

WebSocket Events:
- state_update: Full pipeline state refresh
- node_started: Node execution began
- node_completed: Node finished successfully
- node_failed: Node encountered error
- pipeline_completed: Pipeline finished
```

#### 1.4 Live Pipeline Metrics Panel
```typescript
Component: MetricsPanel.vue

Sections:
1. Data Profile (from load_data node):
   - Sample count, feature count
   - Target distribution (chart.js bar chart)
   - Missing value summary
   - Feature types breakdown

2. Progress Tracking:
   - Node completion percentage (circular progress)
   - Current node name with description
   - Estimated time remaining (calculated from node history)
   - Elapsed time since start

3. Performance Metrics (real-time updates):
   - Model training progress (per algorithm)
   - Cross-validation scores as they complete
   - Current best model with score
   - Grid search iterations completed

4. Resource Monitoring:
   - CPU/Memory usage (if available via backend API)
   - MLflow server status indicator
   - AWS Bedrock API calls made
   - Prompt storage status

5. Quick Links:
   - View in MLflow UI (opens experiment in new tab)
   - Download artifacts (models, plots, reports)
   - View execution logs
   - Export pipeline report
```

#### 1.5 Model Performance Visualization
```typescript
Component: ModelResultsPanel.vue

Features:
- Model comparison table (sortable, filterable):
  * Algorithm name
  * Cross-validation mean score
  * Standard deviation
  * Training time
  * Best hyperparameters
  * Actions: view details, deploy, compare

- Performance Charts (Chart.js / Plotly):
  * Confusion matrix heatmap (classification)
  * ROC curve with AUC scores
  * Precision-Recall curves
  * Feature importance bar charts
  * Learning curves (train vs validation)
  * Residual plots (regression)

- Model Detail Modal:
  * Full hyperparameters grid
  * Cross-validation fold scores
  * Prediction examples
  * Model artifacts download
  * MLflow run link
```

#### 1.6 Agent Decision Explanations
```typescript
Component: AgentDecisionPanel.vue

Features:
- Tabbed interface for each AI agent decision:
  * Agent 0: Configuration Extraction (if natural language mode)
  * Agent 1: Algorithm Selection
  * Agent 2: Model Selection
  * Agent 3: Retraining Decision (if monitoring active)

- Per Agent Display:
  * Confidence score with color-coded indicator
  * Decision summary (which algorithms selected, why)
  * Detailed reasoning as formatted text
  * Input context (what data the agent analyzed)
  * Alternative recommendations
  * Bedrock prompt viewer (expandable code block)
  * Bedrock response viewer (formatted JSON)
  * Timestamp and model ID used

- Agent Prompt Storage:
  * Link to prompt in MLflow artifacts
  * Link to prompt in PostgreSQL database
  * Link to prompt in S3 (if configured)
```

#### 1.7 Run History Management
```typescript
Component: RunList.vue + RunItem.vue

Features:
- Virtualized list for performance (handles 1000+ runs)
- Grouped by date with collapsible sections
- Each run card displays:
  * Status icon (🟢 Running, ✅ Completed, ❌ Failed, 🛑 Stopped)
  * Run ID (shortened, click to copy full ID)
  * Experiment name
  * Start time (relative: "2 hours ago")
  * Current node (if running)
  * Progress percentage (if running)

- Hover Actions:
  * 🛑 Stop (for running pipelines)
  * 🗑️ Delete (confirmation modal)
  * 🗑️ Delete + MLflow Experiment
  * 📋 Duplicate (start new run with same config)
  * 🔬 View in MLflow
  * 📥 Export report (JSON/PDF)

- Search and Filter:
  * Search by experiment name, run ID
  * Filter by status (running, completed, failed)
  * Filter by date range (date picker)
  * Filter by data path or target column
  * Saved filter presets

- Infinite Scroll:
  * Load 20 runs initially
  * Auto-load more on scroll
  * "Load More" button fallback
```

#### 1.8 Detailed Run View
```typescript
Component: RunDetails.vue (Modal or separate route)

Tabs:
1. Overview:
   - Status, start/end times, duration
   - Configuration (data path, target, test size, etc.)
   - MLflow experiment and run IDs
   - Pipeline run ID
   - User prompt (if natural language mode)

2. Nodes:
   - List of all nodes with execution details
   - Per node: status, start/end time, duration, logs
   - Click to expand full logs
   - Error stack traces if failed

3. Metrics:
   - All MLflow logged metrics with history
   - Downloadable as CSV
   - Interactive metric plots

4. Artifacts:
   - List of all artifacts (models, plots, reports)
   - Preview images inline
   - Download buttons for each artifact
   - Model registry integration (register model button)

5. Logs:
   - Full pipeline execution logs
   - Filterable by log level (DEBUG, INFO, WARNING, ERROR)
   - Search functionality
   - Download logs button

6. Bedrock:
   - All AI agent decisions for this run
   - Prompts and responses
   - Confidence scores and reasoning
   - Prompt storage locations (DB, MLflow, S3)

- Actions:
  * Export full run report (JSON, PDF)
  * Compare with another run
  * Restart with same config
  * Delete run and experiment
```

#### 1.9 Real-time Updates via WebSocket
```typescript
Service: websocket.js

WebSocket Connection:
- Endpoint: ws://backend:8000/ws/pipeline/{run_id}
- Auto-connect on pipeline start
- Auto-reconnect on connection loss (exponential backoff)
- Heartbeat/ping every 30s to keep connection alive

Events Handled:
1. state_update:
   - Full pipeline state object
   - Updates Pinia store
   - Triggers Vue component re-renders

2. node_started:
   - Node name, timestamp
   - Updates state diagram (node turns blue)
   - Updates progress percentage

3. node_completed:
   - Node name, duration, output summary
   - Updates state diagram (node turns green)
   - Updates metrics panel if node logged metrics

4. node_failed:
   - Node name, error message, stack trace
   - Updates state diagram (node turns red)
   - Shows error notification toast

5. pipeline_completed:
   - Final status, total duration
   - Triggers confetti animation for success
   - Updates run status in sidebar
   - Disconnects WebSocket

Optimistic Updates:
- UI updates immediately on user action
- Reverts if backend returns error
- Smooth transitions with Vue animations
```

#### 1.10 Pinia State Management
```typescript
Store: pipelineStore.js

State:
- activePipeline: { runId, experimentId, status, currentNode }
- currentState: { /* full PipelineState from backend */ }
- isConnected: boolean (WebSocket connection status)

Actions:
- startPipeline(config): POST to backend, start WebSocket
- stopPipeline(runId): POST to backend, disconnect WebSocket
- updateState(state): Update from WebSocket event
- refreshState(): GET latest state from REST API

Getters:
- isRunning: computed from status
- currentNode: active node name
- progress: percentage of completed nodes
- errors: list of errors from state

Store: runsStore.js

State:
- runs: Array of run summaries
- selectedRun: Currently selected run object
- filters: { status, experiment, dateRange }

Actions:
- fetchRuns(filters): GET from backend API
- selectRun(runId): Load run details
- deleteRun(runId): DELETE from backend
- duplicateRun(runId): Create new run with same config

Getters:
- filteredRuns: computed based on filters
- groupedByDate: runs grouped by date
- runCount: total number of runs
```

#### 1.11 Responsive & Accessible Design
```typescript
Features:
- Mobile-first responsive layout (Tailwind breakpoints)
- Keyboard navigation support
- ARIA labels for screen readers
- Focus management for modals
- Color contrast compliance (WCAG AA)
- Dark mode with system preference detection
- Smooth transitions and animations (Vue transition components)
- Loading skeletons for async content
- Error boundaries for graceful failure handling
- Optimized for performance:
  * Code splitting (lazy-loaded routes)
  * Virtual scrolling (run list)
  * Debounced search input
  * Memoized computed properties
```

### 2. Pipeline Orchestrator (LangGraph Core)
**Responsibility**: Manages workflow execution with AI-powered decision points

**Key Features**:
- Directed graph execution with conditional branching
- Integration with AWS Bedrock decision agents
- Dynamic node routing based on agent recommendations
- State persistence and checkpoint/resume capability
- Support for algorithm-specific nodes

### 2. MLflow Integration Layer
**Responsibility**: Comprehensive experiment tracking and model management

**Components**:

#### 2.1 MLflow Experiment Manager
```python
Features:
- Create/manage experiments
- Start/end runs
- Tag experiments with metadata
- Search and compare runs
```

#### 2.2 MLflow Logger
```python
Features:
- Log parameters (hyperparameters, config)
- Log metrics (accuracy, loss, etc.)
- Log artifacts (models, plots, data)
- Log model signatures
- Version models
```

#### 2.3 MLflow Model Registry
```python
Features:
- Register trained models
- Version management
- Stage transitions (Staging → Production)
- Model annotations
- Lineage tracking
```

### 3. AWS Bedrock Decision Agents

#### Agent 1: Algorithm Selection Agent
**Purpose**: Intelligently select which algorithms to train

**Input Analysis**:
```python
- Dataset size (rows, columns)
- Feature types (numerical, categorical distribution)
- Target distribution (imbalanced classes, range)
- Computational budget
- Time constraints
- Business requirements
```

**Decision Output**:
```python
{
    "recommended_algorithms": ["random_forest", "gradient_boosting"],
    "skip_algorithms": ["svm", "knn"],  # Too slow for large dataset
    "hyperparameter_priority": "medium",  # Full grid vs random search
    "reasoning": "Dataset is large with mixed features..."
}
```

**Benefits**:
- Avoid training irrelevant algorithms
- Optimize computational resources
- Smart hyperparameter search space

#### Agent 2: Model Selection Agent
**Purpose**: Select best model considering multiple factors

**Input Analysis**:
```python
- Cross-validation scores
- Training time
- Model interpretability
- Prediction speed
- Model size
- Business constraints
```

**Decision Output**:
```python
{
    "selected_model": "random_forest",
    "confidence": 0.92,
    "ensemble_recommended": False,
    "further_tuning": False,
    "reasoning": "RF provides best balance of accuracy and speed..."
}
```

**Benefits**:
- Holistic model selection beyond just accuracy
- Business-aware decisions
- Explain model choice

#### Agent 3: Retraining Decision Agent
**Purpose**: Decide if and how to retrain models

**Input Analysis**:
```python
- Current model performance (test metrics)
- Production performance (if available)
- Performance drift over time
- Data drift indicators
- Time since last training
- New data volume
- Compute availability
```

**Decision Output**:
```python
{
    "retrain": True,
    "strategy": "full",  # or "incremental"
    "urgency": "high",   # low, medium, high
    "keep_current": False,
    "reasoning": "Performance dropped 15% with detected concept drift..."
}
```

**Benefits**:
- Automated model maintenance
- Prevent performance degradation
- Resource-aware retraining

### 4. Algorithm-Specific Nodes

Each algorithm is implemented as a separate LangGraph node for modularity and parallel execution.

#### Classification Nodes

**Node: LogisticRegressionNode**
```python
Features:
- Hyperparameter tuning via GridSearchCV
- MLflow parameter logging
- MLflow metric logging (CV scores)
- Model artifact logging
- Custom for logistic regression specifics
```

**Node: RandomForestClassifierNode**
```python
Features:
- Hyperparameter tuning (n_estimators, max_depth, etc.)
- Feature importance extraction
- MLflow logging
- OOB score logging
```

**Node: GradientBoostingClassifierNode**
**Node: SVMClassifierNode**
**Node: KNNClassifierNode**

Each node:
- Independent execution
- Algorithm-specific hyperparameter grids
- MLflow integration
- Can run in parallel if resources allow

#### Regression Nodes

**Node: LinearRegressionNode**
**Node: RidgeRegressionNode**
**Node: LassoRegressionNode**
**Node: RandomForestRegressorNode**
**Node: GradientBoostingRegressorNode**

### 5. Hyperparameter Tuning Module

```python
Component: GridSearchCV Integration

Features:
- Intelligent search space based on agent recommendations
- Cross-validation strategies
- Parallel job execution
- Early stopping for efficient search
- MLflow logging of all trials
- Best parameter selection

Configuration:
- param_grid: Algorithm-specific parameter grids
- cv_strategy: StratifiedKFold, KFold, TimeSeriesSplit
- scoring: Custom metrics
- n_jobs: Parallel workers
- verbose: Logging level
```

### 6. Performance Monitoring System

```python
Component: ModelPerformanceMonitor

Capabilities:
- Real-time metric tracking
- Baseline comparison
- Drift detection (data drift, concept drift)
- Performance degradation alerts
- Historical trend analysis

Metrics Tracked:
- Accuracy, Precision, Recall, F1 (classification)
- RMSE, MAE, R² (regression)
- Prediction latency
- Feature distribution changes
- Prediction distribution changes
```

### 7. Retraining Orchestrator

```python
Component: AutomatedRetrainingSystem

Features:
- Triggered by monitoring system
- Decision agent consultation
- Incremental or full retraining
- A/B testing new vs old model
- Safe deployment with rollback
- Scheduled retraining (optional)

Triggers:
- Performance drop beyond threshold
- Drift detection
- Schedule-based
- Manual trigger
- New data availability
```

### 8. Prompt Storage System

**Responsibility**: Centralized storage and management of user prompts and extracted configurations

**Storage Architecture** (Triple Storage Pattern):

```python
Component: PromptStorageSystem

Storage Backends:
1. MLflow Artifacts
   - Purpose: Experiment lineage and traceability
   - Storage: user_prompt.txt, extracted_config.json, agent_response.txt
   - Benefits: Tied to MLflow runs, versioned with experiments

2. PostgreSQL Database
   - Purpose: Querying, analytics, and search
   - Schema:
     * prompts table (id, timestamp, pipeline_run_id, mlflow_run_id,
                      user_prompt, extracted_config, confidence, reasoning)
   - Benefits: SQL queries, indexing, full-text search
   - Indexes: timestamp, pipeline_run_id, target_column, confidence

3. MinIO/S3 Object Storage
   - Purpose: Long-term archival and backup
   - Structure: s3://ml-pipeline-prompts/{year}/{month}/{pipeline_run_id}/
   - Benefits: Cost-effective, scalable, durable storage
   - Lifecycle: Automatic transition to cold storage after 90 days

Features:
- Automatic synchronization across all 3 storage backends
- Prompt similarity search (keyword-based and semantic)
- Prompt reuse suggestions based on historical data
- Analytics dashboard for prompt patterns
- Bulk export for compliance and auditing
- Data retention policies (default: 2 years)

Configuration Extraction Tracking:
- User prompt (original text)
- Extracted configuration (target_column, test_size, random_state, etc.)
- Confidence score (must be >= 70%)
- Agent reasoning and assumptions
- User hints (if provided before extraction)
- Timestamp and user identity
- Associated MLflow run ID
- Extraction success/failure status
```

**Database Schema** (PostgreSQL):

```sql
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    pipeline_run_id VARCHAR(64) NOT NULL,
    mlflow_run_id VARCHAR(64),
    mlflow_experiment_id VARCHAR(64),
    user_prompt TEXT NOT NULL,
    extracted_config JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    reasoning TEXT,
    assumptions JSONB,
    warnings JSONB,
    user_hints JSONB,
    bedrock_model_id VARCHAR(256),
    extraction_success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_prompts_timestamp ON prompts(timestamp DESC);
CREATE INDEX idx_prompts_pipeline_run ON prompts(pipeline_run_id);
CREATE INDEX idx_prompts_mlflow_run ON prompts(mlflow_run_id);
CREATE INDEX idx_prompts_confidence ON prompts(confidence);
CREATE INDEX idx_prompts_target ON prompts((extracted_config->>'target_column'));
```

**API Endpoints**:

```python
# Save prompt
POST /api/prompts/
{
    "user_prompt": str,
    "extracted_config": Dict,
    "pipeline_run_id": str,
    "mlflow_run_id": str
}

# Search prompts
GET /api/prompts/search?keyword=<term>&target=<column>&limit=10

# Get similar prompts
GET /api/prompts/similar?prompt=<text>&limit=5

# Get prompt by pipeline run
GET /api/prompts/{pipeline_run_id}

# Get prompt statistics
GET /api/prompts/analytics
```

## Data Flow with Decision Points

```
[User Prompt + Data Path]
         ↓
[🤖 Agent 0: Config Extraction]
"Extract target_column, experiment_name, test_size, random_state"
         ↓
    [Store Prompt]
    - MLflow artifacts
    - PostgreSQL database
    - MinIO/S3
         ↓
[Raw Data] → Load → Preprocess → Split → Feature Selection
                                                 ↓
                                    [🤖 Agent 1: Analyze & Decide]
                                    "Train RF, GB; Skip SVM, KNN"
                                                 ↓
                    ┌────────────────────────────┴────────────────────────┐
                    ↓                                                      ↓
        [RF Node: GridSearchCV]                          [GB Node: GridSearchCV]
        - MLflow Run 1                                    - MLflow Run 2
        - Log params & metrics                            - Log params & metrics
                    └────────────────────────────┬────────────────────────┘
                                                 ↓
                                    [🤖 Agent 2: Compare & Select]
                                    "RF wins: better F1 and faster"
                                                 ↓
                                    [Evaluate on Test Set]
                                                 ↓
                                    [Monitor Performance]
                                                 ↓
                                    [🤖 Agent 3: Retrain Decision]
                                    "No retrain needed / Retrain now"
                                                 ↓
                    ┌───────────────────────────┴────────────────────────┐
                    ↓                                                     ↓
        [Save to Model Registry]                            [Trigger Retraining]
        [Generate Reports]                                  [Loop Back]
```

## Technology Stack (Enhanced)

### User Interface (Vue.js 3 SPA)
- **Vue.js 3**: Progressive JavaScript framework (Composition API)
- **Vite**: Next-generation frontend build tool (fast HMR, optimized builds)
- **Pinia**: Official Vue.js state management (replaces Vuex)
- **Vue Router**: Official routing library for SPAs
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Axios**: Promise-based HTTP client for REST API calls
- **WebSocket/SSE**: Real-time bidirectional communication for pipeline updates
- **Mermaid.js**: Diagram rendering for LangGraph state visualization
- **Chart.js / Plotly.js**: Interactive chart library for metrics and performance visualization
- **Docker + Nginx**: Containerized deployment with production-ready web server

### Core Framework
- **LangGraph**: State graph orchestration with decision agents
- **LangChain**: Foundation for LangGraph
- **LangChain-AWS**: Bedrock integration

### AI Decision Making
- **AWS Bedrock**: Claude models for intelligent decision making
- **Boto3**: AWS SDK for Bedrock API calls

### Experiment Tracking
- **MLflow**: Experiment tracking, model registry, deployment
- **MLflow Tracking Server**: Centralized tracking

### Data Processing
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations
- **Scikit-learn**: ML algorithms and utilities

### Hyperparameter Tuning
- **GridSearchCV**: Exhaustive grid search
- **RandomizedSearchCV**: Randomized search (alternative)

### Monitoring
- **Custom monitoring module**: Performance tracking
- **Drift detection algorithms**: Statistical tests

### Visualization
- **Matplotlib**: Static plots
- **Seaborn**: Statistical visualizations
- **MLflow UI**: Experiment comparison

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Production Environment                             │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  MLflow Tracking Server                                      │    │
│  │  - PostgreSQL backend                                        │    │
│  │  - S3 artifact store                                         │    │
│  │  - Authentication & authorization                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  AWS Bedrock                                                 │    │
│  │  - Claude 3 models                                           │    │
│  │  - API Gateway                                               │    │
│  │  - IAM roles & permissions                                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Pipeline Execution Environment                              │    │
│  │  - Kubernetes pods / ECS tasks                               │    │
│  │  - Scheduled jobs (Airflow/Step Functions)                   │    │
│  │  - Auto-scaling based on load                                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Model Serving                                               │    │
│  │  - MLflow Model Server                                       │    │
│  │  - REST API endpoints                                        │    │
│  │  - Load balancing                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Monitoring Dashboard                                        │    │
│  │  - Grafana / CloudWatch                                      │    │
│  │  - Alert manager                                             │    │
│  │  - Performance metrics                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

## Performance Optimizations

### 1. Intelligent Algorithm Selection
- **Benefit**: 30-50% reduction in compute time
- **Method**: Skip unsuitable algorithms early via AI agent

### 2. Parallel Algorithm Training
- **Benefit**: Near-linear speedup with available cores
- **Method**: Train selected algorithms concurrently

### 3. Smart Hyperparameter Search
- **Benefit**: Faster convergence to optimal parameters
- **Method**: Agent recommends focused search spaces

### 4. Early Stopping
- **Benefit**: Avoid wasting compute on poor models
- **Method**: Monitor CV scores and stop early if no improvement

### 5. Incremental Learning
- **Benefit**: Faster retraining on new data
- **Method**: Update existing models instead of full retrain

## Security & Compliance

### 1. AWS IAM Integration
- Role-based access to Bedrock
- Least privilege principle
- Audit logging

### 2. MLflow Authentication
- User authentication
- Experiment access control
- Model registry permissions

### 3. Data Privacy
- PII detection and masking
- Encryption at rest and in transit
- Compliance with GDPR, HIPAA

### 4. Model Governance
- Model approval workflows
- Change tracking
- Rollback capabilities

## Cost Optimization

### 1. Bedrock API Costs
- Cache agent responses
- Batch API calls
- Use appropriate model sizes

### 2. Compute Costs
- Spot instances for training
- Auto-scaling
- Resource limits per experiment

### 3. Storage Costs
- Artifact lifecycle policies
- Compress artifacts
- Archive old experiments

## Future Enhancements

### Phase 2
- **Multi-objective optimization**: Balance accuracy, speed, and cost
- **AutoML integration**: Full automation with Optuna
- **Ensemble strategies**: Intelligent ensemble creation
- **Transfer learning**: Leverage pre-trained models

### Phase 3
- **Federated learning**: Train on distributed data
- **Active learning**: Smart data labeling
- **Explainability**: SHAP/LIME integration
- **Fairness checks**: Bias detection and mitigation

### Phase 4
- **Real-time learning**: Online learning capabilities
- **Multi-cloud**: Support Azure ML, GCP Vertex AI
- **Edge deployment**: Deploy to edge devices
- **AutoML pipelines**: Full pipeline optimization

## Summary

This enhanced architecture provides:
1. ✅ **Natural Language Configuration**: Extract ML pipeline configuration from user prompts with Agent 0
2. ✅ **AI-Powered Decision Making**: Four intelligent agents for optimization (Config, Algorithm, Model, Retraining)
3. ✅ **Triple Prompt Storage**: Centralized storage in MLflow + PostgreSQL + MinIO/S3 for reuse and analytics
4. ✅ **Comprehensive Tracking**: MLflow integration for full experiment management
5. ✅ **Modular Algorithms**: Each algorithm as a separate, tunable node
6. ✅ **Production Monitoring**: Real-time performance tracking
7. ✅ **Automated Retraining**: Intelligent model maintenance
8. ✅ **Cost Efficiency**: Reduce unnecessary computation
9. ✅ **Scalability**: Production-ready deployment
10. ✅ **Reproducibility**: Complete experiment reconstruction

The system combines the power of LangGraph's state management, MLflow's experiment tracking, and AWS Bedrock's AI capabilities to create an intelligent, self-optimizing ML pipeline with natural language configuration extraction.
