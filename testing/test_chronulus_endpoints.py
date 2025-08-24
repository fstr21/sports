#!/usr/bin/env python3
"""
Quick Custom Chronulus Endpoint Test

Test different endpoint formats to find the correct one for pitcher integration.
"""

import asyncio
import httpx

async def test_endpoints():
    """Test different Custom Chronulus endpoint formats"""
    
    base_url = "https://customchronpredictormcp-production.up.railway.app"
    
    # Sample game data
    game_data = {
        "home_team": "Los Angeles Dodgers",
        "away_team": "San Diego Padres", 
        "venue": "Dodger Stadium",
        "game_date": "2025-08-23",
        "home_record": "86-57",
        "away_record": "78-65",
        "home_moneyline": -145,
        "away_moneyline": 125,
        "additional_context": "Division rivalry game. Home starting pitcher: Clayton Kershaw. Away starting pitcher: Yu Darvish."
    }
    
    endpoints_to_test = [
        "/mcp",
        "/tools/call", 
        "/",
        ""
    ]
    
    client = httpx.AsyncClient(timeout=30.0)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing: {url}")
        
        # Test MCP format
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    "expert_count": 5,
                    "analysis_depth": "comprehensive"
                }
            }
        }
        
        try:
            response = await client.post(url, json=payload)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    print(f"   ✅ SUCCESS! Working endpoint: {url}")
                    print(f"   📊 Response preview: {str(result)[:100]}...")
                    break
                else:
                    print(f"   ⚠️ 200 but no result: {result}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_endpoints())