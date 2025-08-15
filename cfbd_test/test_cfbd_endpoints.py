#!/usr/bin/env python3
"""
Test script for CFBD MCP Server endpoints
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

class CFBDTester:
    def __init__(self):
        self.api_key = os.getenv('CFBD_API_KEY')
        if not self.api_key:
            raise ValueError("CFBD_API_KEY not found in environment variables")
    
    async def test_mcp_server(self):
        """Test the CFBD MCP server endpoints"""
        
        # Server parameters - adjust path as needed
        server_params = StdioServerParameters(
            command="uvx",
            args=["lenwood.cfbd-mcp-server@latest"],
            env={"CFBD_API_KEY": self.api_key}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # List available tools
                print("=== Available Tools ===")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")
                
                print("\n=== Testing Endpoints ===")
                
                # Test some common endpoints
                test_cases = [
                    {
                        "name": "get_teams",
                        "args": {"year": 2024}
                    },
                    {
                        "name": "get_games", 
                        "args": {"year": 2024, "week": 1}
                    },
                    {
                        "name": "get_conferences",
                        "args": {}
                    }
                ]
                
                for test_case in test_cases:
                    try:
                        print(f"\n--- Testing {test_case['name']} ---")
                        result = await session.call_tool(
                            test_case['name'], 
                            test_case['args']
                        )
                        
                        # Print first few results
                        if result.content:
                            content = result.content[0]
                            if hasattr(content, 'text'):
                                data = json.loads(content.text)
                                if isinstance(data, list) and len(data) > 0:
                                    print(f"Found {len(data)} results")
                                    print("Sample result:")
                                    print(json.dumps(data[0], indent=2))
                                else:
                                    print("Result:", json.dumps(data, indent=2))
                            else:
                                print("Content:", content)
                        else:
                            print("No content returned")
                            
                    except Exception as e:
                        print(f"Error testing {test_case['name']}: {e}")

async def main():
    """Main test function"""
    try:
        tester = CFBDTester()
        await tester.test_mcp_server()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Set CFBD_API_KEY in your .env file")
        print("2. Installed required packages: pip install -r requirements.txt")
        print("3. Have uvx installed (part of uv package manager)")

if __name__ == "__main__":
    asyncio.run(main())