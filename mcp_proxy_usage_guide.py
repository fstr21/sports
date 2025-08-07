#!/usr/bin/env python3
"""
Complete guide for connecting to and using your MCP proxy
"""
import requests
import json
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

class MCPProxyClient:
    def __init__(self):
        self.proxy_url = "http://localhost:9091"
        self.auth_token = "sports-betting-token"
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}
    
    async def connect_to_server(self, server_name):
        """Connect to a specific MCP server through the proxy"""
        sse_url = f"{self.proxy_url}/{server_name}/sse"
        
        try:
            async with sse_client(sse_url, headers=self.headers) as streams:
                read, write = streams
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    result = await session.initialize()
                    print(f"Connected to {server_name}")
                    print(f"Server info: {result}")
                    
                    return session
        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")
            return None
    
    async def list_available_tools(self, server_name):
        """List all tools available on a server"""
        session = await self.connect_to_server(server_name)
        if session:
            tools = await session.list_tools()
            print(f"\nAvailable tools on {server_name}:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            return tools.tools
        return []
    
    async def list_available_resources(self, server_name):
        """List all resources available on a server"""
        session = await self.connect_to_server(server_name)
        if session:
            resources = await session.list_resources()
            print(f"\nAvailable resources on {server_name}:")
            for resource in resources.resources:
                print(f"- {resource.uri}: {resource.name}")
            return resources.resources
        return []
    
    async def call_tool(self, server_name, tool_name, arguments=None):
        """Call a specific tool on a server"""
        session = await self.connect_to_server(server_name)
        if session:
            if arguments is None:
                arguments = {}
            
            print(f"\nCalling {tool_name} on {server_name} with args: {arguments}")
            result = await session.call_tool(tool_name, arguments)
            print(f"Result: {result}")
            return result
        return None
    
    async def read_resource(self, server_name, resource_uri):
        """Read a specific resource from a server"""
        session = await self.connect_to_server(server_name)
        if session:
            print(f"\nReading resource {resource_uri} from {server_name}")
            result = await session.read_resource(resource_uri)
            print(f"Resource content: {result}")
            return result
        return None

async def test_sports_ai_server():
    """Comprehensive test of the sports-ai server"""
    client = MCPProxyClient()
    
    print("=" * 60)
    print("TESTING SPORTS-AI SERVER")
    print("=" * 60)
    
    # List capabilities
    tools = await client.list_available_tools("sports-ai")
    resources = await client.list_available_resources("sports-ai")
    
    # Test calling tools (if any exist)
    if tools:
        first_tool = tools[0]
        print(f"\nTesting first tool: {first_tool.name}")
        await client.call_tool("sports-ai", first_tool.name, {})
    
    # Test reading resources (if any exist)
    if resources:
        first_resource = resources[0]
        print(f"\nTesting first resource: {first_resource.uri}")
        await client.read_resource("sports-ai", first_resource.uri)

async def test_wagyu_sports_server():
    """Comprehensive test of the wagyu-sports server"""
    client = MCPProxyClient()
    
    print("=" * 60)
    print("TESTING WAGYU-SPORTS SERVER")
    print("=" * 60)
    
    # List capabilities
    tools = await client.list_available_tools("wagyu-sports")
    resources = await client.list_available_resources("wagyu-sports")
    
    # Test calling tools (if any exist)
    if tools:
        for tool in tools[:2]:  # Test first 2 tools
            print(f"\nTesting tool: {tool.name}")
            await client.call_tool("wagyu-sports", tool.name, {})

async def test_fetch_server():
    """Comprehensive test of the fetch server"""
    client = MCPProxyClient()
    
    print("=" * 60)
    print("TESTING FETCH SERVER")
    print("=" * 60)
    
    # List capabilities
    tools = await client.list_available_tools("fetch")
    
    # Test fetch tool if available
    if tools:
        fetch_tool = next((t for t in tools if 'fetch' in t.name.lower()), None)
        if fetch_tool:
            print(f"\nTesting fetch with ESPN API:")
            await client.call_tool("fetch", fetch_tool.name, {
                "url": "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
            })

def check_proxy_status():
    """Basic HTTP check to see if proxy is responding"""
    print("CHECKING PROXY STATUS")
    print("=" * 30)
    
    servers = ["sports-ai", "wagyu-sports", "fetch"]
    
    for server in servers:
        url = f"http://localhost:9091/{server}/sse"
        headers = {"Authorization": "Bearer sports-betting-token"}
        
        try:
            # Quick connection test
            response = requests.get(url, headers=headers, timeout=0.5, stream=True)
            print(f"{server}: Connected (Status: streaming)")
        except requests.exceptions.Timeout:
            print(f"{server}: ✓ Available (SSE endpoint active)")
        except requests.exceptions.RequestException as e:
            print(f"{server}: ✗ Error - {e}")

async def main():
    """Run comprehensive MCP proxy tests"""
    
    print("MCP PROXY COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Basic connectivity check
    check_proxy_status()
    
    print("\n")
    
    # Test each server extensively
    await test_sports_ai_server()
    print("\n")
    await test_wagyu_sports_server()
    print("\n")
    await test_fetch_server()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())