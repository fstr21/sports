from mcp.server.fastmcp import FastMCP
import httpx
import os
import json
from typing import Optional

mcp = FastMCP("enhanced-soccer-data")

# Add health check endpoint for Railway
@mcp.get("/")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {"status": "healthy", "service": "enhanced-soccer-data"}

API_END_POINT = "https://api.soccerdataapi.com/"
AUTH_KEY = os.environ.get("AUTH_KEY")

if not AUTH_KEY:
    raise EnvironmentError("AUTH_KEY is not set in .env")

@mcp.tool()
async def get_livescores():
    """Get live scores for ongoing matches"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_END_POINT + "livescores/",
            params={"auth_token": AUTH_KEY},
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",
            },
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_leagues():
    """Get all available leagues"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_END_POINT + "league/",
            params={"auth_token": AUTH_KEY},
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",
            },
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_league_standings(league_id: int):
    """Get standings for a specific league (EPL=228, La Liga=207, MLS=253)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_END_POINT + "standing/",
            params={
                "league_id": league_id,
                "auth_token": AUTH_KEY
            },
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",
            },
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_league_matches(league_id: int):
    """Get matches for a specific league with detailed events and player data (EPL=228, La Liga=207, MLS=253)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_END_POINT + "matches/",
            params={
                "league_id": league_id,
                "auth_token": AUTH_KEY
            },
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",
            },
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_team_info(team_id: int):
    """Get basic information about a specific team (e.g., Fulham=4145, Liverpool=61826, Brighton=3200)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_END_POINT + "team/",
            params={
                "team_id": team_id,
                "auth_token": AUTH_KEY
            },
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",
            },
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_player_info(player_id: int):
    """Get basic information about a specific player (limited data - just ID and name)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_END_POINT + "player/",
            params={
                "player_id": player_id,
                "auth_token": AUTH_KEY
            },
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",
            },
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def extract_players_from_league(league_id: int):
    """Extract all players from a league's match events (best way to get player data with stats)"""
    try:
        # Get league matches with events
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_END_POINT + "matches/",
                params={
                    "league_id": league_id,
                    "auth_token": AUTH_KEY
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept-Encoding": "gzip",
                },
            )
            response.raise_for_status()
            matches_data = response.json()
        
        # Extract players from match events
        players_db = {}
        player_stats = {}
        
        if isinstance(matches_data, list):
            for league_entry in matches_data:
                if isinstance(league_entry, dict):
                    stage_data = league_entry.get("stage", [])
                    
                    for stage in stage_data:
                        if isinstance(stage, dict):
                            matches = stage.get("matches", [])
                            
                            for match in matches:
                                if isinstance(match, dict):
                                    events = match.get("events", [])
                                    teams = match.get("teams", {})
                                    home_team = teams.get("home", {})
                                    away_team = teams.get("away", {})
                                    
                                    # Process each event for player data
                                    for event in events:
                                        if isinstance(event, dict):
                                            # Extract players from different event types
                                            if "player" in event:
                                                player = event["player"]
                                                if isinstance(player, dict):
                                                    player_id = player.get("id")
                                                    player_name = player.get("name")
                                                    
                                                    if player_id and player_name:
                                                        if player_id not in players_db:
                                                            players_db[player_id] = {
                                                                "id": player_id,
                                                                "name": player_name,
                                                                "teams": set(),
                                                                "stats": {
                                                                    "goals": 0,
                                                                    "assists": 0,
                                                                    "yellow_cards": 0,
                                                                    "red_cards": 0,
                                                                    "substitutions_in": 0,
                                                                    "substitutions_out": 0
                                                                }
                                                            }
                                                        
                                                        # Determine team
                                                        team_name = ""
                                                        if event.get("team") == "home":
                                                            team_name = home_team.get("name", "")
                                                        elif event.get("team") == "away":
                                                            team_name = away_team.get("name", "")
                                                        
                                                        if team_name:
                                                            players_db[player_id]["teams"].add(team_name)
                                                        
                                                        # Count stats
                                                        event_type = event.get("event_type", "")
                                                        if "goal" in event_type:
                                                            players_db[player_id]["stats"]["goals"] += 1
                                                        elif "yellow_card" in event_type:
                                                            players_db[player_id]["stats"]["yellow_cards"] += 1
                                                        elif "red_card" in event_type:
                                                            players_db[player_id]["stats"]["red_cards"] += 1
                                            
                                            # Handle substitutions
                                            if event.get("event_type") == "substitution":
                                                if "player_in" in event:
                                                    player_in = event["player_in"]
                                                    if isinstance(player_in, dict):
                                                        player_id = player_in.get("id")
                                                        player_name = player_in.get("name")
                                                        
                                                        if player_id and player_name:
                                                            if player_id not in players_db:
                                                                players_db[player_id] = {
                                                                    "id": player_id,
                                                                    "name": player_name,
                                                                    "teams": set(),
                                                                    "stats": {
                                                                        "goals": 0, "assists": 0, "yellow_cards": 0,
                                                                        "red_cards": 0, "substitutions_in": 0, "substitutions_out": 0
                                                                    }
                                                                }
                                                            players_db[player_id]["stats"]["substitutions_in"] += 1
                                                
                                                if "player_out" in event:
                                                    player_out = event["player_out"]
                                                    if isinstance(player_out, dict):
                                                        player_id = player_out.get("id")
                                                        player_name = player_out.get("name")
                                                        
                                                        if player_id and player_name:
                                                            if player_id not in players_db:
                                                                players_db[player_id] = {
                                                                    "id": player_id,
                                                                    "name": player_name,
                                                                    "teams": set(),
                                                                    "stats": {
                                                                        "goals": 0, "assists": 0, "yellow_cards": 0,
                                                                        "red_cards": 0, "substitutions_in": 0, "substitutions_out": 0
                                                                    }
                                                                }
                                                            players_db[player_id]["stats"]["substitutions_out"] += 1
                                            
                                            # Handle assists
                                            if "assist_player" in event and event["assist_player"]:
                                                assist_player = event["assist_player"]
                                                if isinstance(assist_player, dict):
                                                    player_id = assist_player.get("id")
                                                    player_name = assist_player.get("name")
                                                    
                                                    if player_id and player_name:
                                                        if player_id not in players_db:
                                                            players_db[player_id] = {
                                                                "id": player_id,
                                                                "name": player_name,
                                                                "teams": set(),
                                                                "stats": {
                                                                    "goals": 0, "assists": 0, "yellow_cards": 0,
                                                                    "red_cards": 0, "substitutions_in": 0, "substitutions_out": 0
                                                                }
                                                            }
                                                        players_db[player_id]["stats"]["assists"] += 1
        
        # Convert sets to lists for JSON serialization
        for player_id, player_data in players_db.items():
            player_data["teams"] = list(player_data["teams"])
        
        result = {
            "total_players_found": len(players_db),
            "league_id": league_id,
            "players": players_db
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_h2h_betting_analysis(team_1_id: int, team_2_id: int, team_1_name: str, team_2_name: str):
    """Get comprehensive head-to-head analysis between two teams for betting insights"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_END_POINT + "head-to-head/",
                params={
                    "team_1_id": team_1_id,
                    "team_2_id": team_2_id,
                    "auth_token": AUTH_TOKEN
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept-Encoding": "gzip",
                },
            )
            response.raise_for_status()
            raw_data = response.json()
        
        # Process the H2H data to extract betting insights
        if not raw_data or "data" not in raw_data:
            return json.dumps({"error": "No H2H data available for these teams"})
        
        h2h_data = raw_data["data"]
        
        # Extract team records
        team1_record = {}
        team2_record = {}
        draws = {"count": 0, "rate": 0.0}
        goals_data = {}
        betting_insights = {}
        
        # Process matches to build comprehensive analysis
        matches = h2h_data.get("matches", [])
        total_meetings = len(matches)
        
        if total_meetings > 0:
            team1_wins = sum(1 for match in matches if match.get("winner_id") == team_1_id)
            team2_wins = sum(1 for match in matches if match.get("winner_id") == team_2_id)
            draws_count = total_meetings - team1_wins - team2_wins
            
            # Calculate team records
            team1_record = {
                "name": team_1_name,
                "wins": team1_wins,
                "win_rate": (team1_wins / total_meetings) * 100
            }
            
            team2_record = {
                "name": team_2_name,
                "wins": team2_wins,
                "win_rate": (team2_wins / total_meetings) * 100
            }
            
            draws = {
                "count": draws_count,
                "rate": (draws_count / total_meetings) * 100
            }
            
            # Calculate goals statistics
            total_goals = sum(match.get("goals", {}).get("home", 0) + match.get("goals", {}).get("away", 0) for match in matches)
            team1_goals = sum(match.get("goals", {}).get("home", 0) if match.get("home_team", {}).get("id") == team_1_id 
                            else match.get("goals", {}).get("away", 0) for match in matches)
            team2_goals = sum(match.get("goals", {}).get("away", 0) if match.get("home_team", {}).get("id") == team_1_id 
                            else match.get("goals", {}).get("home", 0) for match in matches)
            
            goals_data = {
                "average_per_game": total_goals / total_meetings,
                "team_1_total": team1_goals,
                "team_2_total": team2_goals
            }
            
            # Generate betting insights
            avg_goals = total_goals / total_meetings
            if avg_goals > 2.8:
                betting_insights["goals_trend"] = "High-scoring matches - favor Over 2.5"
            elif avg_goals < 2.2:
                betting_insights["goals_trend"] = "Low-scoring matches - favor Under 2.5"
            else:
                betting_insights["goals_trend"] = "Balanced scoring"
        
        result = {
            "total_meetings": total_meetings,
            "team_1_record": team1_record,
            "team_2_record": team2_record,
            "draws": draws,
            "goals": goals_data,
            "betting_insights": betting_insights,
            "data_source": "head-to-head endpoint"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"H2H analysis failed: {str(e)}"})

@mcp.tool()
async def get_betting_matches(date: str, league_filter: str = None):
    """Get matches for a specific date with betting odds across multiple leagues"""
    try:
        # League mapping for the filter
        LEAGUE_MAPPING = {
            "EPL": 228,
            "La Liga": 297,
            "MLS": 168,
            "Bundesliga": 241,
            "Serie A": 253,
            "UEFA": 310
        }
        
        all_matches = {}
        total_matches = 0
        
        # If league filter specified, only get that league
        leagues_to_check = [league_filter] if league_filter and league_filter in LEAGUE_MAPPING else LEAGUE_MAPPING.keys()
        
        for league_code in leagues_to_check:
            league_id = LEAGUE_MAPPING[league_code]
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        API_END_POINT + "matches/",
                        params={
                            "league_id": league_id,
                            "date": date,
                            "auth_token": AUTH_TOKEN
                        },
                        headers={
                            "Content-Type": "application/json",
                            "Accept-Encoding": "gzip",
                        },
                    )
                    
                    if response.status_code == 200:
                        matches_data = response.json()
                        league_matches = []
                        
                        # Extract matches from the API response structure
                        if isinstance(matches_data, list) and matches_data:
                            for league_data in matches_data:
                                if isinstance(league_data, dict):
                                    # Check for direct matches
                                    if 'matches' in league_data:
                                        league_matches.extend(league_data['matches'])
                                    # Check for stage-based matches
                                    elif 'stage' in league_data:
                                        for stage in league_data['stage']:
                                            if 'matches' in stage:
                                                league_matches.extend(stage['matches'])
                        
                        # Filter for matches on the requested date and add betting context
                        filtered_matches = []
                        for match in league_matches:
                            match_date = match.get('date', '')
                            if match_date == date:
                                # Enhance match with betting context
                                enhanced_match = {
                                    **match,
                                    "league_context": {
                                        "code": league_code,
                                        "id": league_id,
                                        "name": league_code
                                    }
                                }
                                filtered_matches.append(enhanced_match)
                        
                        if filtered_matches:
                            all_matches[league_code] = filtered_matches
                            total_matches += len(filtered_matches)
            
            except Exception as league_error:
                # Continue with other leagues if one fails
                continue
        
        result = {
            "date": date,
            "total_matches": total_matches,
            "leagues_found": len(all_matches),
            "matches_by_league": all_matches,
            "league_filter": league_filter
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Betting matches query failed: {str(e)}"})

if __name__ == "__main__":
    mcp.run()