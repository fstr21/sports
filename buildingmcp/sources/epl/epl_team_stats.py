import requests

def get_epl_2024_full_standings_with_headers():
    """
    Fetches and displays a comprehensive table of the 2024-2025 EPL season,
    including the necessary headers to ensure the request is successful.
    """
    
    url = "https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings"
    params = {"season": "2024"}
    
    # Add headers to mimic a browser request, which is often required.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print("Fetching 2024-2025 EPL season data from ESPN API...")
    
    try:
        # Include the headers in the request
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        standings = data['children'][0]['standings']['entries']
        
        print("\n--- English Premier League Final Standings (2024-2025) ---\n")
        
        # Print the table headers
        print(f"{'#':<3} {'Team':<25} {'ID':<5} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<5} {'GA':<5} {'GD':<5} {'Pts':<5} {'Note'}")
        print("-" * 100)

        for team_data in standings:
            stats = {stat['abbreviation']: stat['displayValue'] for stat in team_data['stats']}
            
            team_name = team_data['team'].get('displayName', 'N/A')
            team_id = team_data['team'].get('id', 'N/A')
            note = team_data.get('note', {}).get('description', '')
            
            rank = next((s['displayValue'] for s in team_data['stats'] if s['name'] == 'rank'), '-')
            games_played = stats.get('GP', '-')
            wins = stats.get('W', '-')
            draws = stats.get('D', '-')
            losses = stats.get('L', '-')
            points = stats.get('P', '-')
            goals_for = stats.get('F', '-')
            goals_against = stats.get('A', '-')
            goal_difference = stats.get('GD', '-')
            
            print(f"{rank:<3} {team_name:<25} {team_id:<5} {games_played:<4} {wins:<4} {draws:<4} {losses:<4} {goals_for:<5} {goals_against:<5} {goal_difference:<5} {points:<5} {note}")

    except requests.exceptions.RequestException as e:
        print(f"\nError fetching data: {e}")
    except KeyError:
        print("\nError: Could not parse the data. The API's data structure may have changed. This can happen if the request is blocked.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    get_epl_2024_full_standings_with_headers()