"""
Final MLB player scraper with proper name extraction
Fixes the name+jersey number parsing issue
"""

import requests
from bs4 import BeautifulSoup
import re
import os
import json
from datetime import datetime

# Base URLs
teams_url = "https://www.espn.com/mlb/teams"
base_url = "https://www.espn.com"

# Output folder
output_folder = r"C:\Users\fstr2\Desktop\players\players\mlb"
os.makedirs(output_folder, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def extract_team_info_from_url(roster_url):
    """Extract team abbreviation and potential team ID from roster URL"""
    # URL format: https://www.espn.com/mlb/team/roster/_/name/nyy/new-york-yankees
    team_match = re.search(r'/name/([^/]+)/([^/?]+)', roster_url)
    if team_match:
        team_abbr = team_match.group(1)
        team_slug = team_match.group(2)
        return team_abbr, team_slug
    return None, None

def extract_name_and_jersey(name_jersey_combo):
    """Extract player name and jersey number from combined string like 'Aaron Judge99'"""
    if not name_jersey_combo:
        return "Unknown", "N/A"
    
    # Try to find jersey number at the end (1-3 digits)
    jersey_match = re.search(r'(\d{1,3})$', name_jersey_combo)
    if jersey_match:
        jersey_number = jersey_match.group(1)
        # Remove jersey number to get name
        player_name = name_jersey_combo[:-len(jersey_number)].strip()
    else:
        # No jersey number found
        player_name = name_jersey_combo.strip()
        jersey_number = "N/A"
    
    return player_name, jersey_number

def scrape_team_roster(roster_url):
    """Scrape a single team roster with proper name parsing"""
    print(f"Scraping {roster_url}")
    
    try:
        team_resp = requests.get(roster_url, headers=headers)
        team_resp.raise_for_status()
        team_soup = BeautifulSoup(team_resp.text, "html.parser")

        # Extract team information
        team_abbr, team_slug = extract_team_info_from_url(roster_url)
        
        # Get team name from page title or h1
        team_name_tag = team_soup.find("h1")
        if team_name_tag:
            team_name = team_name_tag.text.strip().replace(" Roster", "")
        else:
            # Try alternate methods
            title_tag = team_soup.find("title")
            if title_tag:
                team_name = title_tag.text.split(" Roster")[0].strip()
            else:
                team_name = "Unknown_Team"

        players = []
        
        # Find the main roster table
        rows = team_soup.select("table tbody tr")
        
        if not rows:
            print(f"  WARNING: No roster rows found for {team_name}")
            return None

        for row in rows:
            cols = row.find_all(["td", "th"])
            if not cols:
                continue

            # Find player link and extract player ID
            link_tag = row.find("a", href=True)
            if not link_tag or "/mlb/player/" not in link_tag.get("href", ""):
                continue

            href = link_tag["href"]
            player_match = re.search(r"/mlb/player/_/id/(\d+)", href)
            if not player_match:
                continue
                
            player_id = player_match.group(1)
            
            # Extract column data
            def get_col_text(index, default="N/A"):
                if index < len(cols):
                    text = cols[index].get_text(strip=True)
                    return text if text else default
                return default
            
            # Based on debug output, the structure is:
            # Column 0: Empty or jersey number
            # Column 1: Name + Jersey Number (e.g., "Aaron Judge99")
            # Column 2: Position (e.g., "RF", "SP", "C")
            # Column 3: Batting hand (e.g., "R", "L", "B")
            # Column 4: Throwing hand (e.g., "R", "L")
            # Column 5: Age (e.g., "33")
            # Column 6: Height (e.g., "6' 7\"")
            # Column 7: Weight (e.g., "282 lbs")
            # Column 8: Birth Place (e.g., "Linden, CA")
            
            name_jersey_combo = get_col_text(1)
            player_name, jersey_from_name = extract_name_and_jersey(name_jersey_combo)
            
            player_data = {
                "player_id": player_id,
                "name": player_name,
                "jersey_number": jersey_from_name,
                "position": get_col_text(2),
                "batting_hand": get_col_text(3),
                "throwing_hand": get_col_text(4),
                "age": get_col_text(5),
                "height": get_col_text(6),
                "weight": get_col_text(7),
                "birth_place": get_col_text(8),
                "team_name": team_name,
                "team_abbreviation": team_abbr,
                "team_slug": team_slug,
                "roster_url": roster_url,
                "espn_url": base_url + href
            }
            
            players.append(player_data)

        return {
            "team_info": {
                "team_name": team_name,
                "team_abbreviation": team_abbr, 
                "team_slug": team_slug,
                "roster_url": roster_url
            },
            "players": players,
            "scrape_date": datetime.now().isoformat(),
            "total_players": len(players)
        }
        
    except Exception as e:
        print(f"  ERROR scraping {roster_url}: {e}")
        return None

def main():
    print("Starting MLB roster scraping (FINAL VERSION)...")
    
    # Get team roster links
    print("Getting team roster links...")
    resp = requests.get(teams_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    team_links = []
    # Updated to use 'string' instead of deprecated 'text' parameter
    for link in soup.find_all("a", href=True, string="Roster"):
        team_links.append(base_url + link["href"])
    
    print(f"Found {len(team_links)} team roster links")
    
    if not team_links:
        print("No roster links found!")
        return

    # Scrape each team
    all_teams_data = {}
    successful_teams = 0
    total_players = 0
    
    for i, roster_url in enumerate(team_links):
        team_data = scrape_team_roster(roster_url)
        
        if team_data:
            team_name = team_data["team_info"]["team_name"]
            safe_team_name = team_name.replace(" ", "_").replace("/", "_")
            
            # Save individual team file
            output_path = os.path.join(output_folder, f"{safe_team_name}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(team_data, f, indent=2, ensure_ascii=False)
            
            print(f"  Saved {team_data['total_players']} players to {safe_team_name}.json")
            all_teams_data[safe_team_name] = team_data
            successful_teams += 1
            total_players += team_data['total_players']
        
        # Small delay to be respectful
        if i < len(team_links) - 1:
            import time
            time.sleep(1)
    
    # Save summary file with team abbreviations mapping
    team_abbr_mapping = {}
    for team_name, team_data in all_teams_data.items():
        abbr = team_data["team_info"]["team_abbreviation"]
        team_abbr_mapping[abbr] = {
            "team_name": team_data["team_info"]["team_name"],
            "safe_name": team_name,
            "slug": team_data["team_info"]["team_slug"],
            "player_count": team_data["total_players"]
        }
    
    summary_data = {
        "scrape_summary": {
            "scrape_date": datetime.now().isoformat(),
            "total_teams_scraped": successful_teams,
            "total_players_scraped": total_players,
            "teams_requested": len(team_links)
        },
        "team_abbreviations": team_abbr_mapping,
        "file_structure": {
            "individual_files": f"Each team saved as {team_name}.json",
            "summary_file": "This file contains overview and team abbreviation mapping",
            "player_data_includes": [
                "player_id", "name", "jersey_number", "position",
                "batting_hand", "throwing_hand", "age", "height", "weight",
                "birth_place", "team_info", "espn_url"
            ]
        }
    }
    
    summary_file = os.path.join(output_folder, "mlb_scrape_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSUCCESS: Scraped {successful_teams}/{len(team_links)} teams")
    print(f"Total players: {total_players}")
    print(f"Summary saved to: mlb_scrape_summary.json")
    print(f"\nTeam abbreviations found:")
    for abbr, info in sorted(team_abbr_mapping.items()):
        print(f"  {abbr}: {info['team_name']} ({info['player_count']} players)")

if __name__ == "__main__":
    main()