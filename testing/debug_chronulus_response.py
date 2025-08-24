#!/usr/bin/env python3
"""
Debug Custom Chronulus Response Format
"""

import asyncio
import json
import httpx

async def debug_response():
    """Debug the actual Custom Chronulus response"""
    
    client = httpx.AsyncClient(timeout=90.0)
    
    game_data = {
        "home_team": "Los Angeles Dodgers",
        "away_team": "San Diego Padres",
        "venue": "Dodger Stadium",
        "game_date": "2025-08-23",
        "home_record": "86-57",
        "away_record": "78-65",
        "home_moneyline": -145,
        "away_moneyline": 125,
        "additional_context": "Division rivalry game with Clayton Kershaw vs Yu Darvish."
    }
    
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
        response = await client.post("https://customchronpredictormcp-production.up.railway.app/mcp", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        result = response.json()
        print(f"\nFull Response:")
        print(json.dumps(result, indent=2))
        
        if "result" in result:
            print(f"\nResult Content:")
            content = result["result"]
            print(json.dumps(content, indent=2))
            
            if "content" in content and len(content["content"]) > 0:
                text_content = content["content"][0].get("text", "")
                print(f"\nText Content Length: {len(text_content)}")
                print(f"Text Content Preview: {text_content[:500]}...")
                
                # Try to parse as JSON
                try:
                    parsed_data = json.loads(text_content)
                    print(f"\nParsed Data:")
                    print(json.dumps(parsed_data, indent=2))
                except:
                    print(f"\nText is not JSON format")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(debug_response())
