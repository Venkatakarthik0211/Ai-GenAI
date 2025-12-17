"""
Configuration Extraction Agent (Agent 0)

Extracts ML pipeline configuration from natural language user prompts.
This is the first agent in the pipeline, executing before all others.
"""

import json
import logging
import re
from typing import Dict, Any

from agents.base_agent import BaseDecisionAgent

logger = logging.getLogger(__name__)


class ConfigExtractionAgent(BaseDecisionAgent):
    """
    Agent 0: Configuration Extraction

    Analyzes natural language user prompts to extract ML pipeline configuration.

    Extracts:
    - target_column: Column name to predict
    - experiment_name: Descriptive MLflow experiment name
    - test_size: Train/test split ratio (default 0.2)
    - random_state: Random seed for reproducibility (default 42)
    - analysis_type: "classification" or "regression"

    Returns:
    - Extracted configuration values
    - Confidence score (0.0-1.0, must be >= 0.70)
    - Reasoning for each extracted value
    - Assumptions made during extraction
    - Warnings if any ambiguity detected

    Fallback Strategy:
    - If confidence < 70%: Return error and suggest trying fallback model
    - If Bedrock unavailable: Return error (NO heuristics fallback)
    """

    def __init__(
        self,
        bedrock_model_id: str,
        aws_region: str = "us-east-1",
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        fallback_model_id: str = None,
        confidence_threshold: float = 0.70,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ):
        """
        Initialize ConfigExtraction Agent.

        Args:
            bedrock_model_id: Primary Bedrock model ID
            aws_region: AWS region
            aws_access_key_id: AWS access key (optional)
            aws_secret_access_key: AWS secret key (optional)
            fallback_model_id: Fallback model ID if primary fails
            confidence_threshold: Minimum confidence score (default 0.70)
            temperature: Sampling temperature (default 0.0 for deterministic)
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
        self.confidence_threshold = confidence_threshold
        logger.info(f"ConfigExtractionAgent initialized (confidence_threshold={confidence_threshold})")

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build structured prompt for configuration extraction.

        Args:
            context: Dictionary containing:
                - user_prompt: Natural language description from user
                - available_columns: List of column names from data preview
                - dataset_preview: Dict with n_rows, n_columns, dtypes
                - user_hints: Optional dict with user-provided hints

        Returns:
            XML-formatted prompt string
        """
        user_prompt = context.get("user_prompt", "")
        available_columns = context.get("available_columns", [])
        dataset_preview = context.get("dataset_preview", {})
        user_hints = context.get("user_hints", {})

        # Format available columns
        columns_str = ", ".join(f'"{col}"' for col in available_columns)

        # Format dataset preview
        dataset_info = (
            f"- Number of rows (preview): {dataset_preview.get('n_rows', 'unknown')}\n"
            f"- Number of columns: {dataset_preview.get('n_columns', 'unknown')}\n"
        )

        # Format dtypes if available
        dtypes = dataset_preview.get('dtypes', {})
        if dtypes:
            dtype_lines = [f"  - {col}: {dtype}" for col, dtype in list(dtypes.items())[:10]]
            dataset_info += "- Column types (first 10):\n" + "\n".join(dtype_lines)

        # Format user hints if provided
        hints_section = ""
        if user_hints:
            hints_str = "\n".join(f"  - {key}: {value}" for key, value in user_hints.items())
            hints_section = f"""
<user_hints>
The user provided these hints to guide extraction:
{hints_str}
</user_hints>
"""

        prompt = f"""<role>
You are an EXPERT ML/AI system architect and prompt engineer with deep knowledge of machine learning algorithms, their characteristics, and optimal use cases. Your task is to analyze natural language ML task descriptions and extract precise pipeline configuration with intelligent algorithm recommendations.
</role>

<task>
Analyze the user's prompt and extract the following configuration:

1. **target_column**: The column name to predict/analyze (MUST exist in available_columns)
2. **experiment_name**: Descriptive name for MLflow experiment (lowercase, underscores, max 50 chars)
3. **test_size**: Train/test split ratio (0.0-1.0, default 0.2)
4. **random_state**: Random seed for reproducibility (integer, default 42)
5. **analysis_type**: One of: "classification", "regression", "clustering", "dimensionality_reduction", "association_rules", "anomaly_detection", "time_series", "feature_importance"
6. **recommended_algorithms**: Array of 3-5 specific algorithms best suited for this task, ranked by suitability
7. **algorithm_rationale**: Brief explanation of why these algorithms were recommended

You must also provide:
- **confidence**: Your confidence score (0.0-1.0) in the extracted configuration
- **reasoning**: Explanation for each extracted value
- **assumptions**: List of assumptions you made
- **warnings**: List of any ambiguities or uncertainties detected
</task>

<context>
<user_prompt>
{user_prompt}
</user_prompt>

<available_columns>
{columns_str}
</available_columns>

<dataset_preview>
{dataset_info}
</dataset_preview>
{hints_section}
</context>

<output_format>
Return ONLY a valid JSON object with this exact structure:

{{
  "target_column": "column_name",
  "experiment_name": "descriptive_name",
  "test_size": 0.2,
  "random_state": 42,
  "analysis_type": "classification",
  "recommended_algorithms": [
    "Decision Tree",
    "Random Forest",
    "XGBoost"
  ],
  "algorithm_rationale": "Decision trees provide interpretability for feature importance analysis. Random Forest and XGBoost offer robust ensemble methods with built-in feature importance.",
  "confidence": 0.95,
  "reasoning": {{
    "target_column": "Explanation for why this column was selected...",
    "experiment_name": "Explanation for the chosen experiment name...",
    "test_size": "Explanation for the test size...",
    "random_state": "Explanation for the random state...",
    "analysis_type": "Explanation for the chosen analysis type...",
    "recommended_algorithms": "Explanation for algorithm selection..."
  }},
  "assumptions": [
    "Assumption 1: ...",
    "Assumption 2: ..."
  ],
  "warnings": [
    "Warning 1: ...",
    "Warning 2: ..."
  ]
}}
</output_format>

<validation_rules>
1. **target_column** MUST be in the available_columns list (case-sensitive)
2. **experiment_name** must be lowercase, use underscores, no spaces, max 50 characters
3. **test_size** must be between 0.0 and 1.0 (typically 0.1 to 0.3)
4. **random_state** must be a positive integer
5. **analysis_type** must be one of: "classification", "regression", "clustering", "dimensionality_reduction", "association_rules", "anomaly_detection", "time_series", "feature_importance"
6. **recommended_algorithms** must be an array of 3-5 algorithm names (strings)
7. **algorithm_rationale** must be a non-empty string explaining algorithm selection
8. **confidence** must be between 0.0 and 1.0
9. All reasoning values must be non-empty strings
10. assumptions and warnings must be arrays (can be empty)
</validation_rules>

<special_guidance_for_association_analysis>
**IMPORTANT: Detecting Association/Feature Importance Queries**

When users ask to "identify which features are associated with" or "what factors influence" or "which attributes are most related to" a target outcome, they are typically asking for FEATURE IMPORTANCE ANALYSIS, not just prediction.

For these queries:
1. **Prefer CLASSIFICATION over regression** when possible - this enables better feature importance analysis
   - If target is continuous (e.g., popularity score 0-100), convert to binary/multi-class categories
   - Example: "high popularity" (>50) vs "low popularity" (≤50)

2. **Look for these keywords that indicate association analysis:**
   - "identify which features are associated with"
   - "what factors influence"
   - "which attributes affect"
   - "what leads to high/low X"
   - "determine associations between"

3. **When detected:**
   - Choose classification if target can be categorized (high/medium/low, yes/no, etc.)
   - This allows using interpretable models like decision trees for feature importance
   - Add a note in reasoning explaining the classification choice enables association analysis

4. **Decision Tree Suitability:**
   - Classification tasks are ideal for decision trees which provide clear feature importance
   - Mention in assumptions that tree-based models will be used for interpretability
</special_guidance_for_association_analysis>

<ml_algorithm_knowledge_base>
**COMPREHENSIVE ML ALGORITHM TAXONOMY & SELECTION GUIDELINES**

You have expert-level knowledge of machine learning algorithms across all paradigms. Use this knowledge to recommend the MOST SUITABLE algorithms for each task.

## 1. SUPERVISED LEARNING ALGORITHMS

### REGRESSION (Continuous Target Prediction)
**Linear Methods:**
- Linear Regression: Simple, interpretable, fast. Best for linear relationships, baseline model.
- Polynomial Regression: Captures non-linear relationships via feature engineering.
- Ridge Regression (L2): Handles multicollinearity, prevents overfitting with regularization.
- Lasso Regression (L1): Feature selection via sparsity, automatic variable elimination.
- Elastic Net: Combines L1 + L2, balanced regularization and feature selection.

**Non-Linear Methods:**
- Support Vector Regression (SVR): Effective in high dimensions, robust to outliers, kernel trick for non-linearity.
- Decision Tree Regressor: Interpretable, handles non-linearity, prone to overfitting.
- Random Forest Regressor: Ensemble of trees, reduces overfitting, feature importance, robust.
- Gradient Boosting (XGBoost, LightGBM, CatBoost): State-of-art accuracy, handles missing values, built-in regularization.
- K-Nearest Neighbors (KNN) Regressor: Non-parametric, no training phase, sensitive to scale and curse of dimensionality.
- Neural Networks (MLP): Universal approximators, requires large data, computationally expensive.

**Time Series Specific:**
- ARIMA/SARIMA: Classical time series, captures trends and seasonality.
- Prophet: Facebook's tool for business time series with holidays and trends.
- LSTM/GRU: Deep learning for sequential data, captures long-term dependencies.

**When to use Regression:**
- Predicting continuous values (prices, temperatures, sales, scores)
- Forecasting numerical outcomes
- When target is numeric and unbounded

### CLASSIFICATION (Categorical Target Prediction)
**Linear Methods:**
- Logistic Regression: Simple, interpretable, probability estimates, fast, good baseline.
- Linear Discriminant Analysis (LDA): Assumes normal distributions, reduces dimensionality.
- Perceptron: Simple binary classifier, foundation for neural networks.

**Probabilistic Methods:**
- Naive Bayes (Gaussian, Multinomial, Bernoulli): Fast, works well with small data, assumes feature independence.

**Instance-Based:**
- K-Nearest Neighbors (KNN): Simple, non-parametric, no training, interpretable but slow at prediction.

**Support Vector Machines:**
- SVM (Linear, RBF, Polynomial kernels): Effective in high dimensions, memory efficient, versatile with kernels.

**Tree-Based Methods:**
- Decision Tree: Highly interpretable, feature importance, handles non-linearity, prone to overfitting.
- Random Forest: Ensemble excellence, robust, feature importance, handles missing values, reduces overfitting.
- Gradient Boosting (XGBoost, LightGBM, CatBoost): State-of-art accuracy, handles imbalanced data, built-in feature importance.
- AdaBoost: Focuses on misclassified samples, simple and effective ensemble.

**Neural Networks:**
- Multi-Layer Perceptron (MLP): Universal approximators, requires large data and tuning.
- Convolutional Neural Networks (CNN): Image classification, spatial hierarchies.
- Recurrent Neural Networks (RNN/LSTM/GRU): Sequential data, text classification, time series.

**When to use Classification:**
- Predicting categories (yes/no, high/medium/low, multi-class labels)
- Binary or multi-class problems
- Feature importance analysis (use tree-based methods)
- When target has discrete classes

## 2. UNSUPERVISED LEARNING ALGORITHMS

### CLUSTERING (Grouping Similar Data)
- K-Means: Fast, spherical clusters, requires k specification, sensitive to initialization.
- Mini-Batch K-Means: Scalable version of K-Means for large datasets.
- DBSCAN: Density-based, arbitrary shapes, automatic outlier detection, no k needed.
- Hierarchical Clustering (Agglomerative): Dendrogram visualization, no k needed upfront, computationally expensive.
- Gaussian Mixture Models (GMM): Probabilistic, soft clustering, assumes Gaussian distributions.
- OPTICS: Density-based like DBSCAN, better for varying densities.
- Mean Shift: Non-parametric, finds modes in density, no k needed.
- Spectral Clustering: Graph-based, works with non-convex clusters.

**When to use Clustering:**
- Customer segmentation, document grouping, image segmentation
- Exploratory data analysis to find natural groupings
- No labeled data available
- Understanding data structure

### DIMENSIONALITY REDUCTION (Feature Extraction & Visualization)
**Linear Methods:**
- Principal Component Analysis (PCA): Fast, linear, preserves global structure, orthogonal components.
- Linear Discriminant Analysis (LDA): Supervised reduction, maximizes class separability.
- Singular Value Decomposition (SVD): Matrix factorization, basis for many techniques.

**Non-Linear Methods:**
- t-SNE: Excellent for visualization, preserves local structure, computationally expensive.
- UMAP: Faster than t-SNE, preserves global and local structure, better scalability.
- Kernel PCA: Non-linear extension of PCA using kernel trick.
- Autoencoders: Neural network-based, learns non-linear mappings, requires training.
- ICA (Independent Component Analysis): Separates mixed signals into independent sources.

**When to use Dimensionality Reduction:**
- High-dimensional data (curse of dimensionality)
- Visualization (reduce to 2D/3D)
- Noise reduction
- Preprocessing before clustering/classification
- Feature extraction

### ASSOCIATION RULE LEARNING (Pattern Discovery)
- Apriori: Classic algorithm, finds frequent itemsets and association rules.
- Eclat: Depth-first search, faster than Apriori for certain datasets.
- FP-Growth: Faster than Apriori, uses frequent pattern tree structure.

**When to use Association Rules:**
- Market basket analysis (what items are bought together)
- Recommendation systems
- Finding correlations between variables
- Pattern mining in transactional data

### ANOMALY DETECTION (Outlier Identification)
- Isolation Forest: Fast, effective for high dimensions, no assumptions about data distribution.
- One-Class SVM: Learns boundary around normal data.
- Local Outlier Factor (LOF): Density-based, identifies local anomalies.
- Elliptic Envelope: Assumes Gaussian distribution, fits ellipse around normal data.
- DBSCAN: Can identify outliers as noise points.
- Autoencoders: Neural network reconstruction error for anomaly detection.

**When to use Anomaly Detection:**
- Fraud detection, network intrusion detection
- Quality control, fault detection
- Identifying unusual patterns in data

## 3. ALGORITHM SELECTION GUIDELINES

### For CLASSIFICATION tasks:
- **Interpretability priority**: Logistic Regression, Decision Tree
- **Feature importance analysis**: Decision Tree, Random Forest, XGBoost (with feature_importances_)
- **High accuracy, tabular data**: XGBoost, LightGBM, CatBoost, Random Forest
- **Small dataset**: Naive Bayes, Logistic Regression, KNN
- **High-dimensional sparse data**: Logistic Regression with L1, Linear SVM
- **Image data**: CNN (ResNet, VGG, EfficientNet)
- **Text data**: Naive Bayes, Logistic Regression, LSTM, Transformers
- **Imbalanced classes**: XGBoost with scale_pos_weight, SMOTE + ensemble, class weights
- **Real-time prediction**: Logistic Regression, Decision Tree, Linear SVM (fast inference)

### For REGRESSION tasks:
- **Linear relationships**: Linear Regression, Ridge, Lasso
- **Non-linear relationships**: Random Forest, XGBoost, SVR, Neural Networks
- **Feature selection needed**: Lasso, Elastic Net
- **Multicollinearity**: Ridge, Elastic Net
- **Time series**: ARIMA, Prophet, LSTM/GRU
- **High accuracy required**: XGBoost, LightGBM, CatBoost, stacked ensembles

### For CLUSTERING tasks:
- **Spherical clusters, known k**: K-Means
- **Arbitrary shapes**: DBSCAN, OPTICS
- **Probabilistic clustering**: GMM
- **Hierarchical structure needed**: Hierarchical Clustering
- **Large datasets**: Mini-Batch K-Means, BIRCH

### For DIMENSIONALITY REDUCTION:
- **Visualization (2D/3D)**: t-SNE, UMAP
- **Preprocessing for ML**: PCA, SVD
- **Non-linear relationships**: Kernel PCA, Autoencoders, UMAP
- **Fast computation needed**: PCA

### For FEATURE IMPORTANCE / ASSOCIATION ANALYSIS:
- **ALWAYS prefer**: Decision Tree, Random Forest, XGBoost, LightGBM
- **Rationale**: Tree-based models provide built-in feature_importances_ showing which features contribute most to predictions
- **Use CLASSIFICATION over REGRESSION**: Even if target is continuous, bin it into categories for better feature importance interpretability

## 4. ENSEMBLE METHODS (Combining Multiple Models)
- **Bagging (Bootstrap Aggregating)**: Random Forest - reduces variance, parallel training
- **Boosting**: XGBoost, LightGBM, CatBoost, AdaBoost - reduces bias, sequential training
- **Stacking**: Combine predictions from multiple models using meta-learner
- **Voting**: Combine predictions via majority vote (classification) or averaging (regression)

**When to recommend Ensembles:**
- Almost always for high-stakes predictions
- When single models underperform
- To balance bias-variance tradeoff
- Random Forest and XGBoost are safe default recommendations for most tabular data tasks

## 5. RECOMMENDATION STRATEGY

For EVERY task, recommend 3-5 algorithms ranked by suitability:
1. **Best algorithm** for this specific task (considering user requirements)
2. **Safe robust alternative** (e.g., Random Forest if XGBoost is #1)
3. **Interpretable baseline** (e.g., Logistic Regression for classification)
4. **Advanced option** (e.g., Neural Network if data is large enough)
5. **Domain-specific option** (e.g., Prophet for time series if applicable)

Always explain WHY each algorithm is recommended based on:
- Task type and user requirements
- Data characteristics (size, dimensions, type)
- Trade-offs (accuracy vs interpretability vs speed)
- Practical considerations (training time, inference speed, resource requirements)
</ml_algorithm_knowledge_base>

<examples>
Example 1:
User: "Predict house prices using the price column"
Available columns: ["price", "bedrooms", "bathrooms", "sqft"]
Output:
{{
  "target_column": "price",
  "experiment_name": "house_price_prediction",
  "test_size": 0.2,
  "random_state": 42,
  "analysis_type": "regression",
  "recommended_algorithms": [
    "XGBoost",
    "Random Forest Regressor",
    "Ridge Regression",
    "LightGBM"
  ],
  "algorithm_rationale": "XGBoost and LightGBM are recommended for their state-of-art accuracy on tabular data with built-in handling of non-linear relationships. Random Forest provides a robust ensemble alternative. Ridge Regression serves as an interpretable baseline and handles multicollinearity well for house price data.",
  "confidence": 0.98,
  "reasoning": {{
    "target_column": "User explicitly mentioned 'price column' and 'predict house prices'",
    "experiment_name": "Derived from user's description 'house price prediction'",
    "test_size": "Standard 80/20 split, not specified by user",
    "random_state": "Default value for reproducibility",
    "analysis_type": "Price prediction is a regression task (continuous numeric target)",
    "recommended_algorithms": "Selected gradient boosting methods (XGBoost, LightGBM) for high accuracy, Random Forest for robustness, and Ridge for interpretability. These handle non-linear relationships in housing data well."
  }},
  "assumptions": [
    "Assumed price column contains numeric values suitable for regression",
    "Assumed standard test_size since not specified",
    "Assumed tabular data with potential non-linear relationships between features and price"
  ],
  "warnings": []
}}

Example 2:
User: "Analyze customer churn using status"
Available columns: ["customer_id", "status", "age", "income", "tenure"]
Output:
{{
  "target_column": "status",
  "experiment_name": "customer_churn_analysis",
  "test_size": 0.2,
  "random_state": 42,
  "analysis_type": "classification",
  "recommended_algorithms": [
    "XGBoost",
    "Random Forest",
    "Logistic Regression",
    "LightGBM",
    "SVM"
  ],
  "algorithm_rationale": "XGBoost and LightGBM excel at handling imbalanced churn data with built-in class weighting and feature importance. Random Forest provides robust predictions with good interpretability. Logistic Regression serves as an interpretable baseline showing which features increase churn probability. SVM is effective for this type of binary classification task.",
  "confidence": 0.92,
  "reasoning": {{
    "target_column": "User mentioned 'churn' and 'status' - status likely indicates churn/active",
    "experiment_name": "Derived from 'customer churn analysis'",
    "test_size": "Standard split, not specified",
    "random_state": "Default for reproducibility",
    "analysis_type": "Churn analysis is classification (binary: churned vs active)",
    "recommended_algorithms": "Churn prediction typically involves class imbalance. XGBoost and LightGBM handle this well. Included interpretable models (Logistic Regression, Random Forest) to understand churn drivers."
  }},
  "assumptions": [
    "Assumed 'status' column contains categorical churn labels",
    "Assumed binary classification (not multi-class)",
    "Assumed potential class imbalance (fewer churned customers than active)"
  ],
  "warnings": [
    "Could not confirm if 'status' is binary or multi-class without seeing values"
  ]
}}

Example 3:
User: "Build a model for sales forecasting"
Available columns: ["date", "sales", "region", "product_category"]
Output:
{{
  "target_column": "sales",
  "experiment_name": "sales_forecasting",
  "test_size": 0.2,
  "random_state": 42,
  "analysis_type": "time_series",
  "recommended_algorithms": [
    "LSTM",
    "Prophet",
    "XGBoost",
    "ARIMA",
    "LightGBM"
  ],
  "algorithm_rationale": "LSTM and GRU excel at capturing temporal dependencies and sequential patterns in sales data. Prophet is specifically designed for business forecasting with automatic handling of trends, seasonality, and holidays. XGBoost and LightGBM can be adapted for time series with proper feature engineering (lag features, rolling statistics). ARIMA provides a classical time series baseline.",
  "confidence": 0.88,
  "reasoning": {{
    "target_column": "User mentioned 'sales forecasting' - sales is the target",
    "experiment_name": "Direct from user's description",
    "test_size": "Standard split",
    "random_state": "Default value",
    "analysis_type": "Time series analysis detected due to 'forecasting' keyword and presence of date column. Sales forecasting requires handling temporal dependencies.",
    "recommended_algorithms": "Selected time-series specific algorithms (LSTM, Prophet, ARIMA) for proper temporal modeling. Included gradient boosting methods that can work with engineered time features."
  }},
  "assumptions": [
    "Assumed 'sales' column contains numeric amounts",
    "Assumed chronological ordering based on date column is important",
    "Assumed temporal patterns (trends, seasonality) exist in sales data"
  ],
  "warnings": [
    "Time series forecasting requires chronological train/test split, not random split",
    "May need to engineer time-based features (lag, rolling means, seasonality indicators)",
    "Date column should be converted to datetime and used for temporal ordering"
  ]
}}

Example 4 (ASSOCIATION ANALYSIS - KEY EXAMPLE):
User: "Identify which keys, tempos, or time signatures are most associated with high popularity"
Available columns: ["track_id", "popularity", "key", "tempo", "time_signature", "danceability", "energy"]
Output:
{{
  "target_column": "popularity",
  "experiment_name": "music_feature_association_analysis",
  "test_size": 0.2,
  "random_state": 42,
  "analysis_type": "feature_importance",
  "recommended_algorithms": [
    "Decision Tree",
    "Random Forest",
    "XGBoost",
    "LightGBM",
    "SHAP with any model"
  ],
  "algorithm_rationale": "Decision Tree is perfect for feature importance analysis as it provides highly interpretable rules showing which features (key, tempo, time_signature) split the data into high vs low popularity. Random Forest and XGBoost provide robust feature importance rankings through built-in feature_importances_ attributes. LightGBM offers fast feature importance calculation. SHAP values can be applied to any model for detailed feature contribution analysis. All these enable identifying which musical attributes are most associated with popularity.",
  "confidence": 0.92,
  "reasoning": {{
    "target_column": "User wants to identify associations with 'high popularity' - popularity is the target to analyze",
    "experiment_name": "Derived from feature association analysis goal with music data",
    "test_size": "Standard 80/20 split for classification",
    "random_state": "Default for reproducibility",
    "analysis_type": "FEATURE IMPORTANCE analysis type chosen because user explicitly asks to 'identify which features are most associated with' popularity. This is not a prediction task but an association/attribution task. Popularity will be binned into categories (high/low) to enable classification-based feature importance analysis using tree models.",
    "recommended_algorithms": "Tree-based algorithms (Decision Tree, Random Forest, XGBoost) are ESSENTIAL for this task as they provide interpretable feature importance scores. Decision Tree shows explicit rules, while ensemble methods provide robust importance rankings."
  }},
  "assumptions": [
    "Assumed popularity will be binned into binary categories (high vs low) or multi-class (high/medium/low) for classification",
    "Assumed user wants feature importance/association analysis, not exact popularity prediction",
    "Assumed tree-based models will be used for interpretability and feature importance",
    "Assumed 'high popularity' refers to top N% or above-median popularity scores",
    "Assumed the goal is to understand WHICH features matter, not to predict exact popularity values"
  ],
  "warnings": [
    "The actual threshold for 'high popularity' will need to be determined from data distribution",
    "Popularity should be binned into categories before training for better interpretability",
    "Feature importance analysis works best with classification, not regression"
  ]
}}

Example 5 (ANOTHER ASSOCIATION QUERY):
User: "What factors lead to customer churn?"
Available columns: ["customer_id", "churned", "age", "tenure", "monthly_spend", "support_calls"]
Output:
{{
  "target_column": "churned",
  "experiment_name": "churn_factor_analysis",
  "test_size": 0.2,
  "random_state": 42,
  "analysis_type": "feature_importance",
  "recommended_algorithms": [
    "Decision Tree",
    "Random Forest",
    "XGBoost",
    "Logistic Regression",
    "SHAP with XGBoost"
  ],
  "algorithm_rationale": "Decision Tree provides clear, interpretable rules showing which factors (age, tenure, support_calls) lead to churn. Random Forest and XGBoost offer robust feature importance rankings showing which factors contribute most to churn prediction. Logistic Regression provides coefficient analysis showing how each factor influences churn probability. SHAP analysis adds detailed per-feature contribution explanations. All enable answering 'what factors lead to churn'.",
  "confidence": 0.95,
  "reasoning": {{
    "target_column": "User asks 'what factors lead to churn' - churned is clearly the target",
    "experiment_name": "Focused on factor/feature analysis of churn",
    "test_size": "Standard split",
    "random_state": "Default",
    "analysis_type": "FEATURE IMPORTANCE chosen because user asks 'what factors lead to' churn. This is a causal/association question requiring feature importance analysis, not just prediction. Classification will be used with interpretable models to identify key churn drivers.",
    "recommended_algorithms": "Tree-based models provide feature importance showing which factors matter most. Logistic Regression shows directional effects (positive/negative coefficients). These algorithms directly answer the user's question about churn factors."
  }},
  "assumptions": [
    "Assumed 'churned' is binary (yes/no or 1/0)",
    "Assumed user wants to understand which features (age, tenure, etc.) are most predictive of churn",
    "Assumed tree-based models will provide feature importance insights",
    "Assumed the goal is identifying factors, not just predicting churn"
  ],
  "warnings": []
}}
</examples>

<critical_instructions>
1. Return ONLY valid JSON, no additional text before or after
2. Ensure target_column EXACTLY matches one of the available columns (case-sensitive)
3. If confidence < 0.70, still return JSON but add warnings explaining uncertainty
4. Do NOT invent column names - only use available_columns
5. Be conservative with confidence scores - only use > 0.90 when very certain
6. If multiple columns could be targets, choose the most likely and note in warnings
</critical_instructions>

Analyze the user prompt and return the configuration JSON:"""

        return prompt

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Bedrock response and extract configuration.

        Args:
            response: Raw response text from Bedrock

        Returns:
            Dictionary with extracted configuration

        Raises:
            ValueError: If response cannot be parsed, validation fails, or confidence too low
        """
        logger.debug(f"Parsing response: {response[:200]}...")

        # Extract JSON from response (handle cases where model adds extra text)
        json_str = self._extract_json(response)

        if not json_str:
            raise ValueError("No valid JSON found in Bedrock response")

        # Parse JSON
        try:
            config = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

        # Validate required fields
        required_fields = [
            "target_column", "experiment_name", "test_size",
            "random_state", "analysis_type", "recommended_algorithms",
            "algorithm_rationale", "confidence", "reasoning"
        ]

        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Validate confidence
        confidence = config.get("confidence", 0.0)
        if not isinstance(confidence, (int, float)):
            raise ValueError(f"Confidence must be numeric, got: {type(confidence)}")

        if confidence < self.confidence_threshold:
            warnings = config.get("warnings", [])
            warnings_str = "; ".join(warnings) if warnings else "Unknown reasons"
            raise ValueError(
                f"Confidence {confidence:.2f} below threshold {self.confidence_threshold:.2f}. "
                f"Warnings: {warnings_str}. "
                f"Consider trying the fallback model or providing more explicit prompts."
            )

        # Validate analysis_type
        valid_analysis_types = [
            "classification", "regression", "clustering", "dimensionality_reduction",
            "association_rules", "anomaly_detection", "time_series", "feature_importance"
        ]
        analysis_type = config.get("analysis_type", "").lower()
        if analysis_type not in valid_analysis_types:
            raise ValueError(
                f"analysis_type must be one of {valid_analysis_types}, got: {analysis_type}"
            )

        # Validate recommended_algorithms
        recommended_algorithms = config.get("recommended_algorithms", [])
        if not isinstance(recommended_algorithms, list):
            raise ValueError(
                f"recommended_algorithms must be a list, got: {type(recommended_algorithms)}"
            )
        if len(recommended_algorithms) < 3 or len(recommended_algorithms) > 5:
            raise ValueError(
                f"recommended_algorithms must contain 3-5 algorithms, got: {len(recommended_algorithms)}"
            )
        for algo in recommended_algorithms:
            if not isinstance(algo, str) or not algo.strip():
                raise ValueError(
                    f"Each algorithm must be a non-empty string, got: {algo}"
                )

        # Validate algorithm_rationale
        algorithm_rationale = config.get("algorithm_rationale", "")
        if not isinstance(algorithm_rationale, str) or not algorithm_rationale.strip():
            raise ValueError(
                "algorithm_rationale must be a non-empty string"
            )

        # Validate test_size
        test_size = config.get("test_size", 0.2)
        if not isinstance(test_size, (int, float)) or not (0.0 < test_size < 1.0):
            raise ValueError(f"test_size must be between 0.0 and 1.0, got: {test_size}")

        # Validate random_state
        random_state = config.get("random_state", 42)
        if not isinstance(random_state, int) or random_state < 0:
            raise ValueError(f"random_state must be non-negative integer, got: {random_state}")

        # Validate experiment_name format
        experiment_name = config.get("experiment_name", "")
        if not experiment_name or len(experiment_name) > 50:
            raise ValueError(f"experiment_name must be 1-50 characters, got: {len(experiment_name)}")

        if not re.match(r'^[a-z0-9_]+$', experiment_name):
            raise ValueError(
                f"experiment_name must be lowercase with underscores only, got: {experiment_name}"
            )

        # Extract algorithm info for logging
        recommended_algorithms = config.get("recommended_algorithms", [])
        algorithms_str = ", ".join(recommended_algorithms[:3])  # Show first 3

        logger.info(
            f"Successfully extracted config: target={config['target_column']}, "
            f"type={config['analysis_type']}, confidence={confidence:.2f}, "
            f"algorithms=[{algorithms_str}]"
        )

        return config

    def _extract_json(self, response: str) -> str:
        """
        Extract JSON object from response text.

        Handles cases where model adds explanatory text before/after JSON.

        Args:
            response: Raw response text

        Returns:
            Extracted JSON string or None if not found
        """
        # Try to find JSON object in response
        # Look for patterns like {...} or [...]
        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'

        matches = re.finditer(json_pattern, response, re.DOTALL)

        for match in matches:
            json_candidate = match.group(0)
            try:
                # Validate it's actually valid JSON
                json.loads(json_candidate)
                return json_candidate
            except json.JSONDecodeError:
                continue

        # If no JSON object found, maybe it's the entire response
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError:
            pass

        return None

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get default decision when agent fails.

        For ConfigExtraction Agent, there is NO safe default.
        Per user requirements, we raise an error instead of using heuristics.

        Args:
            context: Context data (unused)

        Raises:
            ValueError: Always raises - no default fallback for config extraction
        """
        raise ValueError(
            "ConfigExtraction Agent failed to extract configuration. "
            "No automatic fallback available. "
            "Please try: "
            "1. Using the fallback model (Claude 3.7 Sonnet), "
            "2. Providing more explicit prompts with column names, "
            "3. Using user_hints parameter to guide extraction, "
            "4. Manually specifying configuration parameters."
        )
