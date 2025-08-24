#!/usr/bin/env python3
"""
Dump All MLB Team Names
Find the correct team name format
"""

import asyncio
import json
import httpx

async def dump_all_teams():
    """Get all MLB team names to find correct format"""
    
    print("📋 DUMPING ALL MLB TEAM NAMES")
    print("=" * 50)
    
    client = httpx.AsyncClient(timeout=60.0)
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getMLBTeams",
                "arguments": {"season": 2025}
            }
        }
        
        response = await client.post("https://mlbmcp-production.up.railway.app/mcp", json=payload)
        teams_result = response.json()
        
        if "result" in teams_result:
            teams_data = teams_result["result"]
            if "data" in teams_data and "teams" in teams_data["data"]:
                teams = teams_data["data"]["teams"]
                
                print(f"Found {len(teams)} teams:\n")
                
                for team in teams:
                    team_id = team.get("teamId")
                    name = team.get("name", "")
                    team_name = team.get("teamName", "")
                    abbrev = team.get("abbrev", "")
                    location = team.get("locationName", "")
                    
                    print(f"ID: {team_id:3} | Name: '{name}' | TeamName: '{team_name}' | Location: '{location}' | Abbrev: '{abbrev}'")
                
                # Look for Yankees, Dodgers, Red Sox specifically
                print(f"\n🔍 SEARCHING FOR COMMON TEAMS:")
                target_teams = ["Yankees", "Dodgers", "Red Sox"]
                
                for target in target_teams:
                    matches = []
                    for team in teams:
                        full_info = f"{team.get('locationName', '')} {team.get('teamName', '')} {team.get('name', '')}"
                        if target.lower() in full_info.lower():
                            matches.append({
                                "id": team.get("teamId"),
                                "search_name": f"{team.get('locationName', '')} {team.get('teamName', '')}".strip(),
                                "api_name": team.get('name', ''),
                                "abbrev": team.get('abbrev', '')
                            })
                    
                    if matches:
                        print(f"\n   🎯 {target} matches:")
                        for match in matches:
                            print(f"      ID: {match['id']} | Search: '{match['search_name']}' | API: '{match['api_name']}' | Abbrev: '{match['abbrev']}'")
                    else:
                        print(f"\n   ❌ No {target} matches found")
            
        else:
            print(f"❌ API error: {teams_result}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(dump_all_teams())