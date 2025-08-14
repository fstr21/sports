#!/usr/bin/env python3
"""
Quick test of all 4 existing MLB MCP tools
"""

import requests
import json

MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

def call_tool(name, args=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call", 
        "id": 1,
        "params": {"name": name, "arguments": args or {}}
    }
    try:
        r = requests.post(MLB_MCP_URL, json=payload, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def test_tool(name, args, description):
    print(f"🧪 Testing {name}: {description}")
    result = call_tool(name, args)
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return False
    
    if not result.get("result", {}).get("ok"):
        error = result.get("result", {}).get("error", "Unknown error")
        print(f"❌ FAILED: {error}")
        return False
    
    data = result["result"]["data"]
    if "count" in data:
        print(f"✅ SUCCESS: Found {data['count']} items")
    else:
        print(f"✅ SUCCESS: Data retrieved")
    return True

def main():
    print("=" * 60)
    print("Testing All MLB MCP Tools")
    print("=" * 60)
    
    tests = [
        ("getMLBScheduleET", {}, "Today's schedule"),
        ("getMLBTeams", {}, "Current season teams"),
        ("getMLBTeamRoster", {"teamId": 147}, "Yankees roster"),
        ("getMLBPlayerLastN", {"player_ids": [592450], "count": 3}, "Aaron Judge last 3 games")
    ]
    
    passed = 0
    for name, args, desc in tests:
        if test_tool(name, args, desc):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} tools working")
    print("=" * 60)

if __name__ == "__main__":
    main()