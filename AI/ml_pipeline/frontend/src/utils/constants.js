// API Endpoints
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const MLFLOW_URL = import.meta.env.VITE_MLFLOW_URL || 'http://localhost:5000'
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

// Pipeline Status
export const PIPELINE_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  STOPPED: 'stopped'
}

// Node Status
export const NODE_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed'
}

// Status Icons
export const STATUS_ICONS = {
  [PIPELINE_STATUS.PENDING]: '⏳',
  [PIPELINE_STATUS.RUNNING]: '🔄',
  [PIPELINE_STATUS.COMPLETED]: '✅',
  [PIPELINE_STATUS.FAILED]: '❌',
  [PIPELINE_STATUS.STOPPED]: '🛑'
}

// Status Colors (Tailwind classes)
export const STATUS_COLORS = {
  [PIPELINE_STATUS.PENDING]: 'text-gray-500',
  [PIPELINE_STATUS.RUNNING]: 'text-blue-500',
  [PIPELINE_STATUS.COMPLETED]: 'text-green-500',
  [PIPELINE_STATUS.FAILED]: 'text-red-500',
  [PIPELINE_STATUS.STOPPED]: 'text-orange-500'
}

// Example Prompts
export const EXAMPLE_PROMPTS = [
  'Classify iris species using random forest and SVM',
  'Predict house prices, optimize for RMSE',
  'Binary classification with class imbalance handling',
  'Multi-class classification on wine quality dataset'
]

// Pipeline Nodes (in order)
export const PIPELINE_NODES = [
  { id: 'analyze_prompt', name: 'Analyze Prompt', description: 'Extract configuration from natural language' },
  { id: 'load_data', name: 'Load Data', description: 'Load and validate dataset' },
  { id: 'agent_1a', name: 'Agent 1A: Algorithm Predictor', description: 'Predict algorithm category and learning paradigm' },
  { id: 'agent_1b', name: 'Agent 1B: Question Generator', description: 'Generate preprocessing questions' },
  { id: 'await_review_approval', name: 'Review Approval', description: 'Human review checkpoint' },
  // Supervised preprocessing
  { id: 'clean_data', name: 'Clean Data (Supervised)', description: 'Remove outliers and invalid data' },
  { id: 'clean_data_supervised', name: 'Clean Data', description: 'Remove outliers (Supervised)' },
  // Unsupervised preprocessing
  { id: 'clean_outliers', name: 'Clean Outliers (Unsupervised)', description: 'Validate data quality, preserve outliers' },
  { id: 'clean_outliers_unsupervised', name: 'Clean Outliers', description: 'Preserve outliers (Unsupervised)' },
  // Common preprocessing
  { id: 'handle_missing', name: 'Handle Missing', description: 'Impute missing values' },
  { id: 'handle_missing_supervised', name: 'Handle Missing', description: 'Impute missing (Supervised)' },
  { id: 'handle_missing_unsupervised', name: 'Handle Missing', description: 'Impute missing (Unsupervised)' },
  { id: 'encode_features', name: 'Encode Features', description: 'Categorical encoding' },
  { id: 'encode_features_supervised', name: 'Encode Features', description: 'Encode features (Supervised)' },
  { id: 'encode_features_unsupervised', name: 'Encode Features', description: 'Encode features (Unsupervised)' },
  { id: 'scale_features', name: 'Scale Features', description: 'Feature normalization' },
  { id: 'scale_features_supervised', name: 'Scale Features', description: 'Scale features (Supervised)' },
  { id: 'scale_features_unsupervised', name: 'Scale Features', description: 'Scale features (Unsupervised)' },
  { id: 'await_preprocessing_review', name: 'Preprocessing Review', description: 'Review preprocessing results' },
  { id: 'split_data', name: 'Split Data', description: 'Train/test split' },
  { id: 'train_models', name: 'Train Models', description: 'Train multiple algorithms' },
  { id: 'evaluate_models', name: 'Evaluate Models', description: 'Compute metrics' },
  { id: 'select_best', name: 'Select Best', description: 'Choose best model' },
  { id: 'generate_report', name: 'Generate Report', description: 'Create artifacts' }
]

// WebSocket Events
export const WS_EVENTS = {
  STATE_UPDATE: 'state_update',
  NODE_STARTED: 'node_started',
  NODE_COMPLETED: 'node_completed',
  NODE_FAILED: 'node_failed',
  PIPELINE_COMPLETED: 'pipeline_completed'
}

// Local Storage Keys
export const STORAGE_KEYS = {
  DARK_MODE: 'darkMode',
  SELECTED_RUN: 'selectedRunId',
  FILTERS: 'runFilters'
}

// Refresh Intervals (ms)
export const REFRESH_INTERVALS = {
  RUN_LIST: 5000,
  PIPELINE_STATE: 2000,
  METRICS: 3000
}
