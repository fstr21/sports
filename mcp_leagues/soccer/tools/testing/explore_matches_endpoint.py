#!/usr/bin/env python3
"""
Explore Matches Endpoint - Understanding the full data structure
"""
import asyncio
import json
import httpx
import os

AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")
BASE_URL = "https://api.soccerdataapi.com"

async def test_matches_endpoint_variations():
    """Test different ways to call the matches endpoint"""
    
    print("=" * 80)
    print("EXPLORING MATCHES ENDPOINT - ALL VARIATIONS")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "By League + Date",
            "params": {
                "league_id": 228,  # EPL
                "date": "19-08-2025",
                "auth_token": AUTH_KEY
            }
        },
        {
            "name": "By League + Season", 
            "params": {
                "league_id": 228,  # EPL
                "season": "2024-2025",
                "auth_token": AUTH_KEY
            }
        },
        {
            "name": "By Team ID",
            "params": {
                "team_id": 4883,  # Real Madrid
                "auth_token": AUTH_KEY
            }
        },
        {
            "name": "By Team + League",
            "params": {
                "team_id": 4883,  # Real Madrid  
                "league_id": 297,  # La Liga
                "auth_token": AUTH_KEY
            }
        },
        {
            "name": "By Team + Season",
            "params": {
                "team_id": 4883,  # Real Madrid
                "season": "2024-2025", 
                "auth_token": AUTH_KEY
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*60}")
        print(f"Parameters: {test_case['params']}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{BASE_URL}/matches/", params=test_case['params'])
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Response Type: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"List Length: {len(data)}")
                        if data:
                            print(f"First Item Type: {type(data[0])}")
                            if isinstance(data[0], dict):
                                print(f"First Item Keys: {list(data[0].keys())}")
                                
                                # Look for matches in structure
                                matches_found = 0
                                structure_info = []
                                
                                for league_data in data:
                                    if isinstance(league_data, dict):
                                        league_name = league_data.get('league_name', 'Unknown')
                                        
                                        # Check direct matches
                                        if 'matches' in league_data:
                                            league_matches = league_data['matches']
                                            matches_found += len(league_matches)
                                            structure_info.append(f"  {league_name}: {len(league_matches)} direct matches")
                                        
                                        # Check stage-based matches
                                        elif 'stage' in league_data:
                                            stages = league_data['stage']
                                            for stage in stages:
                                                if 'matches' in stage:
                                                    stage_matches = stage['matches']
                                                    matches_found += len(stage_matches)
                                                    stage_name = stage.get('stage_name', 'Unknown Stage')
                                                    structure_info.append(f"  {league_name} - {stage_name}: {len(stage_matches)} matches")
                                
                                print(f"Total Matches Found: {matches_found}")
                                if structure_info:
                                    print("Structure:")
                                    for info in structure_info:
                                        print(info)
                                
                                # Show sample match structure if available
                                sample_match = None
                                for league_data in data:
                                    if isinstance(league_data, dict):
                                        if 'matches' in league_data and league_data['matches']:
                                            sample_match = league_data['matches'][0]
                                            break
                                        elif 'stage' in league_data:
                                            for stage in league_data['stage']:
                                                if 'matches' in stage and stage['matches']:
                                                    sample_match = stage['matches'][0]
                                                    break
                                            if sample_match:
                                                break
                                
                                if sample_match:
                                    print(f"\nSample Match Structure:")
                                    print(f"  Keys: {list(sample_match.keys())}")
                                    
                                    # Show important fields
                                    teams = sample_match.get('teams', {})
                                    if teams:
                                        home = teams.get('home', {})
                                        away = teams.get('away', {})
                                        print(f"  Teams: {home.get('name', 'N/A')} vs {away.get('name', 'N/A')}")
                                        print(f"  Team IDs: {home.get('id', 'N/A')} vs {away.get('id', 'N/A')}")
                                    
                                    print(f"  Date: {sample_match.get('date', 'N/A')}")
                                    print(f"  Status: {sample_match.get('status', 'N/A')}")
                                    
                                    goals = sample_match.get('goals', {})
                                    if goals:
                                        home_goals = goals.get('home_ft_goals', 'N/A')
                                        away_goals = goals.get('away_ft_goals', 'N/A')
                                        print(f"  Score: {home_goals}-{away_goals}")
                                    
                                    events = sample_match.get('events', [])
                                    print(f"  Events: {len(events)} total")
                                    
                                    odds = sample_match.get('odds', {})
                                    if odds:
                                        print(f"  Odds Available: {list(odds.keys())}")
                                
                    elif isinstance(data, dict):
                        print(f"Dict Keys: {list(data.keys())}")
                    
                    # Save sample response
                    filename = f"matches_test_{i}_{test_case['name'].replace(' ', '_').lower()}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"Saved response to: {filename}")
                    
                else:
                    print(f"Error: {response.text}")
                    
        except Exception as e:
            print(f"Exception: {e}")
    
    print(f"\n{'='*80}")
    print("MATCHES ENDPOINT EXPLORATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_matches_endpoint_variations())