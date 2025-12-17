# Sequence Diagrams - MLOps Pipeline Automation

## Document Information
- **Version**: 1.0
- **Date**: 2025-11-30
- **Purpose**: Detailed sequence diagrams for all major workflows

---

## Table of Contents
1. [Complete Pipeline Execution](#1-complete-pipeline-execution)
2. [AI Agent Decision Flow](#2-ai-agent-decision-flow)
3. [Human-in-the-Loop Review Workflow](#3-human-in-the-loop-review-workflow) **[NEW]**
4. [Model Training with GridSearchCV](#4-model-training-with-gridsearchcv)
5. [Monitoring and Retraining Flow](#5-monitoring-and-retraining-flow)
6. [MLflow Integration Flow](#6-mlflow-integration-flow)
7. [User Interaction Flow](#7-user-interaction-flow)

---

## 1. Complete Pipeline Execution

### 1.1 End-to-End Pipeline Flow

```
User          Streamlit        LangGraph          MLflow         DataModule      BedrockAgent
 │                │                │                │                │                │
 │  Start Pipeline │                │                │                │                │
 ├───────────────>│                │                │                │                │
 │                │  Initialize     │                │                │                │
 │                ├───────────────>│                │                │                │
 │                │                │  Create Exp    │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │  Return exp_id │                │                │
 │                │                │<───────────────┤                │                │
 │                │                │  Start Run     │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │  Return run_id │                │                │
 │                │                │<───────────────┤                │                │
 │                │                │                │                │                │
 │                │                │  load_data()   │                │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │   Return data  │                │
 │                │                │<───────────────────────────────┤                │
 │                │                │  Log params    │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │  Status Update │                │                │                │
 │                │<───────────────┤                │                │                │
 │                │                │                │                │                │
 │                │                │  preprocess()  │                │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │  Return cleaned│                │
 │                │                │<───────────────────────────────┤                │
 │                │                │  Log metrics   │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │  Status Update │                │                │                │
 │                │<───────────────┤                │                │                │
 │                │                │                │                │                │
 │                │                │  train_test_split()            │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │  Return splits │                │
 │                │                │<───────────────────────────────┤                │
 │                │                │                │                │                │
 │                │                │  feature_selection()           │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │Return features │                │
 │                │                │<───────────────────────────────┤                │
 │                │                │  Log artifacts │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │  Status Update │                │                │                │
 │                │<───────────────┤                │                │                │
 │                │                │                │                │                │
 │                │                │  agent_1_algorithm_selection() │                │
 │                │                ├───────────────────────────────────────────────>│
 │                │                │                │                │    Analyze    │
 │                │                │                │                │    context    │
 │                │                │                │                │   Return      │
 │                │                │                │                │   decision    │
 │                │                │<───────────────────────────────────────────────┤
 │                │                │  Log decision  │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │  Display Decision               │                │                │
 │                │<───────────────┤                │                │                │
 │                │                │                │                │                │
 │                │                │  train_random_forest()         │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │  Start child run│                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │  GridSearchCV  │                │
 │                │                │                │   (parallel)   │                │
 │                │                │                │  Return model  │                │
 │                │                │<───────────────────────────────┤                │
 │                │                │  Log model     │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │  End child run │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │                │  train_gradient_boosting()     │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │  (similar flow as RF)          │                │
 │                │                │                │                │                │
 │                │  Live Metrics  │                │                │                │
 │                │<───────────────┤                │                │                │
 │                │                │                │                │                │
 │                │                │  agent_2_model_selection()     │                │
 │                │                ├───────────────────────────────────────────────>│
 │                │                │                │                │   Compare &   │
 │                │                │                │                │   select best │
 │                │                │<───────────────────────────────────────────────┤
 │                │                │  Log decision  │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │  Display Best Model             │                │                │
 │                │<───────────────┤                │                │                │
 │                │                │                │                │                │
 │                │                │  evaluate_model()              │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │  Return metrics│                │
 │                │                │<───────────────────────────────┤                │
 │                │                │  Log metrics   │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │                │  detect_drift()                │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │  Return drift  │                │
 │                │                │<───────────────────────────────┤                │
 │                │                │                │                │                │
 │                │                │  monitor_performance()         │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │Return comparison│               │
 │                │                │<───────────────────────────────┤                │
 │                │                │                │                │                │
 │                │                │  agent_3_retraining_decision() │                │
 │                │                ├───────────────────────────────────────────────>│
 │                │                │                │                │   Decide if   │
 │                │                │                │                │   retrain     │
 │                │                │<───────────────────────────────────────────────┤
 │                │                │  Log decision  │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │  Display Retrain Decision       │                │                │
 │                │<───────────────┤                │                │                │
 │                │                │                │                │                │
 │                │                │  save_artifacts()              │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │                │                │
 │                │                │  Register model│                │                │
 │                │                ├───────────────>│                │                │
 │                │                │  Model version │                │                │
 │                │                │<───────────────┤                │                │
 │                │                │                │                │                │
 │                │                │  generate_report()             │                │
 │                │                ├───────────────────────────────>│                │
 │                │                │                │  Return report │                │
 │                │                │<───────────────────────────────┤                │
 │                │                │  End run       │                │                │
 │                │                ├───────────────>│                │                │
 │                │                │                │                │                │
 │                │  Pipeline Complete              │                │                │
 │                │<───────────────┤                │                │                │
 │  View Results  │                │                │                │                │
 │<───────────────┤                │                │                │                │
 │                │                │                │                │                │
```

---

## 2. AI Agent Decision Flow

### 2.1 Agent 1: Algorithm Selection

```
LangGraph      ContextBuilder    BedrockClient    AWS_Bedrock      MLflow
    │                │                │                │              │
    │  Extract state │                │                │              │
    ├───────────────>│                │                │              │
    │                │  Build context │                │              │
    │                ├───────────────>│                │              │
    │                │                │                │              │
    │                │  Context JSON  │                │              │
    │                │<───────────────┤                │              │
    │                │                │                │              │
    │  Load prompt   │                │                │              │
    │  template      │                │                │              │
    ├───────────────>│                │                │              │
    │                │                │                │              │
    │  Format prompt │                │                │              │
    │  with context  │                │                │              │
    │<───────────────┤                │                │              │
    │                │                │                │              │
    │  Invoke model  │                │                │              │
    ├───────────────────────────────>│                │              │
    │                │                │  API call      │              │
    │                │                ├───────────────>│              │
    │                │                │                │              │
    │                │                │  Process with  │              │
    │                │                │  Claude        │              │
    │                │                │                │              │
    │                │                │  Return response│             │
    │                │                │<───────────────┤              │
    │  Response text │                │                │              │
    │<───────────────────────────────┤                │              │
    │                │                │                │              │
    │  Parse JSON    │                │                │              │
    │  from response │                │                │              │
    ├───────────────>│                │                │              │
    │                │                │                │              │
    │  Validate schema                │                │              │
    │                │                │                │              │
    │  Decision dict │                │                │              │
    │<───────────────┤                │                │              │
    │                │                │                │              │
    │  Log to MLflow │                │                │              │
    ├────────────────────────────────────────────────────────────────>│
    │  - prompt.txt  │                │                │              │
    │  - response.txt│                │                │              │
    │  - decision.json                │                │              │
    │                │                │                │  Logged      │
    │<────────────────────────────────────────────────────────────────┤
    │                │                │                │              │
    │  Update state  │                │                │              │
    │  with decision │                │                │              │
    │                │                │                │              │
```

### 2.2 Agent Decision with Retry Logic

```
LangGraph      BedrockClient    AWS_Bedrock      RetryHandler
    │                │                │                │
    │  Invoke agent  │                │                │
    ├───────────────>│                │                │
    │                │  API call      │                │
    │                ├───────────────>│                │
    │                │                │                │
    │                │  Rate limit    │                │
    │                │  error (429)   │                │
    │                │<───────────────┤                │
    │                │                │                │
    │                │  Handle error  │                │
    │                ├───────────────────────────────>│
    │                │                │   Calculate    │
    │                │                │   backoff      │
    │                │                │   (2^n seconds)│
    │                │  Sleep 2s      │                │
    │                │<───────────────────────────────┤
    │                │                │                │
    │                │  Retry API call│                │
    │                ├───────────────>│                │
    │                │                │                │
    │                │  Rate limit    │                │
    │                │  error (429)   │                │
    │                │<───────────────┤                │
    │                │                │                │
    │                │  Sleep 4s      │                │
    │                │<───────────────────────────────┤
    │                │                │                │
    │                │  Retry API call│                │
    │                ├───────────────>│                │
    │                │                │                │
    │                │  Success (200) │                │
    │                │<───────────────┤                │
    │                │                │                │
    │  Response      │                │                │
    │<───────────────┤                │                │
    │                │                │                │
```

---

## 3. Human-in-the-Loop Review Workflow (Algorithm-Aware)

### 3.1 Algorithm Category Prediction (Agent 1A)

```
LangGraph    DataProfiler  Agent1A         BedrockClient    AWS_Bedrock    PostgreSQL    MLflow
    │              │           │                 │                │              │           │
    │ After load_data node     │                 │                │              │           │
    │ Execute      │           │                 │                │              │           │
    │ algorithm_   │           │                 │                │              │           │
    │ category_    │           │                 │                │              │           │
    │ prediction() │           │                 │                │              │           │
    ├─────────────>│           │                 │                │              │           │
    │              │           │                 │                │              │           │
    │              │ Build data profile           │                │              │           │
    │              │ - n_samples                  │                │              │           │
    │              │ - n_features                 │                │              │           │
    │              │ - target_type                │                │              │           │
    │              │ - feature_types              │                │              │           │
    │              │ - class_distribution         │                │              │           │
    │              │ - dataset_size_mb            │                │              │           │
    │              │ - data_characteristics       │                │              │           │
    │              │   (missing%, outlier%,       │                │              │           │
    │              │    duplicate%, correlation)  │                │              │           │
    │              │           │                 │                │              │           │
    │              │ data_profile                 │                │              │           │
    │              ├──────────>│                 │                │              │           │
    │              │           │                 │                │              │           │
    │              │           │ Build context   │                │              │           │
    │              │           │ for Bedrock     │                │              │           │
    │              │           │                 │                │              │           │
    │              │           │ Invoke Bedrock  │                │              │           │
    │              │           ├────────────────>│                │              │           │
    │              │           │                 │ API call       │              │           │
    │              │           │                 ├───────────────>│              │           │
    │              │           │                 │                │              │           │
    │              │           │                 │ Process with   │              │           │
    │              │           │                 │ Claude         │              │           │
    │              │           │                 │ (temp=0.2)     │              │           │
    │              │           │                 │                │              │           │
    │              │           │                 │ Predict:       │              │           │
    │              │           │                 │ algorithm_     │              │           │
    │              │           │                 │ category       │              │           │
    │              │           │                 │<───────────────┤              │           │
    │              │           │ Response        │                │              │           │
    │              │           │<────────────────┤                │              │           │
    │              │           │                 │                │              │           │
    │              │           │ Parse JSON:     │                │              │           │
    │              │           │ {               │                │              │           │
    │              │           │   "algorithm_category": "tree_models",          │           │
    │              │           │   "confidence": 0.87,            │              │           │
    │              │           │   "reasoning": "...",            │              │           │
    │              │           │   "recommended_algorithms": [    │              │           │
    │              │           │     "RandomForest", "XGBoost", "GradientBoosting"│         │
    │              │           │   ],                             │              │           │
    │              │           │   "preprocessing_priorities": {  │              │           │
    │              │           │     "clean_data": "optional",    │              │           │
    │              │           │     "handle_missing": "required",│              │           │
    │              │           │     "encode_features": "required",│             │           │
    │              │           │     "scale_features": "optional" │              │           │
    │              │           │   },                             │              │           │
    │              │           │   "algorithm_requirements": {    │              │           │
    │              │           │     "scaling_required": false,   │              │           │
    │              │           │     "outlier_sensitive": false,  │              │           │
    │              │           │     "handles_missing": true,     │              │           │
    │              │           │     "categorical_encoding_preference": "target"  │           │
    │              │           │   }                              │              │           │
    │              │           │ }                                │              │           │
    │              │           │                 │                │              │           │
    │              │ decision  │                 │                │              │           │
    │<─────────────────────────┤                 │                │              │           │
    │              │           │                 │                │              │           │
    │ Store prediction         │                 │                │              │           │
    ├──────────────────────────────────────────────────────────────────────────────>│
    │ (algorithm_category, confidence, requirements, prompt, response)│  Stored    │
    │<──────────────────────────────────────────────────────────────────────────────┤
    │              │           │                 │                │              │           │
    │ Log to MLflow            │                 │                │              │           │
    ├───────────────────────────────────────────────────────────────────────────────────────>│
    │ - algorithm_category=tree_models           │                │              │  Logged   │
    │ - algorithm_confidence=0.87                │                │              │           │
    │ - agent_1a_prompt.txt                      │                │              │           │
    │ - agent_1a_response.txt                    │                │              │           │
    │<───────────────────────────────────────────────────────────────────────────────────────┤
    │              │           │                 │                │              │           │
    │ Update state:│           │                 │                │              │           │
    │ - algorithm_category: "tree_models"        │                │              │           │
    │ - algorithm_confidence: 0.87               │                │              │           │
    │ - recommended_algorithms: [...]            │                │              │           │
    │ - algorithm_requirements: {...}            │                │              │           │
    │              │           │                 │                │              │           │
```

### 3.2 Preprocessing Question Generation (Agent 1B)

```
LangGraph    Agent1B      BedrockClient    AWS_Bedrock    PostgreSQL    MLflow
    │              │             │                │              │           │
    │ Execute      │             │                │              │           │
    │ review_      │             │                │              │           │
    │ config()     │             │                │              │           │
    ├─────────────>│             │                │              │           │
    │              │             │                │              │           │
    │              │ Build context for question generation      │           │
    │              │ - algorithm_category (from Agent 1A)       │           │
    │              │ - algorithm_confidence                      │           │
    │              │ - algorithm_requirements                    │           │
    │              │ - data_profile (from load_data)            │           │
    │              │   - n_samples, n_features                  │           │
    │              │   - missing_values: {col: count}           │           │
    │              │   - duplicate_rows                         │           │
    │              │   - categorical_columns                    │           │
    │              │   - high_cardinality_columns               │           │
    │              │   - outlier_summary: {col: {Q1, Q3, IQR}} │           │
    │              │ - preprocessing_steps: [                   │           │
    │              │     "clean_data", "handle_missing",        │           │
    │              │     "encode_features", "scale_features"    │           │
    │              │   ]                                        │           │
    │              │             │                │              │           │
    │              │ Invoke Bedrock              │              │           │
    │              ├────────────>│                │              │           │
    │              │             │ API call       │              │           │
    │              │             ├───────────────>│              │           │
    │              │             │                │              │           │
    │              │             │ Process with   │              │           │
    │              │             │ Claude         │              │           │
    │              │             │ (temp=0.3)     │              │           │
    │              │             │                │              │           │
    │              │             │ Generate       │              │           │
    │              │             │ algorithm-aware│              │           │
    │              │             │ questions      │              │           │
    │              │             │ (4-20 total)   │              │           │
    │              │             │<───────────────┤              │           │
    │              │ Response    │                │              │           │
    │              │<────────────┤                │              │           │
    │              │             │                │              │           │
    │              │ Parse JSON: │                │              │           │
    │              │ {           │                │              │           │
    │              │   "questions": [             │              │           │
    │              │     {                        │              │           │
    │              │       "question_id": "clean_q1",            │           │
    │              │       "preprocessing_step": "clean_data",   │           │
    │              │       "question_text": "How should we handle outliers for tree models?",│
    │              │       "question_type": "multiple_choice",    │           │
    │              │       "priority": "low",     │              │           │
    │              │       "context": "Tree models are robust to outliers...",│             │
    │              │       "options": [            │              │           │
    │              │         {                     │              │           │
    │              │           "value": "iqr_method",             │           │
    │              │           "label": "IQR Method",             │           │
    │              │           "recommended": false,              │           │
    │              │           "reasoning": "Removes extreme outliers",      │           │
    │              │           "algorithm_suitability": "acceptable"│        │           │
    │              │         },                    │              │           │
    │              │         {                     │              │           │
    │              │           "value": "none",    │              │           │
    │              │           "label": "No Outlier Removal",     │           │
    │              │           "recommended": true,               │           │
    │              │           "reasoning": "Tree models naturally robust",  │           │
    │              │           "algorithm_suitability": "excellent"│         │           │
    │              │         }                     │              │           │
    │              │       ],                      │              │           │
    │              │       "parameters": []        │              │           │
    │              │     },                        │              │           │
    │              │     {                         │              │           │
    │              │       "question_id": "missing_q1",          │           │
    │              │       "preprocessing_step": "handle_missing",│          │
    │              │       "question_text": "Imputation strategy for 15% missing values?",│
    │              │       "question_type": "multiple_choice",    │           │
    │              │       "priority": "medium",  │              │           │
    │              │       "options": [            │              │           │
    │              │         {"value": "simple_imputation", "label": "Mean/Median", "recommended": true},│
    │              │         {"value": "knn_imputation", "label": "KNN Imputation", "recommended": false},│
    │              │         {"value": "drop_rows", "label": "Drop Rows", "recommended": false}│
    │              │       ],                      │              │           │
    │              │       "parameters": [         │              │           │
    │              │         {                     │              │           │
    │              │           "param_name": "imputation_strategy",│         │           │
    │              │           "param_type": "string",            │           │
    │              │           "default": "median",               │           │
    │              │           "range": ["mean", "median", "mode"],│          │           │
    │              │           "description": "Statistical method"│           │           │
    │              │         }                     │              │           │
    │              │       ]                       │              │           │
    │              │     },                        │              │           │
    │              │     {                         │              │           │
    │              │       "question_id": "encode_q1",            │           │
    │              │       "preprocessing_step": "encode_features",│          │
    │              │       "question_text": "Encoding for high cardinality columns?",│     │
    │              │       "priority": "high",    │              │           │
    │              │       "options": [            │              │           │
    │              │         {"value": "target_encoding", "recommended": true},│          │
    │              │         {"value": "frequency_encoding", "recommended": false},│      │
    │              │         {"value": "one_hot", "recommended": false}│       │           │
    │              │       ]                       │              │           │
    │              │     },                        │              │           │
    │              │     {                         │              │           │
    │              │       "question_id": "scale_q1",             │           │
    │              │       "preprocessing_step": "scale_features",│           │
    │              │       "question_text": "Apply feature scaling for tree models?",│    │
    │              │       "priority": "low",     │              │           │
    │              │       "options": [            │              │           │
    │              │         {"value": "none", "label": "Skip Scaling", "recommended": true,│
    │              │          "reasoning": "Tree models are scale-invariant"},│             │
    │              │         {"value": "standard_scaler", "recommended": false}│            │
    │              │       ]                       │              │           │
    │              │     }                         │              │           │
    │              │   ],  # 4 questions total (1 per step)       │           │
    │              │   "preprocessing_recommendations": {         │           │
    │              │     "clean_data_technique": "none",          │           │
    │              │     "handle_missing_technique": "simple_imputation",│    │           │
    │              │     "encode_technique": "target_encoding",   │           │
    │              │     "scale_technique": "none"                │           │
    │              │   },                          │              │           │
    │              │   "algorithm_context": "Tree models are robust...",│     │           │
    │              │   "question_count_by_step": {                │           │
    │              │     "clean_data": 1,         │              │           │
    │              │     "handle_missing": 1,     │              │           │
    │              │     "encode_features": 1,    │              │           │
    │              │     "scale_features": 1      │              │           │
    │              │   }                           │              │           │
    │              │ }                             │              │           │
    │              │             │                │              │           │
    │ questions    │             │                │              │           │
    │<─────────────┤             │                │              │           │
    │              │             │                │              │           │
    │ Store review session       │                │              │           │
    ├──────────────────────────────────────────────────────────>│           │
    │ (algorithm_category, algorithm_confidence, questions,│     │           │
    │  preprocessing_recommendations, prompt, response)    │  Stored│       │
    │<──────────────────────────────────────────────────────────┤           │
    │              │             │                │              │           │
    │ Log questions to MLflow    │                │              │           │
    ├────────────────────────────────────────────────────────────────────────>│
    │ - review_session.json (questions with technique options)  │  Logged   │
    │ - agent_1b_prompt.txt                       │              │           │
    │ - agent_1b_response.txt                     │              │           │
    │<────────────────────────────────────────────────────────────────────────┤
    │              │             │                │              │           │
    │ Update state:│             │                │              │           │
    │ - review_questions: [4-20 questions]        │              │           │
    │ - question_count_by_step: {...}             │              │           │
    │ - preprocessing_recommendations: {...}      │              │           │
    │ - status: "awaiting_review"                 │              │           │
    │              │             │                │              │           │
    │ [INTERRUPTION TRIGGERED]   │                │              │           │
    │ workflow.interrupt_after(["review_config"]) │              │           │
    │              │             │                │              │           │
```

### 3.3 Complete Algorithm-Aware Review Flow with LangGraph Interruption

```
User        Frontend      API            LangGraph       Agent1A/1B    PostgreSQL    MLflow
 │              │           │                 │                │              │           │
 │ Start        │           │                 │                │              │           │
 │ Pipeline     │           │                 │                │              │           │
 ├─────────────>│           │                 │                │              │           │
 │              │ POST /api/pipeline/start    │                │              │           │
 │              ├──────────>│                 │                │              │           │
 │              │           │ Create state    │                │              │           │
 │              │           ├────────────────>│                │              │           │
 │              │           │                 │ Execute        │              │           │
 │              │           │                 │ analyze_prompt │              │           │
 │              │           │                 │ (Agent 0)      │              │           │
 │              │           │                 │                │              │           │
 │              │           │                 │ Execute        │              │           │
 │              │           │                 │ load_data      │              │           │
 │              │           │                 │ + Start MLflow │              │           │
 │              │           │                 ├────────────────────────────────────────────>│
 │              │           │                 │                │              │  Run ID   │
 │              │           │                 │<────────────────────────────────────────────┤
 │              │           │                 │                │              │           │
 │              │           │                 │ Execute algorithm_category_prediction      │
 │              │           │                 │ (Agent 1A) - See Section 3.1              │
 │              │           │                 ├───────────────>│              │           │
 │              │           │                 │                │              │           │
 │              │           │                 │ prediction:    │              │           │
 │              │           │                 │ - algorithm_category="tree_models"        │
 │              │           │                 │ - confidence=0.87             │           │
 │              │           │                 │ - algorithm_requirements      │           │
 │              │           │                 │<───────────────┤              │           │
 │              │           │                 │                │              │           │
 │              │           │ Status: "predicting_algorithm"  │              │           │
 │              │<──────────┤                 │                │              │           │
 │              │           │                 │                │              │           │
 │              │           │                 │ Execute review_config         │           │
 │              │           │                 │ (Agent 1B) - See Section 3.2  │           │
 │              │           │                 ├───────────────>│              │           │
 │              │           │                 │                │              │           │
 │              │           │                 │                │ Generate 4-20│           │
 │              │           │                 │                │ algorithm-   │           │
 │              │           │                 │                │ aware        │           │
 │              │           │                 │                │ questions    │           │
 │              │           │                 │<───────────────┤              │           │
 │              │           │                 │ questions with │              │           │
 │              │           │                 │ technique      │              │           │
 │              │           │                 │ options        │              │           │
 │              │           │                 │                │              │           │
 │              │           │                 │ Store review session          │           │
 │              │           │                 ├───────────────────────────────>│           │
 │              │           │                 │ (algorithm_category, questions,│          │
 │              │           │                 │  technique options, prompt,    │          │
 │              │           │                 │  response)                     │  Stored  │
 │              │           │                 │<───────────────────────────────┤          │
 │              │           │                 │                │              │           │
 │              │           │                 │ Log to MLflow  │              │           │
 │              │           │                 ├────────────────────────────────────────────>│
 │              │           │                 │ - review_session.json          │  Logged   │
 │              │           │                 │ - agent_1a_prediction.json     │           │
 │              │           │                 │ - agent_1b_questions.json      │           │
 │              │           │                 │<────────────────────────────────────────────┤
 │              │           │                 │                │              │           │
 │              │           │                 │ Update state:  │              │           │
 │              │           │                 │ - algorithm_category="tree_models"        │
 │              │           │                 │ - algorithm_confidence=0.87   │           │
 │              │           │                 │ - review_questions (4-20)     │           │
 │              │           │                 │ - question_count_by_step      │           │
 │              │           │                 │ - preprocessing_recommendations│          │
 │              │           │                 │ - status: "awaiting_review"   │           │
 │              │           │                 │                │              │           │
 │              │           │                 │ [INTERRUPTION TRIGGERED]      │           │
 │              │           │                 │ workflow.interrupt_after([    │           │
 │              │           │                 │   "review_config"             │           │
 │              │           │                 │ ])                            │           │
 │              │           │                 │                │              │           │
 │              │           │ Return status   │                │              │           │
 │              │           │ "awaiting_review"               │              │           │
 │              │           │ + algorithm_category            │              │           │
 │              │           │ + question_count                │              │           │
 │              │<──────────┤                 │                │              │           │
 │              │           │                 │                │              │           │
 │ Display      │           │                 │                │              │           │
 │ Enhanced     │           │                 │                │              │           │
 │ ReviewForm   │           │                 │                │              │           │
 │              │           │                 │                │              │           │
 │ [HUMAN REVIEW - Pipeline Paused - Algorithm-Aware UI]      │              │           │
 │              │           │                 │                │              │           │
 │ ╔══════════════════════════════════════════════════════════╗              │           │
 │ ║ 🎯 Algorithm Category Banner:                            ║              │           │
 │ ║    "Predicted: Tree Models (confidence 87%)"             ║              │           │
 │ ║    "Recommended: RandomForest, XGBoost, GradientBoosting"║              │           │
 │ ╚══════════════════════════════════════════════════════════╝              │           │
 │              │           │                 │                │              │           │
 │ ┌────────────────────────────────────────────────────────┐ │              │           │
 │ │ 📑 Tabbed Interface:                                   │ │              │           │
 │ │    [Clean Data] [Handle Missing] [Encode] [Scale]     │ │              │           │
 │ └────────────────────────────────────────────────────────┘ │              │           │
 │              │           │                 │                │              │           │
 │ Review 4-20  │           │                 │                │              │           │
 │ Algorithm-   │           │                 │                │              │           │
 │ Aware        │           │                 │                │              │           │
 │ Questions:   │           │                 │                │              │           │
 │              │           │                 │                │              │           │
 │ Clean Data Tab:                            │                │              │           │
 │ ❓ Q1: "How should we handle outliers for tree models?"    │              │           │
 │    🔘 IQR Method (acceptable for tree models)              │              │           │
 │    🔘 Z-Score Method (acceptable)           │              │              │           │
 │    ✅ No Outlier Removal (RECOMMENDED - excellent)         │              │           │
 │       💡 "Tree models are naturally robust to outliers"    │              │           │
 │       Priority: LOW                         │              │              │           │
 │              │           │                 │                │              │           │
 │ Handle Missing Tab:                        │                │              │           │
 │ ❓ Q2: "Imputation strategy for 15% missing values?"       │              │           │
 │    ✅ Mean/Median Imputation (RECOMMENDED) │              │              │           │
 │       🎚️ Slider: Strategy [Mean | Median | Mode]          │              │           │
 │       💡 "Tree models handle missing well, simple works"   │              │           │
 │       Priority: MEDIUM                      │              │              │           │
 │    🔘 KNN Imputation (good)                 │              │              │           │
 │       🎚️ Slider: Neighbors [3-10]          │              │              │           │
 │    🔘 Drop Rows (poor - data loss)          │              │              │           │
 │              │           │                 │                │              │           │
 │ Encode Features Tab:                       │                │              │           │
 │ ❓ Q3: "Encoding for high cardinality columns?"            │              │           │
 │    ✅ Target Encoding (RECOMMENDED - excellent)            │              │           │
 │       🎚️ Slider: Smoothing [0.0-5.0]       │              │              │           │
 │       💡 "Best for tree models with high cardinality"      │              │           │
 │       Priority: HIGH                        │              │              │           │
 │    🔘 Frequency Encoding (good)             │              │              │           │
 │    🔘 One-Hot Encoding (poor - creates many features)      │              │           │
 │              │           │                 │                │              │           │
 │ Scale Features Tab:                        │                │              │           │
 │ ❓ Q4: "Apply feature scaling for tree models?"            │              │           │
 │    🔘 StandardScaler (poor - unnecessary)   │              │              │           │
 │    🔘 MinMaxScaler (poor - unnecessary)     │              │              │           │
 │    ✅ Skip Scaling (RECOMMENDED - excellent)│              │              │           │
 │       💡 "Tree models are scale-invariant"  │              │              │           │
 │       Priority: LOW                         │              │              │           │
 │              │           │                 │                │              │           │
 │ User Selects:│           │                 │                │              │           │
 │ - clean_data_technique: "none"              │              │              │           │
 │ - handle_missing_technique: "simple_imputation"            │              │           │
 │   + imputation_strategy: "median"           │              │              │           │
 │ - encode_technique: "target_encoding"       │              │              │           │
 │   + target_smoothing: 1.0                   │              │              │           │
 │ - scale_technique: "none"                   │              │              │           │
 │              │           │                 │                │              │           │
 │ ✅ Approve   │           │                 │                │              │           │
 │ & Continue   │           │                 │                │              │           │
 ├─────────────>│           │                 │                │              │           │
 │              │ POST /api/pipeline/review/{id}/submit       │              │           │
 │              ├──────────>│                 │                │              │           │
 │              │           │ Validate answers                │              │           │
 │              │           │ (4-20 questions)│                │              │           │
 │              │           │ Validate technique selections   │              │           │
 │              │           │ Validate parameters             │              │           │
 │              │           │                 │                │              │           │
 │              │           │ Update review session            │              │           │
 │              │           ├──────────────────────────────────>│              │           │
 │              │           │ (algorithm_category, technique_selections,      │           │
 │              │           │  parameters, approved=true)      │  Updated     │           │
 │              │           │<──────────────────────────────────┤              │           │
 │              │           │                 │                │              │           │
 │              │           │ Update state:   │                │              │           │
 │              │           │ - review_approved: true          │              │           │
 │              │           │ - review_answers (technique selections)         │           │
 │              │           │ - technique_parameters           │              │           │
 │              │           │ - status: "review_approved"      │              │           │
 │              │           │                 │                │              │           │
 │              │ Success   │                 │                │              │           │
 │              │<──────────┤                 │                │              │           │
 │              │           │                 │                │              │           │
 │              │ POST /api/pipeline/{id}/continue            │              │           │
 │              ├──────────>│                 │                │              │           │
 │              │           │ Verify approved │                │              │           │
 │              │           │                 │                │              │           │
 │              │           │ Resume MLflow run                │              │           │
 │              │           ├────────────────────────────────────────────────────────────>│
 │              │           │ mlflow.start_run(run_id)        │              │  Resumed  │
 │              │           │<────────────────────────────────────────────────────────────┤
 │              │           │                 │                │              │           │
 │              │           │ Execute technique-based preprocessing nodes    │           │
 │              │           │                 │                │              │           │
 │              │           │ clean_data_node()               │              │           │
 │              │           │ ├──────────────>│                │              │           │
 │              │           │ │ Read: review_answers["clean_data_technique"]│           │
 │              │           │ │ Execute: technique="none"      │              │           │
 │              │           │ │ (Skip outlier removal - tree models robust) │           │
 │              │           │ │ Log to MLflow:                 │              │           │
 │              │           │ │ - clean_data_technique="none"  │              │           │
 │              │           │ │ - algorithm_category="tree_models"│          │           │
 │              │           │ ├────────────────────────────────────────────────────────────>│
 │              │           │ │<────────────────────────────────────────────────────────────┤
 │              │           │                 │                │              │           │
 │              │           │ handle_missing_node()            │              │           │
 │              │           │ ├──────────────>│                │              │           │
 │              │           │ │ Read: review_answers["handle_missing_technique"]│        │
 │              │           │ │ Execute: technique="simple_imputation"│       │           │
 │              │           │ │          strategy="median"      │              │           │
 │              │           │ │ Impute missing values with median│            │           │
 │              │           │ │ Log to MLflow:                 │              │           │
 │              │           │ │ - handle_missing_technique="simple_imputation"│           │
 │              │           │ │ - imputation_strategy="median"  │              │           │
 │              │           │ │ - missing_values_imputed=340    │              │           │
 │              │           │ ├────────────────────────────────────────────────────────────>│
 │              │           │ │<────────────────────────────────────────────────────────────┤
 │              │           │                 │                │              │           │
 │              │           │ encode_features_node()           │              │           │
 │              │           │ ├──────────────>│                │              │           │
 │              │           │ │ Read: review_answers["encode_technique"]│    │           │
 │              │           │ │ Execute: technique="target_encoding"│         │           │
 │              │           │ │          smoothing=1.0          │              │           │
 │              │           │ │ Encode high cardinality with target│          │           │
 │              │           │ │ Log to MLflow:                 │              │           │
 │              │           │ │ - encode_technique="target_encoding"│         │           │
 │              │           │ │ - target_smoothing=1.0          │              │           │
 │              │           │ │ - high_cardinality_columns_encoded=2│         │           │
 │              │           │ ├────────────────────────────────────────────────────────────>│
 │              │           │ │<────────────────────────────────────────────────────────────┤
 │              │           │                 │                │              │           │
 │              │           │ scale_features_node()            │              │           │
 │              │           │ ├──────────────>│                │              │           │
 │              │           │ │ Read: review_answers["scale_technique"]│     │           │
 │              │           │ │ Execute: technique="none"      │              │           │
 │              │           │ │ (Skip scaling - tree models scale-invariant) │           │
 │              │           │ │ Log to MLflow:                 │              │           │
 │              │           │ │ - scale_technique="none"        │              │           │
 │              │           │ │ - algorithm_category="tree_models"│           │           │
 │              │           │ │ - feature_statistics.json       │              │           │
 │              │           │ ├────────────────────────────────────────────────────────────>│
 │              │           │ │<────────────────────────────────────────────────────────────┤
 │              │           │                 │                │              │  Logged   │
 │              │           │                 │                │              │           │
 │              │           │ Update status:  │                │              │           │
 │              │           │ "preprocessing_completed"       │              │           │
 │              │           │                 │                │              │           │
 │              │           │ End MLflow run  │                │              │           │
 │              │           ├────────────────────────────────────────────────────────────>│
 │              │           │                 │                │              │  Ended    │
 │              │           │<────────────────────────────────────────────────────────────┤
 │              │           │                 │                │              │           │
 │              │ Success   │                 │                │              │           │
 │              │<──────────┤                 │                │              │           │
 │              │           │                 │                │              │           │
 │ Display      │           │                 │                │              │           │
 │ Completed    │           │                 │                │              │           │
 │ with         │           │                 │                │              │           │
 │ Technique    │           │                 │                │              │           │
 │ Summary      │           │                 │                │              │           │
 │<─────────────┤           │                 │                │              │           │
 │              │           │                 │                │              │           │
```

### 3.4 Review Rejection Flow

```
User        Frontend      API            LangGraph       PostgreSQL
 │              │           │                 │                │
 │ [At review step]          │                 │                │
 │              │           │                 │                │
 │ ❌ Reject    │           │                 │                │
 ├─────────────>│           │                 │                │
 │              │ POST /api/pipeline/review/{id}/submit       │
 │              ├──────────>│                 │                │
 │              │           │ Update review session            │
 │              │           ├──────────────────────────────────>│
 │              │           │ (approved=false)│              Updated
 │              │           │<──────────────────────────────────┤
 │              │           │                 │                │
 │              │           │ Update state:   │                │
 │              │           │ - review_approved: false         │
 │              │           │ - status: "review_rejected"     │
 │              │           │                 │                │
 │              │ Success   │                 │                │
 │              │ (rejected)│                 │                │
 │              │<──────────┤                 │                │
 │              │           │                 │                │
 │ Display      │           │                 │                │
 │ Rejection    │           │                 │                │
 │ Message      │           │                 │                │
 │<─────────────┤           │                 │                │
 │              │           │                 │                │
 │ [Pipeline terminated - No preprocessing executed]           │
 │              │           │                 │                │
```

### 3.5 Key Points - Algorithm-Aware HITL System

**Two-Agent Architecture:**
- **Agent 1A (Algorithm Category Predictor)**: Analyzes dataset characteristics and predicts optimal algorithm category (linear_models, tree_models, neural_networks, ensemble, time_series) with confidence score and algorithm-specific requirements
- **Agent 1B (Preprocessing Question Generator)**: Generates 4-20 algorithm-aware questions (1-5 per preprocessing step) with multiple technique options, rankings, and parameters tailored to the predicted algorithm category

**LangGraph Interruption Mechanism:**
- `workflow.interrupt_after(["review_config"])` pauses execution after Agent 1A and Agent 1B complete
- State is persisted in `active_pipelines` dictionary with algorithm_category, algorithm_confidence, and review_questions
- Frontend polls for status and detects `"awaiting_review"` with algorithm context
- Pipeline resumes only after explicit `/continue` API call with user's technique selections

**Storage Strategy:**
- **PostgreSQL**: Permanent storage of review sessions with algorithm_category, algorithm_confidence, technique_selections, and parameters (audit trail)
- **MLflow**: Artifacts (agent_1a_prediction.json, agent_1b_questions.json, review_session.json, prompts, responses)
- **In-memory state**: Active pipeline state for real-time frontend updates with algorithm context

**Algorithm-Aware UI Components:**
- **Algorithm Category Banner**: Displays predicted category with confidence and recommended algorithms
- **Tabbed Interface**: Organizes questions by preprocessing step (Clean Data, Handle Missing, Encode, Scale)
- **Technique Options**: Multiple ranked techniques with algorithm_suitability ratings (excellent, good, acceptable, poor)
- **Parameter Controls**: Dynamic sliders/inputs for technique-specific parameters
- **Priority Badges**: HIGH/MEDIUM/LOW based on algorithm requirements

**Technique-Based Preprocessing Execution:**
- Each preprocessing node reads user-selected techniques from `review_answers`
- Nodes execute specific techniques with user-provided parameters
- Example: For tree_models, clean_data_node executes technique="none" (skip outlier removal), encode_features_node executes technique="target_encoding" with smoothing=1.0
- All technique selections and parameters logged to MLflow with algorithm_category context

**MLflow Run Management:**
- Run is started in `load_data_node`
- Agent 1A prediction logged with algorithm_category, confidence, preprocessing_priorities
- Agent 1B questions logged with technique options and recommendations
- Run is implicitly ended after `review_config_node` (interruption)
- Run is resumed in `/continue` endpoint before preprocessing with technique selections
- Each preprocessing node logs selected technique, parameters, and metrics
- Run is ended after preprocessing completes or fails

**Error Handling:**
- If Agent 1A fails: Return error, fallback to generic questions, no interruption
- If Agent 1B fails: Return error, use preprocessing recommendations from Agent 1A, no interruption
- If user rejects: Pipeline terminates, status="review_rejected", algorithm prediction saved for analysis
- If preprocessing node fails with selected technique: Log error with technique details, MLflow run ends with status="FAILED"

---

## 4. Model Training with GridSearchCV

### 4.1 Single Algorithm Training Flow

```
LangGraph    TrainingNode    GridSearchCV    Estimator    MLflow       CrossVal
    │              │                │              │           │             │
    │  Call node   │                │              │           │             │
    ├─────────────>│                │              │           │             │
    │              │  Start child run              │           │             │
    │              ├───────────────────────────────────────────>│             │
    │              │                │              │  child_run_id            │
    │              │<───────────────────────────────────────────┤             │
    │              │                │              │           │             │
    │              │  Get param_grid│              │           │             │
    │              │  from agent    │              │           │             │
    │              │                │              │           │             │
    │              │  Initialize    │              │           │             │
    │              │  GridSearchCV  │              │           │             │
    │              ├───────────────>│              │           │             │
    │              │                │              │           │             │
    │              │  Fit(X, y)     │              │           │             │
    │              ├───────────────>│              │           │             │
    │              │                │              │           │             │
    │              │                │  For each param combo    │             │
    │              │                │              │           │             │
    │              │                │  Create estimator        │             │
    │              │                ├─────────────>│           │             │
    │              │                │              │           │             │
    │              │                │  Cross-validate          │             │
    │              │                ├─────────────────────────────────────────>
    │              │                │              │           │  Fold 1     │
    │              │                │              │           │  Train/Val  │
    │              │                │              │  fit()    │             │
    │              │                │              │<──────────┤             │
    │              │                │              │  predict()│             │
    │              │                │              │<──────────┤             │
    │              │                │              │  score    │             │
    │              │                │              ├──────────>│             │
    │              │                │              │           │  Fold 2     │
    │              │                │              │  fit()    │             │
    │              │                │              │<──────────┤             │
    │              │                │              │  predict()│             │
    │              │                │              │<──────────┤             │
    │              │                │              │  score    │             │
    │              │                │              ├──────────>│             │
    │              │                │              │           │  ... Fold 5 │
    │              │                │              │           │             │
    │              │                │              │  CV scores│             │
    │              │                │<─────────────────────────────────────────
    │              │                │              │           │             │
    │              │                │  Next param combo        │             │
    │              │                │  (repeat for all combos) │             │
    │              │                │              │           │             │
    │              │  GridSearch    │              │           │             │
    │              │  complete      │              │           │             │
    │              │<───────────────┤              │           │             │
    │              │                │              │           │             │
    │              │  Get best      │              │           │             │
    │              │  estimator     │              │           │             │
    │              ├───────────────>│              │           │             │
    │              │  best_model    │              │           │             │
    │              │<───────────────┤              │           │             │
    │              │                │              │           │             │
    │              │  Evaluate on   │              │           │             │
    │              │  test set      │              │           │             │
    │              │                │              │  predict()│             │
    │              │                │              │<──────────┤             │
    │              │                │              │           │             │
    │              │  Calculate metrics            │           │             │
    │              │  (accuracy, f1, etc.)         │           │             │
    │              │                │              │           │             │
    │              │  Log to MLflow │              │           │             │
    │              ├───────────────────────────────────────────>│             │
    │              │  - best_params │              │           │             │
    │              │  - cv_mean     │              │           │             │
    │              │  - cv_std      │              │           │             │
    │              │  - test_accuracy│             │           │             │
    │              │  - test_f1     │              │           │             │
    │              │  - training_time│             │           │             │
    │              │  - model artifact│            │           │             │
    │              │                │              │  Logged   │             │
    │              │<───────────────────────────────────────────┤             │
    │              │                │              │           │             │
    │              │  End child run │              │           │             │
    │              ├───────────────────────────────────────────>│             │
    │              │                │              │           │             │
    │              │  Return result │              │           │             │
    │<─────────────┤                │              │           │             │
    │              │                │              │           │             │
```

### 4.2 Parallel Algorithm Training

```
LangGraph    Train_RF_Node    Train_GB_Node    Train_LR_Node    MLflow
    │              │                │                │              │
    │  Parallel    │                │                │              │
    │  execution   │                │                │              │
    │              │                │                │              │
    ├─────────────>│                │                │              │
    ├──────────────────────────────>│                │              │
    ├───────────────────────────────────────────────>│              │
    │              │                │                │              │
    │              │  Start child   │                │              │
    │              ├───────────────────────────────────────────────>│
    │              │                │  Start child   │              │
    │              │                ├───────────────────────────────>│
    │              │                │                │  Start child  │
    │              │                │                ├──────────────>│
    │              │                │                │              │
    │              │  GridSearchCV  │                │              │
    │              │  (in progress) │                │              │
    │              │                │  GridSearchCV  │              │
    │              │                │  (in progress) │              │
    │              │                │                │  GridSearchCV│
    │              │                │                │  (in progress)│
    │              │                │                │              │
    │              │  Complete      │                │              │
    │              │  Log model     │                │              │
    │              ├───────────────────────────────────────────────>│
    │              │  Complete      │                │              │
    │              │                ├───────────────────────────────>│
    │              │                │                │  Complete    │
    │              │                │                ├──────────────>│
    │              │                │                │              │
    │  RF result   │                │                │              │
    │<─────────────┤                │                │              │
    │              │  GB result     │                │              │
    │<──────────────────────────────┤                │              │
    │              │                │  LR result     │              │
    │<───────────────────────────────────────────────┤              │
    │              │                │                │              │
    │  Aggregate   │                │                │              │
    │  results     │                │                │              │
    │              │                │                │              │
```

---

## 4. Monitoring and Retraining Flow

### 4.1 Drift Detection Sequence

```
LangGraph    DriftDetector    StatisticalTests    MLflow
    │              │                │                │
    │  detect_drift()               │                │
    ├─────────────>│                │                │
    │              │                │                │
    │              │  Load reference│                │
    │              │  data (train)  │                │
    │              │                │                │
    │              │  Load current  │                │
    │              │  data (test)   │                │
    │              │                │                │
    │              │  For each feature               │
    │              │                │                │
    │              │  Check if numerical            │
    │              │  ├─ Yes: KS test│                │
    │              │  ├───────────────>│                │
    │              │  │              │  ks_2samp()    │
    │              │  │              │  statistic, p  │
    │              │  │<─────────────┤                │
    │              │  │              │                │
    │              │  └─ No: Chi² test                │
    │              │     ├───────────>│                │
    │              │     │            │  chi2_test()   │
    │              │     │<───────────┤                │
    │              │                │                │
    │              │  Calculate PSI │                │
    │              │  for feature   │                │
    │              ├───────────────>│                │
    │              │  PSI value     │                │
    │              │<───────────────┤                │
    │              │                │                │
    │              │  Repeat for all features        │
    │              │                │                │
    │              │  Aggregate drift│                │
    │              │  score         │                │
    │              │                │                │
    │              │  Identify drifted                │
    │              │  features      │                │
    │              │  (p_value < 0.05 or PSI > 0.25) │
    │              │                │                │
    │              │  Create report │                │
    │              │                │                │
    │  Drift report│                │                │
    │<─────────────┤                │                │
    │              │                │                │
    │  Log to MLflow                │                │
    ├─────────────────────────────────────────────────>│
    │  - drift_score                │                │
    │  - drifted_features           │                │
    │  - drift_details.json         │                │
    │  - drift_plot.png             │                │
    │              │                │  Logged        │
    │<─────────────────────────────────────────────────┤
    │              │                │                │
```

### 4.2 Performance Monitoring and Retraining Decision

```
LangGraph    PerformanceMonitor    Agent3    MLflow    RetrainingTrigger
    │              │                    │        │              │
    │  monitor_performance()            │        │              │
    ├─────────────>│                    │        │              │
    │              │                    │        │              │
    │              │  Load current metrics       │              │
    │              │  (from test set)   │        │              │
    │              │                    │        │              │
    │              │  Load baseline metrics      │              │
    │              │  (from validation)│        │              │
    │              │                    │        │              │
    │              │  Calculate drops   │        │              │
    │              │  per metric        │        │              │
    │              │                    │        │              │
    │              │  Compare with      │        │              │
    │              │  threshold (5%)    │        │              │
    │              │                    │        │              │
    │  Comparison  │                    │        │              │
    │<─────────────┤                    │        │              │
    │              │                    │        │              │
    │  Log to MLflow                    │        │              │
    ├───────────────────────────────────────────>│              │
    │              │                    │        │              │
    │  agent_3_retraining_decision()   │        │              │
    ├──────────────────────────────────>│        │              │
    │              │                    │        │              │
    │              │                    │  Prepare context      │
    │              │                    │  - performance_analysis│
    │              │                    │  - drift_analysis     │
    │              │                    │  - business_context   │
    │              │                    │        │              │
    │              │                    │  Invoke Bedrock       │
    │              │                    │  (similar to Agent 1/2)│
    │              │                    │        │              │
    │              │                    │  Decision: retrain=True│
    │              │                    │  reasoning: "..."     │
    │              │                    │  urgency: "high"      │
    │              │                    │        │              │
    │  Retrain decision                │        │              │
    │<──────────────────────────────────┤        │              │
    │              │                    │        │              │
    │  Log decision│                    │        │              │
    ├───────────────────────────────────────────>│              │
    │              │                    │        │              │
    │  Route based on decision          │        │              │
    │  if retrain == True:              │        │              │
    │                                                             │
    │  trigger_retrain()                │        │              │
    ├─────────────────────────────────────────────────────────────>
    │              │                    │        │  Create new │
    │              │                    │        │  pipeline   │
    │              │                    │        │  run        │
    │              │                    │        │             │
    │  New pipeline started             │        │             │
    │<─────────────────────────────────────────────────────────────
    │              │                    │        │              │
```

---

## 5. MLflow Integration Flow

### 5.1 Experiment and Run Management

```
LangGraph    MLflowManager    MLflowServer    PostgreSQL    S3/MinIO
    │              │                │              │             │
    │  Initialize  │                │              │             │
    ├─────────────>│                │              │             │
    │              │  Set tracking URI             │             │
    │              ├───────────────>│              │             │
    │              │                │              │             │
    │              │  Create or get experiment     │             │
    │              ├───────────────>│              │             │
    │              │                │  Query DB    │             │
    │              │                ├─────────────>│             │
    │              │                │  Return exp  │             │
    │              │                │<─────────────┤             │
    │              │  exp_id        │              │             │
    │              │<───────────────┤              │             │
    │  exp_id      │                │              │             │
    │<─────────────┤                │              │             │
    │              │                │              │             │
    │  start_run   │                │              │             │
    ├─────────────>│                │              │             │
    │              │  Create run    │              │             │
    │              ├───────────────>│              │             │
    │              │                │  INSERT INTO runs│         │
    │              │                ├─────────────>│             │
    │              │                │  run_id      │             │
    │              │                │<─────────────┤             │
    │              │  run_id        │              │             │
    │              │<───────────────┤              │             │
    │  run_id      │                │              │             │
    │<─────────────┤                │              │             │
    │              │                │              │             │
    │  log_params  │                │              │             │
    ├─────────────>│                │              │             │
    │              │  Log parameters│              │             │
    │              ├───────────────>│              │             │
    │              │                │  INSERT INTO params│       │
    │              │                ├─────────────>│             │
    │              │                │  OK          │             │
    │              │                │<─────────────┤             │
    │              │  OK            │              │             │
    │              │<───────────────┤              │             │
    │  OK          │                │              │             │
    │<─────────────┤                │              │             │
    │              │                │              │             │
    │  log_metrics │                │              │             │
    ├─────────────>│                │              │             │
    │              │  Log metrics   │              │             │
    │              ├───────────────>│              │             │
    │              │                │  INSERT INTO metrics│      │
    │              │                ├─────────────>│             │
    │              │                │  OK          │             │
    │              │                │<─────────────┤             │
    │              │  OK            │              │             │
    │              │<───────────────┤              │             │
    │  OK          │                │              │             │
    │<─────────────┤                │              │             │
    │              │                │              │             │
    │  log_artifact│                │              │             │
    ├─────────────>│                │              │             │
    │              │  Upload artifact│             │             │
    │              ├───────────────>│              │             │
    │              │                │  Store to S3 │             │
    │              │                ├─────────────────────────────>
    │              │                │              │  Upload     │
    │              │                │              │  complete   │
    │              │                │<─────────────────────────────
    │              │                │  Update DB   │             │
    │              │                │  with URI    │             │
    │              │                ├─────────────>│             │
    │              │                │  OK          │             │
    │              │                │<─────────────┤             │
    │              │  OK            │              │             │
    │              │<───────────────┤              │             │
    │  OK          │                │              │             │
    │<─────────────┤                │              │             │
    │              │                │              │             │
    │  log_model   │                │              │             │
    ├─────────────>│                │              │             │
    │              │  Serialize model│             │             │
    │              │  (pickle/joblib)│             │             │
    │              │                │              │             │
    │              │  Create model signature        │             │
    │              │  (input/output schema)         │             │
    │              │                │              │             │
    │              │  Log model     │              │             │
    │              ├───────────────>│              │             │
    │              │                │  Store to S3 │             │
    │              │                ├─────────────────────────────>
    │              │                │              │  model.pkl  │
    │              │                │              │  MLmodel    │
    │              │                │              │  requirements.txt│
    │              │                │<─────────────────────────────
    │              │                │  Update DB   │             │
    │              │                ├─────────────>│             │
    │              │  OK            │              │             │
    │              │<───────────────┤              │             │
    │  OK          │                │              │             │
    │<─────────────┤                │              │             │
    │              │                │              │             │
    │  end_run     │                │              │             │
    ├─────────────>│                │              │             │
    │              │  End run       │              │             │
    │              ├───────────────>│              │             │
    │              │                │  UPDATE runs │             │
    │              │                │  SET status=FINISHED│      │
    │              │                │  SET end_time│             │
    │              │                ├─────────────>│             │
    │              │                │  OK          │             │
    │              │                │<─────────────┤             │
    │              │  OK            │              │             │
    │              │<───────────────┤              │             │
    │  OK          │                │              │             │
    │<─────────────┤                │              │             │
    │              │                │              │             │
```

### 5.2 Model Registry Flow

```
LangGraph    ModelRegistry    MLflowServer    PostgreSQL
    │              │                │              │
    │  register_model()             │              │
    ├─────────────>│                │              │
    │              │  Create/get registered model  │
    │              ├───────────────>│              │
    │              │                │  INSERT INTO registered_models│
    │              │                ├─────────────>│
    │              │                │  model_name  │
    │              │                │<─────────────┤
    │              │  Create model version         │
    │              ├───────────────>│              │
    │              │                │  INSERT INTO model_versions│
    │              │                │  (name, version, source, run_id)│
    │              │                ├─────────────>│
    │              │                │  version_id  │
    │              │                │<─────────────┤
    │              │  model_version │              │
    │              │<───────────────┤              │
    │  model_version                │              │
    │<─────────────┤                │              │
    │              │                │              │
    │  transition_model_stage()     │              │
    │  (to Production)              │              │
    ├─────────────>│                │              │
    │              │  Transition stage             │
    │              ├───────────────>│              │
    │              │                │  UPDATE model_versions│
    │              │                │  SET current_stage='Production'│
    │              │                ├─────────────>│
    │              │                │              │
    │              │                │  (Optional) Archive old Production│
    │              │                │  UPDATE model_versions│
    │              │                │  SET current_stage='Archived'│
    │              │                ├─────────────>│
    │              │                │  OK          │
    │              │                │<─────────────┤
    │              │  OK            │              │
    │              │<───────────────┤              │
    │  OK          │                │              │
    │<─────────────┤                │              │
    │              │                │              │
```

---

## 6. User Interaction Flow

### 6.1 Pipeline Configuration and Execution

```
User        StreamlitUI    ConfigValidator    LangGraph    BackendAPI
 │              │              │                  │              │
 │  Open UI     │              │                  │              │
 ├─────────────>│              │                  │              │
 │              │              │                  │              │
 │  Display dashboard          │                  │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  Upload CSV  │              │                  │              │
 ├─────────────>│              │                  │              │
 │              │  Validate file│                  │              │
 │              ├─────────────>│                  │              │
 │              │  File OK     │                  │              │
 │              │<─────────────┤                  │              │
 │              │              │                  │              │
 │  Show file preview          │                  │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  Configure   │              │                  │              │
 │  parameters: │              │                  │              │
 │  - test_size=0.2            │                  │              │
 │  - cv_folds=5│              │                  │              │
 │  - algorithms=["RF", "GB"]  │                  │              │
 ├─────────────>│              │                  │              │
 │              │  Validate config                 │              │
 │              ├─────────────>│                  │              │
 │              │  Config OK   │                  │              │
 │              │<─────────────┤                  │              │
 │              │              │                  │              │
 │  Click "Start Pipeline"     │                  │              │
 ├─────────────>│              │                  │              │
 │              │  POST /pipeline/start           │              │
 │              ├─────────────────────────────────────────────────>
 │              │              │                  │  Validate & │
 │              │              │                  │  start      │
 │              │              │  Initialize      │              │
 │              │              │  pipeline        │              │
 │              │              │<─────────────────┤              │
 │              │              │                  │  run_id     │
 │              │<─────────────────────────────────────────────────
 │              │              │                  │              │
 │  Display run_id and status  │                  │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  WebSocket: subscribe to updates               │              │
 │  /ws/pipeline/{run_id}      │                  │              │
 ├─────────────>│              │                  │              │
 │              │  Establish WebSocket            │              │
 │              │  connection  │                  │              │
 │              │              │                  │              │
 │              │  (Pipeline executing)           │              │
 │              │              │                  │              │
 │              │  Status update: "preprocessing" │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  Update progress bar        │                  │              │
 │              │              │                  │              │
 │              │  Status update: "feature_selection"│           │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │              │  Agent decision: algorithm_selection│          │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  Display agent reasoning    │                  │              │
 │              │              │                  │              │
 │              │  Status update: "training RF"   │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  Update training progress   │                  │              │
 │              │              │                  │              │
 │              │  Live metrics: RF cv_mean=0.87  │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  Update metrics table       │                  │              │
 │              │              │                  │              │
 │              │  (Continue for all stages)      │              │
 │              │              │                  │              │
 │              │  Status update: "completed"     │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
 │  Display completion message │                  │              │
 │  "Best model: GB (90% accuracy)"               │              │
 │              │              │                  │              │
 │  Click "View Results"       │                  │              │
 ├─────────────>│              │                  │              │
 │              │  GET /results/{run_id}          │              │
 │              ├─────────────────────────────────────────────────>
 │              │              │                  │  Fetch       │
 │              │              │                  │  results     │
 │              │<─────────────────────────────────────────────────
 │              │              │                  │              │
 │  Display:    │              │                  │              │
 │  - Confusion matrix         │                  │              │
 │  - Feature importance       │                  │              │
 │  - Model comparison         │                  │              │
 │  - Drift analysis           │                  │              │
 │<─────────────┤              │                  │              │
 │              │              │                  │              │
```

### 6.2 Manual Retraining Trigger

```
User        StreamlitUI    BackendAPI    LangGraph    MLflow
 │              │              │              │           │
 │  Navigate to│              │              │           │
 │  Monitoring │              │              │           │
 │  Dashboard  │              │              │           │
 ├─────────────>│              │              │           │
 │              │              │              │           │
 │  Display performance metrics│              │           │
 │  - Current accuracy: 0.85   │              │           │
 │  - Baseline: 0.90           │              │           │
 │  - Drift detected: Yes      │              │           │
 │<─────────────┤              │              │           │
 │              │              │              │           │
 │  Click "Trigger Retraining" │              │           │
 ├─────────────>│              │              │           │
 │              │  Confirm dialog             │           │
 │              │  "Are you sure?"            │           │
 │<─────────────┤              │              │           │
 │              │              │              │           │
 │  Confirm     │              │              │           │
 ├─────────────>│              │              │           │
 │              │  POST /retrain/trigger      │           │
 │              ├─────────────>│              │           │
 │              │              │  Create new  │           │
 │              │              │  pipeline run│           │
 │              │              ├─────────────>│           │
 │              │              │              │  Start run│
 │              │              │              ├──────────>│
 │              │              │              │  run_id   │
 │              │              │              │<──────────┤
 │              │              │  new_run_id  │           │
 │              │              │<─────────────┤           │
 │              │  new_run_id  │              │           │
 │              │<─────────────┤              │           │
 │              │              │              │           │
 │  "Retraining started: {new_run_id}"        │           │
 │<─────────────┤              │              │           │
 │              │              │              │           │
 │  Redirect to pipeline dashboard            │           │
 │  with new_run_id            │              │           │
 │<─────────────┤              │              │           │
 │              │              │              │           │
```

---

## Summary

These sequence diagrams provide detailed views of:

1. **Complete Pipeline Execution**: End-to-end flow from user initiation to completion
2. **AI Agent Decisions**: How Bedrock agents analyze context and make decisions
3. **Model Training**: Detailed GridSearchCV execution with parallel training
4. **Monitoring & Retraining**: Drift detection, performance monitoring, and retraining triggers
5. **MLflow Integration**: Experiment tracking, model logging, and model registry
6. **User Interactions**: UI flows for configuration, monitoring, and manual controls

All interactions follow a consistent pattern:
- **Asynchronous communication** where appropriate (WebSockets for real-time updates)
- **MLflow logging** at every critical stage for reproducibility
- **Error handling** with retries for external services (AWS Bedrock, MLflow)
- **State management** through LangGraph for checkpoint/resume capability

---

**End of Sequence Diagrams Document**
