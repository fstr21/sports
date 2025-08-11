import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time

def get_team_roster_links(teams_page_url):
    """
    Scrapes the main league teams page to get the name and roster URL for every team.

    Args:
        teams_page_url (str): The URL of the main league teams page.

    Returns:
        dict: A dictionary where keys are team names and values are their roster URLs.
    """
    print(f"Finding all team roster links from: {teams_page_url}")
    team_links = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(teams_page_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find team links using the correct pattern for NHL
        link_containers = soup.find_all('a', class_='AnchorLink', href=re.compile(r'/nhl/team/_/name/'))

        for container in link_containers:
            roster_link = container.find_next('a', href=re.compile(r'/roster/'))
            team_name_element = container.find('h2')

            if roster_link and team_name_element:
                team_name = team_name_element.text.strip()
                full_roster_url = f"https://www.espn.com{roster_link['href']}"
                if team_name not in team_links:
                    team_links[team_name] = full_roster_url
                    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching team list: {e}")
    
    print(f"Found {len(team_links)} teams.")
    return team_links


def scrape_espn_roster(url, full_output_path, team_name):
    """
    Scrapes a given ESPN NHL team roster page, extracts key player data,
    and saves it to a JSON file.

    Args:
        url (str): The URL of the ESPN roster page.
        full_output_path (str): The full path including directories and filename for the output.
        team_name (str): The name of the team being scraped.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"\nScraping roster for '{team_name}' from: {url}")

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
                player_link = row.find('a', href=re.compile(r'/nhl/player/_/id/'))
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
                # Cell 0: Empty or contains player image
                # Cell 1: Player name with jersey number
                # Cell 2: Age
                # Cell 3: Height
                # Cell 4: Weight
                # Cell 5: Shooting hand
                # Cell 6: Birthplace
                # Cell 7: Birthdate
                
                # Extract player name and jersey number
                name_cell = cells[1]
                player_link = name_cell.find('a', href=re.compile(r'/nhl/player/_/id/'))
                if not player_link:
                    continue
                    
                player_name = player_link.text.strip()
                
                # Extract jersey number from span if available
                jersey_span = name_cell.find('span')
                jersey_number = jersey_span.text.strip() if jersey_span else "N/A"
                
                # Extract player ID from the link
                href = player_link['href']
                player_id_match = re.search(r'/id/(\d+)', href)
                player_id = player_id_match.group(1) if player_id_match else "N/A"
                
                # Extract other player details
                age = cells[2].text.strip() if len(cells) > 2 else "N/A"
                height = cells[3].text.strip() if len(cells) > 3 else "N/A"
                weight = cells[4].text.strip() if len(cells) > 4 else "N/A"
                shooting_hand = cells[5].text.strip() if len(cells) > 5 else "N/A"
                birthplace = cells[6].text.strip() if len(cells) > 6 else "N/A"
                birthdate = cells[7].text.strip() if len(cells) > 7 else "N/A"
                
                # Create player dictionary
                player_dict = {
                    "id": player_id,
                    "name": player_name,
                    "jersey_number": jersey_number,
                    "age": age,
                    "height": height,
                    "weight_lbs": weight,
                    "shooting_hand": shooting_hand,
                    "birthplace": birthplace,
                    "birthdate": birthdate
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
        print(f"✅ Success! Roster data saved to: {full_output_path}")
        print(f"   Extracted {len(roster_data)} players")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {url}: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    LEAGUE_ACRONYM = "nhl"
    LEAGUE_TEAMS_URL = f"https://www.espn.com/{LEAGUE_ACRONYM}/teams"

    BASE_OUTPUT_DIR = os.path.join('players', LEAGUE_ACRONYM)
    
    all_teams = get_team_roster_links(LEAGUE_TEAMS_URL)
    
    if not all_teams:
        print("Could not retrieve team list. Exiting.")
    else:
        print(f"\nProcessing {len(all_teams)} teams...")
        for team_name, roster_url in all_teams.items():
            # Create a clean folder name from the team name
            safe_folder_name = team_name.lower().replace(' ', '_')
            team_directory = os.path.join(BASE_OUTPUT_DIR, safe_folder_name)
            
            # Create the directory structure
            os.makedirs(team_directory, exist_ok=True)
            
            json_output_path = os.path.join(team_directory, "roster.json")
            
            # Scrape the roster data
            scrape_espn_roster(roster_url, json_output_path, team_name)
            
            # Be a good internet citizen: wait a moment before the next request
            time.sleep(1)
            
        print("\n--- All teams processed. ---")
