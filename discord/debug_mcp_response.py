#!/usr/bin/env python3
"""
Debug the actual MCP server response to see what we're getting
"""

import asyncio
import httpx
import json
import os

async def debug_mcp_response():
    """Debug the actual MCP server response"""
    print("🔍 Debugging MCP Server Response")
    print("=" * 50)
    
    mcp_url = "https://soccermcp-production.up.railway.app/mcp"
    
    # Test with a date that had a large response
    test_date = "17-08-2025"  # DD-MM-YYYY format
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_betting_matches",
                    "arguments": {"date": test_date}
                }
            }
            
            print(f"📤 Sending request: {json.dumps(payload, indent=2)}")
            
            response = await client.post(mcp_url, json=payload)
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Response size: {len(response.text)} characters")
                
                # Print the structure
                print(f"📋 Response structure:")
                print(f"   Keys: {list(data.keys())}")
                
                if "result" in data:
                    result = data["result"]
                    print(f"   Result type: {type(result)}")
                    print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                    
                    # Print first part of result
                    result_str = json.dumps(result, indent=2)
                    print(f"📄 First 1000 characters of result:")
                    print(result_str[:1000])
                    
                    if len(result_str) > 1000:
                        print("... (truncated)")
                        
                        # Look for matches data
                        if "matches" in result_str.lower():
                            print("\n🔍 Found 'matches' in response!")
                        if "league" in result_str.lower():
                            print("🔍 Found 'league' in response!")
                        if "team" in result_str.lower():
                            print("🔍 Found 'team' in response!")
                
                else:
                    print("❌ No 'result' field in response")
                    
            else:
                print(f"❌ Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_mcp_response())