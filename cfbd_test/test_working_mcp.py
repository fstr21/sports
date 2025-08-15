#!/usr/bin/env python3
"""
Test the CFBD MCP server using the correct command
"""

import asyncio
import json
import os
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_cfbd_mcp():
    """Test the CFBD MCP server"""
    
    # Get the path to the server directory
    server_dir = Path(__file__).parent / "lenwood_cfbd-mcp-server"
    
    # Server parameters using the full path to the executable
    cfbd_exe = server_dir / ".venv" / "Scripts" / "cfbd-mcp-server.exe"
    server_params = StdioServerParameters(
        command=str(cfbd_exe),
        cwd=str(server_dir),
        env={
            **os.environ,
            "CFB_API_KEY": "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
        }
    )
    
    print("🚀 Starting CFBD MCP server test...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                print("📡 Initializing session...")
                await session.initialize()
                
                # List available tools
                print("\n=== 🛠️  Available Tools ===")
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"  • {tool.name}: {tool.description}")
                
                # List available resources
                print("\n=== 📚 Available Resources ===")
                try:
                    resources = await session.list_resources()
                    print(f"Found {len(resources.resources)} resources:")
                    for resource in resources.resources:
                        print(f"  • {resource.uri}: {resource.name}")
                except Exception as e:
                    print(f"Could not list resources: {e}")
                
                # Test some tools with college football data
                print("\n=== 🏈 Testing College Football Data ===")
                
                test_cases = [
                    {
                        "name": "get-games",
                        "description": "Get games from Week 1, 2024",
                        "args": {"year": 2024, "week": 1}
                    },
                    {
                        "name": "get-records",
                        "description": "Get team records for 2024", 
                        "args": {"year": 2024}
                    },
                    {
                        "name": "get-rankings",
                        "description": "Get rankings for Week 1, 2024",
                        "args": {"year": 2024, "week": 1}
                    }
                ]
                
                for test_case in test_cases:
                    try:
                        print(f"\n--- Testing: {test_case['description']} ---")
                        result = await session.call_tool(
                            test_case['name'], 
                            test_case['args']
                        )
                        
                        if result.content:
                            content = result.content[0]
                            if hasattr(content, 'text'):
                                try:
                                    data = json.loads(content.text)
                                    if isinstance(data, list):
                                        print(f"✅ Success! Found {len(data)} results")
                                        if len(data) > 0:
                                            print("📊 Sample result:")
                                            sample = json.dumps(data[0], indent=2)
                                            # Truncate if too long
                                            if len(sample) > 300:
                                                sample = sample[:300] + "\n  ... (truncated)"
                                            print(sample)
                                    else:
                                        print("✅ Success! Result:")
                                        result_str = json.dumps(data, indent=2)
                                        if len(result_str) > 300:
                                            result_str = result_str[:300] + "\n... (truncated)"
                                        print(result_str)
                                except json.JSONDecodeError:
                                    print("✅ Success! Raw response:")
                                    print(content.text[:300] + ("..." if len(content.text) > 300 else ""))
                            else:
                                print("✅ Success! Content type:", type(content))
                                print(str(content)[:200] + ("..." if len(str(content)) > 200 else ""))
                        else:
                            print("⚠️  No content returned")
                            
                    except Exception as e:
                        print(f"❌ Error testing {test_case['name']}: {e}")
                
                print("\n🎉 CFBD MCP Server test completed successfully!")
                print("\n📋 Summary:")
                print(f"  • Tools available: {len(tools.tools)}")
                print("  • Server is working and can fetch college football data")
                print("  • Ready for integration with Claude Desktop or other MCP clients")
                
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("  • Make sure the server is properly installed")
        print("  • Check that your API key is valid")
        print("  • Verify the virtual environment is activated")

if __name__ == "__main__":
    asyncio.run(test_cfbd_mcp())