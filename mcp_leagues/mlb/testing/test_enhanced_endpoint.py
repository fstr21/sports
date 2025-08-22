#!/usr/bin/env python3
"""
Test Enhanced Team Form MCP Endpoint

Quick test to verify the new getMLBTeamFormEnhanced endpoint works
"""

import asyncio
import json
import httpx

async def test_enhanced_endpoint():
    """Test the enhanced team form endpoint"""
    print("🧪 Testing Enhanced Team Form MCP Endpoint")
    print("=" * 50)
    
    mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
    test_team_id = 115  # Rockies
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getMLBTeamFormEnhanced",
            "arguments": {
                "team_id": test_team_id
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"🔧 Calling getMLBTeamFormEnhanced for team {test_team_id}")
            response = await client.post(mcp_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                return False
            
            data = result.get("result", {}).get("data", {})
            
            print("✅ SUCCESS!")
            print(f"Team: {data.get('team_name', 'Unknown')}")
            
            enhanced = data.get("enhanced_records", {})
            print(f"Last 10: {enhanced.get('last_10', 'N/A')}")
            print(f"Home recent: {enhanced.get('home_recent', 'N/A')}")
            print(f"Away recent: {enhanced.get('away_recent', 'N/A')}")
            
            streak = data.get("streak_info", {})
            print(f"Streak: {streak.get('display', 'N/A')}")
            
            print(f"\n📄 Full response:")
            print(json.dumps(result, indent=2))
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_endpoint())
    if success:
        print("\n🎯 Enhanced endpoint is ready for Discord integration!")
    else:
        print("\n💥 Need to debug the enhanced endpoint first")