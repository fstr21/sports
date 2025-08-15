#!/usr/bin/env python3
"""
Test the locally installed CFBD MCP server
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

# Add the server path to Python path
server_path = Path(__file__).parent / "lenwood_cfbd-mcp-server" / "src"
sys.path.insert(0, str(server_path))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_local_cfbd_server():
    """Test the locally installed CFBD MCP server"""
    
    # Get the path to the virtual environment python
    server_dir = Path(__file__).parent / "lenwood_cfbd-mcp-server"
    venv_python = server_dir / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print(f"Virtual environment python not found at: {venv_python}")
        return
    
    # Server parameters
    server_params = StdioServerParameters(
        command=str(venv_python),
        args=["-m", "cfbd_mcp_server"],
        cwd=str(server_dir),
        env={
            **os.environ,
            "CFB_API_KEY": "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
        }
    )
    
    print("Starting CFBD MCP server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                print("Initializing session...")
                await session.initialize()
                
                # List available tools
                print("\n=== Available Tools ===")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")
                
                # List available resources
                print("\n=== Available Resources ===")
                try:
                    resources = await session.list_resources()
                    for resource in resources.resources:
                        print(f"- {resource.uri}: {resource.name}")
                except Exception as e:
                    print(f"Could not list resources: {e}")
                
                # Test some tools
                print("\n=== Testing Tools ===")
                
                test_cases = [
                    {
                        "name": "get-games",
                        "args": {"year": 2024, "week": 1}
                    },
                    {
                        "name": "get-records", 
                        "args": {"year": 2024}
                    }
                ]
                
                for test_case in test_cases:
                    try:
                        print(f"\n--- Testing {test_case['name']} ---")
                        result = await session.call_tool(
                            test_case['name'], 
                            test_case['args']
                        )
                        
                        if result.content:
                            content = result.content[0]
                            if hasattr(content, 'text'):
                                data = json.loads(content.text)
                                if isinstance(data, list) and len(data) > 0:
                                    print(f"✅ Success! Found {len(data)} results")
                                    print("Sample result:")
                                    print(json.dumps(data[0], indent=2)[:500] + "...")
                                else:
                                    print("✅ Success! Result:")
                                    print(json.dumps(data, indent=2)[:500] + "...")
                            else:
                                print("✅ Success! Content:", str(content)[:200] + "...")
                        else:
                            print("⚠️  No content returned")
                            
                    except Exception as e:
                        print(f"❌ Error testing {test_case['name']}: {e}")
                
                print("\n🎉 MCP Server test completed!")
                
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")

if __name__ == "__main__":
    asyncio.run(test_local_cfbd_server())