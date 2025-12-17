"""
Streamlit AWS Documentation Dashboard
"""

__version__ = "1.0.0"
__author__ = "AWS Documentation Dashboard"

from .services.redis_service import RedisService
from .services.mcp_service import MCPService
from .components.display import DocumentDisplay
from .components.sidebar import SidebarControls
from .components.tabs import TabManager

__all__ = [
    'RedisService',
    'MCPService', 
    'DocumentDisplay',
    'SidebarControls',
    'TabManager'
]