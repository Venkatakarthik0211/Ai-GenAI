"""
Base Decision Agent for AWS Bedrock

Provides abstract base class for all AI decision agents in the pipeline.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

from utils.bedrock_client import BedrockClient, BedrockClientError, BedrockModelAccessError, BedrockThrottlingError

logger = logging.getLogger(__name__)


class BaseDecisionAgent(ABC):
    """
    Abstract base class for AI decision agents.

    All decision agents (ConfigExtraction, AlgorithmSelection, ModelSelection, RetrainingDecision)
    inherit from this class and implement the abstract methods.

    Provides:
    - Bedrock client integration
    - Retry logic with exponential backoff
    - Error handling and fallback strategies
    - Structured prompt building and response parsing
    """

    def __init__(
        self,
        bedrock_model_id: str,
        aws_region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        fallback_model_id: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize decision agent.

        Args:
            bedrock_model_id: Primary Bedrock model ID
            aws_region: AWS region
            aws_access_key_id: AWS access key (optional, for user mode)
            aws_secret_access_key: AWS secret key (optional, for user mode)
            fallback_model_id: Fallback model ID if primary fails
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum retry attempts
            retry_delay: Initial delay between retries (seconds)
        """
        self.bedrock_model_id = bedrock_model_id
        self.aws_region = aws_region
        self.fallback_model_id = fallback_model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Initialize Bedrock client
        self.bedrock_client = BedrockClient(
            model_id=bedrock_model_id,
            aws_region=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            max_retries=max_retries,
            retry_delay=retry_delay,
            fallback_model_id=fallback_model_id
        )

        logger.info(f"Initialized {self.__class__.__name__} with model: {bedrock_model_id}")

    @abstractmethod
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build prompt for Bedrock model based on context.

        Args:
            context: Context data for decision making

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Bedrock response and extract structured decision.

        Args:
            response: Raw response text from Bedrock

        Returns:
            Structured decision dictionary

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        pass

    @abstractmethod
    def get_default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get default decision when agent fails.

        Args:
            context: Context data for decision making

        Returns:
            Default decision dictionary

        Raises:
            Exception: If no safe default exists
        """
        pass

    def invoke(
        self,
        context: Dict[str, Any],
        use_fallback: bool = False
    ) -> Dict[str, Any]:
        """
        Invoke agent to make a decision.

        Main execution method that:
        1. Builds prompt from context
        2. Invokes Bedrock model
        3. Parses response
        4. Returns structured decision

        Implements retry logic with exponential backoff.
        Falls back to default decision if all retries fail.

        Args:
            context: Context data for decision making
            use_fallback: If True, use fallback model instead of primary

        Returns:
            Dictionary with:
                - decision: Parsed decision from agent
                - prompt: Prompt sent to Bedrock
                - response: Raw response from Bedrock
                - model_id: Model ID used
                - tokens: Token usage information

        Raises:
            BedrockClientError: On critical failures
        """
        agent_name = self.__class__.__name__
        logger.info(f"{agent_name}: Starting decision process")

        # Build prompt
        try:
            prompt = self.build_prompt(context)
            logger.debug(f"{agent_name}: Built prompt ({len(prompt)} chars)")
        except Exception as e:
            logger.error(f"{agent_name}: Failed to build prompt: {e}")
            raise

        # Try to invoke Bedrock with retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"{agent_name}: Invoking Bedrock (attempt {attempt + 1}/{self.max_retries})")

                # Invoke Bedrock
                bedrock_response = self.bedrock_client.invoke(
                    prompt=prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    use_fallback=use_fallback
                )

                logger.info(
                    f"{agent_name}: Bedrock response received "
                    f"({bedrock_response.input_tokens} in, {bedrock_response.output_tokens} out)"
                )

                # Parse response
                try:
                    decision = self.parse_response(bedrock_response.content)
                    logger.info(f"{agent_name}: Successfully parsed decision")

                    # Return complete result
                    return {
                        "decision": decision,
                        "prompt": prompt,
                        "response": bedrock_response.content,
                        "model_id": bedrock_response.model_id,
                        "tokens": {
                            "input_tokens": bedrock_response.input_tokens,
                            "output_tokens": bedrock_response.output_tokens,
                            "total_tokens": bedrock_response.total_tokens
                        },
                        "stop_reason": bedrock_response.stop_reason
                    }

                except ValueError as e:
                    logger.warning(f"{agent_name}: Failed to parse response: {e}")
                    last_exception = e

                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        logger.info(f"{agent_name}: Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"{agent_name}: Max retries exceeded for parsing")
                        # Try default decision
                        break

            except BedrockModelAccessError as e:
                # No retry for access errors
                logger.error(f"{agent_name}: Model access denied: {e}")
                raise

            except BedrockThrottlingError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"{agent_name}: Throttled, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"{agent_name}: Max retries exceeded for throttling")
                    # Try default decision
                    break

            except BedrockClientError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"{agent_name}: Bedrock error, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"{agent_name}: Max retries exceeded")
                    # Try default decision
                    break

        # All retries failed, try default decision
        logger.warning(f"{agent_name}: All retries failed, attempting default decision")
        try:
            default_decision = self.get_default_decision(context)
            logger.info(f"{agent_name}: Using default decision")

            return {
                "decision": default_decision,
                "prompt": prompt,
                "response": None,
                "model_id": None,
                "tokens": None,
                "fallback": True,
                "error": str(last_exception) if last_exception else "Unknown error"
            }

        except Exception as default_error:
            logger.error(f"{agent_name}: Default decision also failed: {default_error}")
            raise BedrockClientError(
                f"{agent_name} failed after {self.max_retries} retries. "
                f"Last error: {last_exception}. Default decision error: {default_error}"
            )

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get token usage statistics.

        Returns:
            Dictionary with invocation count and token usage
        """
        return self.bedrock_client.get_usage_stats()

    def reset_usage_stats(self):
        """Reset token usage counters"""
        self.bedrock_client.reset_usage_stats()
