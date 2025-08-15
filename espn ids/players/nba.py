import requests
from bs4 import BeautifulSoup
import re
import os
import json

teams_url = "https://www.espn.com/nba/teams"
base_url = "https://www.espn.com"

output_folder = r"C:\Users\fstr2\Desktop\player_stats_mcp_test\players\nba"
os.makedirs(output_folder, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0"}

# Step 1: Get all team roster links
resp = requests.get(teams_url, headers=headers)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

team_links = [base_url + a["href"] for a in soup.find_all("a", href=True, text="Roster")]

# Step 2: Loop through teams
for roster_url in team_links:
    print(f"Scraping {roster_url}")
    r = requests.get(roster_url, headers=headers)
    r.raise_for_status()
    rsoup = BeautifulSoup(r.text, "html.parser")

    # Get team name
    team_name_tag = rsoup.find("h1")
    team_name = team_name_tag.text.strip().replace(" Roster", "") if team_name_tag else "Unknown_Team"

    players = []
    rows = rsoup.select("table tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        # First column: Jersey + Name
        jersey = cols[0].text.strip()
        name_tag = cols[1].find("a", href=True)
        if not name_tag:
            continue
        player_name = name_tag.text.strip()

        # Player ID
        href = name_tag["href"]
        pid_match = re.search(r"/id/(\d+)", href)
        if not pid_match:
            continue
        player_id = pid_match.group(1)

        # Other attributes
        position = cols[2].text.strip()
        age = cols[3].text.strip()
        height = cols[4].text.strip()
        weight = cols[5].text.strip()
        college = cols[6].text.strip() if len(cols) > 6 else "N/A"

        players.append({
            "id": player_id,
            "name": player_name,
            "jersey_number": jersey if jersey else "N/A",
            "position": position,
            "age": age,
            "height": height,
            "weight_lbs": weight,
            "college": college
        })

    # Save JSON
    safe_team = team_name.replace(" ", "_").replace("/", "_")
    path = os.path.join(output_folder, f"{safe_team}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=4)

    print(f"Saved {len(players)} players to {path}")

print("✅ NBA scraping complete")
