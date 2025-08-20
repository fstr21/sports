#!/usr/bin/env python3
"""
Simple MCP Test - Check what's actually available
"""
import asyncio
import json
import httpx

MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

async def test_mcp_connection():
    """Test what MCP tools are actually available"""
    
    # Test 1: List tools
    print("Testing tools/list...")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            
            print(f"Response status: {response.status_code}")
            print("Available tools:")
            
            if "tools" in result:
                for tool in result["tools"]:
                    print(f"  - {tool['name']}")
            else:
                print("No tools found or different response format:")
                print(json.dumps(result, indent=2))
                
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try the working betting analysis tool
    print("\n" + "="*50)
    print("Testing working betting analysis tool...")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_betting_matches",
            "arguments": {"date": "19-08-2025"}
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            
            if "result" in result and "content" in result["result"]:
                data = json.loads(result["result"]["content"][0]["text"])
                print("get_betting_matches SUCCESS!")
                print(f"Found leagues: {list(data.get('matches_by_league', {}).keys())}")
                
                # Check if there are any matches
                matches_by_league = data.get('matches_by_league', {})
                total_matches = sum(len(matches) for matches in matches_by_league.values())
                print(f"Total matches found: {total_matches}")
                
                if total_matches > 0:
                    for league, matches in matches_by_league.items():
                        if matches:
                            print(f"{league}: {len(matches)} matches")
                            # Show first match structure
                            print("Sample match structure:")
                            print(json.dumps(matches[0], indent=2)[:300] + "...")
                            break
            else:
                print("Error in betting matches:")
                print(json.dumps(result, indent=2))
                
    except Exception as e:
        print(f"Error testing betting matches: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())