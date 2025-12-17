from fastmcp import Context
from typing import Any, Annotated, List, Dict, Optional, Union, Dict, Literal
from pydantic import Field
import json
from errors import handle_aws_api_error, ClientError, ServerError

async def list_resources(
    ctx: Context,
    resource_types: list[str] = Field(
        description='A list of AWS resource types (e.g., ["AWS::S3::Bucket", "AWS::RDS::DBInstance"])'
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """List AWS resources for multiple specified types.

    Parameters:
        resource_types: List of AWS resource types (e.g., ["AWS::S3::Bucket", "AWS::RDS::DBInstance"])
        region: AWS region to use (e.g., "us-east-1", "us-west-2")

    Returns:
        A dictionary mapping resource type to a list of resource identifiers
    """
    aws_session = ctx.fastmcp.aws_session
    aws_region_name = ctx.fastmcp.region_name
    aws_session_config = ctx.fastmcp.session_config

    if not resource_types or not isinstance(resource_types, list):
        raise ClientError('Please provide a list of resource types (e.g., ["AWS::S3::Bucket"])')

    cloudcontrol = aws_session.client('cloudcontrol', region_name=region)
    paginator = cloudcontrol.get_paginator('list_resources')

    all_results = {}
    for resource_type in resource_types:
        results = []
        page_iterator = paginator.paginate(TypeName=resource_type)
        try:
            for page in page_iterator:
                results.extend(page['ResourceDescriptions'])
        except Exception as e:
            # Optionally, you can skip errors for a type or collect errors per type
            all_results[resource_type] = {'error': str(e)}
            continue
        all_results[resource_type] = [response['Identifier'] for response in results]

    return all_results