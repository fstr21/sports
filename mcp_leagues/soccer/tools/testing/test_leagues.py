#!/usr/bin/env python3
"""
Quick test to check which league names are supported
"""
import asyncio
import json
import httpx

MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

async def test_league(league_name):
    """Test a specific league name"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_betting_matches",
            "arguments": {
                "date": "19-08-2025",
                "league_filter": league_name
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            
            if "result" in result and "content" in result["result"]:
                data = json.loads(result["result"]["content"][0]["text"])
                if "error" in data:
                    return f"ERROR: {data['error']}"
                else:
                    return f"SUCCESS - found {data.get('total_matches', 0)} matches"
            else:
                return f"ERROR: Unexpected response: {result}"
                
    except Exception as e:
        return f"ERROR: Request failed: {e}"

async def main():
    print("Testing League Name Recognition")
    print("=" * 50)
    
    # Test all possible league names
    test_leagues = [
        "EPL",
        "MLS", 
        "UEFA",
        "La Liga",
        "LA LIGA",
        "Bundesliga", 
        "BUNDESLIGA",
        "Serie A",
        "SERIE A"
    ]
    
    for league in test_leagues:
        print(f"Testing '{league}'...")
        result = await test_league(league)
        print(f"  {result}")
    
    print(f"\n{'=' * 50}")
    print("This shows which exact league names work with your server.")

if __name__ == "__main__":
    asyncio.run(main())