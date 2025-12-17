"""
MCP Client for AWS Documentation and Best Practices
"""

__version__ = "1.0.0"
__author__ = "MCP AWS Client"

from .client.mcp_client import MCPClient
from .client.result import MCPResult
from .config.config_loader import load_config
from .processors.document_processor import DocumentProcessor
from .processors.data_converter import convert_to_dict
from .utils.testing import test_connection

__all__ = [
    'MCPClient',
    'MCPResult', 
    'load_config',
    'DocumentProcessor',
    'convert_to_dict',
    'test_connection'
]