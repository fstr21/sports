#!/usr/bin/env python3
"""
Debug Team Mapping and Pitcher Panel
Test why the enhanced pitcher panel is not working
"""

import asyncio
import json
import httpx

async def debug_team_mapping():
    """Debug the team mapping process"""
    
    print("🔍 DEBUGGING TEAM MAPPING AND PITCHER PANEL")
    print("=" * 60)
    
    client = httpx.AsyncClient(timeout=60.0)
    
    try:
        # Test 1: Get MLB Teams
        print("\n1️⃣ Testing getMLBTeams call...")
        
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
        
        print(f"📊 Teams API Response: {str(teams_result)[:300]}...")
        
        if "result" in teams_result:
            teams_data = teams_result["result"]
            if "data" in teams_data and "teams" in teams_data["data"]:
                teams = teams_data["data"]["teams"]
                print(f"✅ Found {len(teams)} teams")
                
                # Create team mapping
                team_mapping = {}
                for team in teams[:3]:  # Show first 3 teams
                    team_name = team.get("name", "")
                    team_id = team.get("teamId")
                    print(f"   🏟️ {team_name} (ID: {team_id})")
                    team_mapping[team_name] = team_id
                
                # Test with real team names
                test_teams = ["New York Yankees", "Los Angeles Dodgers", "Boston Red Sox"]
                
                print(f"\n2️⃣ Testing team name lookups...")
                for team_name in test_teams:
                    team_id = team_mapping.get(team_name)
                    if team_id:
                        print(f"   ✅ {team_name} → ID: {team_id}")
                        
                        # Test roster call
                        await test_roster_call(client, team_id, team_name)
                        
                    else:
                        print(f"   ❌ {team_name} → Not found in mapping")
                        
                        # Look for partial matches
                        matches = [t for t in team_mapping.keys() if any(word in t for word in team_name.split())]
                        if matches:
                            print(f"      Possible matches: {matches}")
                
            else:
                print("❌ Teams data structure not as expected")
        else:
            print(f"❌ Teams API error: {teams_result}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()

async def test_roster_call(client, team_id, team_name):
    """Test roster call for a specific team"""
    
    try:
        print(f"\n   📋 Testing roster for {team_name} (ID: {team_id})...")
        
        roster_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getMLBTeamRoster",
                "arguments": {"teamId": team_id}
            }
        }
        
        response = await client.post("https://mlbmcp-production.up.railway.app/mcp", json=roster_payload)
        roster_result = response.json()
        
        if "result" in roster_result:
            roster_data = roster_result["result"]
            if "data" in roster_data and "players" in roster_data["data"]:
                players = roster_data["data"]["players"]
                pitchers = [p for p in players if p.get("position") == "P"]
                
                print(f"      ✅ Roster: {len(players)} players, {len(pitchers)} pitchers")
                
                if pitchers:
                    pitcher = pitchers[0]
                    pitcher_id = pitcher.get("playerId")
                    pitcher_name = pitcher.get("fullName", "Unknown")
                    
                    print(f"      🥎 First pitcher: {pitcher_name} (ID: {pitcher_id})")
                    
                    # Test pitcher stats call
                    await test_pitcher_stats_call(client, pitcher_id, pitcher_name)
                else:
                    print(f"      ⚠️ No pitchers found")
            else:
                print(f"      ❌ Roster data structure unexpected: {str(roster_data)[:200]}...")
        else:
            print(f"      ❌ Roster API error: {roster_result}")
    
    except Exception as e:
        print(f"      ❌ Roster error: {e}")

async def test_pitcher_stats_call(client, pitcher_id, pitcher_name):
    """Test pitcher stats call"""
    
    try:
        print(f"         📊 Testing stats for {pitcher_name} (ID: {pitcher_id})...")
        
        stats_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getMLBPitcherMatchup",
                "arguments": {"pitcher_id": pitcher_id}
            }
        }
        
        response = await client.post("https://mlbmcp-production.up.railway.app/mcp", json=stats_payload)
        stats_result = response.json()
        
        if "result" in stats_result:
            stats_data = stats_result["result"]
            if "data" in stats_data:
                pitcher_data = stats_data["data"]
                aggregates = pitcher_data.get("aggregates", {})
                
                if aggregates:
                    era = aggregates.get("era", 0)
                    whip = aggregates.get("whip", 0)
                    k9 = aggregates.get("k_per_9", 0)
                    
                    print(f"            ✅ Stats: {era:.2f} ERA, {whip:.3f} WHIP, {k9:.1f} K/9")
                else:
                    print(f"            ❌ No aggregates in stats: {str(pitcher_data)[:150]}...")
            else:
                print(f"            ❌ Stats data structure unexpected: {str(stats_data)[:200]}...")
        else:
            print(f"            ❌ Stats API error: {stats_result}")
    
    except Exception as e:
        print(f"            ❌ Stats error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_team_mapping())