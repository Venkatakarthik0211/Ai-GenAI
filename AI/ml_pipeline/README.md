# Enhanced ML Pipeline with LangGraph & AWS Bedrock

An intelligent, automated MLOps pipeline leveraging **LangGraph** for workflow orchestration, **AWS Bedrock** (Claude) for AI-driven decision-making, **MLflow** for experiment tracking, and **GridSearchCV** for hyperparameter tuning.

## Features

- **Intelligent Algorithm Selection**: AI agents automatically select optimal algorithms based on data characteristics
- **Automated Hyperparameter Tuning**: GridSearchCV integration for each algorithm
- **Comprehensive Experiment Tracking**: MLflow logging of all experiments, parameters, metrics, and models
- **Performance Monitoring**: Data drift detection and performance degradation monitoring
- **Automated Retraining**: AI-driven decisions on when to retrain models
- **Modular Architecture**: Individual LangGraph nodes for each algorithm and processing step
- **Production-Ready**: Complete testing suite, deployment scripts, and monitoring

## Architecture

```
User Input → LangGraph Orchestration → AI Agents (Bedrock) → Algorithm Nodes → MLflow Tracking
     ↓                                         ↓                      ↓              ↓
Data Loading → Preprocessing → Feature Eng → Training → Evaluation → Model Registry
                                                  ↓
                                           GridSearchCV Tuning
```

## Quick Start

### Prerequisites

- Python 3.9+
- AWS Account with Bedrock access
- MLflow server (or use local tracking)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ml_pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials and MLflow URI
```

### Setup MLflow

```bash
# Start MLflow tracking server
bash scripts/setup_mlflow.sh

# Or manually:
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

### Run Pipeline

```bash
# Run complete pipeline
python scripts/run_pipeline.py --data data/raw/train.csv --target target_column

# Or with custom config
python scripts/run_pipeline.py --config config/custom_config.yaml
```

## Project Structure

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for complete structure documentation.

```
ml_pipeline/
├── config/              # Configuration files
├── core/                # Core pipeline components (state, graph)
├── nodes/               # LangGraph node implementations
│   ├── preprocessing/   # Data preprocessing nodes
│   ├── classification/  # Classification algorithm nodes
│   ├── regression/      # Regression algorithm nodes
│   └── ...
├── agents/              # AI decision agents (Bedrock)
├── tuning/              # Hyperparameter tuning modules
├── monitoring/          # Performance monitoring
├── mlflow_utils/        # MLflow integration utilities
└── tests/               # Test suite
```

## AI Decision Agents

### Agent 1: Algorithm Selection
- **Purpose**: Selects which ML algorithms to train based on data profile
- **Input**: Data statistics, target type, feature characteristics
- **Output**: List of recommended algorithms with reasoning

### Agent 2: Model Selection
- **Purpose**: Selects the best model from trained algorithms
- **Input**: Cross-validation scores, test metrics, training time
- **Output**: Best model name with detailed reasoning

### Agent 3: Retraining Decision
- **Purpose**: Decides if model retraining is needed
- **Input**: Performance metrics, drift detection results, time since last training
- **Output**: Retrain decision (yes/no) with reasoning

## MLflow Integration

All pipeline runs are automatically logged to MLflow:

- **Parameters**: Data paths, algorithm configs, hyperparameters
- **Metrics**: Accuracy, precision, recall, F1, RMSE, R², etc.
- **Artifacts**: Trained models, plots, reports, agent decisions
- **Tags**: Experiment metadata, algorithm names, agent decisions

Access MLflow UI:
```bash
# Default: http://localhost:5000
mlflow ui
```

## Monitoring & Retraining

### Data Drift Detection
- Kolmogorov-Smirnov test for numerical features
- Chi-squared test for categorical features
- Population Stability Index (PSI)

### Performance Monitoring
- Baseline vs. current performance comparison
- Threshold-based alerting
- Automated retraining triggers

## Configuration

### Default Configuration (`config/default_config.yaml`)

```yaml
data:
  train_path: "data/raw/train.csv"
  target_column: "target"
  test_size: 0.2

algorithms:
  classification:
    - logistic_regression
    - random_forest
    - gradient_boosting
  regression:
    - linear_regression
    - ridge
    - random_forest

mlflow:
  tracking_uri: "http://localhost:5000"
  experiment_name: "ml_pipeline_experiment"

bedrock:
  model_id: "anthropic.claude-3-sonnet-20240229-v1:0"
  region: "us-east-1"
  temperature: 0.0
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Deployment

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

```bash
# Deploy best model
python scripts/deploy_model.py --model-name best_model --version 1
```

## Documentation

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Data Flow Architecture](docs/DATA_FLOW_ARCHITECTURE.md)
- [High-Level Design](docs/HLD_MLOPS_AUTOMATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

[Specify License]

## Contact

[Contact Information]
