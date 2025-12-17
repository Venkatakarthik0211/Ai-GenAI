"""
AWS Bedrock Client Wrapper

Provides a clean interface for interacting with AWS Bedrock Claude models
with retry logic, error handling, and token tracking.

Supports both user mode (with credentials) and service mode (IAM role).
"""

import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


@dataclass
class BedrockResponse:
    """Structured response from Bedrock API"""
    content: str
    input_tokens: int
    output_tokens: int
    model_id: str
    stop_reason: str

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class BedrockClientError(Exception):
    """Base exception for Bedrock client errors"""
    pass


class BedrockModelAccessError(BedrockClientError):
    """Raised when model access is denied"""
    pass


class BedrockThrottlingError(BedrockClientError):
    """Raised when API throttling occurs"""
    pass


class BedrockClient:
    """
    AWS Bedrock client wrapper for Claude models.

    Supports:
    - Both user mode (with credentials) and service mode (IAM role)
    - Retry logic with exponential backoff
    - Token usage tracking
    - Response parsing
    - Primary and fallback model support

    Usage:
        # User mode (development)
        client = BedrockClient(
            model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            aws_region="us-east-1",
            aws_access_key_id="AKIA...",
            aws_secret_access_key="..."
        )

        # Service mode (production)
        client = BedrockClient(
            model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            aws_region="us-east-1"
        )

        # Invoke model
        response = client.invoke(
            prompt="Extract config from: Predict prices using price column",
            temperature=0.0,
            max_tokens=4096
        )
    """

    def __init__(
        self,
        model_id: str,
        aws_region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        fallback_model_id: Optional[str] = None
    ):
        """
        Initialize Bedrock client.

        Args:
            model_id: Primary Bedrock model ID
            aws_region: AWS region for Bedrock
            aws_access_key_id: AWS access key (optional, for user mode)
            aws_secret_access_key: AWS secret key (optional, for user mode)
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            fallback_model_id: Fallback model ID if primary fails
        """
        self.model_id = model_id
        self.aws_region = aws_region
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fallback_model_id = fallback_model_id

        # Create boto3 client
        # If credentials provided, use them (user mode)
        # Otherwise, boto3 will use default credential chain (service mode)
        session_kwargs = {"region_name": aws_region}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key
            logger.info("BedrockClient initialized in USER MODE with provided credentials")
        else:
            logger.info("BedrockClient initialized in SERVICE MODE using default credential chain")

        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                **session_kwargs
            )
            logger.info(f"BedrockClient initialized successfully for region: {aws_region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise BedrockClientError(f"Failed to initialize Bedrock client: {e}")

        # Token usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.invocation_count = 0

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        use_fallback: bool = False
    ) -> BedrockResponse:
        """
        Invoke Bedrock model with retry logic.

        Args:
            prompt: User prompt text
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            use_fallback: If True, use fallback model instead of primary

        Returns:
            BedrockResponse with content and token usage

        Raises:
            BedrockClientError: On invocation failure
            BedrockModelAccessError: On access denied
            BedrockThrottlingError: On throttling
        """
        model_id = self.fallback_model_id if use_fallback else self.model_id

        if not model_id:
            raise BedrockClientError("No model ID available for invocation")

        logger.info(f"Invoking Bedrock model: {model_id}")

        # Build request body
        body = self._build_request_body(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )

        # Retry loop
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self._invoke_with_retry(
                    model_id=model_id,
                    body=body,
                    attempt=attempt
                )

                # Update tracking
                self.total_input_tokens += response.input_tokens
                self.total_output_tokens += response.output_tokens
                self.invocation_count += 1

                logger.info(
                    f"Bedrock invocation successful. "
                    f"Tokens: {response.input_tokens} in, {response.output_tokens} out"
                )

                return response

            except BedrockThrottlingError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Throttling detected, retrying in {delay}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries exceeded for throttling")
                    raise

            except BedrockModelAccessError as e:
                # No retry for access errors
                logger.error(f"Model access denied: {e}")
                raise

            except BedrockClientError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Bedrock error, retrying in {delay}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries exceeded")
                    raise

        # Should not reach here, but just in case
        raise last_exception or BedrockClientError("Invocation failed after retries")

    def _invoke_with_retry(
        self,
        model_id: str,
        body: Dict[str, Any],
        attempt: int
    ) -> BedrockResponse:
        """
        Single invocation attempt.

        Args:
            model_id: Model ID to invoke
            body: Request body
            attempt: Current attempt number

        Returns:
            BedrockResponse

        Raises:
            BedrockClientError: On invocation failure
        """
        try:
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )

            # Parse response
            response_body = json.loads(response['body'].read().decode('utf-8'))

            return self._parse_response(response_body, model_id)

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')

            if error_code == 'AccessDeniedException':
                raise BedrockModelAccessError(
                    f"Access denied to model {model_id}. "
                    f"Please request model access in AWS Bedrock console. "
                    f"Error: {error_message}"
                )
            elif error_code in ['ThrottlingException', 'TooManyRequestsException']:
                raise BedrockThrottlingError(
                    f"API throttling for model {model_id}: {error_message}"
                )
            else:
                raise BedrockClientError(
                    f"Bedrock API error (code: {error_code}): {error_message}"
                )

        except BotoCoreError as e:
            raise BedrockClientError(f"Boto3 error: {e}")

        except json.JSONDecodeError as e:
            raise BedrockClientError(f"Failed to parse Bedrock response: {e}")

        except Exception as e:
            raise BedrockClientError(f"Unexpected error invoking Bedrock: {e}")

    def _build_request_body(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """
        Build request body for Bedrock Claude model.

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            system_prompt: Optional system prompt

        Returns:
            Request body dict
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        if system_prompt:
            body["system"] = system_prompt

        return body

    def _parse_response(
        self,
        response_body: Dict[str, Any],
        model_id: str
    ) -> BedrockResponse:
        """
        Parse Bedrock API response.

        Args:
            response_body: Raw response body
            model_id: Model ID used

        Returns:
            BedrockResponse

        Raises:
            BedrockClientError: If response format is invalid
        """
        try:
            # Extract content from response
            content_blocks = response_body.get('content', [])
            if not content_blocks:
                raise BedrockClientError("No content in Bedrock response")

            # Concatenate all text content
            content = ""
            for block in content_blocks:
                if block.get('type') == 'text':
                    content += block.get('text', '')

            # Extract token usage
            usage = response_body.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)

            # Extract stop reason
            stop_reason = response_body.get('stop_reason', 'unknown')

            return BedrockResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model_id=model_id,
                stop_reason=stop_reason
            )

        except Exception as e:
            raise BedrockClientError(f"Failed to parse Bedrock response: {e}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get token usage statistics.

        Returns:
            Dict with usage stats
        """
        return {
            "invocation_count": self.invocation_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }

    def reset_usage_stats(self):
        """Reset token usage counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.invocation_count = 0
        logger.info("BedrockClient usage stats reset")


def create_bedrock_client_from_env() -> BedrockClient:
    """
    Create BedrockClient from environment variables.

    Expected environment variables:
    - BEDROCK_MODEL_ID (required)
    - AWS_REGION (default: us-east-1)
    - AWS_ACCESS_KEY_ID (optional, for user mode)
    - AWS_SECRET_ACCESS_KEY (optional, for user mode)
    - BEDROCK_FALLBACK_MODEL_ID (optional)
    - BEDROCK_MAX_RETRIES (default: 3)

    Returns:
        Configured BedrockClient
    """
    import os

    model_id = os.getenv('BEDROCK_MODEL_ID')
    if not model_id:
        raise ValueError("BEDROCK_MODEL_ID environment variable is required")

    return BedrockClient(
        model_id=model_id,
        aws_region=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        fallback_model_id=os.getenv('BEDROCK_FALLBACK_MODEL_ID'),
        max_retries=int(os.getenv('BEDROCK_MAX_RETRIES', '3'))
    )
