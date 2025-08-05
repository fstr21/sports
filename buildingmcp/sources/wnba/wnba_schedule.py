# wnba_clean_export.py

import requests
import json
import os
import datetime

def process_and_save_game_data():
    """
    Fetches WNBA game data, processes it into a clean JSON format,
    and saves it to a local file.
    """
    
    # --- 1. Fetch Raw Data from API ---
    base_url = "http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
    game_date = "20250805"
    params = {"dates": game_date}
    
    print(f"Fetching game data for {game_date}...")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        raw_data = response.json()
        
        if not raw_data.get('events'):
            print(f"No games found for {game_date}.")
            return
            
        # We will process the first game found
        game_event = raw_data['events'][0]

        # --- 2. Process Raw Data into a Clean Structure ---
        print("Processing raw data into clean JSON format...")
        
        # The main competition object contains most of the details
        competition = game_event['competitions'][0]
        
        # Identify home and away teams
        home_team_data = next(c for c in competition['competitors'] if c['homeAway'] == 'home')
        away_team_data = next(c for c in competition['competitors'] if c['homeAway'] == 'away')
        
        # Extract odds information if it exists
        odds_data = competition.get('odds', [{}])[0]
        
        # Build the new, clean JSON object
        clean_game_data = {
            "gameInfo": {
                "gameId": game_event.get('id'),
                "gameName": game_event.get('name'),
                "gameDateUTC": game_event.get('date'),
                "gameStatus": game_event['status']['type'].get('description'),
                "venueName": competition['venue'].get('fullName'),
                "venueCity": competition['venue']['address'].get('city'),
                "venueState": competition['venue']['address'].get('state'),
                "broadcast": ", ".join([b['names'][0] for b in competition.get('broadcasts', []) if b.get('names')])
            },
            "odds": {
                "provider": odds_data.get('provider', {}).get('name', 'N/A'),
                "details": odds_data.get('details'),
                "spread": odds_data.get('spread'),
                "overUnder": odds_data.get('overUnder')
            },
            "homeTeam": {
                "teamId": home_team_data['team'].get('id'),
                "teamName": home_team_data['team'].get('displayName'),
                "record": next((rec['summary'] for rec in home_team_data.get('records', []) if rec['name'] == 'overall'), None),
                "moneyLine": odds_data.get('homeTeamOdds', {}).get('moneyLine'),
                "spreadOdds": odds_data.get('homeTeamOdds', {}).get('spreadOdds'),
                "stats": {stat['name']: stat['displayValue'] for stat in home_team_data.get('statistics', [])},
                "leaders": {
                    leader['name']: {
                        "playerName": leader['leaders'][0]['athlete'].get('displayName'),
                        "value": leader['leaders'][0].get('displayValue')
                    } for leader in home_team_data.get('leaders', []) if leader.get('leaders')
                }
            },
            "awayTeam": {
                "teamId": away_team_data['team'].get('id'),
                "teamName": away_team_data['team'].get('displayName'),
                "record": next((rec['summary'] for rec in away_team_data.get('records', []) if rec['name'] == 'overall'), None),
                "moneyLine": odds_data.get('awayTeamOdds', {}).get('moneyLine'),
                "spreadOdds": odds_data.get('awayTeamOdds', {}).get('spreadOdds'),
                "stats": {stat['name']: stat['displayValue'] for stat in away_team_data.get('statistics', [])},
                "leaders": {
                    leader['name']: {
                        "playerName": leader['leaders'][0]['athlete'].get('displayName'),
                        "value": leader['leaders'][0].get('displayValue')
                    } for leader in away_team_data.get('leaders', []) if leader.get('leaders')
                }
            }
        }

        # --- 3. Save the Clean Data to File ---
        output_dir = r"C:\Users\fstr2\Desktop\sports\buildingmcp"
        file_name = "wnba_schedule_raw.json"
        full_path = os.path.join(output_dir, file_name)

        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Saving cleaned data to: {full_path}")
        
        with open(full_path, 'w') as json_file:
            json.dump(clean_game_data, json_file, indent=2)
            
        print("\nSuccess! The cleaned JSON file has been created.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except Exception as e:
        print(f"An error occurred during processing or file writing: {e}")


if __name__ == "__main__":
    process_and_save_game_data()