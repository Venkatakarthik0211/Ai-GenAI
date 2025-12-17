"""
AI Decision Agents Module

Provides AWS Bedrock-powered decision agents for the ML pipeline.

Available Agents:
- ConfigExtractionAgent: Extracts configuration from natural language (Agent 0)
- AlgorithmSelectionAgent: Selects which algorithms to train (Agent 1)
- ModelSelectionAgent: Selects best model from trained algorithms (Agent 2)
- RetrainingDecisionAgent: Decides if retraining is needed (Agent 3)
"""

from agents.base_agent import BaseDecisionAgent
from agents.config_extraction import ConfigExtractionAgent
from agents.algorithm_category_predictor import AlgorithmCategoryPredictorAgent
from agents.preprocessing_question_generator import PreprocessingQuestionGeneratorAgent
# Old agent - keeping for backwards compatibility
from agents.review_question_generator import ReviewQuestionGeneratorAgent

__all__ = [
    "BaseDecisionAgent",
    "ConfigExtractionAgent",
    "AlgorithmCategoryPredictorAgent",
    "PreprocessingQuestionGeneratorAgent",
    "ReviewQuestionGeneratorAgent",  # Deprecated - use Agent 1A + 1B instead
]
