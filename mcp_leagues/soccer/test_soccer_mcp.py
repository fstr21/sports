#!/usr/bin/env python3
"""
Simple test script for Soccer MCP Server
"""

import asyncio
import json
import sys
import os

# Add current directory to path to import our server
sys.path.insert(0, os.path.dirname(__file__))

from soccer_mcp_server import (
    handle_initialize,
    handle_tools_list,
    handle_tools_call,
    TOOLS
)

async def test_mcp_functions():
    """Test basic MCP functionality"""
    print("Testing Soccer MCP Server...")
    print("=" * 50)
    
    # Test initialize
    print("1. Testing initialize...")
    init_result = await handle_initialize({})
    print(f"   Initialize result: {json.dumps(init_result, indent=2)}")
    
    # Test tools list
    print("\n2. Testing tools list...")
    tools_result = await handle_tools_list({})
    print(f"   Found {len(tools_result.get('tools', []))} tools:")
    for tool in tools_result.get('tools', []):
        print(f"   - {tool['name']}: {tool['description']}")
    
    # Test a simple tool call with test mode
    print("\n3. Testing getCompetitions with test mode...")
    competitions_result = await handle_tools_call({
        "name": "getCompetitions",
        "arguments": {"use_test_mode": True}
    })
    print(f"   Competitions result: {json.dumps(competitions_result, indent=2)}")
    
    # Test another tool call with test mode
    print("\n4. Testing getCompetitionMatches with test mode...")
    matches_result = await handle_tools_call({
        "name": "getCompetitionMatches",
        "arguments": {"competition_id": "PL", "use_test_mode": True}
    })
    print(f"   Matches result: {json.dumps(matches_result, indent=2)}")
    
    print("\n" + "=" * 50)
    print(f"All tests completed! Server has {len(TOOLS)} tools registered.")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_mcp_functions())
    if result:
        print("✅ Soccer MCP Server test passed!")
    else:
        print("❌ Soccer MCP Server test failed!")
        sys.exit(1)