# UML Diagrams - MLOps Pipeline Automation

## Document Information
- **Version**: 1.0
- **Date**: 2025-11-30
- **Purpose**: Class diagrams and component diagrams for system design

---

## Table of Contents
1. [Component Diagram](#1-component-diagram)
2. [Class Diagrams](#2-class-diagrams)
3. [Deployment Diagram](#3-deployment-diagram)
4. [State Machine Diagram](#4-state-machine-diagram)

---

## 1. Component Diagram

### 1.1 High-Level Component Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          System Components                              │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    <<component>>                                  │  │
│  │                   Streamlit UI Layer                             │  │
│  │                                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │ Dashboard    │  │ Graph        │  │ Monitoring   │          │  │
│  │  │ Component    │  │ Visualizer   │  │ Component    │          │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │  │
│  │         │                  │                  │                  │  │
│  └─────────┼──────────────────┼──────────────────┼──────────────────┘  │
│            │                  │                  │                      │
│            └──────────────────┼──────────────────┘                      │
│                               │                                         │
│  ┌────────────────────────────┼──────────────────────────────────────┐ │
│  │            <<component>>    │                                      │ │
│  │         API Gateway / Backend Service                             │ │
│  │                             │                                      │ │
│  │  ┌──────────────┐  ┌───────▼──────┐  ┌──────────────┐           │ │
│  │  │ REST API     │  │ WebSocket    │  │ Config       │           │ │
│  │  │ Controller   │  │ Manager      │  │ Manager      │           │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │ │
│  └─────────┼──────────────────┼──────────────────┼───────────────────┘ │
│            │                  │                  │                      │
│            └──────────────────┼──────────────────┘                      │
│                               │                                         │
│  ┌────────────────────────────▼──────────────────────────────────────┐ │
│  │            <<component>>                                           │ │
│  │          LangGraph Orchestration Engine                           │ │
│  │                                                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │ │
│  │  │ State        │  │ Node         │  │ Edge         │           │ │
│  │  │ Manager      │  │ Executor     │  │ Router       │           │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │ │
│  └─────────┼──────────────────┼──────────────────┼───────────────────┘ │
│            │                  │                  │                      │
│    ┌───────┼──────────────────┼──────────────────┼──────┐              │
│    │       │                  │                  │      │              │
│    │  ┌────▼────────┐  ┌──────▼──────┐  ┌───────▼──────▼──┐          │
│    │  │ <<comp>>    │  │ <<comp>>    │  │ <<comp>>        │          │
│    │  │ AI Decision │  │ ML          │  │ Monitoring      │          │
│    │  │ Layer       │  │ Processing  │  │ Module          │          │
│    │  │             │  │ Layer       │  │                 │          │
│    │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐    │          │
│    │  │ │Agent 1  │ │  │ │Preprocess│ │  │ │Drift    │    │          │
│    │  │ │Algorithm│ │  │ │Module   │ │  │ │Detector │    │          │
│    │  │ │Selection│ │  │ └─────────┘ │  │ └─────────┘    │          │
│    │  │ └─────────┘ │  │ ┌─────────┐ │  │ ┌─────────┐    │          │
│    │  │ ┌─────────┐ │  │ │Training │ │  │ │Perf     │    │          │
│    │  │ │Agent 2  │ │  │ │Module   │ │  │ │Monitor  │    │          │
│    │  │ │Model    │ │  │ └─────────┘ │  │ └─────────┘    │          │
│    │  │ │Selection│ │  │ ┌─────────┐ │  │                 │          │
│    │  │ └─────────┘ │  │ │Evaluation│ │  │                 │          │
│    │  │ ┌─────────┐ │  │ │Module   │ │  │                 │          │
│    │  │ │Agent 3  │ │  │ └─────────┘ │  │                 │          │
│    │  │ │Retrain  │ │  │             │  │                 │          │
│    │  │ │Decision │ │  │             │  │                 │          │
│    │  │ └─────────┘ │  │             │  │                 │          │
│    │  └─────┬───────┘  └──────┬──────┘  └────────┬────────┘          │
│    │        │                  │                  │                   │
│    │        └──────────────────┼──────────────────┘                   │
│    │                           │                                      │
│    │  ┌────────────────────────▼──────────────────────────────────┐  │
│    │  │            <<component>>                                   │  │
│    │  │          MLflow Integration Layer                         │  │
│    │  │                                                            │  │
│    │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│    │  │  │ Experiment   │  │ Model        │  │ Artifact     │   │  │
│    │  │  │ Manager      │  │ Registry     │  │ Manager      │   │  │
│    │  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │  │
│    │  └─────────┼──────────────────┼──────────────────┼───────────┘  │
│    │            │                  │                  │              │
│    └────────────┼──────────────────┼──────────────────┼──────────────┘
│                 │                  │                  │
│  ┌──────────────▼──────────────────▼──────────────────▼─────────────┐
│  │            <<component>>                                          │
│  │          External Services                                       │
│  │                                                                   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  │ AWS Bedrock  │  │ MLflow       │  │ PostgreSQL   │          │
│  │  │ Claude API   │  │ Server       │  │ Database     │          │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │
│  │                                                                   │
│  │  ┌──────────────┐                                                │
│  │  │ S3/MinIO     │                                                │
│  │  │ Storage      │                                                │
│  │  └──────────────┘                                                │
│  └───────────────────────────────────────────────────────────────────┘
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Class Diagrams

### 2.1 Core Pipeline Classes

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Pipeline Core Classes                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        <<TypedDict>>                    │
│        PipelineState                    │
├─────────────────────────────────────────┤
│ + raw_data: pd.DataFrame                │
│ + cleaned_data: pd.DataFrame            │
│ + X_train: pd.DataFrame                 │
│ + X_test: pd.DataFrame                  │
│ + y_train: pd.Series                    │
│ + y_test: pd.Series                     │
│ + selected_features: List[str]          │
│ + feature_importance: Dict[str, float]  │
│ + mlflow_experiment_id: str             │
│ + mlflow_run_id: str                    │
│ + algorithm_results: Dict[str, Any]     │
│ + best_model_name: str                  │
│ + best_model: Any                       │
│ + drift_detected: bool                  │
│ + drift_score: float                    │
│ + retraining_triggered: bool            │
│ + error_messages: List[str]             │
└─────────────────────────────────────────┘
                    △
                    │
                    │ uses
                    │
┌─────────────────────────────────────────┐
│        MLPipelineOrchestrator           │
├─────────────────────────────────────────┤
│ - graph: StateGraph                     │
│ - mlflow_manager: MLflowManager         │
│ - config: PipelineConfig                │
├─────────────────────────────────────────┤
│ + __init__(config: PipelineConfig)      │
│ + build_graph() -> StateGraph           │
│ + execute(data_path: str) -> State     │
│ + get_current_state() -> State          │
│ + pause()                               │
│ + resume()                              │
│ + stop()                                │
└─────────────────────────────────────────┘
                    │
                    │ contains
                    │
                    ▼
┌─────────────────────────────────────────┐
│        StateGraph                       │
│        (from LangGraph)                 │
├─────────────────────────────────────────┤
│ - nodes: Dict[str, Node]                │
│ - edges: List[Edge]                     │
│ - state: State                          │
├─────────────────────────────────────────┤
│ + add_node(name: str, func: Callable)   │
│ + add_edge(from: str, to: str)          │
│ + add_conditional_edges(...)            │
│ + compile() -> CompiledGraph            │
│ + invoke(input: State) -> State         │
└─────────────────────────────────────────┘
```

### 2.2 Data Processing Classes

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Data Processing Classes                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        DataLoader                       │
├─────────────────────────────────────────┤
│ - file_path: str                        │
│ - file_type: str                        │
├─────────────────────────────────────────┤
│ + load_csv(path: str) -> pd.DataFrame   │
│ + load_parquet(path: str) -> DataFrame  │
│ + validate_data(df: DataFrame) -> bool  │
│ + get_data_summary(df) -> Dict          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        DataPreprocessor                 │
├─────────────────────────────────────────┤
│ - imputation_strategy: str              │
│ - scaling_method: str                   │
│ - encoding_method: str                  │
├─────────────────────────────────────────┤
│ + handle_missing_values(df) -> DataFrame│
│ + detect_outliers(df) -> Dict           │
│ + remove_outliers(df) -> DataFrame      │
│ + encode_categorical(df) -> DataFrame   │
│ + scale_features(df) -> DataFrame       │
│ + fit_transform(df) -> DataFrame        │
│ + transform(df) -> DataFrame            │
│ + get_metadata() -> Dict                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        FeatureSelector                  │
├─────────────────────────────────────────┤
│ - method: str                           │
│ - n_features: int                       │
│ - selector: SelectKBest                 │
├─────────────────────────────────────────┤
│ + fit(X, y)                             │
│ + transform(X) -> DataFrame             │
│ + fit_transform(X, y) -> DataFrame      │
│ + get_feature_importance() -> Dict      │
│ + get_selected_features() -> List[str]  │
└─────────────────────────────────────────┘
```

### 2.3 Training Module Classes

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Training Module Classes                         │
└─────────────────────────────────────────────────────────────────────┘

                ┌─────────────────────────────────┐
                │   <<abstract>>                  │
                │   BaseAlgorithmTrainer          │
                ├─────────────────────────────────┤
                │ # algorithm_name: str           │
                │ # estimator: Any                │
                │ # param_grid: Dict              │
                │ # mlflow_manager: MLflowManager │
                ├─────────────────────────────────┤
                │ + train(X, y) -> AlgorithmResult│
                │ + evaluate(X, y) -> Dict        │
                │ + log_to_mlflow()               │
                │ # _create_estimator() -> Any    │
                │ # _get_param_grid() -> Dict     │
                └─────────────────┬───────────────┘
                                  │
                                  │ extends
                    ┌─────────────┼─────────────┐
                    │             │             │
        ┌───────────▼──────┐ ┌────▼─────────┐ ┌▼──────────────┐
        │RandomForest      │ │Gradient      │ │Logistic       │
        │Trainer           │ │BoostingTrainer│ │RegressionTrainer│
        ├──────────────────┤ ├──────────────┤ ├───────────────┤
        │+ train()         │ │+ train()     │ │+ train()      │
        │+ evaluate()      │ │+ evaluate()  │ │+ evaluate()   │
        │- _create_estimator()│- _create_estimator()│- _create_estimator()│
        │- _get_param_grid()│ │- _get_param_grid()│ │- _get_param_grid()│
        └──────────────────┘ └──────────────┘ └───────────────┘

┌─────────────────────────────────────────┐
│        HyperparameterTuner              │
├─────────────────────────────────────────┤
│ - estimator: Any                        │
│ - param_grid: Dict                      │
│ - cv: int                               │
│ - scoring: str                          │
│ - n_jobs: int                           │
├─────────────────────────────────────────┤
│ + tune(X, y) -> GridSearchCV            │
│ + get_best_params() -> Dict             │
│ + get_best_score() -> float             │
│ + get_cv_results() -> DataFrame         │
└─────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌─────────────────────────────────────────┐
│        GridSearchCV                     │
│        (from sklearn)                   │
├─────────────────────────────────────────┤
│ + fit(X, y)                             │
│ + predict(X) -> ndarray                 │
│ + score(X, y) -> float                  │
│ - best_estimator_: Any                  │
│ - best_params_: Dict                    │
│ - cv_results_: Dict                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        AlgorithmResult                  │
├─────────────────────────────────────────┤
│ + model: Any                            │
│ + best_params: Dict[str, Any]           │
│ + cv_scores: List[float]                │
│ + cv_mean: float                        │
│ + cv_std: float                         │
│ + test_accuracy: float                  │
│ + test_f1: float                        │
│ + test_precision: float                 │
│ + test_recall: float                    │
│ + training_time: float                  │
│ + mlflow_run_id: str                    │
│ + predictions: np.ndarray               │
└─────────────────────────────────────────┘
```

### 2.4 AI Agent Classes

```
┌─────────────────────────────────────────────────────────────────────┐
│                       AI Agent Classes                               │
└─────────────────────────────────────────────────────────────────────┘

                ┌─────────────────────────────────┐
                │   <<abstract>>                  │
                │   BaseBedrockAgent              │
                ├─────────────────────────────────┤
                │ # bedrock_client: BedrockClient │
                │ # model_id: str                 │
                │ # temperature: float            │
                │ # max_tokens: int               │
                ├─────────────────────────────────┤
                │ + decide(context: Dict) -> Dict │
                │ # _prepare_context(state) -> Dict│
                │ # _build_prompt(context) -> str │
                │ # _invoke_bedrock(prompt) -> str│
                │ # _parse_response(resp) -> Dict │
                │ # _validate_decision(d) -> bool │
                │ # _log_to_mlflow(...)           │
                └─────────────────┬───────────────┘
                                  │
                                  │ extends
                    ┌─────────────┼─────────────┐
                    │             │             │
        ┌───────────▼──────┐ ┌────▼─────────┐ ┌▼──────────────┐
        │Algorithm         │ │Model         │ │Retraining     │
        │SelectionAgent    │ │SelectionAgent│ │DecisionAgent  │
        ├──────────────────┤ ├──────────────┤ ├───────────────┤
        │+ decide()        │ │+ decide()    │ │+ decide()     │
        │- _prepare_context()│ │- _prepare_context()│- _prepare_context()│
        │- _build_prompt() │ │- _build_prompt()│ │- _build_prompt()│
        └──────────────────┘ └──────────────┘ └───────────────┘

┌─────────────────────────────────────────┐
│        BedrockClient                    │
├─────────────────────────────────────────┤
│ - boto3_client: Any                     │
│ - region: str                           │
│ - retry_config: RetryConfig             │
├─────────────────────────────────────────┤
│ + invoke_model(prompt, config) -> str   │
│ - _handle_rate_limit()                  │
│ - _exponential_backoff(attempt) -> float│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        ContextBuilder                   │
├─────────────────────────────────────────┤
│ + build_algorithm_context(state) -> Dict│
│ + build_model_context(state) -> Dict    │
│ + build_retrain_context(state) -> Dict  │
│ + format_feature_stats(stats) -> Dict   │
│ + format_model_results(results) -> List │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        AgentDecision                    │
├─────────────────────────────────────────┤
│ + decision: Dict[str, Any]              │
│ + reasoning: str                        │
│ + confidence: float                     │
│ + prompt: str                           │
│ + raw_response: str                     │
│ + timestamp: datetime                   │
└─────────────────────────────────────────┘
```

### 2.5 Monitoring Classes

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Monitoring Classes                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        DriftDetector                    │
├─────────────────────────────────────────┤
│ - reference_data: pd.DataFrame          │
│ - drift_threshold: float                │
│ - psi_threshold: float                  │
├─────────────────────────────────────────┤
│ + detect_drift(current) -> DriftReport  │
│ - _ks_test(ref, cur) -> Tuple           │
│ - _chi2_test(ref, cur) -> Tuple         │
│ - _calculate_psi(ref, cur) -> float     │
│ - _aggregate_drift_score() -> float     │
└─────────────────────────────────────────┘
                    │
                    │ produces
                    ▼
┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        DriftReport                      │
├─────────────────────────────────────────┤
│ + drift_detected: bool                  │
│ + overall_drift_score: float            │
│ + drifted_features: List[str]           │
│ + feature_drift_scores: Dict[str, float]│
│ + psi_values: Dict[str, float]          │
│ + drift_details: Dict[str, Any]         │
│ + timestamp: datetime                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        PerformanceMonitor               │
├─────────────────────────────────────────┤
│ - baseline_metrics: Dict[str, float]    │
│ - threshold: float                      │
├─────────────────────────────────────────┤
│ + compare_performance(current) -> Report│
│ - _calculate_drop(base, cur) -> float   │
│ - _calculate_drop_pct(base, cur) -> float│
│ - _check_threshold(drop) -> bool        │
└─────────────────────────────────────────┘
                    │
                    │ produces
                    ▼
┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        PerformanceReport                │
├─────────────────────────────────────────┤
│ + performance_drop: float               │
│ + performance_drop_pct: float           │
│ + threshold_exceeded: bool              │
│ + metric_comparison: Dict[str, Dict]    │
│ + timestamp: datetime                   │
└─────────────────────────────────────────┘
```

### 2.6 MLflow Integration Classes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MLflow Integration Classes                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        MLflowManager                    │
├─────────────────────────────────────────┤
│ - tracking_uri: str                     │
│ - experiment_name: str                  │
│ - experiment_id: str                    │
│ - run_id: str                           │
│ - client: MlflowClient                  │
├─────────────────────────────────────────┤
│ + create_experiment(name) -> str        │
│ + start_run(name, nested) -> str        │
│ + end_run()                             │
│ + log_params(params: Dict)              │
│ + log_metrics(metrics: Dict, step)      │
│ + log_artifact(path: str)               │
│ + log_model(model, path, sig)           │
│ + get_run(run_id) -> Run                │
│ + search_runs(filter) -> List[Run]      │
└─────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌─────────────────────────────────────────┐
│        MlflowClient                     │
│        (from mlflow)                    │
├─────────────────────────────────────────┤
│ + create_experiment(name) -> str        │
│ + create_run(exp_id) -> Run             │
│ + log_param(run_id, key, val)           │
│ + log_metric(run_id, key, val, step)    │
│ + log_artifact(run_id, path)            │
│ + search_runs(exp_ids, filter) -> List  │
│ + get_run(run_id) -> Run                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        ModelRegistry                    │
├─────────────────────────────────────────┤
│ - client: MlflowClient                  │
├─────────────────────────────────────────┤
│ + register_model(uri, name) -> Version  │
│ + transition_stage(name, ver, stage)    │
│ + get_latest_version(name, stage) -> Ver│
│ + update_model_version(name, ver, desc) │
│ + search_model_versions(filter) -> List │
└─────────────────────────────────────────┘
                    │
                    │ manages
                    ▼
┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        ModelVersion                     │
├─────────────────────────────────────────┤
│ + name: str                             │
│ + version: int                          │
│ + creation_time: datetime               │
│ + current_stage: str                    │
│ + source: str                           │
│ + run_id: str                           │
│ + status: str                           │
│ + description: str                      │
└─────────────────────────────────────────┘
```

### 2.7 Configuration Classes

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Configuration Classes                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        PipelineConfig                   │
├─────────────────────────────────────────┤
│ + data_config: DataConfig               │
│ + preprocessing_config: PreprocessConfig│
│ + training_config: TrainingConfig       │
│ + monitoring_config: MonitoringConfig   │
│ + mlflow_config: MLflowConfig           │
│ + bedrock_config: BedrockConfig         │
├─────────────────────────────────────────┤
│ + load_from_yaml(path: str) -> Config   │
│ + save_to_yaml(path: str)               │
│ + validate() -> bool                    │
└─────────────────────────────────────────┘
                    │
                    │ contains
        ┌───────────┼───────────┬───────────────┐
        │           │           │               │
        ▼           ▼           ▼               ▼
┌──────────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│DataConfig    │ │Preprocess│ │Training  │ │Monitoring│
│              │ │Config    │ │Config    │ │Config    │
├──────────────┤ ├─────────┤ ├──────────┤ ├──────────┤
│+ file_path   │ │+ impute  │ │+ cv_folds│ │+ drift   │
│+ file_type   │ │  _method │ │+ scoring │ │  _thresh │
│+ target_col  │ │+ scaling │ │+ n_jobs  │ │+ perf    │
│+ test_size   │ │  _method │ │+ timeout │ │  _thresh │
│+ random_state│ │+ encoding│ │+ algos   │ │+ baseline│
└──────────────┘ └─────────┘ └──────────┘ └──────────┘

┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        MLflowConfig                     │
├─────────────────────────────────────────┤
│ + tracking_uri: str                     │
│ + experiment_name: str                  │
│ + artifact_location: str                │
│ + log_models: bool                      │
│ + log_artifacts: bool                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        <<dataclass>>                    │
│        BedrockConfig                    │
├─────────────────────────────────────────┤
│ + region: str                           │
│ + model_id: str                         │
│ + temperature: float                    │
│ + max_tokens: int                       │
│ + retry_attempts: int                   │
│ + timeout: int                          │
└─────────────────────────────────────────┘
```

---

## 3. Deployment Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                       Deployment Architecture                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  <<Execution Environment>>                    │  │
│  │                  Kubernetes Cluster                           │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │               <<Node>> Web Server Node                   │ │  │
│  │  │                                                           │ │  │
│  │  │  ┌─────────────────────────────────────────────────────┐ │ │  │
│  │  │  │      <<Container>> Streamlit Pod                    │ │ │  │
│  │  │  │  ┌─────────────────────────────────────────────┐    │ │ │  │
│  │  │  │  │  <<Artifact>> streamlit_ui:latest           │    │ │ │  │
│  │  │  │  │  - Dashboard Component                      │    │ │ │  │
│  │  │  │  │  - Visualization Module                     │    │ │ │  │
│  │  │  │  │  - Monitoring Interface                     │    │ │ │  │
│  │  │  │  └─────────────────────────────────────────────┘    │ │ │  │
│  │  │  │       Port: 8501                                    │ │ │  │
│  │  │  │       Replicas: 3                                   │ │ │  │
│  │  │  └─────────────────────────────────────────────────────┘ │ │  │
│  │  └───────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │           <<Node>> Application Server Nodes              │ │  │
│  │  │                                                           │ │  │
│  │  │  ┌─────────────────────────────────────────────────────┐ │ │  │
│  │  │  │    <<Container>> Pipeline Backend Pod               │ │ │  │
│  │  │  │  ┌─────────────────────────────────────────────┐    │ │ │  │
│  │  │  │  │  <<Artifact>> pipeline_backend:latest        │    │ │ │  │
│  │  │  │  │  - LangGraph Orchestrator                   │    │ │ │  │
│  │  │  │  │  - ML Processing Modules                    │    │ │ │  │
│  │  │  │  │  - AI Agent Clients                         │    │ │ │  │
│  │  │  │  │  - MLflow Integration                       │    │ │ │  │
│  │  │  │  └─────────────────────────────────────────────┘    │ │ │  │
│  │  │  │       Port: 8000                                    │ │ │  │
│  │  │  │       Replicas: 4                                   │ │ │  │
│  │  │  │       Resources:                                    │ │ │  │
│  │  │  │         CPU: 2-4 cores                              │ │ │  │
│  │  │  │         Memory: 4-8 GB                              │ │ │  │
│  │  │  └─────────────────────────────────────────────────────┘ │ │  │
│  │  └───────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │            <<Node>> MLflow Server Node                   │ │  │
│  │  │                                                           │ │  │
│  │  │  ┌─────────────────────────────────────────────────────┐ │ │  │
│  │  │  │       <<Container>> MLflow Server                   │ │ │  │
│  │  │  │  ┌─────────────────────────────────────────────┐    │ │ │  │
│  │  │  │  │  <<Artifact>> mlflow-server:latest          │    │ │ │  │
│  │  │  │  │  - Tracking Server                          │    │ │ │  │
│  │  │  │  │  - Model Registry                           │    │ │ │  │
│  │  │  │  │  - Artifact Repository Interface            │    │ │ │  │
│  │  │  │  └─────────────────────────────────────────────┘    │ │ │  │
│  │  │  │       Port: 5000                                    │ │ │  │
│  │  │  └─────────────────────────────────────────────────────┘ │ │  │
│  │  └───────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │            <<Node>> Database Node                        │ │  │
│  │  │                                                           │ │  │
│  │  │  ┌─────────────────────────────────────────────────────┐ │ │  │
│  │  │  │       <<Container>> PostgreSQL                      │ │ │  │
│  │  │  │  ┌─────────────────────────────────────────────┐    │ │ │  │
│  │  │  │  │  <<Artifact>> postgres:14                   │    │ │ │  │
│  │  │  │  │  Database: mlflow                           │    │ │ │  │
│  │  │  │  │  - experiments table                        │    │ │ │  │
│  │  │  │  │  - runs table                               │    │ │ │  │
│  │  │  │  │  - metrics table                            │    │ │ │  │
│  │  │  │  │  - params table                             │    │ │ │  │
│  │  │  │  │  - model_versions table                     │    │ │ │  │
│  │  │  │  └─────────────────────────────────────────────┘    │ │ │  │
│  │  │  │       Port: 5432                                    │ │ │  │
│  │  │  │       Persistent Volume: 100GB                      │ │ │  │
│  │  │  └─────────────────────────────────────────────────────┘ │ │  │
│  │  └───────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                <<External Services>>                          │  │
│  │                                                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │ AWS Bedrock  │  │    AWS S3    │  │   AWS RDS    │       │  │
│  │  │ Claude API   │  │  (Artifacts) │  │ (PostgreSQL) │       │  │
│  │  │ us-east-1    │  │              │  │ (Production) │       │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Communication Protocols:                                          │
│  ─────────────────────────────────                                 │
│  • HTTP/HTTPS for REST APIs                                        │
│  • WebSocket for real-time updates                                 │
│  • gRPC for internal service communication (optional)              │
│  • PostgreSQL wire protocol for database                           │
│  • S3 API for artifact storage                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 4. State Machine Diagram

### 4.1 Pipeline State Transitions

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Pipeline State Machine                              │
└─────────────────────────────────────────────────────────────────────┘

                         ┌───────────────┐
                         │    START      │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   INITIALIZING         │
                    │ • Create MLflow exp    │
                    │ • Start run            │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   LOADING_DATA         │
                    │ • Load CSV/Parquet     │
                    │ • Validate data        │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   PREPROCESSING        │
                    │ • Handle missing       │
                    │ • Encode categorical   │
                    │ • Scale features       │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   SPLITTING_DATA       │
                    │ • Train/test split     │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   SELECTING_FEATURES   │
                    │ • Feature importance   │
                    │ • Select top-k         │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   AGENT_1_DECIDING     │
                    │ 🤖 Algorithm selection │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   TRAINING_MODELS      │
                    │ • Parallel GridSearchCV│
                    │ • Per-algorithm tuning │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   AGENT_2_DECIDING     │
                    │ 🤖 Model selection     │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   EVALUATING_MODEL     │
                    │ • Test set metrics     │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   DETECTING_DRIFT      │
                    │ • KS test, Chi² test   │
                    │ • PSI calculation      │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   MONITORING_PERFORMANCE│
                    │ • Compare with baseline│
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │   AGENT_3_DECIDING     │
                    │ 🤖 Retraining decision │
                    └────────┬───────────────┘
                             │
                   ┌─────────┴────────┐
                   │                  │
        (retrain=True)      (retrain=False)
                   │                  │
                   ▼                  ▼
        ┌───────────────────┐  ┌─────────────────┐
        │ TRIGGERING_RETRAIN│  │ SAVING_ARTIFACTS│
        │ • Create new run  │  │ • Register model│
        └─────┬─────────────┘  │ • Save metadata │
              │                └─────────┬───────┘
              │ (loops back              │
              │  to START)               ▼
              │              ┌───────────────────────┐
              └─────────────>│  GENERATING_REPORT    │
                             │ • Create visualizations│
                             │ • Generate summary    │
                             └───────────┬───────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │    COMPLETED         │
                              │ • End MLflow run     │
                              └──────────────────────┘
                                         │
                                         ▼
                                    ┌────────┐
                                    │  END   │
                                    └────────┘

Error States (from any state):
─────────────────────────────────
Any state can transition to:
┌────────────────────────┐
│   ERROR                │
│ • Log error details    │
│ • Mark run as failed   │
│ • Notify user          │
└────────────────────────┘
         │
         ▼
┌────────────────────────┐
│   FAILED               │
└────────────────────────┘

Pause/Resume:
─────────────
From any active state:
┌────────────────────────┐
│   PAUSED               │
│ • Save checkpoint      │
│ • Suspend execution    │
└────────────────────────┘
         │ (resume)
         ▼
(return to previous state)
```

### 4.2 Model Version State Machine (MLflow)

```
┌─────────────────────────────────────────────────────────────────────┐
│                Model Version State Machine                           │
└─────────────────────────────────────────────────────────────────────┘

                         ┌───────────────┐
                         │  Model Trained│
                         └───────┬───────┘
                                 │
                                 │ register_model()
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │        NONE            │
                    │ (newly registered)     │
                    └────────┬───────────────┘
                             │
                             │ transition_stage("Staging")
                             │
                             ▼
                    ┌────────────────────────┐
                    │       STAGING          │
                    │ • Testing phase        │
                    │ • Validation           │
                    └────────┬───────────────┘
                             │
                             │ transition_stage("Production")
                             │
                             ▼
                    ┌────────────────────────┐
                    │      PRODUCTION        │
                    │ • Actively serving     │
                    │ • Performance tracking │
                    └────────┬───────────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
        (new model deployed)   (performance degraded)
                  │                     │
                  ▼                     ▼
        ┌─────────────────┐   ┌────────────────────┐
        │    ARCHIVED      │   │   ARCHIVED         │
        │ • Superseded     │   │ • Deprecated       │
        │ • Kept for audit │   │ • Kept for rollback│
        └──────────────────┘   └────────────────────┘
```

---

## Summary

These UML diagrams provide comprehensive views of:

1. **Component Diagram**: High-level system architecture with component dependencies
2. **Class Diagrams**: Detailed class structures organized by functional modules:
   - Core pipeline classes
   - Data processing classes
   - Training module classes
   - AI agent classes
   - Monitoring classes
   - MLflow integration classes
   - Configuration classes
3. **Deployment Diagram**: Container and node architecture with resource allocations
4. **State Machine Diagrams**:
   - Pipeline execution states
   - Model version lifecycle in MLflow

Key Design Patterns Used:
- **Strategy Pattern**: Different algorithm trainers implementing common interface
- **Factory Pattern**: Creating estimators and agents
- **Observer Pattern**: State updates notifying UI components
- **Command Pattern**: Pipeline operations as executable commands
- **Singleton Pattern**: MLflowManager and BedrockClient instances
- **Template Method**: BaseAlgorithmTrainer with algorithm-specific implementations

All classes follow:
- **SOLID principles** for maintainability
- **Type hints** for clarity
- **Dataclasses** for data structures
- **Abstract base classes** for extensibility

---

**End of UML Diagrams Document**
