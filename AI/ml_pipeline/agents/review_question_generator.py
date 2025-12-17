"""
Review Question Generator Agent (Agent 1)

Generates validation questions for human-in-the-loop review after Agent 0.
This agent creates questions to confirm the extracted configuration and data quality.
"""

import json
import logging
import re
from typing import Dict, Any, List

from agents.base_agent import BaseDecisionAgent

logger = logging.getLogger(__name__)


class ReviewQuestionGeneratorAgent(BaseDecisionAgent):
    """
    Agent 1: Review Question Generator

    Analyzes Agent 0's extracted configuration and data profile to generate
    validation questions for the user.

    Generates questions about:
    - Target column correctness
    - Analysis type (classification vs regression) appropriateness
    - Data quality and completeness
    - Test/train split appropriateness
    - Any potential issues or concerns

    Returns:
    - List of questions with question_type (yes/no, multiple_choice, text)
    - Question context and explanations
    - Suggested answers or options
    - Priority level for each question
    """

    def __init__(
        self,
        bedrock_model_id: str,
        aws_region: str = "us-east-1",
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        fallback_model_id: str = None,
        temperature: float = 0.3,  # Slightly higher for more natural questions
        max_tokens: int = 4096
    ):
        """
        Initialize ReviewQuestionGenerator Agent.

        Args:
            bedrock_model_id: Primary Bedrock model ID
            aws_region: AWS region
            aws_access_key_id: AWS access key (optional)
            aws_secret_access_key: AWS secret key (optional)
            fallback_model_id: Fallback model ID if primary fails
            temperature: Sampling temperature (default 0.3 for natural questions)
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
        logger.info(f"ReviewQuestionGeneratorAgent initialized (temperature={temperature})")

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build structured prompt for review question generation.

        Args:
            context: Dictionary containing:
                - user_prompt: Original user prompt
                - extracted_config: Configuration extracted by Agent 0
                - agent0_confidence: Agent 0's confidence score
                - data_profile: Data profile from load_data node
                - config_reasoning: Agent 0's reasoning
                - config_assumptions: Agent 0's assumptions
                - config_warnings: Agent 0's warnings

        Returns:
            XML-formatted prompt string
        """
        user_prompt = context.get("user_prompt", "")
        extracted_config = context.get("extracted_config", {})
        agent0_confidence = context.get("agent0_confidence", 0.0)
        data_profile = context.get("data_profile", {})
        config_reasoning = context.get("config_reasoning", {})
        config_assumptions = context.get("config_assumptions", [])
        config_warnings = context.get("config_warnings", [])

        # Format extracted config
        config_str = json.dumps(extracted_config, indent=2)

        # Format data profile
        data_profile_str = f"""- Number of samples: {data_profile.get('n_samples', 'unknown')}
- Number of features: {data_profile.get('n_features', 'unknown')}
- Target column: {data_profile.get('target_column', 'unknown')}
- Feature names: {', '.join(data_profile.get('feature_names', [])[:10])}{"..." if len(data_profile.get('feature_names', [])) > 10 else ""}"""

        # Format assumptions and warnings
        assumptions_str = "\n".join(f"  - {a}" for a in config_assumptions) if config_assumptions else "  None"
        warnings_str = "\n".join(f"  - {w}" for w in config_warnings) if config_warnings else "  None"

        prompt = f"""<role>
You are an expert ML validation assistant. Your task is to generate clear, concise validation questions to confirm that the AI-extracted configuration and loaded data are correct before proceeding with the ML pipeline.
</role>

<task>
Generate 3-5 validation questions for the user to review and confirm:

1. Questions should be **actionable** - user can answer yes/no, select from options, or provide brief text
2. Focus on **critical validations** that could affect pipeline success
3. Questions should be **clear and specific** - no technical jargon unless necessary
4. Prioritize questions based on Agent 0's confidence and warnings

Each question should have:
- **question_id**: Unique identifier (e.g., "q1", "q2", etc.)
- **question_text**: The question to ask the user
- **question_type**: "yes_no", "multiple_choice", or "text_input"
- **options**: For multiple_choice, provide 2-4 options as an array
- **context**: Brief explanation of why this question matters
- **priority**: "high", "medium", or "low"
- **default_answer**: Suggested answer (optional)
</task>

<context>
<original_user_prompt>
{user_prompt}
</original_user_prompt>

<agent0_extracted_configuration>
{config_str}
</agent0_extracted_configuration>

<agent0_confidence>
{agent0_confidence:.2f} (out of 1.0)
</agent0_confidence>

<agent0_assumptions>
{assumptions_str}
</agent0_assumptions>

<agent0_warnings>
{warnings_str}
</agent0_warnings>

<loaded_data_profile>
{data_profile_str}
</loaded_data_profile>
</context>

<output_format>
Return ONLY a valid JSON object with this exact structure:

{{
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Is '{extracted_config.get('target_column', 'unknown')}' the correct target column you want to predict?",
      "question_type": "yes_no",
      "options": null,
      "context": "Agent 0 identified this as the target column based on your prompt.",
      "priority": "high",
      "default_answer": "yes"
    }},
    {{
      "question_id": "q2",
      "question_text": "The AI suggests this is a {extracted_config.get('analysis_type', 'unknown')} problem. Do you agree?",
      "question_type": "yes_no",
      "options": null,
      "context": "This determines which algorithms will be used.",
      "priority": "high",
      "default_answer": "yes"
    }},
    {{
      "question_id": "q3",
      "question_text": "The loaded data has {data_profile.get('n_samples', 'X')} samples and {data_profile.get('n_features', 'X')} features. Does this match your expectations?",
      "question_type": "yes_no",
      "options": null,
      "context": "Verifying data was loaded correctly.",
      "priority": "medium",
      "default_answer": "yes"
    }}
  ],
  "summary": "Brief summary of what user is being asked to validate",
  "recommendation": "Proceed with pipeline" or "Review configuration carefully"
}}
</output_format>

<question_generation_guidelines>
1. **High Priority Questions** (MUST include):
   - Confirm target column if Agent 0 confidence < 0.9 or warnings present
   - Confirm analysis type (classification vs regression)
   - Confirm data loaded correctly (row/column counts)

2. **Medium Priority Questions** (include if relevant):
   - Confirm test/train split ratio if non-standard
   - Address specific warnings from Agent 0
   - Confirm feature set makes sense

3. **Low Priority Questions** (optional):
   - Experiment name preference
   - Random seed preference
   - Additional user preferences

4. **Question Types**:
   - Use "yes_no" for simple confirmations (most common)
   - Use "multiple_choice" when there are 2-4 clear alternatives
   - Use "text_input" ONLY when absolutely necessary (requires user typing)

5. **Question Quality**:
   - Be specific (mention actual values, not placeholders)
   - Be concise (one question, one validation point)
   - Provide context (why this matters)
   - Suggest default when appropriate
</question_generation_guidelines>

<examples>
Example 1 - High Confidence, No Warnings:
User Prompt: "Predict house prices using the price column"
Agent 0 Confidence: 0.98
Output:
{{
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Is 'price' the correct target column you want to predict?",
      "question_type": "yes_no",
      "options": null,
      "context": "This will be the value your model predicts.",
      "priority": "high",
      "default_answer": "yes"
    }},
    {{
      "question_id": "q2",
      "question_text": "The loaded data has 1000 samples and 5 features. Does this look correct?",
      "question_type": "yes_no",
      "options": null,
      "context": "Verifying the correct dataset was loaded.",
      "priority": "medium",
      "default_answer": "yes"
    }},
    {{
      "question_id": "q3",
      "question_text": "Ready to proceed with 80/20 train/test split?",
      "question_type": "yes_no",
      "options": null,
      "context": "This is a standard split ratio for model training.",
      "priority": "low",
      "default_answer": "yes"
    }}
  ],
  "summary": "Confirming target column, data loaded correctly, and training parameters",
  "recommendation": "Proceed with pipeline"
}}

Example 2 - Low Confidence, Multiple Warnings:
User Prompt: "Analyze customer data"
Agent 0 Confidence: 0.72
Agent 0 Warnings: ["Target column unclear", "Analysis type ambiguous"]
Output:
{{
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Which column do you want to predict?",
      "question_type": "multiple_choice",
      "options": ["customer_status", "purchase_amount", "churn_label"],
      "context": "The AI couldn't confidently determine your target column.",
      "priority": "high",
      "default_answer": null
    }},
    {{
      "question_id": "q2",
      "question_text": "What type of prediction are you making?",
      "question_type": "multiple_choice",
      "options": ["Classification (categories)", "Regression (numeric values)"],
      "context": "This determines which algorithms to use.",
      "priority": "high",
      "default_answer": null
    }},
    {{
      "question_id": "q3",
      "question_text": "The data has 500 samples. Is this the complete dataset?",
      "question_type": "yes_no",
      "options": null,
      "context": "Small datasets may require different approaches.",
      "priority": "medium",
      "default_answer": "yes"
    }}
  ],
  "summary": "Clarifying target column and analysis type due to ambiguous prompt",
  "recommendation": "Review configuration carefully"
}}
</examples>

<critical_instructions>
1. Return ONLY valid JSON, no additional text before or after
2. Generate 3-5 questions (no more, no less)
3. At least 2 questions must be priority="high"
4. Question IDs must be unique (q1, q2, q3, etc.)
5. question_type must be exactly "yes_no", "multiple_choice", or "text_input"
6. For multiple_choice, options array is REQUIRED and must have 2-4 items
7. For yes_no, options should be null
8. Be specific - use actual values from extracted_config and data_profile
9. Default answers should match the question_type
10. Recommendation must be either "Proceed with pipeline" or "Review configuration carefully"
</critical_instructions>

Generate the validation questions now:"""

        return prompt

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Bedrock response and extract review questions.

        Args:
            response: Raw response text from Bedrock

        Returns:
            Dictionary with questions array and metadata

        Raises:
            ValueError: If response cannot be parsed or validation fails
        """
        logger.debug(f"Parsing response: {response[:200]}...")

        # Extract JSON from response
        json_str = self._extract_json(response)

        if not json_str:
            raise ValueError("No valid JSON found in Bedrock response")

        # Parse JSON
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

        # Validate required fields
        if "questions" not in result:
            raise ValueError("Missing required field: questions")

        questions = result.get("questions", [])

        if not isinstance(questions, list) or len(questions) < 3 or len(questions) > 5:
            raise ValueError(f"Must have 3-5 questions, got: {len(questions)}")

        # Validate each question
        for i, q in enumerate(questions):
            self._validate_question(q, i + 1)

        # Validate at least 2 high priority questions
        high_priority_count = sum(1 for q in questions if q.get("priority") == "high")
        if high_priority_count < 2:
            logger.warning(f"Only {high_priority_count} high priority questions (recommend >= 2)")

        logger.info(f"Successfully generated {len(questions)} review questions")

        return result

    def _validate_question(self, question: Dict[str, Any], question_num: int):
        """
        Validate a single question object.

        Args:
            question: Question dictionary
            question_num: Question number for error messages

        Raises:
            ValueError: If validation fails
        """
        required_fields = [
            "question_id", "question_text", "question_type",
            "context", "priority"
        ]

        for field in required_fields:
            if field not in question:
                raise ValueError(f"Question {question_num} missing required field: {field}")

        # Validate question_type
        question_type = question.get("question_type")
        valid_types = ["yes_no", "multiple_choice", "text_input"]
        if question_type not in valid_types:
            raise ValueError(
                f"Question {question_num}: question_type must be one of {valid_types}, got: {question_type}"
            )

        # Validate options for multiple_choice
        if question_type == "multiple_choice":
            options = question.get("options")
            if not options or not isinstance(options, list):
                raise ValueError(f"Question {question_num}: multiple_choice requires options array")
            if len(options) < 2 or len(options) > 4:
                raise ValueError(f"Question {question_num}: options must have 2-4 items, got: {len(options)}")

        # Validate priority
        priority = question.get("priority")
        valid_priorities = ["high", "medium", "low"]
        if priority not in valid_priorities:
            raise ValueError(
                f"Question {question_num}: priority must be one of {valid_priorities}, got: {priority}"
            )

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

        For ReviewQuestionGenerator, we can provide sensible defaults
        based on Agent 0's output.

        Args:
            context: Context data with extracted_config

        Returns:
            Dictionary with default questions
        """
        logger.warning("ReviewQuestionGenerator failed, using default questions")

        extracted_config = context.get("extracted_config", {})
        data_profile = context.get("data_profile", {})

        default_questions = [
            {
                "question_id": "q1",
                "question_text": f"Is '{extracted_config.get('target_column', 'unknown')}' the correct target column?",
                "question_type": "yes_no",
                "options": None,
                "context": "Confirming the target column for prediction.",
                "priority": "high",
                "default_answer": "yes"
            },
            {
                "question_id": "q2",
                "question_text": f"This appears to be a {extracted_config.get('analysis_type', 'unknown')} problem. Is this correct?",
                "question_type": "yes_no",
                "options": None,
                "context": "Confirming the type of ML problem.",
                "priority": "high",
                "default_answer": "yes"
            },
            {
                "question_id": "q3",
                "question_text": f"The data has {data_profile.get('n_samples', 'unknown')} rows and {data_profile.get('n_features', 'unknown')} columns. Does this look correct?",
                "question_type": "yes_no",
                "options": None,
                "context": "Verifying data was loaded correctly.",
                "priority": "medium",
                "default_answer": "yes"
            }
        ]

        return {
            "questions": default_questions,
            "summary": "Basic validation questions (generated from fallback)",
            "recommendation": "Review configuration carefully"
        }
