import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time

def get_team_roster_links(teams_page_url):
    """
    Scrapes the main WNBA teams page to get the name and roster URL for every team.

    Args:
        teams_page_url (str): The URL of the main WNBA teams page.

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

        link_containers = soup.find_all('a', class_='AnchorLink', href=re.compile(r'/wnba/team/_/name/'))

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


def scrape_espn_roster(url, full_output_path):
    """
    Scrapes a given ESPN team roster page, extracts player data,
    and saves it to a JSON file at the specified full path.

    Args:
        url (str): The URL of the ESPN roster page.
        full_output_path (str): The full path including directories and filename for the output.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"\nScraping roster from: {url}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        roster_data = []
        roster_sections = soup.find_all('div', class_='Roster')

        if not roster_sections:
            print(f"Warning: Could not find any roster sections on the page for {url}")
            return

        for section in roster_sections:
            player_rows = section.find_all('tr', class_='Table__TR')
            for row in player_rows:
                if row.find('th'):
                    continue
                cells = row.find_all('td')
                if len(cells) >= 6:
                    try:
                        name_cell = cells[1]
                        player_link = name_cell.find('a')
                        if not player_link: continue
                        player_name = player_link.text.strip()
                        player_href = player_link['href']
                        player_id_match = re.search(r'/id/(\d+)/', player_href)
                        player_id = player_id_match.group(1) if player_id_match else 'N/A'
                        jersey_span = name_cell.find('span', class_='player-jersey')
                        jersey_number = jersey_span.text.strip() if jersey_span else 'N/A'
                        position = cells[2].text.strip()
                        age = cells[3].text.strip()
                        height = cells[4].text.strip()
                        weight = cells[5].text.strip()
                        college = cells[6].text.strip()
                        player_dict = {
                            "id": player_id, "name": player_name, "jersey_number": jersey_number,
                            "position": position or 'N/A', "age": age or 'N/A',
                            "height": height or 'N/A', "weight_lbs": weight or 'N/A',
                            "college": college or 'N/A',
                        }
                        roster_data.append(player_dict)
                    except (AttributeError, IndexError, TypeError) as e:
                        print(f"Skipping a row due to parsing error: {e}")
                        continue
        
        if not roster_data:
            print(f"Warning: No players were found for {url}.")
            return

        # The full path is now passed directly to this function
        with open(full_output_path, 'w', encoding='utf-8') as f:
            json.dump(roster_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Success! Roster data saved to: {full_output_path}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {url}: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    WNBA_TEAMS_URL = "https://www.espn.com/wnba/teams"
    # Define the base directory for all output
    BASE_OUTPUT_DIR = os.path.join('players', 'wnba')
    
    # 1. Get all the team roster URLs first
    all_teams = get_team_roster_links(WNBA_TEAMS_URL)
    
    if not all_teams:
        print("Could not retrieve team list. Exiting.")
    else:
        # 2. Loop through each team and scrape its roster
        for team_name, roster_url in all_teams.items():
            # Create a clean folder name from the team name
            # e.g., "Atlanta Dream" -> "atlanta_dream"
            safe_folder_name = team_name.lower().replace(' ', '_')
            team_directory = os.path.join(BASE_OUTPUT_DIR, safe_folder_name)
            
            # Create the directory structure (e.g., players/wnba/atlanta_dream)
            # exist_ok=True prevents an error if the directory already exists
            os.makedirs(team_directory, exist_ok=True)
            
            # Define the full path for the output JSON file
            json_output_path = os.path.join(team_directory, "roster.json")
            
            scrape_espn_roster(roster_url, json_output_path)
            
            # Be a good internet citizen: wait a moment before the next request
            time.sleep(1)
            
        print("\n--- All teams processed. ---")
