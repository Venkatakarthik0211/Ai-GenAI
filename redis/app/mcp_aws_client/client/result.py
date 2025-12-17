"""
Result wrapper for MCP responses
"""

from typing import Any, Optional


class MCPResult:
    """Result wrapper to match usage pattern with .data attribute"""
    
    def __init__(self, data: Any = None, error: Optional[str] = None):
        self.data = data
        self.error = error
    
    def __bool__(self) -> bool:
        """Return True if no error occurred"""
        return self.error is None
    
    def __repr__(self) -> str:
        if self.error:
            return f"MCPResult(error='{self.error}')"
        return f"MCPResult(data={type(self.data).__name__})"