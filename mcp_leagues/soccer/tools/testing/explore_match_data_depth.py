#!/usr/bin/env python3
"""
Explore what additional data is available in matches endpoint
"""
import asyncio
import json
import httpx
import os
from datetime import datetime, timedelta

AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")
BASE_URL = "https://api.soccerdataapi.com"

async def explore_match_data_depth():
    """Explore all available data in a single match"""
    
    print("=" * 80)
    print("EXPLORING DETAILED MATCH DATA STRUCTURE")
    print("=" * 80)
    
    # Get a completed match to see full data structure
    test_params = [
        {"team_id": 4883, "season": "2024-2025"},  # Real Madrid
        {"league_id": 228, "date": "25-05-2025"},   # EPL recent date
        {"league_id": 297, "date": "24-05-2025"},   # La Liga recent date
    ]
    
    for i, params in enumerate(test_params, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {params}")
        print(f"{'='*60}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params["auth_token"] = AUTH_KEY
                response = await client.get(f"{BASE_URL}/matches/", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract first completed match
                    sample_match = None
                    if isinstance(data, list) and data:
                        for league_data in data:
                            if isinstance(league_data, dict):
                                matches = []
                                
                                # Get matches from structure
                                if 'matches' in league_data:
                                    matches = league_data['matches']
                                elif 'stage' in league_data:
                                    for stage in league_data['stage']:
                                        if 'matches' in stage:
                                            matches.extend(stage['matches'])
                                
                                # Find a completed match with full data
                                for match in matches:
                                    status = match.get('status', '')
                                    if status in ['finished', 'complete', 'full-time']:
                                        # Check if it has meaningful team names
                                        teams = match.get('teams', {})
                                        home_name = teams.get('home', {}).get('name', '')
                                        away_name = teams.get('away', {}).get('name', '')
                                        
                                        if home_name and away_name and 'None' not in [home_name, away_name]:
                                            sample_match = match
                                            break
                                
                                if sample_match:
                                    break
                    
                    if sample_match:
                        print(f"FOUND COMPLETED MATCH:")
                        teams = sample_match.get('teams', {})
                        home_team = teams.get('home', {})
                        away_team = teams.get('away', {})
                        print(f"  {home_team.get('name')} vs {away_team.get('name')}")
                        print(f"  Date: {sample_match.get('date')}")
                        print(f"  Status: {sample_match.get('status')}")
                        
                        print(f"\nFULL MATCH DATA STRUCTURE:")
                        print(f"{'='*50}")
                        
                        # Top-level keys
                        print(f"TOP-LEVEL KEYS: {list(sample_match.keys())}")
                        
                        # Explore each section in detail
                        sections_to_explore = [
                            'teams', 'goals', 'events', 'odds', 'venue', 'referee', 
                            'stats', 'lineups', 'weather', 'formations', 'substitutions'
                        ]
                        
                        for section in sections_to_explore:
                            if section in sample_match:
                                section_data = sample_match[section]
                                print(f"\n{section.upper()}:")
                                print(f"  Type: {type(section_data)}")
                                
                                if isinstance(section_data, dict):
                                    print(f"  Keys: {list(section_data.keys())}")
                                    
                                    # Show sample values for interesting keys
                                    if section == 'teams':
                                        for team_type in ['home', 'away']:
                                            if team_type in section_data:
                                                team = section_data[team_type]
                                                print(f"    {team_type}: {team}")
                                    
                                    elif section == 'goals':
                                        print(f"    Content: {section_data}")
                                    
                                    elif section == 'venue':
                                        print(f"    Content: {section_data}")
                                    
                                    elif section == 'referee':
                                        print(f"    Content: {section_data}")
                                    
                                    elif section == 'weather':
                                        print(f"    Content: {section_data}")
                                    
                                    elif section == 'formations':
                                        print(f"    Content: {section_data}")
                                    
                                    elif section == 'stats' and section_data:
                                        print(f"    Available stats: {list(section_data.keys())}")
                                        # Show sample stat details
                                        for stat_key in list(section_data.keys())[:3]:
                                            stat_value = section_data[stat_key]
                                            print(f"      {stat_key}: {type(stat_value)} = {stat_value}")
                                    
                                    elif section == 'odds' and section_data:
                                        print(f"    Available odds: {list(section_data.keys())}")
                                        for odds_key in section_data:
                                            odds_value = section_data[odds_key]
                                            print(f"      {odds_key}: {type(odds_value)} = {odds_value}")
                                
                                elif isinstance(section_data, list):
                                    print(f"  Length: {len(section_data)}")
                                    
                                    if section == 'events' and section_data:
                                        print(f"    Sample events:")
                                        for event in section_data[:3]:
                                            event_type = event.get('type', 'unknown')
                                            minute = event.get('minute', '?')
                                            player = event.get('player', {}).get('name', 'Unknown')
                                            team = event.get('team', {}).get('name', 'Unknown')
                                            print(f"      {minute}': {event_type} - {player} ({team})")
                                            
                                            # Show full event structure for first one
                                            if section_data.index(event) == 0:
                                                print(f"        Full event keys: {list(event.keys())}")
                                    
                                    elif section == 'lineups' and section_data:
                                        print(f"    Lineup structure:")
                                        for lineup in section_data[:1]:
                                            print(f"      Keys: {list(lineup.keys())}")
                                    
                                    elif section == 'substitutions' and section_data:
                                        print(f"    Substitution structure:")
                                        for sub in section_data[:1]:
                                            print(f"      Keys: {list(sub.keys())}")
                                            print(f"      Content: {sub}")
                                
                                else:
                                    print(f"  Value: {section_data}")
                        
                        # Save full match data for inspection
                        filename = f"full_match_sample_{i}.json"
                        with open(filename, 'w') as f:
                            json.dump(sample_match, f, indent=2)
                        print(f"\nSaved full match data to: {filename}")
                        
                        break  # Found what we need, stop searching
                    else:
                        print("No completed matches with full data found")
                        
                else:
                    print(f"API Error: {response.status_code}")
                    
        except Exception as e:
            print(f"Exception: {e}")
    
    print(f"\n{'='*80}")
    print("MATCH DATA EXPLORATION COMPLETE")
    print("Check the JSON files for full details!")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(explore_match_data_depth())