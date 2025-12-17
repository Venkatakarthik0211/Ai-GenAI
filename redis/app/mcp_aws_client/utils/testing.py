"""
Testing utilities for MCP client
"""

from typing import Dict, Any
from ..client.mcp_client import MCPClient


async def test_connection(base_url: str) -> bool:
    """
    Test basic connectivity to MCP server
    
    Args:
        base_url: The base URL of the MCP server
        
    Returns:
        True if connection successful, False otherwise
    """
    print(f"🧪 Testing connection to {base_url}")
    
    client = MCPClient(base_url)
    
    try:
        async with client:
            # Test health check
            health = await client.health_check()
            print(f"🏥 Server health: {health}")
            
            if health.get('status') != 'ok':
                print("❌ Server is not healthy")
                return False
            
            # Test list tools
            tools_result = await client.list_tools()
            
            if 'result' in tools_result and 'tools' in tools_result['result']:
                tools = tools_result['result']['tools']
                print(f"📋 Available tools ({len(tools)}):")
                for tool in tools:
                    name = tool.get('name')
                    description = tool.get('description', 'No description')
                    print(f"  - {name}: {description}")
                    
                    # Show input schema if available
                    input_schema = tool.get('inputSchema', {})
                    if 'properties' in input_schema:
                        print(f"    Parameters: {list(input_schema['properties'].keys())}")
                
                print("✅ Connection test successful")
                return True
            elif 'error' in tools_result:
                print(f"❌ Error: {tools_result['error']}")
                return False
            else:
                print(f"📋 Unexpected response: {tools_result}")
                return False
                
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False


async def run_diagnostic_tests(base_url: str) -> Dict[str, Any]:
    """
    Run comprehensive diagnostic tests
    
    Args:
        base_url: The base URL of the MCP server
        
    Returns:
        Dictionary containing test results
    """
    results = {
        "connection": False,
        "health_check": False,
        "tools_list": False,
        "sample_search": False,
        "errors": []
    }
    
    client = MCPClient(base_url)
    
    try:
        async with client:
            # Test 1: Health check
            try:
                health = await client.health_check()
                results["health_check"] = health.get('status') == 'ok'
                if not results["health_check"]:
                    results["errors"].append(f"Health check failed: {health}")
            except Exception as e:
                results["errors"].append(f"Health check error: {str(e)}")
            
            # Test 2: List tools
            try:
                tools_result = await client.list_tools()
                results["tools_list"] = 'result' in tools_result and 'tools' in tools_result['result']
                if not results["tools_list"]:
                    results["errors"].append(f"Tools list failed: {tools_result}")
            except Exception as e:
                results["errors"].append(f"Tools list error: {str(e)}")
            
            # Test 3: Sample search
            try:
                search_result = await client.call_tool(
                    "search_documentation",
                    arguments={"search_phrase": "AWS IAM best practices"},
                    timeout=30
                )
                results["sample_search"] = not search_result.error
                if search_result.error:
                    results["errors"].append(f"Sample search failed: {search_result.error}")
            except Exception as e:
                results["errors"].append(f"Sample search error: {str(e)}")
            
            results["connection"] = all([
                results["health_check"],
                results["tools_list"],
                results["sample_search"]
            ])
            
    except Exception as e:
        results["errors"].append(f"Client initialization error: {str(e)}")
    
    return results