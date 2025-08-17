#!/usr/bin/env python3
"""
Debug the standings response to understand the actual structure

The response had keys: ['country', 'league', 'season', 'stage']
Let's see what's inside these keys to find the team data.
"""

import json
import glob

def debug_standings_response():
    """Debug the actual standings response structure"""
    
    # Find the most recent standings file
    files = glob.glob("epl_standings_teams_*.json")
    if not files:
        print("❌ No standings JSON files found")
        return
    
    latest_file = max(files, key=lambda x: x.split('_')[-1])
    print(f"📁 Debugging file: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("🔍 DEBUGGING STANDINGS RESPONSE STRUCTURE")
        print("=" * 50)
        
        print(f"📊 Top-level type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"📊 Top-level keys: {list(data.keys())}")
            
            # Examine each key
            for key in data.keys():
                value = data[key]
                print(f"\n🔑 Key: '{key}'")
                print(f"   Type: {type(value)}")
                
                if isinstance(value, dict):
                    print(f"   Dict keys: {list(value.keys())}")
                    
                    # Look for team-like data in nested dicts
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, list) and sub_value:
                            print(f"      '{sub_key}' is a list with {len(sub_value)} items")
                            if isinstance(sub_value[0], dict):
                                print(f"         First item keys: {list(sub_value[0].keys())}")
                                # Check if this looks like team data
                                first_item = sub_value[0]
                                team_indicators = ['team', 'name', 'id', 'position', 'points']
                                found_indicators = [ind for ind in team_indicators if ind in first_item]
                                if found_indicators:
                                    print(f"         🎯 POTENTIAL TEAM DATA! Found: {found_indicators}")
                        elif isinstance(sub_value, dict):
                            print(f"      '{sub_key}' is a dict with keys: {list(sub_value.keys())}")
                        else:
                            print(f"      '{sub_key}': {str(sub_value)[:100]}...")
                
                elif isinstance(value, list):
                    print(f"   List with {len(value)} items")
                    if value and isinstance(value[0], dict):
                        print(f"   First item keys: {list(value[0].keys())}")
                        # Check if this is team data
                        first_item = value[0]
                        team_indicators = ['team', 'name', 'id', 'position', 'points']
                        found_indicators = [ind for ind in team_indicators if ind in first_item]
                        if found_indicators:
                            print(f"      🎯 POTENTIAL TEAM DATA! Found: {found_indicators}")
                
                else:
                    print(f"   Value: {str(value)[:100]}...")
        
        # Look for any nested data that might contain teams
        print(f"\n🔍 DEEP SEARCH FOR TEAM DATA:")
        teams_found = find_teams_in_nested_data(data, [])
        
        if teams_found:
            print(f"✅ Found potential team data!")
            for path, team_data in teams_found:
                print(f"   Path: {' -> '.join(path)}")
                print(f"   Sample: {team_data}")
        else:
            print(f"❌ No obvious team data found")
        
        # Show the full structure for manual inspection
        print(f"\n📄 FULL JSON STRUCTURE (first 1000 chars):")
        json_str = json.dumps(data, indent=2)
        print(json_str[:1000] + "..." if len(json_str) > 1000 else json_str)
        
    except Exception as e:
        print(f"❌ Error debugging response: {e}")

def find_teams_in_nested_data(data, path):
    """Recursively search for team-like data"""
    teams_found = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = path + [key]
            
            # Check if this dict looks like team data
            if isinstance(value, dict):
                team_indicators = ['team', 'name', 'id', 'position', 'points']
                if any(indicator in value for indicator in team_indicators):
                    teams_found.append((new_path, value))
                
                # Recurse into nested dicts
                teams_found.extend(find_teams_in_nested_data(value, new_path))
            
            elif isinstance(value, list):
                # Check if this is a list of team-like objects
                if value and isinstance(value[0], dict):
                    team_indicators = ['team', 'name', 'id', 'position', 'points']
                    if any(indicator in value[0] for indicator in team_indicators):
                        teams_found.append((new_path, f"List of {len(value)} team-like objects"))
                
                # Recurse into list items
                for i, item in enumerate(value):
                    teams_found.extend(find_teams_in_nested_data(item, new_path + [f"[{i}]"]))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            teams_found.extend(find_teams_in_nested_data(item, path + [f"[{i}]"]))
    
    return teams_found

if __name__ == "__main__":
    debug_standings_response()