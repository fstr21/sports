import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time

def get_mls_teams():
    """
    Scrapes the MLS teams page to get the name and squad URL for every team.

    Returns:
        dict: A dictionary where keys are team names and values are their squad URLs.
    """
    teams_url = "https://www.espn.com/soccer/teams/_/league/usa.1"
    print(f"Finding all MLS team squad links from: {teams_url}")
    teams = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(teams_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for team links with specific pattern
        team_links = soup.find_all('a', href=re.compile(r'/soccer/team/_/id/\d+/'))
        
        for link in team_links:
            href = link.get('href', '')
            team_name = link.text.strip()
            
            # Skip empty names
            if not team_name:
                continue
                
            # Extract team ID
            team_id_match = re.search(r'/id/(\d+)/', href)
            if team_id_match:
                team_id = team_id_match.group(1)
                # Construct squad URL
                squad_url = f"https://www.espn.com/soccer/team/squad/_/id/{team_id}"
                teams[team_name] = squad_url
                    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching team list: {e}")
    
    # Filter out national teams (USMNT, USWNT) if they're included
    filtered_teams = {name: url for name, url in teams.items() 
                     if 'USMNT' not in name and 'USWNT' not in name}
    
    print(f"Found {len(filtered_teams)} MLS teams.")
    return filtered_teams


def scrape_mls_squad(url, full_output_path, team_name):
    """
    Scrapes a given ESPN MLS team squad page, extracts key player data,
    and saves it to a JSON file.

    Args:
        url (str): The URL of the ESPN squad page.
        full_output_path (str): The full path including directories and filename for the output.
        team_name (str): The name of the team being scraped.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"\nScraping squad for '{team_name}' from: {url}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        roster_data = []
        
        # Find all table rows
        rows = soup.find_all('tr')
        
        # Look for rows that contain player data
        player_rows = []
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:  # Player rows typically have multiple cells
                # Check if any cell contains a player link
                player_link = row.find('a', href=re.compile(r'/soccer/player/_/id/'))
                if player_link:
                    player_rows.append(row)

        if not player_rows:
            print(f"Warning: Could not find any player rows for {url}")
            return

        for row in player_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 8:
                continue
                
            try:
                # Extract player information from cells
                # Cell 0: Player name with jersey number
                # Cell 1: Position
                # Cell 2: Age
                # Cell 3: Height
                # Cell 4: Weight
                # Cell 5: Nationality
                # Cell 6: Games Played
                # Cell 7: Goals
                # Cell 8: Assists
                # ... (more stats)
                
                # Extract player name and jersey number
                name_cell = cells[0]
                player_link = name_cell.find('a', href=re.compile(r'/soccer/player/_/id/'))
                if not player_link:
                    continue
                    
                player_name = player_link.text.strip()
                
                # Extract jersey number from the name text
                jersey_number = "N/A"
                name_text = name_cell.text.strip()
                jersey_match = re.search(r'(\d+)$', name_text)
                if jersey_match:
                    jersey_number = jersey_match.group(1)
                
                # Extract player ID from the link
                href = player_link['href']
                player_id_match = re.search(r'/id/(\d+)', href)
                player_id = player_id_match.group(1) if player_id_match else "N/A"
                
                # Extract other player details
                position = cells[1].text.strip() if len(cells) > 1 else "N/A"
                age = cells[2].text.strip() if len(cells) > 2 else "N/A"
                height = cells[3].text.strip() if len(cells) > 3 else "N/A"
                weight = cells[4].text.strip() if len(cells) > 4 else "N/A"
                nationality = cells[5].text.strip() if len(cells) > 5 else "N/A"
                games_played = cells[6].text.strip() if len(cells) > 6 else "N/A"
                goals = cells[7].text.strip() if len(cells) > 7 else "N/A"
                assists = cells[8].text.strip() if len(cells) > 8 else "N/A"
                
                # Create player dictionary
                player_dict = {
                    "id": player_id,
                    "name": player_name,
                    "jersey_number": jersey_number,
                    "position": position,
                    "age": age,
                    "height": height,
                    "weight_lbs": weight,
                    "nationality": nationality,
                    "games_played": games_played,
                    "goals": goals,
                    "assists": assists
                }
                
                roster_data.append(player_dict)
                
            except (AttributeError, IndexError, TypeError) as e:
                print(f"Skipping a row due to parsing error: {e}")
                continue
        
        if not roster_data:
            print(f"Warning: No players found at {url}.")
            return

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        
        with open(full_output_path, 'w', encoding='utf-8') as f:
            json.dump(roster_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Success! Squad data saved to: {full_output_path}")
        print(f"   Extracted {len(roster_data)} players")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {url}: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    BASE_OUTPUT_DIR = os.path.join('players', 'mls')
    
    all_teams = get_mls_teams()
    
    if not all_teams:
        print("Could not retrieve team list. Exiting.")
    else:
        print(f"\nProcessing {len(all_teams)} teams...")
        for team_name, squad_url in all_teams.items():
            # Create a clean folder name from the team name
            safe_folder_name = re.sub(r'[^\w\s-]', '', team_name).strip().lower()
            safe_folder_name = re.sub(r'[-\s]+', '_', safe_folder_name)
            team_directory = os.path.join(BASE_OUTPUT_DIR, safe_folder_name)
            
            # Create the directory structure
            os.makedirs(team_directory, exist_ok=True)
            
            json_output_path = os.path.join(team_directory, "roster.json")
            
            # Scrape the squad data
            scrape_mls_squad(squad_url, json_output_path, team_name)
            
            # Be a good internet citizen: wait a moment before the next request
            time.sleep(1)
            
        print("\n--- All teams processed. ---")
