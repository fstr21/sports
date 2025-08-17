#!/usr/bin/env python3
"""
Extract EPL Teams from Standings Response - FIXED

Now that we know the structure: stage[0].standings contains the team data
Each team has: team_id, team_name, position, points, etc.

No additional API calls needed - just parse the existing JSON file.
"""

import json
import glob
from datetime import datetime

def extract_epl_teams():
    """Extract EPL teams from the standings response we already have"""
    
    # Find the most recent standings file
    files = glob.glob("epl_standings_teams_*.json")
    if not files:
        print("❌ No standings JSON files found")
        return None
    
    latest_file = max(files, key=lambda x: x.split('_')[-1])
    print(f"📁 Using file: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("⚽ EXTRACTING EPL TEAMS FROM STANDINGS")
        print("=" * 50)
        
        # Navigate to the teams data: stage[0].standings
        if "stage" in data and isinstance(data["stage"], list) and data["stage"]:
            stage_data = data["stage"][0]
            
            if "standings" in stage_data:
                standings = stage_data["standings"]
                
                print(f"✅ Found {len(standings)} EPL teams in standings")
                
                teams = []
                
                print(f"\n🏆 EPL TEAMS (2025-2026 Season):")
                print("=" * 60)
                
                for team_standing in standings:
                    team_info = {
                        "id": team_standing.get("team_id"),
                        "name": team_standing.get("team_name"),
                        "position": team_standing.get("position"),
                        "points": team_standing.get("points"),
                        "games_played": team_standing.get("games_played"),
                        "wins": team_standing.get("wins"),
                        "draws": team_standing.get("draws"),
                        "losses": team_standing.get("losses"),
                        "goals_for": team_standing.get("goals_for"),
                        "goals_against": team_standing.get("goals_against")
                    }
                    
                    teams.append(team_info)
                    
                    # Display team info
                    print(f"{team_info['position']:2d}. {team_info['name']:<20} (ID: {team_info['id']}) - {team_info['points']} pts")
                
                # Save teams to a clean file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                teams_file = f"epl_teams_final_{timestamp}.json"
                
                with open(teams_file, 'w', encoding='utf-8') as f:
                    json.dump(teams, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Extracted {len(teams)} EPL teams")
                print(f"📁 Teams saved to: {teams_file}")
                
                # Highlight key teams for betting
                print(f"\n🎯 KEY TEAMS FOR BETTING:")
                key_teams = ["manchester city", "liverpool", "arsenal", "chelsea", "manchester united", "tottenham"]
                
                for key_team in key_teams:
                    found_team = next((team for team in teams if key_team in team['name'].lower()), None)
                    if found_team:
                        print(f"   ✅ {found_team['name']}: ID {found_team['id']}")
                    else:
                        print(f"   ❌ {key_team.title()}: Not found")
                
                # Show what we can do next
                print(f"\n💡 NEXT STEPS:")
                print(f"   Now we have all 20 EPL team IDs!")
                print(f"   Pick any team and get players with: /team/?team_id=XXXX")
                print(f"   Example: Liverpool (ID: {next((t['id'] for t in teams if 'liverpool' in t['name'].lower()), 'TBD')})")
                
                return teams
            
            else:
                print("❌ No 'standings' found in stage data")
                return None
        
        else:
            print("❌ No 'stage' data found in response")
            return None
            
    except Exception as e:
        print(f"❌ Error extracting teams: {e}")
        return None

def main():
    print("🚀 EXTRACT EPL TEAMS - NO API CALLS NEEDED")
    print("Using existing standings data to get all EPL team IDs")
    
    teams = extract_epl_teams()
    
    print(f"\n📊 FINAL SUMMARY:")
    if teams:
        print(f"✅ SUCCESS: Extracted {len(teams)} EPL teams with IDs")
        print(f"📁 Check the final teams JSON file")
        print(f"🎯 Ready to test getting players for any team")
        print(f"⚠️  No additional API calls used (still 72 remaining)")
    else:
        print("❌ FAILED: Could not extract team data")
    
    return teams

if __name__ == "__main__":
    teams = main()