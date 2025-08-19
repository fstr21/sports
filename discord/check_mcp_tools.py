#!/usr/bin/env python3
"""
Check what tools are available on the Soccer MCP server
"""

import asyncio
import httpx
import json

async def check_available_tools():
    """Check what tools are available on the MCP server"""
    print("🔍 Checking Available MCP Tools")
    print("=" * 40)
    
    mcp_url = "https://soccermcp-production.up.railway.app/mcp"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            response = await client.post(mcp_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("result", {}).get("tools", [])
                
                print(f"Found {len(tools)} available tools:")
                print("-" * 40)
                
                for tool in tools:
                    name = tool.get("name", "Unknown")
                    description = tool.get("description", "No description")
                    print(f"🔧 {name}")
                    print(f"   📝 {description}")
                    
                    # Show input schema if available
                    if "inputSchema" in tool:
                        schema = tool["inputSchema"]
                        if "properties" in schema:
                            print(f"   📋 Parameters:")
                            for param, details in schema["properties"].items():
                                param_type = details.get("type", "unknown")
                                param_desc = details.get("description", "")
                                print(f"      - {param} ({param_type}): {param_desc}")
                    print()
                
                return tools
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return []
                
    except Exception as e:
        print(f"Exception: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(check_available_tools())