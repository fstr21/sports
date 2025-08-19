#!/usr/bin/env python3
"""
Explore H2H endpoint - see what additional data is available
"""
import asyncio
import json
import httpx

MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

async def explore_h2h_data():
    """Get complete H2H data and show everything available"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_h2h_betting_analysis",
            "arguments": {
                "team_1_id": 4883,  # Real Madrid
                "team_2_id": 4888,  # Osasuna
                "team_1_name": "Real Madrid",
                "team_2_name": "Osasuna"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            
            print("=== COMPLETE H2H DATA EXPLORATION ===")
            print("Raw MCP Response Structure:")
            print(json.dumps(result, indent=2))
            
            if "result" in result and "content" in result["result"]:
                h2h_data = json.loads(result["result"]["content"][0]["text"])
                print("\n=== PARSED H2H DATA ===")
                print("Available fields in H2H response:")
                
                def explore_dict(data, prefix=""):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            print(f"{prefix}{key}: (dict with {len(value)} fields)")
                            explore_dict(value, prefix + "  ")
                        elif isinstance(value, list):
                            print(f"{prefix}{key}: (list with {len(value)} items)")
                            if value and isinstance(value[0], dict):
                                print(f"{prefix}  Sample item keys: {list(value[0].keys())}")
                        else:
                            print(f"{prefix}{key}: {type(value).__name__} = {value}")
                
                explore_dict(h2h_data)
                
                print(f"\n=== COMPLETE H2H DATA DUMP ===")
                print(json.dumps(h2h_data, indent=2))
                
    except Exception as e:
        print(f"Error: {e}")

async def explore_raw_api():
    """Also check the raw SoccerDataAPI directly"""
    print(f"\n=== EXPLORING RAW SOCCER API H2H ===")
    
    import os
    AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.soccerdataapi.com/head-to-head/",
                params={
                    "team_1_id": 4883,  # Real Madrid
                    "team_2_id": 4888,  # Osasuna  
                    "auth_token": AUTH_KEY
                }
            )
            
            if response.status_code == 200:
                raw_data = response.json()
                print("Raw SoccerDataAPI H2H Response:")
                print(json.dumps(raw_data, indent=2))
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"Raw API Error: {e}")

if __name__ == "__main__":
    asyncio.run(explore_h2h_data())
    asyncio.run(explore_raw_api())