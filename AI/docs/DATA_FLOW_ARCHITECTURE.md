# Data Flow Architecture - Enhanced ML Pipeline

## Overview

This document describes how data flows through the **enhanced ML pipeline** system, including:
- Core data transformations
- **AI decision agent data flows**
- **MLflow logging points**
- **Algorithm-specific parallel training**
- **Monitoring and drift detection**

## Enhanced End-to-End Data Flow

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                   ENHANCED ML PIPELINE DATA FLOW                                │
│                   (with AI Agents, MLflow, and Monitoring)                      │
└────────────────────────────────────────────────────────────────────────────────┘

STAGE 0: PROMPT ANALYSIS & CONFIG EXTRACTION (NEW)
┌──────────────────────────────────────────┐
│  User Inputs:                            │
│  - data_path: str                        │
│  - user_prompt: str                      │
│  - user_hints: Dict (optional)           │
└─────────────────┬────────────────────────┘
                  │ Quick data peek (first 100 rows)
                  ▼
    ┌─────────────┴─────────────────────────────────────────────┐
    │                                                             │
    │          🤖 DECISION POINT 0: CONFIG EXTRACTION            │
    │                 (Agent 0 - AWS Bedrock Claude)             │
    │          Model: us.anthropic.claude-sonnet-4-5-*           │
    │                                                             │
    │  INPUT DATA PACKAGE:                                       │
    │  ┌──────────────────────────────────────────────────┐     │
    │  │ Context for Agent:                               │     │
    │  │ {                                                │     │
    │  │   "user_prompt": "Analyze liveness vs genre",   │     │
    │  │   "data_path": "data/spotify.csv",               │     │
    │  │   "available_columns": ["liveness", "genre",...],│     │
    │  │   "dataset_preview": {                           │     │
    │  │     "n_rows": 100,                               │     │
    │  │     "n_columns": 15,                             │     │
    │  │     "dtypes": {"liveness": "float64", ...}       │     │
    │  │   },                                             │     │
    │  │   "user_hints": {...}  # Optional                │     │
    │  │ }                                                │     │
    │  └──────────────────────────────────────────────────┘     │
    │                       │                                    │
    │                       ▼                                    │
    │            [Bedrock Claude Analysis]                       │
    │               (with retry logic)                           │
    │                       │                                    │
    │                       ▼                                    │
    │  OUTPUT DATA PACKAGE:                                      │
    │  ┌──────────────────────────────────────────────────┐     │
    │  │ extracted_config:                                │     │
    │  │ {                                                │     │
    │  │   "target_column": "liveness",                   │     │
    │  │   "experiment_name": "liveness_genre_analysis",  │     │
    │  │   "test_size": 0.2,                              │     │
    │  │   "random_state": 42,                            │     │
    │  │   "analysis_type": "regression",                 │     │
    │  │   "confidence": 0.95,  # MUST be >= 0.70         │     │
    │  │   "reasoning": "...",                            │     │
    │  │   "assumptions": [...],                          │     │
    │  │   "warnings": [...]                              │     │
    │  │ }                                                │     │
    │  └──────────────────────────────────────────────────┘     │
    │             ◄─ Store prompt in triple storage:            │
    │                - MLflow artifacts                          │
    │                - PostgreSQL database                       │
    │                - MinIO/S3                                  │
    └───────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────┐
│  pipeline_config: Dict                   │
│  - target_column: "liveness"             │
│  - experiment_name: "liveness_genre_..." │
│  - test_size: 0.2                        │
│  - random_state: 42                      │
│  prompt_analysis: Dict                   │
│  - user_prompt, confidence, reasoning    │
└─────────────────┬────────────────────────┘
                  │
                  │
                  │
                  │
STAGE 1: INPUT + MLflow INITIALIZATION
┌──────────────────────────────────────────┐
│  data.csv                                │
│  Format: CSV │ Rows: N │ Cols: M         │
└─────────────────┬────────────────────────┘
                  │ Read CSV + Start MLflow Run
                  ▼
┌──────────────────────────────────────────┐
│  raw_data: pd.DataFrame (N, M)           │
│  mlflow_experiment_id: str               │  ◄─ MLflow: Log data_path, n_rows, n_cols
│  mlflow_run_id: str                      │
└─────────────────┬────────────────────────┘
                  │
                  │ STAGE 1.5: ALGORITHM-AWARE HITL REVIEW
                  │ (Human-in-the-Loop with Intelligent Preprocessing)
                  │
    ┌─────────────┴─────────────────────────────────────────────┐
    │                                                             │
    │      🤖 STEP 1: ALGORITHM CATEGORY PREDICTION              │
    │                 (Agent 1A - AWS Bedrock Claude)            │
    │          Model: us.anthropic.claude-sonnet-4-5-*           │
    │                  Temperature: 0.2                           │
    │                                                             │
    │  INPUT DATA PACKAGE:                                       │
    │  ┌──────────────────────────────────────────────────┐     │
    │  │ Context for Agent 1A:                            │     │
    │  │ {                                                │     │
    │  │   "n_samples": 114000,                           │     │
    │  │   "n_features": 20,  # excluding target          │     │
    │  │   "target_type": "regression",                   │     │
    │  │   "feature_types": {                             │     │
    │  │     "numeric_count": 16,                         │     │
    │  │     "categorical_count": 4,                      │     │
    │  │     "high_cardinality_count": 2                  │     │
    │  │   },                                             │     │
    │  │   "dataset_size_mb": 25.3,                       │     │
    │  │   "data_characteristics": {                      │     │
    │  │     "missing_percentage": 5.2,                   │     │
    │  │     "duplicate_percentage": 0.13,                │     │
    │  │     "outlier_percentage": 8.7,                   │     │
    │  │     "feature_correlation_max": 0.82              │     │
    │  │   }                                              │     │
    │  │ }                                                │     │
    │  └──────────────────────────────────────────────────┘     │
    │                       │                                    │
    │                       ▼                                    │
    │            [Bedrock Claude Analysis]                       │
    │            "Predict best algorithm category"               │
    │               (with retry logic)                           │
    │                       │                                    │
    │                       ▼                                    │
    │  OUTPUT DATA PACKAGE:                                      │
    │  ┌──────────────────────────────────────────────────┐     │
    │  │ algorithm_category: "tree_models"                │     │
    │  │ confidence: 0.87                                 │     │
    │  │ reasoning: "Medium-sized dataset with mixed...   │     │
    │  │ recommended_algorithms: [                        │     │
    │  │   "RandomForest", "XGBoost", "GradientBoosting" │     │
    │  │ ]                                                │     │
    │  │ preprocessing_priorities: {                      │     │
    │  │   "clean_data": "optional",                      │     │
    │  │   "handle_missing": "required",                  │     │
    │  │   "encode_features": "required",                 │     │
    │  │   "scale_features": "optional"                   │     │
    │  │ }                                                │     │
    │  │ algorithm_requirements: {                        │     │
    │  │   "scaling_required": false,                     │     │
    │  │   "outlier_sensitive": false,                    │     │
    │  │   "handles_missing": true,                       │     │
    │  │   "categorical_encoding_preference": "target"    │     │
    │  │ }                                                │     │
    │  └──────────────────────────────────────────────────┘     │
    │             ◄─ Store prediction in triple storage:         │
    │                - State["algorithm_category"]               │
    │                - MLflow: log_param("algorithm_category")   │
    │                - PostgreSQL: review_questions table        │
    │                                                             │
    └─────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                                                               │
    │      🤖 STEP 2: PREPROCESSING QUESTION GENERATION            │
    │                 (Agent 1B - AWS Bedrock Claude)              │
    │          Model: us.anthropic.claude-sonnet-4-5-*             │
    │                  Temperature: 0.3                             │
    │                                                               │
    │  INPUT DATA PACKAGE:                                         │
    │  ┌────────────────────────────────────────────────────┐     │
    │  │ Context for Agent 1B:                              │     │
    │  │ {                                                  │     │
    │  │   "algorithm_category": "tree_models",  # From 1A  │     │
    │  │   "algorithm_confidence": 0.87,                    │     │
    │  │   "algorithm_requirements": {...},  # From 1A      │     │
    │  │   "data_profile": {                                │     │
    │  │     "n_samples": 114000,                           │     │
    │  │     "n_features": 20,                              │     │
    │  │     "missing_values": {                            │     │
    │  │       "energy": 230, "tempo": 110                  │     │
    │  │     },                                             │     │
    │  │     "duplicate_rows": 150,                         │     │
    │  │     "categorical_columns": ["key", "mode",...],    │     │
    │  │     "high_cardinality_columns": ["artists"],       │     │
    │  │     "outlier_summary": {                           │     │
    │  │       "loudness": {count: 1200, Q1: -10, Q3: -3}   │     │
    │  │     }                                              │     │
    │  │   },                                               │     │
    │  │   "preprocessing_steps": [                         │     │
    │  │     "clean_data", "handle_missing",                │     │
    │  │     "encode_features", "scale_features"            │     │
    │  │   ]                                                │     │
    │  │ }                                                  │     │
    │  └────────────────────────────────────────────────────┘     │
    │                       │                                      │
    │                       ▼                                      │
    │            [Bedrock Claude Analysis]                         │
    │       "Generate algorithm-aware preprocessing questions"     │
    │               (with retry logic)                             │
    │                       │                                      │
    │                       ▼                                      │
    │  OUTPUT DATA PACKAGE:                                        │
    │  ┌────────────────────────────────────────────────────┐     │
    │  │ questions: [                                       │     │
    │  │   {                                                │     │
    │  │     "question_id": "clean_q1",                     │     │
    │  │     "preprocessing_step": "clean_data",            │     │
    │  │     "question_text": "How should we handle...?",   │     │
    │  │     "question_type": "multiple_choice",            │     │
    │  │     "priority": "low",  # Tree models robust       │     │
    │  │     "options": [                                   │     │
    │  │       {"value": "iqr_method", "label": "IQR...",   │     │
    │  │        "recommended": true, "reasoning": "..."},    │     │
    │  │       {"value": "none", "label": "No removal",     │     │
    │  │        "recommended": true}                         │     │
    │  │     ]                                              │     │
    │  │   },                                               │     │
    │  │   { # handle_missing question },                   │     │
    │  │   { # encode_features question (HIGH priority) },  │     │
    │  │   { # scale_features question (LOW priority) }     │     │
    │  │ ]  # Total: 4-20 questions (1-5 per step)          │     │
    │  │ preprocessing_recommendations: {                   │     │
    │  │   "clean_data_technique": "iqr_method",            │     │
    │  │   "handle_missing_technique": "simple_imputation", │     │
    │  │   "encode_technique": "target_encoding",           │     │
    │  │   "scale_technique": "none"                        │     │
    │  │ }                                                  │     │
    │  │ algorithm_context: "Tree models are robust..."     │     │
    │  └────────────────────────────────────────────────────┘     │
    │             ◄─ Store questions in triple storage:            │
    │                - PostgreSQL (review_questions table)          │
    │                - MLflow artifacts (review_session.json)       │
    │                - State["review_questions"]                    │
    │                                                               │
    └─────────────┬─────────────────────────────────────────────────┘
                  │
                  │ ◄─ [LANGGRAPH INTERRUPTION]
                  │    workflow.interrupt_after(["review_config"])
                  │    Pipeline pauses, awaiting human input
                  │    pipeline_status = "awaiting_review"
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  👤 HUMAN REVIEW (Enhanced Frontend UI - ReviewForm.jsx)    │
│                                                              │
│  🎯 Algorithm Category Banner:                              │
│     "Predicted: Tree Models (confidence 87%)"               │
│     "Recommended: RandomForest, XGBoost, GradientBoosting"  │
│                                                              │
│  📑 Tabbed Interface:                                        │
│     [Clean Data] [Handle Missing] [Encode] [Scale]          │
│                                                              │
│  ❓ Questions (4-20 total, grouped by preprocessing step):   │
│     - Each question shows multiple technique options        │
│     - Recommended options highlighted (green checkmark)     │
│     - Algorithm-specific context tooltips                   │
│     - Priority badges (HIGH/MEDIUM/LOW)                     │
│     - Parameter sliders for selected techniques             │
│                                                              │
│  User selects techniques and parameters:                    │
│  {                                                          │
│    "clean_data_technique": "iqr_method",                    │
│    "iqr_multiplier": 1.5,                                   │
│    "handle_missing_technique": "simple_imputation",         │
│    "imputation_strategy": "median",                         │
│    "encode_technique": "target_encoding",                   │
│    "target_smoothing": 1.0,                                 │
│    "scale_technique": "none"                                │
│  }                                                          │
│                                                              │
│  User decides:                                               │
│  ✅ Approve & Continue Pipeline                             │
│  🔄 Request Re-Analysis                                      │
│                                                              │
│  Answers stored in PostgreSQL (review_questions.answers)    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ If APPROVED
                  ▼
┌──────────────────────────────────────────┐
│  review_approved: true                   │
│  review_answers: {                       │  ◄─ PostgreSQL: Update review session
│    "clean_data_technique": "iqr_method", │     with algorithm context
│    "handle_missing_technique": "simple", │
│    "encode_technique": "target_encoding",│
│    "scale_technique": "none"             │
│  }                                       │
│  pipeline_status: "review_approved"      │
│  algorithm_category: "tree_models"       │  ◄─ Carried forward to preprocessing
└─────────────────┬────────────────────────┘
                  │
                  │ Resume MLflow run
                  │ Continue to algorithm-aware preprocessing
                  │
                  │ STAGE 2: TECHNIQUE-BASED PREPROCESSING
                  │ (Nodes execute user-selected techniques)
                  ▼
┌──────────────────────────────────────────┐
│  clean_data_node:                        │
│    - Execute technique="iqr_method"      │
│    - With multiplier=1.5                 │
│    - Log: "clean_data_technique=iqr"     │  ◄─ MLflow: Log selected technique
│  handle_missing_node:                    │
│    - Execute technique="simple"          │     and parameters
│    - With strategy="median"              │
│  encode_features_node:                   │
│    - Execute technique="target_encoding" │
│    - With smoothing=1.0                  │
│  scale_features_node:                    │
│    - Execute technique="none" (skip)     │
│    - Log: "Tree models don't need scale" │
│                                          │
│  cleaned_data: pd.DataFrame (N', M')     │
│  feature_metadata: {                     │  ◄─ MLflow: Comprehensive preprocessing
│    "algorithm_category": "tree_models",  │     metrics and metadata
│    "techniques_used": {...},             │
│    "outliers_removed": 1200,             │
│    "missing_imputed": 340,               │
│    "encoding_mappings": {...}            │
│  }                                       │
└─────────────────┬────────────────────────┘
                  │
                  │ STAGE 3: TRAIN/TEST SPLIT
                  ▼
┌──────────────────────────────────────────┐
│  X_train: (0.8*N', M'-1)                 │
│  y_train: (0.8*N',)                      │  ◄─ MLflow: Log split params
│  X_test: (0.2*N', M'-1)                  │     (test_size, stratify)
│  y_test: (0.2*N',)                       │
└─────────────────┬────────────────────────┘
                  │
                  │ STAGE 4: FEATURE SELECTION
                  ▼
┌──────────────────────────────────────────┐
│  X_train: (0.8*N', F)                    │
│  X_test: (0.2*N', F)                     │
│  selected_features: List[str] (F items)  │  ◄─ MLflow: Log feature importance
│  feature_importance: Dict[str, float]    │
│  feature_statistics: Dict (for agent)    │
└─────────────────┬────────────────────────┘
                  │
                  │
    ┌─────────────┴─────────────────────────────────────────────┐
    │                                                             │
    │          🤖 DECISION POINT 1: ALGORITHM SELECTION          │
    │                 (Agent 1 - AWS Bedrock Claude)             │
    │                                                             │
    │  INPUT DATA PACKAGE:                                       │
    │  ┌──────────────────────────────────────────────────┐     │
    │  │ Context for Agent:                               │     │
    │  │ {                                                │     │
    │  │   "n_samples": 800,                              │     │
    │  │   "n_features": 15,                              │     │
    │  │   "target_type": "binary_classification",        │     │
    │  │   "class_distribution": {0: 450, 1: 350},        │     │
    │  │   "feature_correlations": {...},                 │     │
    │  │   "computational_budget": {                      │     │
    │  │     "max_time_minutes": 60,                      │     │
    │  │     "max_parallel": 3                            │     │
    │  │   }                                              │     │
    │  │ }                                                │     │
    │  └──────────────────────────────────────────────────┘     │
    │                       │                                    │
    │                       ▼                                    │
    │            [Bedrock Claude Analysis]                       │
    │                       │                                    │
    │                       ▼                                    │
    │  OUTPUT DATA PACKAGE:                                      │
    │  ┌──────────────────────────────────────────────────┐     │
    │  │ algorithm_selection_decision:                    │     │
    │  │ {                                                │     │
    │  │   "selected_algorithms": [                       │     │
    │  │     "random_forest",                             │     │
    │  │     "gradient_boosting",                         │     │
    │  │     "logistic_regression"                        │     │
    │  │   ],                                             │     │
    │  │   "reasoning": {...},                            │     │
    │  │   "hyperparameter_suggestions": {...},           │     │
    │  │   "estimated_times": {...}                       │     │
    │  │ }                                                │     │
    │  └──────────────────────────────────────────────────┘     │
    │                                                             │
    └─────────────┬───────────────────────────────────────────────┘
                  │
                  │ ◄─ MLflow: Log agent decision, prompt, response
                  │
                  ▼
    ┌─────────────────────────────────────────────┐
    │  Conditional Routing Based on Agent Decision │
    │  selected_algorithms = ["random_forest",     │
    │                         "gradient_boosting",  │
    │                         "logistic_regression"]│
    └─────────────┬───────────────────────────────┘
                  │
                  │ STAGE 5: PARALLEL ALGORITHM TRAINING
                  │ (Each algorithm trains independently with GridSearchCV)
                  │
         ┌────────┼────────┬────────────────┐
         │        │        │                │
         ▼        ▼        ▼                ▼
    ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
    │Random  │ │Gradient│ │Logistic  │ │   SVM    │
    │Forest  │ │Boosting│ │Regression│ │(skipped) │
    │        │ │        │ │          │ │          │
    │MLflow  │ │MLflow  │ │MLflow    │ │          │
    │Child   │ │Child   │ │Child     │ │          │
    │Run     │ │Run     │ │Run       │ │          │
    └────┬───┘ └────┬───┘ └────┬─────┘ └──────────┘
         │          │          │
         │          │          │ Each logs:
         │          │          │ - Best hyperparameters
         │          │          │ - CV scores
         │          │          │ - Test metrics
         │          │          │ - Training time
         │          │          │ - Model artifact
         │          │          │
         └──────────┴──────────┴─────────┐
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────┐
│  algorithm_results: Dict[str, AlgorithmResult]               │
│  {                                                           │
│    "random_forest": {                                        │
│      "model": <RandomForestClassifier>,                      │
│      "cv_mean": 0.87, "cv_std": 0.02,                        │
│      "test_accuracy": 0.88, "test_f1": 0.87,                 │
│      "training_time": 45.2,                                  │
│      "best_params": {...},                                   │
│      "mlflow_run_id": "abc123"                               │
│    },                                                        │
│    "gradient_boosting": {...},                              │
│    "logistic_regression": {...}                             │
│  }                                                           │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          │
    ┌─────────────────────┴─────────────────────────────────┐
    │                                                         │
    │        🤖 DECISION POINT 2: MODEL SELECTION            │
    │               (Agent 2 - AWS Bedrock Claude)           │
    │                                                         │
    │  INPUT DATA PACKAGE:                                   │
    │  ┌───────────────────────────────────────────────┐    │
    │  │ Context for Agent:                            │    │
    │  │ {                                             │    │
    │  │   "trained_models": [                         │    │
    │  │     {                                         │    │
    │  │       "algorithm": "random_forest",           │    │
    │  │       "cv_mean": 0.87, "cv_std": 0.02,        │    │
    │  │       "test_accuracy": 0.88,                  │    │
    │  │       "test_f1": 0.87,                        │    │
    │  │       "training_time": 45.2,                  │    │
    │  │       "complexity": "high"                    │    │
    │  │     },                                        │    │
    │  │     {                                         │    │
    │  │       "algorithm": "logistic_regression",     │    │
    │  │       "cv_mean": 0.84, "cv_std": 0.03,        │    │
    │  │       "test_accuracy": 0.85,                  │    │
    │  │       "test_f1": 0.84,                        │    │
    │  │       "training_time": 5.3,                   │    │
    │  │       "complexity": "low"                     │    │
    │  │     },                                        │    │
    │  │     {...}                                     │    │
    │  │   ],                                          │    │
    │  │   "business_requirements": {                  │    │
    │  │     "max_latency_ms": 100,                    │    │
    │  │     "interpretability": "high"                │    │
    │  │   }                                           │    │
    │  │ }                                             │    │
    │  └───────────────────────────────────────────────┘    │
    │                       │                                │
    │                       ▼                                │
    │            [Bedrock Claude Analysis]                   │
    │                       │                                │
    │                       ▼                                │
    │  OUTPUT DATA PACKAGE:                                  │
    │  ┌───────────────────────────────────────────────┐    │
    │  │ model_selection_decision:                     │    │
    │  │ {                                             │    │
    │  │   "selected_model": "random_forest",          │    │
    │  │   "reasoning": "Best balance of accuracy...", │    │
    │  │   "confidence": 0.95,                         │    │
    │  │   "trade_offs": {                             │    │
    │  │     "accuracy": "3% better than logreg",      │    │
    │  │     "speed": "8x slower inference"            │    │
    │  │   },                                          │    │
    │  │   "risks": ["May overfit small datasets"],    │    │
    │  │   "alternative_model": "logistic_regression"  │    │
    │  │ }                                             │    │
    │  └───────────────────────────────────────────────┘    │
    │                                                         │
    └─────────────────────┬───────────────────────────────────┘
                          │
                          │ ◄─ MLflow: Log model selection decision
                          │
                          ▼
┌──────────────────────────────────────────┐
│  best_model_name: "random_forest"        │
│  best_model: <RandomForestClassifier>    │
└─────────────────┬────────────────────────┘
                  │
                  │ STAGE 6: DRIFT DETECTION
                  ▼
┌──────────────────────────────────────────────────┐
│  Drift Analysis:                                 │
│  - KS test for numerical features                │
│  - Chi² test for categorical features            │
│  - PSI calculation per feature                   │
│                                                   │
│  drift_detected: bool                            │  ◄─ MLflow: Log drift metrics
│  drift_score: float                              │     (drift_score, psi_max,
│  drift_details: Dict                             │      drifted_features)
│  {                                                │
│    "drifted_features": ["feature_2", "feature_5"],│
│    "feature_drift_scores": {...},                │
│    "psi_values": {...}                           │
│  }                                                │
└─────────────────┬────────────────────────────────┘
                  │
                  │ STAGE 7: PERFORMANCE MONITORING
                  ▼
┌──────────────────────────────────────────────────┐
│  Performance Comparison:                         │
│  current_accuracy: 0.85                          │
│  baseline_accuracy: 0.90                         │
│  performance_drop: 0.05 (5.56%)                  │  ◄─ MLflow: Log performance metrics
│                                                   │
│  performance_comparison: Dict                    │
│  {                                                │
│    "current_performance": {...},                 │
│    "baseline_performance": {...},                │
│    "performance_drop": 0.05,                     │
│    "performance_drop_pct": 5.56                  │
│  }                                                │
└─────────────────┬────────────────────────────────┘
                  │
                  │
    ┌─────────────┴─────────────────────────────────────────┐
    │                                                         │
    │       🤖 DECISION POINT 3: RETRAINING DECISION         │
    │              (Agent 3 - AWS Bedrock Claude)            │
    │                                                         │
    │  INPUT DATA PACKAGE:                                   │
    │  ┌───────────────────────────────────────────────┐    │
    │  │ Context for Agent:                            │    │
    │  │ {                                             │    │
    │  │   "performance_analysis": {                   │    │
    │  │     "current_accuracy": 0.85,                 │    │
    │  │     "baseline_accuracy": 0.90,                │    │
    │  │     "performance_drop": 0.05,                 │    │
    │  │     "performance_drop_pct": 5.56,             │    │
    │  │     "threshold": 0.05                         │    │
    │  │   },                                          │    │
    │  │   "drift_analysis": {                         │    │
    │  │     "drift_detected": true,                   │    │
    │  │     "drift_score": 0.15,                      │    │
    │  │     "affected_features": [...]                │    │
    │  │   },                                          │    │
    │  │   "business_context": {                       │    │
    │  │     "model_age_days": 45,                     │    │
    │  │     "predictions_per_day": 10000              │    │
    │  │   }                                           │    │
    │  │ }                                             │    │
    │  └───────────────────────────────────────────────┘    │
    │                       │                                │
    │                       ▼                                │
    │            [Bedrock Claude Analysis]                   │
    │                       │                                │
    │                       ▼                                │
    │  OUTPUT DATA PACKAGE:                                  │
    │  ┌───────────────────────────────────────────────┐    │
    │  │ retraining_decision:                          │    │
    │  │ {                                             │    │
    │  │   "retrain": true,                            │    │
    │  │   "reasoning": "Performance dropped 5.56%...",│    │
    │  │   "urgency": "medium",                        │    │
    │  │   "confidence": 0.9,                          │    │
    │  │   "contributing_factors": [                   │    │
    │  │     "Performance drop exceeds threshold",     │    │
    │  │     "Significant drift in 2 features"         │    │
    │  │   ],                                          │    │
    │  │   "recommended_actions": [...]                │    │
    │  │ }                                             │    │
    │  └───────────────────────────────────────────────┘    │
    │                                                         │
    └─────────────────────┬───────────────────────────────────┘
                          │
                          │ ◄─ MLflow: Log retraining decision
                          │
                          ▼
┌──────────────────────────────────────────┐
│  retraining_triggered: bool              │
│  retraining_reason: str                  │
│  retraining_urgency: str                 │
└─────────────────┬────────────────────────┘
                  │
                  │ STAGE 8: REPORTING
                  ▼
┌──────────────────────────────────────────────────┐
│  Comprehensive Report Including:                 │
│  - All algorithm results                         │
│  - Agent decisions (all 3 agents)                │
│  - Feature importance                            │
│  - Performance metrics                           │
│  - Drift analysis                                │
│  - Retraining recommendation                     │
│                                                   │  ◄─ MLflow: Log reports, plots
│  output_paths: Dict                              │
│  {                                                │
│    "model_comparison": "path.png",               │
│    "feature_importance": "path.png",             │
│    "agent_decisions": "path.pdf"                 │
│  }                                                │
└─────────────────┬────────────────────────────────┘
                  │
                  │ STAGE 9: SAVE ARTIFACTS + MLflow REGISTRY
                  ▼
┌──────────────────────────────────────────────────┐
│  MLflow Model Registry:                          │
│  - Register best model                           │
│  - Add version tags                              │
│  - Store all metadata                            │
│                                                   │
│  Local Artifacts:                                │
│  outputs/{timestamp}/                            │
│    ├── models/                                   │
│    ├── metrics/                                  │
│    ├── plots/                                    │
│    ├── agent_decisions/                          │
│    └── reports/                                  │
│                                                   │
│  mlflow.end_run()                                │  ◄─ MLflow: End run, register model
└──────────────────────────────────────────────────┘
```

---

## Data Structures by Stage

### Stage 1: Data Loading + MLflow Init

**Input**: File path (str)
**Output**: DataFrame + MLflow IDs

```python
# Input
data_path: str = "data/train.csv"
mlflow_tracking_uri: str = "http://localhost:5000"
mlflow_experiment_name: str = "ml_pipeline_v2"

# Output
{
    "raw_data": pd.DataFrame(shape=(10000, 25)),
    "mlflow_experiment_id": "5",
    "mlflow_run_id": "abc123def456",
    "mlflow_tracking_uri": "http://localhost:5000"
}

# MLflow Logged:
# - Parameters: data_path, n_rows, n_cols
# - Metrics: data_size_mb
# - Tags: pipeline_version, timestamp
```

---

### Stage 2: Preprocessing

**Input**: raw_data
**Output**: cleaned_data + feature_metadata + feature_statistics + scaler + encoding_mappings

Stage 2 consists of 4 sequential preprocessing nodes:

#### 2.1: clean_data_node

**Operations**:
- Remove duplicate rows
- Remove rows with all NaN values
- Outlier detection and removal using IQR method:
  - For each numeric column: Q1 = 25th percentile, Q3 = 75th percentile, IQR = Q3 - Q1
  - Define bounds: `lower = Q1 - 1.5*IQR`, `upper = Q3 + 1.5*IQR`
  - Remove rows where `(value < lower) OR (value > upper)`

**State Updates**:
```python
{
    "cleaned_data": pd.DataFrame,  # After duplicate/outlier removal
    "outliers_removed": int,       # Total outlier count
    "outlier_columns": List[str],  # Columns with outliers
    "outlier_report": Dict[str, Dict]  # Per-column outlier details (Q1, Q3, IQR, bounds)
}
```

**MLflow Logged**:
- Metrics: duplicates_removed, all_nan_removed, outliers_removed, total_rows_removed, original_rows, final_rows
- Parameters: outlier_detection_method="IQR", outlier_multiplier=1.5

#### 2.2: handle_missing_node

**Operations**:
- Analyze missing value percentage per column: `missing_pct = null_count / total_rows`
- Drop columns with >70% missing values
- Impute remaining missing values:
  - **Numeric columns**: Use mean or median based on skewness
    - If `abs(skewness) > 1.0`: Use median (highly skewed)
    - Else: Use mean (relatively normal)
  - **Categorical columns**: Use mode (most frequent value)

**State Updates**:
```python
{
    "cleaned_data": pd.DataFrame,  # After imputation
    "dropped_columns": List[str],  # Columns dropped due to >70% missing
    "imputation_applied": Dict[str, str],  # {col: method} e.g., {"age": "mean", "gender": "mode"}
    "missing_value_report": Dict[str, Dict]  # Per-column missing stats
}
```

**MLflow Logged**:
- Parameters: missing_threshold=0.7, imputation_methods
- Metrics: columns_dropped, columns_imputed, remaining_nulls

#### 2.3: encode_features_node

**Operations**:
- Identify categorical columns (object/category dtypes)
- Apply encoding strategy based on cardinality:
  - **Binary (2 unique values)**: Label encoding (0, 1) using LabelEncoder
  - **Low cardinality (<10 unique)**: One-hot encoding using pd.get_dummies()
  - **High cardinality (>=10 unique)**: Frequency encoding (map to value frequencies)

**State Updates**:
```python
{
    "cleaned_data": pd.DataFrame,  # After encoding (may have more columns from one-hot)
    "encoding_mappings": Dict[str, Any],  # Stores encoders and mappings for inverse transform
    "encoded_columns": List[str],  # Columns that were encoded
    "encoding_methods": Dict[str, str],  # {col: method} e.g., {"gender": "label_encoding"}
    "feature_names": List[str]  # Updated column names after encoding
}
```

**MLflow Logged**:
- Parameters: encoding_methods, categorical_columns_encoded
- Metrics: features_added, original_features, final_features

#### 2.4: scale_features_node

**Operations**:
- Identify numeric columns
- Apply StandardScaler (z-score normalization): `scaled = (value - mean) / std`
- Calculate comprehensive feature statistics
- Perform data validation:
  - Assert no null values remain
  - Assert no infinite values in numeric columns
  - Check for duplicate rows
- Build consolidated feature_metadata

**State Updates**:
```python
{
    "cleaned_data": pd.DataFrame,  # Fully preprocessed data
    "scaler": StandardScaler,  # Fitted scaler object for transform
    "scaled_columns": List[str],  # Numeric columns that were scaled
    "feature_statistics": Dict[str, Dict],  # Per-feature stats for all features
    "feature_metadata": Dict  # Consolidated metadata from all preprocessing steps
}
```

**feature_statistics format**:
```python
{
    "numeric_col": {
        "mean": float,
        "std": float,
        "min": float,
        "max": float,
        "median": float,
        "q1": float,
        "q3": float,
        "dtype": str
    },
    "categorical_col": {
        "unique_values": int,
        "dtype": str
    }
}
```

**feature_metadata format**:
```python
{
    "dropped_columns": List[str],  # From handle_missing_node
    "imputation_applied": Dict[str, str],  # From handle_missing_node
    "encoding_mappings": Dict[str, str],  # From encode_features_node
    "scaler": StandardScaler,  # From scale_features_node
    "outliers_removed": int,  # From clean_data_node
    "original_shape": Tuple[int, int],  # From raw_data
    "final_shape": Tuple[int, int],  # After all preprocessing
    "scaled_columns": List[str],  # From scale_features_node
    "feature_names": List[str]  # Final column names
}
```

**MLflow Logged**:
- Parameters: scaling_method="StandardScaler", features_scaled
- Metrics: final_features, final_samples, validation_passed
- Artifacts: feature_statistics.json (comprehensive stats for all features)

#### Complete Stage 2 Example

```python
# Input
raw_data: pd.DataFrame(shape=(10000, 25), dtype=mixed)

# After clean_data_node
{
    "cleaned_data": pd.DataFrame(shape=(9800, 25)),  # 150 duplicates + 50 outliers removed
    "outliers_removed": 50
}

# After handle_missing_node
{
    "cleaned_data": pd.DataFrame(shape=(9800, 24)),  # 1 column dropped (>70% missing)
    "dropped_columns": ["col_with_80pct_missing"],
    "imputation_applied": {"age": "median", "income": "mean", "gender": "mode"}
}

# After encode_features_node
{
    "cleaned_data": pd.DataFrame(shape=(9800, 35)),  # Expanded from one-hot encoding
    "encoding_methods": {
        "gender": "label_encoding",  # Binary: Male=0, Female=1
        "city": "onehot_encoding",  # Low cardinality: created 5 columns
        "user_id": "frequency_encoding"  # High cardinality: replaced with frequencies
    }
}

# After scale_features_node (FINAL OUTPUT)
{
    "cleaned_data": pd.DataFrame(shape=(9800, 35)),  # All numeric columns scaled
    "scaler": <StandardScaler>,
    "feature_metadata": {
        "dropped_columns": ["col_with_80pct_missing"],
        "imputation_applied": {"age": "median", "income": "mean", "gender": "mode"},
        "encoding_mappings": {"gender": "label_encoding", "city": "onehot_encoding"},
        "scaler": <StandardScaler>,
        "outliers_removed": 50,
        "original_shape": (10000, 25),
        "final_shape": (9800, 35),
        "scaled_columns": ["age", "income", "height", ...],  # 15 numeric columns
        "feature_names": ["age", "income", "gender", "city_NY", "city_LA", ...]  # 35 total
    },
    "feature_statistics": {
        "age": {"mean": 0.0, "std": 1.0, "min": -2.5, "max": 3.2, "dtype": "float64"},
        "gender": {"unique_values": 2, "dtype": "int64"},
        # ... for all 35 features
    }
}

# MLflow Logged Across All 4 Nodes:
# - Parameters: outlier_detection_method, missing_threshold, encoding_methods, scaling_method
# - Metrics: duplicates_removed, outliers_removed, columns_dropped, columns_imputed, features_added, final_features, final_samples
# - Artifacts: feature_statistics.json
```

---

### Stage 3: Train/Test Split

**Input**: cleaned_data
**Output**: X_train, X_test, y_train, y_test

```python
# Input
cleaned_data: pd.DataFrame(shape=(9800, 35))

# Output
{
    "X_train": pd.DataFrame(shape=(7840, 34)),  # 80% of 9800
    "X_test": pd.DataFrame(shape=(1960, 34)),   # 20% of 9800
    "y_train": pd.Series(shape=(7840,)),
    "y_test": pd.Series(shape=(1960,)),
    "train_data": pd.DataFrame(shape=(7840, 35)),  # X_train + y_train
    "test_data": pd.DataFrame(shape=(1960, 35))    # X_test + y_test
}

# MLflow Logged:
# - Parameters: test_size=0.2, stratified=True, random_state=42
# - Metrics: train_samples=7840, test_samples=1960
# - Artifacts: class_distribution.json
```

---

### Stage 4: Feature Selection

**Input**: X_train, y_train
**Output**: Selected features + importance scores

```python
# Input
X_train: pd.DataFrame(shape=(7840, 34))
y_train: pd.Series(shape=(7840,))

# Output
{
    "selected_features": ["feature_1", "feature_3", "feature_7", ...],  # 15 features
    "feature_importance": {
        "feature_1": 0.25,
        "feature_3": 0.18,
        "feature_7": 0.15,
        # ... all 34 features with scores
    },
    "dropped_features": ["feature_2", "feature_4", ...],  # 19 features
    "X_train": pd.DataFrame(shape=(7840, 15)),  # Filtered
    "X_test": pd.DataFrame(shape=(1960, 15)),   # Filtered
    "feature_statistics": {
        # Enhanced stats for Agent 1
        "n_features": 15,
        "multicollinearity": {"feature_3": 0.85},
        "univariate_scores": {...}
    }
}

# MLflow Logged:
# - Parameters: selection_method, n_features_selected
# - Metrics: n_features_dropped
# - Artifacts: feature_importance.json, importance_plot.png
```

---

## Decision Point 1: Algorithm Selection Agent

### Input Data Package for Agent

```python
context_for_agent = {
    "n_samples": 7840,
    "n_features": 15,
    "target_type": "binary_classification",
    "class_distribution": {
        "class_0": 4500,
        "class_1": 3340
    },
    "feature_types": {
        "numerical": 10,
        "categorical_encoded": 5
    },
    "feature_correlations": {
        "max_correlation": 0.85,
        "multicollinearity_features": ["feature_3", "feature_7"],
        "target_correlations": {
            "feature_1": 0.65,
            "feature_3": 0.52,
            # ...
        }
    },
    "missing_values_pct": 0.0,
    "outliers_pct": 2.04,
    "data_quality": {
        "class_imbalance_ratio": 1.35,
        "feature_variance_low_count": 2
    },
    "computational_budget": {
        "max_training_time_minutes": 60,
        "max_parallel_algorithms": 3,
        "available_memory_gb": 8
    }
}
```

### Agent Processing

```
1. Receives context JSON
2. Analyzes data characteristics
3. Evaluates algorithm suitability
4. Generates JSON decision
5. Returns structured response
```

### Output Data Package from Agent

```python
algorithm_selection_decision = {
    "selected_algorithms": [
        "random_forest",
        "gradient_boosting",
        "logistic_regression"
    ],
    "reasoning": {
        "random_forest": "Robust to non-linearity, handles feature interactions well, good baseline",
        "gradient_boosting": "Likely highest accuracy given dataset size and feature count",
        "logistic_regression": "Fast training, interpretable, good for imbalanced data"
    },
    "hyperparameter_suggestions": {
        "random_forest": {
            "n_estimators": [100, 200],
            "max_depth": [10, 20, None],
            "min_samples_split": [2, 5]
        },
        "gradient_boosting": {
            "n_estimators": [100, 200],
            "learning_rate": [0.01, 0.1],
            "max_depth": [3, 5]
        },
        "logistic_regression": {
            "C": [0.1, 1.0, 10.0],
            "penalty": ["l1", "l2"]
        }
    },
    "estimated_times": {
        "random_forest": 25.0,
        "gradient_boosting": 35.0,
        "logistic_regression": 5.0
    },
    "skip_algorithms": ["svm", "knn"],
    "skip_reasons": {
        "svm": "Too slow for dataset size (7840 samples)",
        "knn": "Poor performance expected with 15 features and moderate noise"
    }
}

# Stored in state
state["algorithm_selection_decision"] = algorithm_selection_decision
state["selected_algorithms"] = ["random_forest", "gradient_boosting", "logistic_regression"]
state["algorithms_to_skip"] = ["svm", "knn"]
state["agent_prompts"]["algorithm_selection"] = prompt_text
state["agent_responses"]["algorithm_selection"] = raw_response_text

# MLflow Logged:
# - Parameters: agent1_model, agent1_temperature
# - Artifacts:
#   - agents/algorithm_selection_decision.json
#   - agents/algorithm_selection_prompt.txt
#   - agents/algorithm_selection_response.txt
```

---

## Stage 5: Sequential Algorithm Training 

### Input per Algorithm

```python
# Each selected algorithm receives:
{
    "X_train": pd.DataFrame(shape=(7840, 15)),
    "y_train": pd.Series(shape=(7840,)),
    "X_test": pd.DataFrame(shape=(1960, 15)),
    "y_test": pd.Series(shape=(1960,)),
    "param_grid": {  # From agent suggestion or default
        "n_estimators": [100, 200],
        "max_depth": [10, 20, None]
    },
    "cv_folds": 5,
    "scoring": "f1_weighted"
}
```

### Processing per Algorithm (e.g., Random Forest)

```
1. Start MLflow child run: mlflow.start_run(nested=True, run_name="random_forest")
2. Initialize GridSearchCV with param_grid
3. Fit: grid_search.fit(X_train, y_train)
4. Extract best estimator and parameters
5. Evaluate on test set
6. Log everything to MLflow:
   - Parameters: best_params, cv_folds, scoring
   - Metrics: cv_mean, cv_std, test_accuracy, test_f1, training_time
   - Model: mlflow.sklearn.log_model(best_model, "model")
   - Artifacts: cv_results.json
7. End child run
8. Return AlgorithmResult
```

### Output per Algorithm

```python
# Random Forest result
{
    "model": <RandomForestClassifier object>,
    "best_params": {
        "n_estimators": 200,
        "max_depth": 20,
        "min_samples_split": 5
    },
    "cv_scores": [0.86, 0.88, 0.87, 0.85, 0.89],
    "cv_mean": 0.87,
    "cv_std": 0.015,
    "test_accuracy": 0.88,
    "test_f1": 0.87,
    "training_time": 45.2,
    "mlflow_run_id": "child_run_abc123",
    "predictions": np.array([0, 1, 1, 0, ...])  # shape (1960,)
}

# Gradient Boosting result
{
    "model": <GradientBoostingClassifier object>,
    "best_params": {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 5},
    "cv_mean": 0.89,
    "cv_std": 0.012,
    "test_accuracy": 0.90,
    "test_f1": 0.89,
    "training_time": 62.8,
    "mlflow_run_id": "child_run_def456",
    "predictions": np.array([0, 1, 1, 0, ...])
}

# Logistic Regression result
{
    "model": <LogisticRegression object>,
    "best_params": {"C": 1.0, "penalty": "l2"},
    "cv_mean": 0.84,
    "cv_std": 0.020,
    "test_accuracy": 0.85,
    "test_f1": 0.84,
    "training_time": 5.3,
    "mlflow_run_id": "child_run_ghi789",
    "predictions": np.array([0, 1, 1, 0, ...])
}
```

### Aggregated Output

```python
state["algorithm_results"] = {
    "random_forest": {random_forest_result},
    "gradient_boosting": {gradient_boosting_result},
    "logistic_regression": {logistic_regression_result}
}

# MLflow Logged (per algorithm via child runs):
# - All parameters, metrics, models logged in nested runs
# - Parent run shows summary of all algorithms
```

---

## Decision Point 2: Model Selection Agent

### Input Data Package

```python
context_for_agent = {
    "trained_models": [
        {
            "algorithm": "random_forest",
            "cv_mean": 0.87,
            "cv_std": 0.015,
            "test_accuracy": 0.88,
            "test_f1": 0.87,
            "test_precision": 0.89,
            "test_recall": 0.86,
            "training_time": 45.2,
            "model_complexity": "high",
            "n_parameters": 15000,
            "best_params": {"n_estimators": 200, "max_depth": 20}
        },
        {
            "algorithm": "gradient_boosting",
            "cv_mean": 0.89,
            "cv_std": 0.012,
            "test_accuracy": 0.90,
            "test_f1": 0.89,
            "training_time": 62.8,
            "model_complexity": "high",
            "n_parameters": 12000
        },
        {
            "algorithm": "logistic_regression",
            "cv_mean": 0.84,
            "cv_std": 0.020,
            "test_accuracy": 0.85,
            "test_f1": 0.84,
            "training_time": 5.3,
            "model_complexity": "low",
            "n_parameters": 16
        }
    ],
    "business_requirements": {
        "max_prediction_latency_ms": 100,
        "interpretability_importance": "medium",
        "deployment_environment": "cloud_server",
        "model_update_frequency": "monthly",
        "cost_sensitivity": "medium"
    }
}
```

### Output Data Package

```python
model_selection_decision = {
    "selected_model": "gradient_boosting",
    "reasoning": "Gradient Boosting achieves highest accuracy (90%) with acceptable training time. While 2% more accurate than Random Forest, it's more stable (lower CV std). The 3% accuracy gain over Logistic Regression justifies the additional complexity for this use case.",
    "confidence": 0.95,
    "trade_offs": {
        "accuracy": "Gradient Boosting: 90% (best), Random Forest: 88% (+2%), Logistic Regression: 85% (+5%)",
        "speed": "Training: GB 63s vs RF 45s vs LR 5s. Inference: GB and RF similar (~10ms), LR fastest (~1ms)",
        "interpretability": "Logistic Regression most interpretable, GB and RF less so but acceptable with SHAP",
        "complexity": "GB and RF high complexity (12k-15k params), LR low (16 params)"
    },
    "risks": [
        "Gradient Boosting may overfit on smaller datasets",
        "Requires careful monitoring for distribution shift",
        "Longer training time (63s) may impact rapid iteration"
    ],
    "alternative_model": "random_forest",
    "recommendation": "Deploy Gradient Boosting for production. Monitor with Random Forest as fallback if performance degrades."
}

state["model_selection_decision"] = model_selection_decision
state["best_model_name"] = "gradient_boosting"
state["best_model"] = state["algorithm_results"]["gradient_boosting"]["model"]

# MLflow Logged:
# - Parameters: best_model=gradient_boosting, selection_confidence=0.95
# - Metrics: selection_confidence=0.95
# - Artifacts: agents/model_selection_decision.json, prompt, response
```

---

## Stage 6: Drift Detection

### Input

```python
{
    "X_train": pd.DataFrame(shape=(7840, 15)),  # Training distribution
    "X_test": pd.DataFrame(shape=(1960, 15)),   # Test/production distribution
    "drift_threshold": 0.1,
    "psi_threshold": 0.25
}
```

### Processing

```python
for feature in features:
    if feature is numerical:
        # Kolmogorov-Smirnov test
        ks_statistic, p_value = ks_2samp(X_train[feature], X_test[feature])
        if p_value < 0.05:
            drift_detected = True

    if feature is categorical:
        # Chi-squared test
        contingency_table = pd.crosstab(X_train[feature], X_test[feature])
        chi2, p_value, _, _ = chi2_contingency(contingency_table)
        if p_value < 0.05:
            drift_detected = True

    # Population Stability Index
    psi = calculate_psi(X_train[feature], X_test[feature])
    if psi >= 0.25:
        significant_drift = True
```

### Output

```python
{
    "drift_detected": True,
    "overall_drift_score": 0.15,
    "drifted_features": ["feature_2", "feature_5", "feature_9"],
    "feature_drift_scores": {
        "feature_1": 0.05,  # No drift
        "feature_2": 0.28,  # Significant drift
        "feature_3": 0.08,  # No drift
        "feature_5": 0.32,  # Significant drift
        # ...
    },
    "psi_values": {
        "feature_1": 0.08,
        "feature_2": 0.28,
        # ...
    },
    "drift_details": {
        "ks_tests": {
            "feature_1": {"statistic": 0.12, "pvalue": 0.15},
            "feature_2": {"statistic": 0.45, "pvalue": 0.001},
            # ...
        }
    }
}

state["drift_detected"] = True
state["drift_score"] = 0.15
state["drift_details"] = drift_details

# MLflow Logged:
# - Metrics: drift_score=0.15, psi_max=0.32, drift_features_count=3
# - Artifacts: monitoring/drift_analysis.json, drift_plot.png
```

---

## Stage 7: Performance Monitoring

### Input

```python
{
    "current_metrics": {
        "accuracy": 0.85,
        "f1_weighted": 0.84,
        "precision": 0.86,
        "recall": 0.83
    },
    "baseline_performance": {  # From previous run or validation
        "accuracy": 0.90,
        "f1_weighted": 0.89,
        "precision": 0.91,
        "recall": 0.88
    },
    "threshold": 0.05  # 5% drop threshold
}
```

### Processing

```python
for metric in metrics:
    drop = baseline[metric] - current[metric]
    drop_pct = (drop / baseline[metric]) * 100
    if drop >= threshold:
        threshold_exceeded = True
```

### Output

```python
{
    "performance_drop": 0.05,
    "performance_drop_pct": 5.56,
    "threshold_exceeded": True,
    "metric_comparison": {
        "accuracy": {
            "current": 0.85,
            "baseline": 0.90,
            "drop": 0.05,
            "drop_pct": 5.56
        },
        "f1_weighted": {
            "current": 0.84,
            "baseline": 0.89,
            "drop": 0.05,
            "drop_pct": 5.62
        },
        # ...
    }
}

state["performance_comparison"] = performance_comparison
state["performance_drop"] = 0.05

# MLflow Logged:
# - Metrics: current_accuracy, baseline_accuracy, performance_drop, performance_drop_pct
# - Artifacts: monitoring/performance_comparison.json
```

---

## Decision Point 3: Retraining Decision Agent

### Input Data Package

```python
context_for_agent = {
    "performance_analysis": {
        "current_accuracy": 0.85,
        "baseline_accuracy": 0.90,
        "performance_drop": 0.05,
        "performance_drop_pct": 5.56,
        "threshold": 0.05,
        "threshold_exceeded": True
    },
    "drift_analysis": {
        "drift_detected": True,
        "drift_score": 0.15,
        "drift_threshold": 0.1,
        "affected_features": ["feature_2", "feature_5", "feature_9"],
        "severity": "moderate"
    },
    "business_context": {
        "model_age_days": 45,
        "predictions_per_day": 10000,
        "business_impact": "high",
        "last_retrain_date": "2024-10-15",
        "deployment_environment": "production"
    }
}
```

### Output Data Package

```python
retraining_decision = {
    "retrain": True,
    "reasoning": "Performance has dropped by 5.56% which exceeds the 5% threshold. Additionally, significant drift detected in 3 features (feature_2, feature_5, feature_9) with drift score 0.15 > threshold 0.1. The combination of performance degradation and data drift indicates the model is no longer aligned with current data distribution. Given the high business impact and 10,000 daily predictions, retraining is recommended.",
    "urgency": "medium",
    "confidence": 0.9,
    "contributing_factors": [
        "Performance dropped by 5.56% (exceeds 5% threshold)",
        "Significant drift detected in 3 features (drift score: 0.15)",
        "Model age: 45 days (approaching typical refresh cycle)",
        "High prediction volume (10,000/day) magnifies impact"
    ],
    "recommended_actions": [
        "Retrain model with data from last 90 days",
        "Investigate root cause of drift in feature_2, feature_5, feature_9",
        "Consider feature engineering updates for drifted features",
        "Increase monitoring frequency to daily for next 30 days",
        "Validate retrained model on holdout set before deployment"
    ],
    "estimated_improvement": "5-10% accuracy gain expected, bringing performance back to baseline",
    "retraining_priority": "high"
}

state["retraining_decision"] = retraining_decision
state["retraining_triggered"] = True
state["retraining_reason"] = "Performance drop (5.56%) + data drift detected"
state["retraining_urgency"] = "medium"

# MLflow Logged:
# - Parameters: retraining_triggered=True, retraining_urgency=medium
# - Artifacts: agents/retraining_decision.json, prompt, response
```

---

## MLflow Logging Summary

### What Gets Logged at Each Stage

| Stage | Parameters | Metrics | Artifacts |
|-------|-----------|---------|-----------|
| **0. Prompt Analysis** | user_prompt, confidence_threshold | config_confidence | user_prompt.txt, extracted_config.json, agent_response.txt |
| **1. Data Loading** | data_path, n_rows, n_cols | data_size_mb | - |
| **2. Preprocessing** | outlier_detection_method, outlier_multiplier, missing_threshold, imputation_methods, encoding_methods, scaling_method, features_scaled | duplicates_removed, all_nan_removed, outliers_removed, total_rows_removed, original_rows, final_rows, columns_dropped, columns_imputed, remaining_nulls, features_added, original_features, final_features, final_samples, validation_passed | feature_statistics.json |
| **3. Split** | test_size, stratified, random_state | train_samples, test_samples | class_distribution.json |
| **4. Feature Selection** | selection_method, n_features_selected | n_features_dropped | importance.json, importance_plot.png |
| **5a. Agent 1** | agent1_model, agent1_temperature | - | algorithm_selection.json, prompt.txt, response.txt |
| **5b. Algorithm Training** | best_params (per algo) | cv_mean, test_acc, training_time (per algo) | cv_results.json, model (per algo) |
| **6. Agent 2** | best_model, selection_confidence | selection_confidence | model_selection.json, prompt.txt, response.txt |
| **7. Drift Detection** | drift_threshold, psi_threshold | drift_score, psi_max, drift_features_count | drift_analysis.json, drift_plot.png |
| **8. Performance Monitor** | performance_threshold | current_accuracy, baseline_accuracy, performance_drop | performance_comparison.json |
| **9. Agent 3** | retraining_triggered, retraining_urgency | - | retraining_decision.json, prompt.txt, response.txt |
| **10. Reporting** | - | - | reports.pdf, plots (various) |
| **11. Save Artifacts** | deployment_status | - | Final model in Model Registry |

---

## Summary

This enhanced data flow architecture provides:

✅ **Complete Data Flow** from raw CSV to deployed model
✅ **AI Decision Points** with structured input/output packages
✅ **MLflow Integration** at every stage
✅ **Parallel Algorithm Training** with individual result tracking
✅ **Monitoring Data Flows** for drift and performance
✅ **Comprehensive Logging** of all decisions and artifacts

The architecture ensures:
- **Traceability**: Every decision is logged with rationale
- **Reproducibility**: All parameters and random states logged
- **Observability**: Complete visibility into pipeline execution
- **Intelligent Optimization**: AI agents reduce unnecessary computation
- **Production Readiness**: Monitoring and retraining built-in
