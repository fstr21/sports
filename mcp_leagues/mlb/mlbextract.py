import requests
import json
import os
from datetime import datetime

# Base URL for MLB Stats API
BASE_URL = "https://statsapi.mlb.com/api/v1"
OUTPUT_DIR = r"C:\Users\fstr2\Desktop\sports\mcp_leagues\mlb"

# Create directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def explore_endpoint(endpoint, description):
    """Explore an MLB Stats API endpoint and return results"""
    result = {
        "endpoint": endpoint,
        "description": description,
        "url": f"{BASE_URL}{endpoint}",
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "data": None,
        "structure": None,
        "error": None
    }
    
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        r.raise_for_status()
        data = r.json()
        
        result["success"] = True
        result["status_code"] = r.status_code
        
        # Analyze structure
        structure = {
            "top_level_keys": {},
            "sample_items": {}
        }
        
        # Document top-level structure
        for key in data.keys():
            structure["top_level_keys"][key] = {
                "type": type(data[key]).__name__,
                "length": len(data[key]) if isinstance(data[key], (list, dict)) else None
            }
            
            # If it's a list with items, show first item structure
            if isinstance(data[key], list) and data[key]:
                first_item = data[key][0]
                if isinstance(first_item, dict):
                    structure["sample_items"][key] = {
                        "fields": list(first_item.keys()),
                        "sample": first_item
                    }
        
        result["structure"] = structure
        result["data"] = data
        
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
    
    return result

# Key endpoints to explore
endpoints_to_explore = [
    # Core endpoints
    ("/statsapi", "Available stat types and API info"),
    
    # Player stats - different stat types
    ("/people/660271/stats?stats=gameLog&season=2024&group=hitting", "Player game logs (Ohtani hitting)"),
    ("/people/660271/stats?stats=career&season=2024", "Career stats"),
    ("/people/660271/stats?stats=statSplits&season=2024", "Stat splits"),
    ("/people/660271/stats?stats=vsTeam&season=2024&group=hitting", "vs Team stats"),
    ("/people/660271/stats?stats=vsPlayer&season=2024", "vs Player stats"),
    ("/people/660271/stats?stats=sabermetrics&season=2024", "Sabermetrics"),
    ("/people/660271/stats?stats=expectedStatistics&season=2024", "Expected stats"),
    
    # Pitcher specific (using a pitcher ID)
    ("/people/605483/stats?stats=gameLog&season=2024&group=pitching", "Pitcher game logs (example)"),
    ("/people/605483/stats?stats=pitchingStatSplits&season=2024", "Pitching splits"),
    
    # Team stats endpoints
    ("/teams/119/stats?season=2024&stats=season", "Team season stats"),
    ("/teams/119/stats?season=2024&stats=gameLog", "Team game logs"),
    ("/teams/119/stats?season=2024&stats=teamStatSplits", "Team splits"),
    
    # Game-specific data (using a real game ID from 2024)
    ("/game/745470/feed/live", "Live game data structure"),
    ("/game/745470/boxscore", "Boxscore structure"),
    ("/game/745470/linescore", "Linescore structure"),
    
    # Schedule with hydrations
    ("/schedule?sportId=1&date=2024-07-01&hydrate=team,probablePitcher,weather,linescore", "Schedule with full hydration"),
    
    # Standings
    ("/standings?leagueId=103,104&season=2024&standingsTypes=regularSeason", "Regular season standings"),
    
    # Venues
    ("/venues/1", "Venue information (Angels stadium)"),
    
    # Config/metadata endpoints
    ("/statTypes", "All available stat types"),
    ("/statGroups", "Stat groups (hitting/pitching/fielding)"),
    ("/gameTypes", "Game types"),
    ("/platforms", "Platforms"),
    ("/positions", "Positions"),
    ("/situationCodes", "Situation codes"),
]

# Collect all results
all_results = {
    "exploration_date": datetime.now().isoformat(),
    "api_base": BASE_URL,
    "endpoints": {}
}

print("MLB Stats API Explorer")
print("=" * 60)
print(f"Output directory: {OUTPUT_DIR}")
print(f"Exploring {len(endpoints_to_explore)} endpoints...\n")

# Explore each endpoint
for endpoint, desc in endpoints_to_explore:
    print(f"Exploring: {endpoint}... ", end="", flush=True)
    result = explore_endpoint(endpoint, desc)
    
    # Create a clean key for the results
    clean_key = endpoint.replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "_")
    all_results["endpoints"][clean_key] = result
    
    if result["success"]:
        print("✓")
    else:
        print(f"✗ ({result['error']})")

# Special: Get all available stat types with details
print("\nFetching comprehensive stat types list... ", end="", flush=True)
try:
    r = requests.get(f"{BASE_URL}/statTypes")
    stat_types_data = r.json()
    
    # Organize by what they're valid for
    organized_stats = {
        "player_stats": [],
        "team_stats": [],
        "pitcher_stats": [],
        "all_stats": stat_types_data
    }
    
    for st in stat_types_data:
        if 'person' in st.get('validFor', []):
            organized_stats["player_stats"].append({
                "name": st['name'],
                "description": st.get('description', ''),
                "validFor": st.get('validFor', [])
            })
        if 'team' in st.get('validFor', []):
            organized_stats["team_stats"].append({
                "name": st['name'],
                "description": st.get('description', ''),
                "validFor": st.get('validFor', [])
            })
    
    all_results["stat_types"] = organized_stats
    print("✓")
except Exception as e:
    print(f"✗ ({e})")

# Save full results
output_file = os.path.join(OUTPUT_DIR, f"mlb_api_exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {output_file}")

# Also create a summary file with just the successful endpoints and their fields
summary = {
    "exploration_date": datetime.now().isoformat(),
    "successful_endpoints": [],
    "available_stat_types": organized_stats if 'organized_stats' in locals() else {},
    "failed_endpoints": []
}

for key, result in all_results["endpoints"].items():
    if result["success"]:
        # Only add if structure exists
        if result.get("structure"):
            summary["successful_endpoints"].append({
                "endpoint": result["endpoint"],
                "description": result["description"],
                "fields": result["structure"].get("top_level_keys", {}),
                "sample_data_keys": result["structure"].get("sample_items", {})
            })
    else:
        summary["failed_endpoints"].append({
            "endpoint": result["endpoint"],
            "error": result.get("error", "Unknown error")
        })

summary_file = os.path.join(OUTPUT_DIR, f"mlb_api_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"Summary saved to: {summary_file}")
print("\nExploration complete!")
print(f"Total endpoints explored: {len(endpoints_to_explore)}")
print(f"Successful: {len(summary['successful_endpoints'])}")
print(f"Failed: {len(summary['failed_endpoints'])}")