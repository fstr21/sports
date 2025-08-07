#!/usr/bin/env python3
"""
Debug script to examine what data ESPN API actually returns.
"""

import asyncio
import json
import httpx

async def test_espn_endpoints():
    """Test different ESPN endpoints to see what player data is available."""
    
    print("=" * 80)
    print("ESPN API Data Exploration")
    print("=" * 80)
    
    base_url = "http://site.api.espn.com/apis/site/v2/sports"
    
    endpoints_to_test = [
        "/basketball/wnba/scoreboard?dates=20250807",
        "/basketball/wnba/scoreboard",  # Current games
        "/basketball/wnba/teams",
        "/basketball/wnba/news"
    ]
    
    async with httpx.AsyncClient(timeout=15) as client:
        for endpoint in endpoints_to_test:
            print(f"\n{'='*60}")
            print(f"Testing: {endpoint}")
            print('='*60)
            
            try:
                url = f"{base_url}{endpoint}"
                response = await client.get(url, headers={
                    "user-agent": "sports-ai-analyzer/1.0",
                    "accept": "application/json"
                })
                response.raise_for_status()
                data = response.json()
                
                print(f"Status: {response.status_code}")
                print(f"Response size: {len(json.dumps(data))} characters")
                
                # Look for player information
                if "events" in data:
                    print(f"Found {len(data['events'])} events")
                    
                    for i, event in enumerate(data["events"][:2]):  # Check first 2 events
                        print(f"\n--- Event {i+1}: {event.get('name', 'Unknown')} ---")
                        
                        # Check for player leaders
                        if "competitions" in event:
                            for comp in event["competitions"]:
                                if "leaders" in comp:
                                    print("FOUND LEADERS:")
                                    leaders = comp["leaders"]
                                    for category in leaders:
                                        print(f"  {category['name']}:")
                                        for leader in category.get("leaders", []):
                                            athlete = leader.get("athlete", {})
                                            print(f"    {athlete.get('displayName', 'Unknown')}: {leader.get('displayValue', 'N/A')}")
                                
                                # Check for team rosters in competitors
                                if "competitors" in comp:
                                    for competitor in comp["competitors"]:
                                        team_name = competitor.get("team", {}).get("displayName", "Unknown")
                                        print(f"  Team: {team_name}")
                                        
                                        # Look for roster data
                                        if "roster" in competitor:
                                            print(f"    Roster found: {len(competitor['roster'])} players")
                                            for player in competitor["roster"][:3]:  # First 3 players
                                                print(f"      {player.get('displayName', 'Unknown')}")
                                        
                                        # Look for statistics
                                        if "statistics" in competitor:
                                            print(f"    Statistics available: {len(competitor['statistics'])} categories")
                
                elif "teams" in data:
                    print(f"Found {len(data['teams'])} teams")
                    for team in data["teams"][:2]:  # First 2 teams
                        print(f"  {team.get('displayName', 'Unknown')}")
                
                elif "articles" in data:
                    print(f"Found {len(data['articles'])} news articles")
                    for article in data["articles"][:2]:
                        print(f"  {article.get('headline', 'No headline')}")
                
                # Save full response for detailed inspection
                filename = f"test/logs/espn_debug_{endpoint.replace('/', '_').replace('?', '_')}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Full response saved to: {filename}")
                
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    import os
    os.makedirs("test/logs", exist_ok=True)
    asyncio.run(test_espn_endpoints())