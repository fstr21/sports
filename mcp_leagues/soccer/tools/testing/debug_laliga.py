#!/usr/bin/env python3
"""
Debug La Liga specifically
"""
import asyncio
import json
import httpx

MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

async def debug_laliga():
    """Debug La Liga response in detail"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_betting_matches",
            "arguments": {
                "date": "19-08-2025",
                "league_filter": "La Liga"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            
            print("Raw response:")
            print(json.dumps(result, indent=2))
            
            if "result" in result and "content" in result["result"]:
                data = json.loads(result["result"]["content"][0]["text"])
                print("\nParsed data:")
                print(json.dumps(data, indent=2))
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_laliga())