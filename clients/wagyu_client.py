#!/usr/bin/env python3
"""
Wagyu MCP Client for accessing betting odds data.

This client provides direct access to the Wagyu MCP server for fetching
sports betting odds, spreads, and other betting-related data.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import pytz

# Add the MCP client to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from mcp_client import MCPClient, MCPClientError

# Eastern timezone
EASTERN_TZ = pytz.timezone('US/Eastern')

logger = logging.getLogger(__name__)

class WagyuMCPError(Exception):
    """Base exception for Wagyu MCP errors."""
    pass

class WagyuClient:
    """Client for accessing Wagyu MCP server."""
    
    def __init__(self):
        self.server_path = self._get_wagyu_server_path()
    
    def _get_wagyu_server_path(self) -> str:
        """Get the path to the Wagyu MCP server."""
        # Get the project root directory
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        server_path = os.path.join(project_root, "sports_mcp", "wagyu_sports", "mcp_server", "odds_client_server.py")
        
        if not os.path.exists(server_path):
            raise WagyuMCPError(f"Wagyu MCP server not found at {server_path}")
        
        return server_path
    
    async def get_sports(self, all_sports: bool = False) -> Dict[str, Any]:
        """
        Get list of available sports for betting.
        
        Args:
            all_sports: Include out-of-season sports if True
            
        Returns:
            Dictionary containing sports data
        """
        try:
            async with MCPClient(self.server_path) as client:
                result = await client.call_tool("get_sports", {
                    "all_sports": all_sports
                })
                return self._parse_mcp_response(result)
        except Exception as e:
            logger.error(f"Error getting sports: {e}")
            raise WagyuMCPError(f"Failed to get sports: {e}")
    
    async def get_odds(self, sport: str, regions: str = "us", markets: str = "h2h,spreads,totals", 
                      odds_format: str = "american", date_format: str = "iso") -> Dict[str, Any]:
        """
        Get betting odds for a specific sport.
        
        Args:
            sport: Sport key (e.g., 'basketball_nba', 'americanfootball_nfl')
            regions: Comma-separated regions (e.g., 'us,uk')
            markets: Comma-separated markets (e.g., 'h2h,spreads,totals')
            odds_format: Format for odds ('decimal' or 'american')
            date_format: Format for dates ('unix' or 'iso')
            
        Returns:
            Dictionary containing odds data
        """
        try:
            async with MCPClient(self.server_path) as client:
                result = await client.call_tool("get_odds", {
                    "sport": sport,
                    "regions": regions,
                    "markets": markets,
                    "odds_format": odds_format,
                    "date_format": date_format
                })
                return self._parse_mcp_response(result)
        except Exception as e:
            logger.error(f"Error getting odds for {sport}: {e}")
            raise WagyuMCPError(f"Failed to get odds for {sport}: {e}")
    
    async def get_event_odds(self, sport: str, event_id: str, regions: str = "us", 
                           markets: str = "player_points,player_rebounds,player_assists", 
                           odds_format: str = "american", date_format: str = "iso") -> Dict[str, Any]:
        """
        Get odds for a specific event (required for player props).
        
        Args:
            sport: Sport key (e.g., 'basketball_nba', 'basketball_wnba')
            event_id: Event ID from the odds API
            regions: Comma-separated regions (e.g., 'us,uk')  
            markets: Comma-separated markets (e.g., 'player_points,player_rebounds,player_assists')
            odds_format: Format for odds ('decimal' or 'american')
            date_format: Format for dates ('unix' or 'iso')
            
        Returns:
            Dictionary containing event-specific odds data including player props
        """
        try:
            async with MCPClient(self.server_path) as client:
                result = await client.call_tool("get_event_odds", {
                    "sport": sport,
                    "event_id": event_id,
                    "regions": regions,
                    "markets": markets,
                    "odds_format": odds_format,
                    "date_format": date_format
                })
                return self._parse_mcp_response(result)
        except Exception as e:
            logger.error(f"Error getting event odds for {sport} event {event_id}: {e}")
            raise WagyuMCPError(f"Failed to get event odds: {e}")

    async def get_quota_info(self) -> Dict[str, Any]:
        """
        Get API quota information.
        
        Returns:
            Dictionary containing quota information
        """
        try:
            async with MCPClient(self.server_path) as client:
                result = await client.call_tool("get_quota_info", {})
                return self._parse_mcp_response(result)
        except Exception as e:
            logger.error(f"Error getting quota info: {e}")
            raise WagyuMCPError(f"Failed to get quota info: {e}")
    
    def _parse_mcp_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MCP response and extract data."""
        try:
            content = response.get("content", [])
            if not content:
                raise WagyuMCPError("Empty response from Wagyu MCP server")
            
            first_content = content[0]
            if first_content.get("type") == "text":
                text_content = first_content.get("text", "")
                try:
                    # Try to parse as JSON
                    if text_content.strip().startswith("{") or text_content.strip().startswith("["):
                        data = json.loads(text_content)
                        # Convert times to Eastern timezone
                        return self._convert_times_to_eastern(data)
                    else:
                        return {"content": text_content}
                except json.JSONDecodeError:
                    return {"content": text_content}
            else:
                # Handle direct data response (new format)
                return self._convert_times_to_eastern(first_content)
                
        except Exception as e:
            logger.error(f"Error parsing MCP response: {e}")
            raise WagyuMCPError(f"Failed to parse response: {e}")
    
    def _convert_times_to_eastern(self, data: Any) -> Any:
        """Convert UTC times in the data to Eastern timezone."""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'commence_time' and isinstance(value, str):
                    try:
                        # Parse UTC time and convert to Eastern
                        utc_time = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        eastern_time = utc_time.astimezone(EASTERN_TZ)
                        result[key] = eastern_time.isoformat()
                    except:
                        result[key] = value
                else:
                    result[key] = self._convert_times_to_eastern(value)
            return result
        elif isinstance(data, list):
            return [self._convert_times_to_eastern(item) for item in data]
        else:
            return data
    
    async def get_todays_games_eastern(self, sport: str) -> List[Dict[str, Any]]:
        """Get today's games filtered by Eastern timezone date."""
        try:
            # Get current Eastern date
            eastern_now = datetime.now(EASTERN_TZ)
            today_eastern = eastern_now.date()
            
            # Get all odds
            odds_data = await self.get_odds(sport)
            
            # Extract games from the response
            games = []
            if isinstance(odds_data, dict) and "data" in odds_data:
                games = odds_data["data"]
            elif isinstance(odds_data, list):
                games = odds_data
            elif isinstance(odds_data, dict) and "content" in odds_data:
                try:
                    games = json.loads(odds_data["content"])
                except:
                    games = []
            
            todays_games = []
            for game in games:
                if isinstance(game, dict) and 'commence_time' in game:
                    try:
                        # Parse the Eastern time
                        game_time = datetime.fromisoformat(game['commence_time'])
                        if game_time.date() == today_eastern:
                            todays_games.append(game)
                    except:
                        # If we can't parse the time, include the game anyway
                        todays_games.append(game)
            
            return todays_games
            
        except Exception as e:
            logger.error(f"Error getting today's games: {e}")
            raise WagyuMCPError(f"Failed to get today's games: {e}")

# Sport key mappings for common leagues
SPORT_MAPPINGS = {
    'nfl': 'americanfootball_nfl',
    'nba': 'basketball_nba',
    'wnba': 'basketball_wnba',
    'mlb': 'baseball_mlb',
    'nhl': 'icehockey_nhl',
    'mls': 'soccer_usa_mls',
    'epl': 'soccer_epl',
    'ncaaf': 'americanfootball_ncaaf',
    'ncaab': 'basketball_ncaab'
}

def get_sport_key(league: str) -> str:
    """Convert league code to Wagyu sport key."""
    return SPORT_MAPPINGS.get(league.lower(), league)

# Convenience functions
async def get_nfl_odds() -> Dict[str, Any]:
    """Get NFL betting odds."""
    client = WagyuClient()
    return await client.get_odds('americanfootball_nfl')

async def get_nba_odds() -> Dict[str, Any]:
    """Get NBA betting odds."""
    client = WagyuClient()
    return await client.get_odds('basketball_nba')

async def get_wnba_odds() -> Dict[str, Any]:
    """Get WNBA betting odds."""
    client = WagyuClient()
    return await client.get_odds('basketball_wnba')

async def get_wnba_player_props(event_id: str) -> Dict[str, Any]:
    """Get WNBA player props for a specific game."""
    client = WagyuClient()
    return await client.get_event_odds('basketball_wnba', event_id)

async def get_mlb_odds() -> Dict[str, Any]:
    """Get MLB betting odds."""
    client = WagyuClient()
    return await client.get_odds('baseball_mlb')

async def test_wagyu_connection() -> Dict[str, Any]:
    """Test Wagyu MCP connection."""
    try:
        client = WagyuClient()
        
        # Test getting sports list
        sports = await client.get_sports()
        
        # Test getting quota info
        quota = await client.get_quota_info()
        
        return {
            "status": "success",
            "sports_count": len(sports) if isinstance(sports, list) else "unknown",
            "quota_info": quota,
            "message": "Wagyu MCP connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Wagyu MCP connection failed"
        }

if __name__ == "__main__":
    # Test the connection
    async def main():
        print("Testing Wagyu MCP connection...")
        result = await test_wagyu_connection()
        print(json.dumps(result, indent=2))
        
        if result["status"] == "success":
            print("\nTesting WNBA odds...")
            try:
                client = WagyuClient()
                wnba_odds = await client.get_odds('basketball_wnba')
                print(f"WNBA odds: {len(wnba_odds) if isinstance(wnba_odds, list) else 'data received'}")
            except Exception as e:
                print(f"WNBA odds error: {e}")
    
    asyncio.run(main())