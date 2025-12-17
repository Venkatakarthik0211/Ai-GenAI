"""
Preprocessing Question Generator Agent (Agent 1B)

Second agent in the two-agent HITL preprocessing system.
Generates 4-20 algorithm-aware preprocessing questions tailored to the predicted algorithm category.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseDecisionAgent

logger = logging.getLogger(__name__)


class PreprocessingQuestionGeneratorAgent(BaseDecisionAgent):
    """
    Agent 1B: Preprocessing Question Generator

    Generates algorithm-aware preprocessing questions based on Agent 1A's prediction.
    Creates 4-20 dynamic questions (1-5 per preprocessing step) with technique options
    ranked by algorithm suitability.

    Preprocessing Steps:
    1. clean_data: Outlier handling (8 techniques)
    2. handle_missing: Missing value imputation (7 techniques)
    3. encode_features: Categorical encoding (7 techniques)
    4. scale_features: Feature scaling (7 techniques)

    Returns:
    - questions: List of Question objects with technique options
    - preprocessing_recommendations: Summary of recommendations
    - algorithm_context: Algorithm category and requirements from Agent 1A
    - question_count_by_step: Number of questions per step
    """

    def __init__(
        self,
        bedrock_model_id: str,
        aws_region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        fallback_model_id: Optional[str] = None,
        temperature: float = 0.3,  # Slightly higher for natural phrasing
        max_tokens: int = 4096
    ):
        """
        Initialize PreprocessingQuestionGenerator Agent.

        Args:
            bedrock_model_id: Primary Bedrock model ID
            aws_region: AWS region
            aws_access_key_id: AWS access key (optional)
            aws_secret_access_key: AWS secret key (optional)
            fallback_model_id: Fallback model ID if primary fails
            temperature: Sampling temperature (0.3 for natural questions)
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
        logger.info(f"PreprocessingQuestionGeneratorAgent initialized (temperature={temperature})")

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build structured prompt for algorithm-aware question generation.

        Args:
            context: Dictionary containing:
                - algorithm_category: Predicted category from Agent 1A
                - algorithm_confidence: Agent 1A's confidence
                - algorithm_requirements: Algorithm requirements dict
                - preprocessing_priorities: Preprocessing priorities dict
                - data_profile: Enhanced data profile with missing values, outliers, etc.
                - n_samples: Number of samples
                - n_features: Number of features
                - target_type: "classification" or "regression"

        Returns:
            Formatted prompt string for Bedrock
        """
        algorithm_category = context.get("algorithm_category", "unknown")
        algorithm_confidence = context.get("algorithm_confidence", 0.0)
        algorithm_requirements = context.get("algorithm_requirements", {})
        preprocessing_priorities = context.get("preprocessing_priorities", {})
        data_profile = context.get("data_profile", {})
        n_samples = context.get("n_samples", 0)
        n_features = context.get("n_features", 0)
        target_type = context.get("target_type", "unknown")
        learning_paradigm = context.get("learning_paradigm", "supervised")

        # Different preprocessing approaches for supervised vs unsupervised
        if learning_paradigm == "unsupervised":
            step_name_clean = "clean_outliers"
            clean_data_guidance = """**clean_outliers** (Data Quality Validation - PRESERVE OUTLIERS!):
   - keep_all: Keep all data including outliers (RECOMMENDED - outliers could be clusters!)
   - remove_duplicates: Only remove exact duplicate rows
   - remove_invalid: Only remove inf/-inf/NaN values

   **CRITICAL**: For unsupervised learning, outliers are MEANINGFUL (separate clusters, anomalies to detect)"""

            missing_guidance = """**handle_missing** (Missing Value Imputation - SIMPLE ONLY!):
   - drop_rows: Drop rows with any missing values (PREFERRED - preserves data integrity)
   - drop_columns: Drop columns with high missing percentage
   - simple_imputation: Mean/median/mode imputation (use only if dropping loses too much data)

   **NOT AVAILABLE**: knn_imputation, mice, iterative_imputation (create artificial patterns that mislead clustering)"""

            encode_guidance = """**encode_features** (Categorical Encoding - NO TARGET ENCODING!):
   - label_encoding: Label encoding (ordinal integers) - RECOMMENDED for clustering
   - ordinal_encoding: Ordinal encoding with custom ordering
   - frequency_encoding: Frequency-based encoding
   - hash_encoding: Hash encoding (for high cardinality)

   **NOT AVAILABLE**: target_encoding (no target!), one_hot (dimension explosion)"""

            scale_guidance = """**scale_features** (Feature Scaling - MANDATORY!):
   - standard_scaler: StandardScaler (RECOMMENDED for K-means, PCA)
   - minmax_scaler: MinMaxScaler (scale to [0, 1])
   - robust_scaler: RobustScaler (robust to outliers, good for DBSCAN)
   - maxabs_scaler: MaxAbsScaler (preserves sparsity)

   **CRITICAL**: Scaling is MANDATORY for distance-based algorithms (K-means, DBSCAN)!"""
        else:
            step_name_clean = "clean_data"
            clean_data_guidance = """**clean_data** (Outlier Handling):
   - none: Skip outlier removal
   - iqr_method: Remove outliers using IQR (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
   - z_score: Remove outliers using Z-score threshold (default 3.0)
   - winsorization: Cap outliers at percentiles
   - isolation_forest: Detect outliers using Isolation Forest
   - dbscan: Identify outliers using DBSCAN clustering
   - robust_scalers: Apply RobustScaler to reduce outlier impact
   - domain_clipping: Clip values to domain-specific ranges"""

            missing_guidance = """**handle_missing** (Missing Value Imputation):
   - drop_rows: Drop rows with any missing values
   - simple_imputation: Mean/median/mode imputation
   - knn_imputation: KNN-based imputation (k=5)
   - mice: MICE (Multiple Imputation by Chained Equations)
   - domain_specific: Domain-specific imputation strategies
   - forward_fill: Forward fill for time series
   - interpolation: Linear/polynomial interpolation"""

            encode_guidance = """**encode_features** (Categorical Encoding):
   - one_hot: One-hot encoding (creates binary columns)
   - label_encoding: Label encoding (ordinal integers)
   - target_encoding: Target/mean encoding (uses target statistics)
   - frequency_encoding: Frequency-based encoding
   - binary_encoding: Binary encoding (fewer columns than one-hot)
   - hash_encoding: Hash encoding (fixed dimensionality)
   - embeddings: Learned embeddings (for neural networks)"""

            scale_guidance = """**scale_features** (Feature Scaling):
   - none: Skip scaling (for tree-based models)
   - standard_scaler: StandardScaler (z-score normalization)
   - minmax_scaler: MinMaxScaler (scale to [0, 1])
   - robust_scaler: RobustScaler (uses median and IQR, robust to outliers)
   - maxabs_scaler: MaxAbsScaler (scale by maximum absolute value)
   - normalizer: Normalizer (normalize samples to unit norm)
   - quantile_transformer: QuantileTransformer (transform to uniform/normal distribution)"""

        prompt = f"""You are an expert ML engineer generating preprocessing questions for a HITL review system.

**Learning Paradigm: {learning_paradigm.upper()}**

**Algorithm Context (from Agent 1A):**
- Predicted Category: {algorithm_category}
- Confidence: {algorithm_confidence:.2f}
- Scaling Required: {algorithm_requirements.get('scaling_required', False)}
- Outlier Sensitive: {algorithm_requirements.get('outlier_sensitive', False)}
- Handles Missing: {algorithm_requirements.get('handles_missing', False)}
- Categorical Encoding Preference: {algorithm_requirements.get('categorical_encoding_preference', 'one_hot')}

**Preprocessing Priorities:**
- Clean Data: {preprocessing_priorities.get('clean_data', 'optional')}
- Handle Missing: {preprocessing_priorities.get('handle_missing', 'required')}
- Encode Features: {preprocessing_priorities.get('encode_features', 'required')}
- Scale Features: {preprocessing_priorities.get('scale_features', 'optional')}

**Dataset Characteristics:**
- Samples: {n_samples}
- Features: {n_features}
- Target Type: {target_type}
- Missing Values: {data_profile.get('missing_percentage', 0):.2f}%
- Outliers: {data_profile.get('outlier_percentage', 0):.2f}%
- Categorical Features: {data_profile.get('categorical_count', 0)}
- High Cardinality Features: {data_profile.get('high_cardinality_count', 0)}

**Task:**
Generate 4-20 preprocessing questions (1-5 per step) tailored to the {algorithm_category} category.

**Preprocessing Techniques:**

1. {clean_data_guidance}

2. {missing_guidance}

3. {encode_guidance}

4. {scale_guidance}

**Algorithm-Specific Recommendations for {learning_paradigm.upper()}:**

{"**Supervised Learning Algorithms:**" if learning_paradigm == "supervised" else "**Unsupervised Learning Algorithms:**"}
{"- **linear_models**: Require scaling, sensitive to outliers, prefer winsorization over removal" if learning_paradigm == "supervised" else "- **clustering** (K-means, DBSCAN, Hierarchical): MANDATORY scaling with standard_scaler or robust_scaler"}
{"- **tree_models**: No scaling needed, robust to outliers, handle missing values naturally" if learning_paradigm == "supervised" else "- **dimensionality_reduction** (PCA, t-SNE, UMAP): MANDATORY scaling with standard_scaler"}
{"- **neural_networks**: Require scaling, prefer robust scaling, use KNN/MICE for missing values" if learning_paradigm == "supervised" else "- **anomaly_detection**: Use robust_scaler to preserve outlier information"}
{"- **ensemble**: Depends on base models, generally robust to outliers" if learning_paradigm == "supervised" else ""}
{"- **time_series**: Special handling for temporal ordering, use forward fill/interpolation" if learning_paradigm == "supervised" else ""}

**Question Generation Guidelines:**

1. Generate 1-3 questions per preprocessing step (total 4-12 questions to stay under token limit)
2. For each question, provide 2-3 technique options (keep it concise!)
3. Mark ONE recommended technique with "recommended": true
4. Assign priority: "high", "medium", or "low"
5. Keep context brief (max 1 sentence explaining why this matters)

**Required Output (CONCISE JSON - keep it small!):**
{{
    "questions": [
        {{
            "question_id": "clean_data_q1",
            "preprocessing_step": "clean_data",
            "question_type": "multiple_choice",
            "question_text": "<question>",
            "priority": "high|medium|low",
            "context": "<1 sentence: why this matters>",
            "options": [
                {{
                    "value": "iqr_method",
                    "label": "IQR Method",
                    "recommended": true
                }},
                {{
                    "value": "z_score",
                    "label": "Z-Score Filtering",
                    "recommended": false
                }}
            ]
        }}
    ],
    "preprocessing_recommendations": {{
        "{step_name_clean}": "<technique_name>",
        "handle_missing": "<technique_name>",
        "encode_features": "<technique_name>",
        "scale_features": "<technique_name>"
    }},
    "question_count_by_step": {{
        "{step_name_clean}": <1-3>,
        "handle_missing": <1-3>,
        "encode_features": <1-3>,
        "scale_features": <1-3>
    }}
}}

**CRITICAL - Keep JSON Small:**
- Total questions: 4-12 (1-3 per step, NOT 1-5!)
- Options per question: 2-3 (NOT 2-4!)
- Context: Max 1 sentence
- Labels: Short (5-15 chars)
- NO extra fields beyond what's shown above
- Return ONLY the JSON object, no markdown, no explanations
"""

        return prompt

    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Bedrock response into structured questions.

        Args:
            response_text: Raw response from Bedrock

        Returns:
            Parsed questions with validation

        Raises:
            ValueError: If response cannot be parsed or validation fails
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in response")

            result = json.loads(json_match.group(0))

            # Validate required fields
            required_fields = [
                "questions",
                "preprocessing_recommendations",
                "question_count_by_step"
            ]
            missing = [f for f in required_fields if f not in result]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")

            # Validate questions
            questions = result["questions"]
            if not isinstance(questions, list):
                raise ValueError("'questions' must be a list")

            if len(questions) < 3 or len(questions) > 15:
                logger.warning(
                    f"Question count {len(questions)} outside recommended range 4-12"
                )

            # Validate each question
            for i, q in enumerate(questions):
                required_q_fields = [
                    "question_id", "preprocessing_step", "question_type",
                    "question_text", "priority", "options"
                ]
                missing_q = [f for f in required_q_fields if f not in q]
                if missing_q:
                    raise ValueError(
                        f"Question {i+1} missing fields: {missing_q}"
                    )

                # Validate preprocessing_step (accept both supervised and unsupervised step names)
                valid_steps = ["clean_data", "clean_outliers", "handle_missing", "encode_features", "scale_features"]
                if q["preprocessing_step"] not in valid_steps:
                    raise ValueError(
                        f"Invalid preprocessing_step in question {i+1}: {q['preprocessing_step']}"
                    )

                # Validate question_type
                if q["question_type"] not in ["multiple_choice", "text"]:
                    raise ValueError(
                        f"Invalid question_type in question {i+1}: {q['question_type']}"
                    )

                # Validate priority
                if q["priority"] not in ["high", "medium", "low"]:
                    raise ValueError(
                        f"Invalid priority in question {i+1}: {q['priority']}"
                    )

                # Validate options
                if not q.get("options") or len(q["options"]) < 2:
                    raise ValueError(
                        f"Question {i+1} must have at least 2 options"
                    )

            # Validate question count by step
            question_count = result.get("question_count_by_step", {})
            for step, count in question_count.items():
                if count < 1 or count > 3:
                    logger.warning(
                        f"Question count for {step} is {count}, recommended 1-3"
                    )

            # Log successful generation
            total_questions = len(questions)
            logger.info(
                f"✓ Generated {total_questions} preprocessing questions"
            )
            logger.info(f"  Questions by step: {question_count}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            raise ValueError(f"Invalid JSON in response: {e}")
        except Exception as e:
            logger.error(f"Error parsing preprocessing questions: {e}")
            raise

    def generate_questions(
        self,
        algorithm_category: str,
        algorithm_confidence: float,
        algorithm_requirements: Dict[str, Any],
        preprocessing_priorities: Dict[str, str],
        data_profile: Dict[str, Any],
        n_samples: int,
        n_features: int,
        target_type: str,
        learning_paradigm: str = "supervised"
    ) -> Dict[str, Any]:
        """
        Generate algorithm-aware preprocessing questions.

        Args:
            algorithm_category: Predicted category from Agent 1A
            algorithm_confidence: Agent 1A's confidence
            algorithm_requirements: Algorithm requirements dict
            preprocessing_priorities: Preprocessing priorities dict
            data_profile: Enhanced data profile
            n_samples: Number of samples
            n_features: Number of features
            target_type: "classification", "regression", or "unsupervised"
            learning_paradigm: "supervised" or "unsupervised" (from Agent 1A)

        Returns:
            Questions and recommendations dict

        Raises:
            Exception: If question generation fails
        """
        context = {
            "algorithm_category": algorithm_category,
            "algorithm_confidence": algorithm_confidence,
            "algorithm_requirements": algorithm_requirements,
            "preprocessing_priorities": preprocessing_priorities,
            "data_profile": data_profile,
            "n_samples": n_samples,
            "n_features": n_features,
            "target_type": target_type,
            "learning_paradigm": learning_paradigm
        }

        logger.info(
            f"Generating preprocessing questions for {algorithm_category} category "
            f"({learning_paradigm} learning, confidence: {algorithm_confidence:.2f})"
        )

        # Execute with retry logic (inherited from BaseDecisionAgent)
        result = self.invoke(context)

        return result["decision"]

    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get default preprocessing questions when agent fails.

        Returns minimal set of standard questions that work for most algorithms.

        Args:
            context: Context data (algorithm_category, data_profile, etc.)

        Returns:
            Default questions dict
        """
        logger.warning("Using default preprocessing questions (agent failed)")

        # Minimal safe default questions
        default_questions = [
            {
                "question_id": "default_missing",
                "preprocessing_step": "handle_missing",
                "question_text": "How should we handle missing values?",
                "question_type": "multiple_choice",
                "priority": "high",
                "context": "Missing values need to be handled before model training.",
                "options": [
                    {
                        "value": "mean_imputation",
                        "label": "Mean Imputation (fill with column mean)",
                        "recommended": True,
                        "reasoning": "Simple and effective for numeric features"
                    },
                    {
                        "value": "drop_rows",
                        "label": "Drop Rows (remove rows with missing values)",
                        "recommended": False,
                        "reasoning": "May lose too much data"
                    }
                ]
            },
            {
                "question_id": "default_encoding",
                "preprocessing_step": "encode_features",
                "question_text": "How should we encode categorical variables?",
                "question_type": "multiple_choice",
                "priority": "high",
                "context": "Categorical features need to be encoded as numbers.",
                "options": [
                    {
                        "value": "one_hot_encoding",
                        "label": "One-Hot Encoding",
                        "recommended": True,
                        "reasoning": "Standard approach for categorical features"
                    },
                    {
                        "value": "label_encoding",
                        "label": "Label Encoding (ordinal)",
                        "recommended": False,
                        "reasoning": "Only for ordinal categories"
                    }
                ]
            },
            {
                "question_id": "default_scaling",
                "preprocessing_step": "scale_features",
                "question_text": "Should we scale numerical features?",
                "question_type": "yes_no",
                "priority": "medium",
                "context": "Scaling may be beneficial depending on the algorithm.",
                "recommended_answer": "yes",
                "reasoning": "Scaling is generally helpful for most algorithms"
            }
        ]

        return {
            "questions": default_questions,
            "question_count_by_step": {
                "handle_missing": 1,
                "encode_features": 1,
                "scale_features": 1
            },
            "preprocessing_recommendations": {
                "handle_missing": "mean_imputation",
                "encode_features": "one_hot_encoding",
                "scale_features": "standard_scaler"
            },
            "algorithm_context": {
                "algorithm_category": context.get("algorithm_category", "unknown"),
                "fallback": True
            }
        }
