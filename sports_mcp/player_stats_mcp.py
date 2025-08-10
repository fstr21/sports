#!/usr/bin/env python3
"""
Player Stats MCP Server - ESPN Player Statistics Integration

This MCP server provides comprehensive player statistics from ESPN's API,
designed to work seamlessly with the existing sports ecosystem.
"""
import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pytz

import httpx
from fastmcp import FastMCP

# Add the current directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

class PlayerStatsMcpServer:
    """MCP server for ESPN player statistics."""
    
    def __init__(self):
        """Initialize the Player Stats MCP server."""
        self.server = FastMCP("player-stats-mcp")
        self.client = httpx.AsyncClient(timeout=15.0)
        self.register_tools()
    
    def register_tools(self):
        """Register MCP tools for player statistics."""
        
        @self.server.tool(
            name="get_player_stats",
            description="Get comprehensive player statistics including season averages, recent games, and key performance metrics"
        )
        async def get_player_stats(
            sport: str,
            league: str, 
            player_id: str,
            season: Optional[str] = None,
            games_limit: int = 10
        ) -> Dict[str, Any]:
            """
            Get player statistics from ESPN Core API.
            
            Args:
                sport: Sport name (basketball, football, baseball, etc.)
                league: League name (nba, wnba, nfl, mlb, etc.)
                player_id: ESPN player ID
                season: Season year (optional, defaults to current)
                games_limit: Number of recent games to include (default 10)
                
            Returns:
                Comprehensive player statistics with recent performance
            """
            try:
                # Build ESPN Core API URL
                base_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{player_id}"
                
                # Get base player profile
                response = await self.client.get(base_url)
                if response.status_code != 200:
                    return {
                        "ok": False,
                        "error": f"ESPN API error: {response.status_code}",
                        "player_id": player_id
                    }
                
                player_data = response.json()
                
                # Get season statistics
                season_stats = {}
                parsed_stats = {}
                
                if "statistics" in player_data and isinstance(player_data["statistics"], dict):
                    stats_ref = player_data["statistics"].get("$ref")
                    if stats_ref:
                        stats_url = f"{stats_ref}"
                        if season:
                            stats_url += f"?season={season}"
                            
                        stats_response = await self.client.get(stats_url)
                        if stats_response.status_code == 200:
                            season_data = stats_response.json()
                            
                            # Parse the nested splits structure
                            if "splits" in season_data:
                                splits = season_data["splits"]
                                parsed_stats = self._parse_espn_statistics(splits, sport)
                
                # Get recent game logs
                recent_games = []
                if "statisticslog" in player_data and isinstance(player_data["statisticslog"], dict):
                    log_ref = player_data["statisticslog"].get("$ref")
                    if log_ref:
                        log_url = f"{log_ref}?limit={games_limit}"
                        
                        gamelog_response = await self.client.get(log_url)
                        if gamelog_response.status_code == 200:
                            gamelog_data = gamelog_response.json()
                            recent_games = gamelog_data.get("entries", [])
                
                # Calculate trending metrics
                trending_metrics = self._calculate_trends(recent_games, sport)
                
                # Format comprehensive response
                result = {
                    "ok": True,
                    "player_profile": {
                        "id": player_data.get("id"),
                        "displayName": player_data.get("displayName", "Unknown"),
                        "position": player_data.get("position", {}),
                        "team": player_data.get("team", {}),
                        "height": player_data.get("displayHeight", "Unknown"),
                        "weight": player_data.get("displayWeight", "Unknown"),
                        "age": player_data.get("age")
                    },
                    "season_averages": parsed_stats,
                    "recent_games": recent_games[:games_limit],
                    "trending_metrics": trending_metrics,
                    "prediction_ready": {
                        "has_season_stats": len(parsed_stats) > 0,
                        "recent_games_count": len(recent_games),
                        "sport": sport,
                        "league": league
                    },
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                return result
                
            except Exception as e:
                return {
                    "ok": False,
                    "error": f"Error fetching player stats: {str(e)}",
                    "player_id": player_id
                }
        
        @self.server.tool(
            name="get_players_by_team",
            description="Get all players for a specific team with basic stats"
        )
        async def get_players_by_team(
            sport: str,
            league: str,
            team_id: str
        ) -> Dict[str, Any]:
            """Get all players for a team."""
            try:
                base_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/teams/{team_id}/athletes"
                
                response = await self.client.get(base_url)
                if response.status_code != 200:
                    return {
                        "ok": False,
                        "error": f"ESPN API error: {response.status_code}",
                        "team_id": team_id
                    }
                
                data = response.json()
                players = []
                
                for item in data.get("items", []):
                    if "$ref" in item:
                        # Get individual player data
                        player_response = await self.client.get(item["$ref"])
                        if player_response.status_code == 200:
                            player_data = player_response.json()
                            players.append({
                                "id": player_data.get("id"),
                                "displayName": player_data.get("displayName"),
                                "position": player_data.get("position", {}),
                                "jersey": player_data.get("jersey")
                            })
                
                return {
                    "ok": True,
                    "team_id": team_id,
                    "players": players,
                    "count": len(players)
                }
                
            except Exception as e:
                return {
                    "ok": False,
                    "error": f"Error fetching team players: {str(e)}",
                    "team_id": team_id
                }
        
        @self.server.tool(
            name="find_player_by_name",
            description="Search for a player by name across leagues to get their ESPN ID"
        )
        async def find_player_by_name(
            player_name: str,
            sport: str = "basketball",
            league: str = "nba"
        ) -> Dict[str, Any]:
            """
            Find a player by name to get their ESPN ID for stats lookup.
            
            This is crucial for connecting player names from odds to ESPN stats.
            """
            try:
                # This would need to be implemented with ESPN's search API or
                # by maintaining a mapping of player names to IDs
                # For now, return a structure that indicates this need
                
                return {
                    "ok": False,
                    "message": "Player search not yet implemented",
                    "suggestion": "Need to implement ESPN player search or maintain player name -> ID mapping",
                    "player_name": player_name,
                    "sport": sport,
                    "league": league
                }
                
            except Exception as e:
                return {
                    "ok": False,
                    "error": f"Error searching for player: {str(e)}",
                    "player_name": player_name
                }
    
    def _parse_espn_statistics(self, splits_data: Dict, sport: str) -> Dict[str, Any]:
        """Parse ESPN statistics from splits.categories.stats structure."""
        stats_found = {}
        
        if not isinstance(splits_data, dict) or "categories" not in splits_data:
            return stats_found
        
        categories = splits_data["categories"]
        
        for category in categories:
            stats = category.get("stats", [])
            
            for stat in stats:
                name = stat.get("name", "").lower()
                display_value = stat.get("displayValue", str(stat.get("value", 0)))
                
                # Basketball-specific stats (can expand for other sports)
                if sport == "basketball":
                    if name == "points":
                        stats_found["points_per_game"] = display_value
                    elif name == "rebounds":
                        stats_found["rebounds_per_game"] = display_value  
                    elif name == "assists":
                        stats_found["assists_per_game"] = display_value
                    elif name == "steals":
                        stats_found["steals_per_game"] = display_value
                    elif name == "blocks":
                        stats_found["blocks_per_game"] = display_value
                    elif "threepointfieldgoalsmade" in name.replace(" ", ""):
                        stats_found["three_pointers_made_per_game"] = display_value
                    elif "threepointfieldgoalattempts" in name.replace(" ", ""):
                        stats_found["three_point_attempts_per_game"] = display_value
                    elif "threepointfieldgoalpercentage" in name.replace(" ", ""):
                        stats_found["three_point_percentage"] = display_value
                    elif "fieldgoalpercentage" in name.replace(" ", ""):
                        stats_found["field_goal_percentage"] = display_value
                    elif name == "minutes":
                        stats_found["minutes_per_game"] = display_value
        
        return stats_found
    
    def _calculate_trends(self, recent_games: List, sport: str) -> Dict[str, Any]:
        """Calculate trending metrics from recent games."""
        if not recent_games:
            return {"trend_available": False}
        
        # This would calculate things like:
        # - Last 5 games average vs season average
        # - Hot/cold streaks
        # - Performance vs specific opponents
        # - Home vs away splits
        
        return {
            "trend_available": True,
            "recent_games_analyzed": len(recent_games),
            "note": "Trend analysis implementation needed"
        }
    
    async def run(self):
        """Run the MCP server."""
        await self.server.run_stdio_async()

def main():
    """Run the Player Stats MCP server."""
    server = PlayerStatsMcpServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()