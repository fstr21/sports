#!/usr/bin/env python3
"""
Debug script to see what data we get from match details
"""

import asyncio
import json
import os
import sys
import httpx
from dotenv import load_dotenv

# Add parent directory to path to load .env
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
load_dotenv(os.path.join(parent_dir, '.env'))

async def debug_match():
    soccer_mcp_url = "https://soccermcp-production.up.railway.app/mcp"
    
    # Use the Liverpool vs Bournemouth match ID (you can get this from the previous output)
    match_id = 465849  # This might be different, we'll need to get it from the game list
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getMatchDetails",
            "arguments": {"match_id": match_id}
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                soccer_mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("Full match details response:")
                print(json.dumps(result, indent=2))
            else:
                print(f"HTTP Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_match())