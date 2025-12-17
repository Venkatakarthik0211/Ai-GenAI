"""
Algorithm Category Predictor Agent (Agent 1A)

First agent in the two-agent HITL preprocessing system.
Analyzes dataset characteristics and predicts the optimal algorithm category.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseDecisionAgent

logger = logging.getLogger(__name__)


class AlgorithmCategoryPredictorAgent(BaseDecisionAgent):
    """
    Agent 1A: Algorithm Category Predictor

    Analyzes dataset characteristics to predict which algorithm category
    will perform best. This prediction guides preprocessing decisions in Agent 1B.

    Algorithm Categories:
    - linear_models: LogisticRegression, LinearRegression, Ridge, Lasso
    - tree_models: RandomForest, XGBoost, GradientBoosting, DecisionTree
    - neural_networks: MLP, Deep Learning models
    - ensemble: Stacking, Voting, Blending
    - time_series: ARIMA, LSTM, Prophet (for temporal data)
    - clustering: KMeans, DBSCAN, Hierarchical, GMM (for unsupervised grouping)

    Returns:
    - algorithm_category: Predicted category
    - confidence: Prediction confidence (must be >= 0.70)
    - reasoning: Explanation for the prediction
    - recommended_algorithms: Specific algorithms within the category
    - preprocessing_priorities: Required/optional for each preprocessing step
    - algorithm_requirements: Scaling, outlier sensitivity, etc.
    """

    def __init__(
        self,
        bedrock_model_id: str,
        aws_region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        fallback_model_id: Optional[str] = None,
        temperature: float = 0.2,  # Low for consistent predictions
        max_tokens: int = 2000
    ):
        """
        Initialize AlgorithmCategoryPredictor Agent.

        Args:
            bedrock_model_id: Primary Bedrock model ID
            aws_region: AWS region
            aws_access_key_id: AWS access key (optional)
            aws_secret_access_key: AWS secret key (optional)
            fallback_model_id: Fallback model ID if primary fails
            temperature: Sampling temperature (0.2 for consistent predictions)
            max_tokens: Maximum tokens to generate
        """
        super().__init__(
            bedrock_model_id=bedrock_model_id,
            aws_region=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            fallback_model_id=fallback_model_id,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.info(f"AlgorithmCategoryPredictorAgent initialized (temperature={temperature})")

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build structured prompt for algorithm category prediction.

        Args:
            context: Dictionary containing:
                - n_samples: Number of samples
                - n_features: Number of features
                - target_type: "classification", "regression", or "clustering"
                - feature_types: Dict with numeric_count, categorical_count, high_cardinality_count
                - class_distribution: Dict of class frequencies (for classification)
                - dataset_size_mb: Dataset size in MB
                - data_characteristics: Dict with missing_percentage, duplicate_percentage,
                                       outlier_percentage, feature_correlation_max

        Returns:
            Formatted prompt string for Bedrock
        """
        n_samples = context.get("n_samples", "unknown")
        n_features = context.get("n_features", "unknown")
        target_type = context.get("target_type", "unknown")
        feature_types = context.get("feature_types", {})
        class_distribution = context.get("class_distribution", {})
        dataset_size_mb = context.get("dataset_size_mb", 0)
        data_chars = context.get("data_characteristics", {})

        prompt = f"""You are an expert ML engineer tasked with predicting the optimal algorithm category for a dataset.

**Dataset Characteristics:**
- Samples: {n_samples}
- Features: {n_features}
- Target Type: {target_type}
- Numeric Features: {feature_types.get('numeric_count', 0)}
- Categorical Features: {feature_types.get('categorical_count', 0)}
- High Cardinality Features: {feature_types.get('high_cardinality_count', 0)}
- Dataset Size: {dataset_size_mb:.2f} MB
- Missing Values: {data_chars.get('missing_percentage', 0):.2f}%
- Duplicates: {data_chars.get('duplicate_percentage', 0):.2f}%
- Outliers: {data_chars.get('outlier_percentage', 0):.2f}%
- Max Feature Correlation: {data_chars.get('feature_correlation_max', 0):.2f}
"""

        if target_type == "classification" and class_distribution:
            prompt += f"\n**Class Distribution:**\n"
            for cls, count in class_distribution.items():
                pct = (count / n_samples * 100) if isinstance(n_samples, (int, float)) else 0
                prompt += f"  - {cls}: {count} ({pct:.1f}%)\n"

        prompt += """
**Task:**
Analyze these characteristics and predict the optimal algorithm category.

**Algorithm Categories:**
1. **linear_models**: Best for linearly separable data, interpretable models
   - Examples: LogisticRegression, LinearRegression, Ridge, Lasso
   - Use when: Linear relationships, interpretability important, small-medium datasets

2. **tree_models**: Best for non-linear relationships, robust to outliers
   - Examples: RandomForest, XGBoost, GradientBoosting, DecisionTree
   - Use when: Non-linear patterns, mixed feature types, medium-large datasets

3. **neural_networks**: Best for complex patterns, large datasets
   - Examples: MLP, Deep Learning models
   - Use when: Complex non-linear patterns, large datasets (>10K samples), high-dimensional data

4. **ensemble**: Best for maximizing performance, combining multiple models
   - Examples: Stacking, Voting, Blending
   - Use when: Performance critical, sufficient data for multiple models

5. **time_series**: Best for temporal/sequential data
   - Examples: ARIMA, LSTM, Prophet
   - Use when: Data has temporal ordering, forecasting needed

6. **clustering**: Best for unsupervised grouping tasks (no target column)
   - Examples: KMeans, DBSCAN, Hierarchical Clustering, GMM
   - Use when: No target labels, finding natural groups/segments, exploratory analysis

**Analysis Guidelines:**
- Consider dataset size (small <1K, medium 1K-10K, large >10K)
- Consider feature-to-sample ratio (high ratio favors simpler models)
- Consider class imbalance (tree models handle better)
- Consider interpretability needs (linear models more interpretable)
- Consider computational constraints (neural networks require more resources)

**Required Output (JSON):**
{
    "learning_paradigm": "<supervised|unsupervised>",
    "algorithm_category": "<category>",
    "confidence": <0.0-1.0>,
    "reasoning": "<detailed explanation>",
    "recommended_algorithms": ["<algo1>", "<algo2>", "<algo3>"],
    "preprocessing_priorities": {
        "clean_data": "<critical|required|optional>",
        "handle_missing": "<critical|required|optional>",
        "encode_features": "<critical|required|optional>",
        "scale_features": "<critical|required|optional>"
    },
    "algorithm_requirements": {
        "scaling_required": <true|false>,
        "outlier_sensitive": <true|false>,
        "handles_missing": <true|false>,
        "categorical_encoding_preference": "<one_hot|target|label|ordinal>"
    }
}

**Learning Paradigm Guidelines:**
- **supervised**: Task has a target column for prediction (classification, regression)
  - Examples: Predict customer churn, forecast sales, classify images, detect fraud
  - Algorithm categories: linear_models, tree_models, neural_networks, ensemble
- **unsupervised**: Task has NO target column, finding patterns in data
  - Examples: Customer segmentation, anomaly detection, dimensionality reduction, topic modeling
  - Algorithm categories: clustering, dimensionality_reduction, anomaly_detection

**Important:**
- Confidence must be >= 0.70 (otherwise return "uncertain")
- Provide clear reasoning based on dataset characteristics
- Consider preprocessing requirements for the chosen algorithm category
- Return ONLY the JSON object, no additional text
"""

        return prompt

    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Bedrock response into structured prediction.

        Args:
            response_text: Raw response from Bedrock

        Returns:
            Parsed prediction with validation

        Raises:
            ValueError: If response cannot be parsed or confidence < 0.70
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in response")

            prediction = json.loads(json_match.group(0))

            # Validate required fields
            required_fields = [
                "learning_paradigm",
                "algorithm_category",
                "confidence",
                "reasoning",
                "recommended_algorithms",
                "preprocessing_priorities",
                "algorithm_requirements"
            ]
            missing = [f for f in required_fields if f not in prediction]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")

            # Validate learning paradigm
            valid_paradigms = ["supervised", "unsupervised"]
            if prediction["learning_paradigm"] not in valid_paradigms:
                raise ValueError(
                    f"Invalid learning_paradigm: {prediction['learning_paradigm']}. "
                    f"Must be one of: {valid_paradigms}"
                )

            # Validate algorithm category
            valid_categories = ["linear_models", "tree_models", "neural_networks", "ensemble", "time_series", "clustering", "dimensionality_reduction", "anomaly_detection"]
            if prediction["algorithm_category"] not in valid_categories:
                raise ValueError(
                    f"Invalid algorithm_category: {prediction['algorithm_category']}. "
                    f"Must be one of: {valid_categories}"
                )

            # Validate confidence threshold
            confidence = float(prediction["confidence"])
            if confidence < 0.70:
                logger.warning(
                    f"Low confidence prediction: {confidence:.2f} < 0.70. "
                    f"Category: {prediction['algorithm_category']}"
                )
                raise ValueError(
                    f"Confidence {confidence:.2f} below threshold (0.70). "
                    "Cannot make reliable algorithm category prediction."
                )

            # Validate preprocessing priorities
            valid_priorities = ["critical", "required", "optional"]
            for step, priority in prediction["preprocessing_priorities"].items():
                if priority not in valid_priorities:
                    raise ValueError(
                        f"Invalid priority '{priority}' for {step}. "
                        f"Must be one of: {valid_priorities}"
                    )

            # Log successful prediction
            logger.info(
                f"Learning paradigm: {prediction['learning_paradigm']}, "
                f"Algorithm category: {prediction['algorithm_category']} "
                f"(confidence: {confidence:.2f})"
            )
            logger.info(f"Recommended algorithms: {prediction['recommended_algorithms']}")

            return prediction

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            raise ValueError(f"Invalid JSON in response: {e}")
        except Exception as e:
            logger.error(f"Error parsing algorithm prediction: {e}")
            raise

    def predict_category(
        self,
        n_samples: int,
        n_features: int,
        target_type: str,
        feature_types: Dict[str, int],
        class_distribution: Optional[Dict[str, int]] = None,
        dataset_size_mb: float = 0,
        data_characteristics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Predict optimal algorithm category for the dataset.

        Args:
            n_samples: Number of samples
            n_features: Number of features
            target_type: "classification", "regression", or "clustering" (unsupervised)
            feature_types: Dict with numeric_count, categorical_count, high_cardinality_count
            class_distribution: Dict of class frequencies (for classification)
            dataset_size_mb: Dataset size in MB
            data_characteristics: Dict with missing_percentage, duplicate_percentage,
                                 outlier_percentage, feature_correlation_max

        Returns:
            Algorithm category prediction dict

        Raises:
            Exception: If prediction fails or confidence < 0.70
        """
        context = {
            "n_samples": n_samples,
            "n_features": n_features,
            "target_type": target_type,
            "feature_types": feature_types,
            "class_distribution": class_distribution or {},
            "dataset_size_mb": dataset_size_mb,
            "data_characteristics": data_characteristics or {}
        }

        logger.info(
            f"Predicting algorithm category for {target_type} task: "
            f"{n_samples} samples, {n_features} features"
        )

        # Execute with retry logic (inherited from BaseDecisionAgent)
        result = self.invoke(context)

        return result["decision"]

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get default algorithm category when agent fails.

        Returns appropriate default based on target_type:
        - clustering: For unsupervised tasks
        - tree_models: For supervised tasks (safest default)

        Args:
            context: Context data (n_samples, target_type, etc.)

        Returns:
            Default algorithm category prediction
        """
        target_type = context.get("target_type", "classification")

        logger.warning(
            f"Using default algorithm category prediction for {target_type} task"
        )

        # For clustering tasks, return clustering default
        if target_type == "clustering" or target_type == "unsupervised":
            return {
                "algorithm_category": "clustering",
                "confidence": 0.50,
                "reasoning": "Default fallback for unsupervised learning: KMeans clustering is selected as a safe default because it: (1) Works well for most clustering tasks, (2) Fast and scalable, (3) Easy to interpret with clear cluster assignments, (4) Handles numeric features well, and (5) Requires minimal hyperparameter tuning (mainly number of clusters).",
                "recommended_algorithms": ["KMeans", "DBSCAN", "Hierarchical Clustering"],
                "preprocessing_priorities": {
                    "clean_data": "required",
                    "handle_missing": "critical",
                    "encode_features": "required",
                    "scale_features": "critical"
                },
                "algorithm_requirements": {
                    "requires_scaling": True,
                    "outlier_sensitive": True,
                    "handles_missing": False,
                    "handles_categorical": False,
                    "requires_normalization": True
                }
            }

        # For supervised tasks (classification/regression)
        return {
            "algorithm_category": "tree_models",
            "confidence": 0.50,
            "reasoning": "Default fallback: Tree-based models (Random Forest, XGBoost) are selected as a safe default because they: (1) Work well for most classification and regression tasks, (2) Handle missing values and outliers robustly, (3) Don't require feature scaling, (4) Provide feature importance, and (5) Are less sensitive to data quality issues.",
            "recommended_algorithms": ["Random Forest", "XGBoost", "Gradient Boosting"],
            "preprocessing_priorities": {
                "clean_data": "optional",
                "handle_missing": "recommended",
                "encode_features": "required",
                "scale_features": "optional"
            },
            "algorithm_requirements": {
                "requires_scaling": False,
                "outlier_sensitive": False,
                "handles_missing": True,
                "handles_categorical": True,
                "requires_normalization": False
            }
        }
