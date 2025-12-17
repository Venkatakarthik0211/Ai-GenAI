"""
MCP Client implementation for communicating with MCP servers
"""

import asyncio
import json
import httpx
import uuid
from typing import Dict, Any, Optional

from .result import MCPResult


class MCPClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.mcp_url = f"{self.base_url}/mcp/"
        self.http_client = None
        self.session_id = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(
            timeout=120.0,
            follow_redirects=True,
            headers={
                "User-Agent": "MCP-Client/1.0",
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            }
        )
        
        await self._initialize_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def _initialize_session(self):
        """Initialize MCP session and get server's session ID"""
        payload = {
            "jsonrpc": "2.0",
            "id": "initialize",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "MCP-Python-Client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            print(f"🔄 Initializing session...")
            response = await self.http_client.post(
                self.mcp_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            print(f"📥 Initialize response status: {response.status_code}")
            
            if response.status_code == 200:
                self.session_id = response.headers.get('mcp-session-id')
                print(f"✅ Session initialized successfully: {self.session_id}")
                
                content_type = response.headers.get("content-type", "")
                if "text/event-stream" in content_type:
                    result = await self._handle_streaming_response(response)
                else:
                    result = response.json()
                
                await self._send_initialized_notification()
            else:
                print(f"❌ Failed to initialize session: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Session initialization error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def _send_initialized_notification(self):
        """Send initialized notification"""
        if not self.session_id:
            print("⚠️ No session ID for initialized notification")
            return
            
        payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        try:
            response = await self.http_client.post(
                self.mcp_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )
            print(f"✅ Initialized notification sent: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Failed to send initialized notification: {str(e)}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], timeout: int = 100) -> MCPResult:
        """Call a tool on the MCP server"""
        if not self.session_id:
            print("❌ No active session")
            return MCPResult(data=[], error="No active session")
        
        payload = {
            "jsonrpc": "2.0",
            "id": f"call-{tool_name}-{uuid.uuid4()}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        print(f"🔧 Calling tool: {tool_name}")
        
        try:
            response = await self.http_client.post(
                self.mcp_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                },
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"📥 Error response body: {response.text}")
                return MCPResult(data=[], error=f"HTTP {response.status_code}: {response.text}")
            
            content_type = response.headers.get("content-type", "")
            
            if "text/event-stream" in content_type:
                result = await self._handle_streaming_response(response)
            else:
                result = response.json()
            
            if 'error' in result:
                print(f"❌ MCP Error calling {tool_name}: {result['error']}")
                return MCPResult(data=[], error=result['error'])
            
            tool_result = result.get('result', {})
            return self._process_tool_result(tool_result)
                
        except httpx.TimeoutException:
            print(f"⏰ Timeout calling {tool_name}")
            return MCPResult(data=[], error="Timeout")
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error calling {tool_name}: {e.response.status_code}")
            return MCPResult(data=[], error=f"HTTP {e.response.status_code}")
        except Exception as e:
            print(f"❌ Error calling {tool_name}: {str(e)}")
            return MCPResult(data=[], error=str(e))

    def _process_tool_result(self, tool_result: Dict[str, Any]) -> MCPResult:
        """Process tool result and extract data"""
        if isinstance(tool_result, dict):
            if 'content' in tool_result:
                content = tool_result['content']
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        data = content[0]['text']
                        try:
                            if data.strip().startswith(('[', '{')):
                                data = json.loads(data)
                        except json.JSONDecodeError:
                            pass
                        return MCPResult(data=data)
                    else:
                        return MCPResult(data=content)
                else:
                    return MCPResult(data=content)
            else:
                return MCPResult(data=tool_result)
        else:
            return MCPResult(data=tool_result)

    async def _handle_streaming_response(self, response):
        """Handle server-sent events (streaming) response"""
        result = {}
        async for line in response.aiter_lines():
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    result = data
                except json.JSONDecodeError:
                    continue
        return result

    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        try:
            response = await self.http_client.get(f"{self.base_url}/status")
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        if not self.session_id:
            print("❌ No active session")
            return {"error": "No active session"}
            
        payload = {
            "jsonrpc": "2.0",
            "id": f"list-tools-{uuid.uuid4()}",
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = await self.http_client.post(
                self.mcp_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )
            
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
            
            content_type = response.headers.get("content-type", "")
            
            if "text/event-stream" in content_type:
                result = await self._handle_streaming_response(response)
            else:
                result = response.json()
                
            return result
        except Exception as e:
            print(f"❌ Error listing tools: {str(e)}")
            return {"error": str(e)}