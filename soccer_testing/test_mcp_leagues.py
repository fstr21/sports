#!/usr/bin/env python3
"""
Test SoccerDataAPI MCP Server - Leagues Only

This script tests the Node.js MCP server for SoccerDataAPI to get leagues data.
Uses MCP protocol instead of direct API calls.

IMPORTANT: Still counts toward 75 API calls/day limit!
"""

import json
import asyncio
import httpx
from datetime import datetime

# MCP Server Configuration
# Note: This assumes the MCP server is running locally
# We'll need to set up the Node.js MCP server first
MCP_SERVER_URL = "http://localhost:3000/mcp"  # Default MCP server URL

async def call_mcp_tool(tool_name, arguments=None):
    """
    Call a tool through the MCP server
    
    Args:
        tool_name: Name of the MCP tool to call
        arguments: Dictionary of arguments for the tool
    """
    if arguments is None:
        arguments = {}
    
    # MCP JSON-RPC 2.0 payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    print(f"🔄 Calling MCP tool: {tool_name}")
    print(f"📊 Arguments: {arguments}")
    print(f"⚠️  WARNING: This will use 1 of your 75 daily API calls!")
    
    # Confirm before making call
    confirm = input("Continue with MCP call? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ MCP call cancelled")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_SERVER_URL, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"❌ MCP Error: {result['error']}")
                return None
            
            # Save response to file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcp_soccerdata_leagues_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Success! MCP response saved to: {filename}")
            
            # Extract the actual data from MCP response
            mcp_data = result.get("result", {})
            
            # Show preview of data
            print("\n📊 MCP Response Preview:")
            print(f"  Response keys: {list(result.keys())}")
            
            if "result" in result:
                tool_result = result["result"]
                print(f"  Tool result type: {type(tool_result)}")
                
                # If it's content with text, show preview
                if isinstance(tool_result, list) and tool_result:
                    first_item = tool_result[0]
                    if isinstance(first_item, dict) and "text" in first_item:
                        try:
                            # Try to parse the text as JSON (common MCP pattern)
                            text_data = json.loads(first_item["text"])
                            print(f"  Parsed data type: {type(text_data)}")
                            
                            if isinstance(text_data, list):
                                print(f"  Number of leagues: {len(text_data)}")
                                if text_data:
                                    print(f"  First league sample: {list(text_data[0].keys()) if isinstance(text_data[0], dict) else text_data[0]}")
                            elif isinstance(text_data, dict):
                                print(f"  Data keys: {list(text_data.keys())}")
                        except json.JSONDecodeError:
                            print(f"  Text content preview: {first_item['text'][:200]}...")
            
            return result
            
    except httpx.RequestError as e:
        print(f"❌ MCP connection failed: {e}")
        print("💡 Make sure the Node.js MCP server is running!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None

async def test_leagues():
    """
    Test getting leagues through the MCP server
    """
    print("\n🏆 Testing Leagues via MCP Server")
    print("This will call the SoccerDataAPI MCP to get all available leagues")
    print("Expected: 125+ leagues from around the world")
    
    # The actual tool name depends on how the MCP server implements it
    # Common names might be: "getLeagues", "leagues", "get_leagues"
    # We'll try the most likely one first
    
    result = await call_mcp_tool("getLeagues")
    
    if result:
        print(f"\n✅ Leagues test completed!")
        print(f"📁 Check the generated JSON file for full league data")
        print(f"💡 This will show all available leagues vs our current 2 (EPL + La Liga)")
    else:
        print(f"\n❌ Leagues test failed!")
        print(f"💡 Possible issues:")
        print(f"   - MCP server not running")
        print(f"   - Wrong tool name (try 'leagues' or 'get_leagues')")
        print(f"   - API key not configured in MCP server")

def setup_instructions():
    """
    Show setup instructions for the MCP server
    """
    print("🔧 SETUP REQUIRED:")
    print("=" * 50)
    print("Before running this test, you need to set up the Node.js MCP server:")
    print()
    print("1. Install the MCP server:")
    print("   npm install @yeonupark/mcp-soccer-data@latest")
    print()
    print("2. Set up environment variable:")
    print("   export SOCCERDATA_API_KEY=a9f37754a540df435e8c40ed89c08565166524ed")
    print()
    print("3. Run the MCP server:")
    print("   npx @yeonupark/mcp-soccer-data@latest")
    print()
    print("4. Server should be available at: http://localhost:3000/mcp")
    print()
    print("5. Then run this test script")
    print("=" * 50)

async def main():
    print("🚨 SoccerDataAPI MCP Testing - Leagues Only")
    print("=" * 60)
    print(f"⚠️  FREE PLAN: 75 calls/day limit!")
    print(f"📅 This test uses 1 API call")
    print(f"🔗 Using MCP server instead of direct API")
    print("=" * 60)
    
    # Check if user wants setup instructions
    setup = input("Need setup instructions? (y/n): ").lower().strip()
    if setup == 'y':
        setup_instructions()
        return
    
    # Run the test
    await test_leagues()

if __name__ == "__main__":
    asyncio.run(main())