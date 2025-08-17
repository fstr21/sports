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

if __name__ == "__main__":
    mcp.run()