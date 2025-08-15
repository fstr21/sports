#!/usr/bin/env python3
"""
NFL MCP Server
Provides NFL data via Model Context Protocol using nfl_data_py
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import traceback

# MCP and web framework imports
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn

# NFL data import
import nfl_data_py as nfl
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NFLMCPServer:
    """NFL MCP Server providing NFL data tools"""
    
    def __init__(self):
        self.app = Starlette(routes=[
            Route("/mcp", self.handle_mcp_request, methods=["POST"]),
            Route("/health", self.health_check, methods=["GET"]),
            Route("/", self.root, methods=["GET"])
        ])
        
        # Initialize data cache
        self.data_cache = {}
        self.cache_expiry = {}
        
        logger.info("NFL MCP Server initialized")
    
    async def root(self, request):
        """Root endpoint"""
        return JSONResponse({
            "service": "NFL MCP Server",
            "version": "1.0.0",
            "status": "operational",
            "tools": list(TOOLS.keys()),
            "description": "NFL data via Model Context Protocol using nfl_data_py"
        })
    
    async def health_check(self, request):
        """Health check endpoint"""
        try:
            # Quick test of NFL data
            current_year = datetime.now().year
            test_schedule = nfl.import_schedules([current_year])
            
            return JSONResponse({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "data_available": len(test_schedule) > 0,
                "total_games": len(test_schedule)
            })
        except Exception as e:
            return JSONResponse({
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status_code=500)
    
    async def handle_mcp_request(self, request):
        """Handle MCP protocol requests"""
        try:
            body = await request.json()
            method = body.get("method")
            params = body.get("params", {})
            request_id = body.get("id", 1)
            
            logger.info(f"MCP Request: {method}")
            
            if method == "tools/list":
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": name,
                                "description": tool["description"],
                                "inputSchema": tool["parameters"]
                            }
                            for name, tool in TOOLS.items()
                        ]
                    }
                })
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name not in TOOLS:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                # Execute tool
                handler = TOOLS[tool_name]["handler"]
                result = await handler(self, arguments)
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                })
            
            else:
                raise ValueError(f"Unknown method: {method}")
        
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            logger.error(traceback.format_exc())
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -1,
                    "message": str(e)
                }
            }, status_code=400)

# NFL MCP Tool Handlers

async def handle_get_nfl_schedule(server: NFLMCPServer, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get NFL schedule with optional filters"""
    try:
        # Get parameters
        season = args.get("season", datetime.now().year)
        week = args.get("week")
        team = args.get("team")
        date_from = args.get("date_from")
        date_to = args.get("date_to")
        game_type = args.get("game_type", "REG")  # REG, POST, WC, DIV, CON, SB
        use_test_mode = args.get("use_test_mode", False)
        
        # Handle test mode
        if use_test_mode:
            return {
                "ok": True,
                "content_md": f"## NFL Schedule (Test Mode)\n\nTest NFL schedule data for season {season}",
                "data": {
                    "source": "test_mode",
                    "season": season,
                    "games": [
                        {
                            "game_id": f"test_{season}_01_KC_PHI",
                            "week": 1,
                            "date": "2025-09-04",
                            "away_team": "KC",
                            "home_team": "PHI",
                            "game_type": "REG",
                            "betting_odds": {
                                "away_moneyline": -150,
                                "home_moneyline": 130,
                                "spread_line": -3.0,
                                "total_line": 45.5
                            }
                        }
                    ]
                }
            }
        
        # Load NFL schedule
        cache_key = f"schedule_{season}"
        if cache_key not in server.data_cache or _is_cache_expired(server, cache_key):
            logger.info(f"Loading NFL schedule for {season}")
            schedule = nfl.import_schedules([season])
            server.data_cache[cache_key] = schedule
            server.cache_expiry[cache_key] = datetime.now() + timedelta(hours=6)
        else:
            schedule = server.data_cache[cache_key]
        
        # Apply filters
        filtered = schedule.copy()
        
        if week:
            filtered = filtered[filtered['week'] == week]
        
        if team:
            team = team.upper()
            filtered = filtered[
                (filtered['away_team'] == team) | (filtered['home_team'] == team)
            ]
        
        if game_type:
            filtered = filtered[filtered['game_type'] == game_type]
        
        if date_from:
            filtered = filtered[filtered['gameday'] >= date_from]
        
        if date_to:
            filtered = filtered[filtered['gameday'] <= date_to]
        
        # Convert to response format
        games = []
        for idx, game in filtered.iterrows():
            games.append({
                "game_id": game.get('game_id'),
                "season": game.get('season'),
                "week": game.get('week'),
                "date": game.get('gameday'),
                "weekday": game.get('weekday'),
                "time": game.get('gametime'),
                "away_team": game.get('away_team'),
                "home_team": game.get('home_team'),
                "away_score": game.get('away_score') if pd.notna(game.get('away_score')) else None,
                "home_score": game.get('home_score') if pd.notna(game.get('home_score')) else None,
                "game_type": game.get('game_type'),
                "stadium": game.get('stadium'),
                "surface": game.get('surface'),
                "roof": game.get('roof'),
                "betting_odds": {
                    "away_moneyline": game.get('away_moneyline') if pd.notna(game.get('away_moneyline')) else None,
                    "home_moneyline": game.get('home_moneyline') if pd.notna(game.get('home_moneyline')) else None,
                    "spread_line": game.get('spread_line') if pd.notna(game.get('spread_line')) else None,
                    "total_line": game.get('total_line') if pd.notna(game.get('total_line')) else None,
                    "away_spread_odds": game.get('away_spread_odds') if pd.notna(game.get('away_spread_odds')) else None,
                    "home_spread_odds": game.get('home_spread_odds') if pd.notna(game.get('home_spread_odds')) else None
                },
                "team_info": {
                    "away_qb": game.get('away_qb_name'),
                    "home_qb": game.get('home_qb_name'),
                    "away_coach": game.get('away_coach'),
                    "home_coach": game.get('home_coach')
                }
            })
        
        # Create content markdown
        content_md = f"## NFL Schedule\n\n"
        content_md += f"Season: {season}\n"
        if week:
            content_md += f"Week: {week}\n"
        if team:
            content_md += f"Team: {team}\n"
        content_md += f"Games found: {len(games)}\n"
        
        return {
            "ok": True,
            "content_md": content_md,
            "data": {
                "source": "nfl_data_py",
                "season": season,
                "filters_applied": {
                    "week": week,
                    "team": team,
                    "game_type": game_type,
                    "date_from": date_from,
                    "date_to": date_to
                },
                "games": games,
                "total_games": len(games)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_nfl_schedule: {e}")
        return {
            "ok": False,
            "error": str(e),
            "content_md": f"## Error\n\nFailed to get NFL schedule: {str(e)}"
        }

async def handle_get_nfl_teams(server: NFLMCPServer, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get NFL teams information"""
    try:
        division = args.get("division")
        conference = args.get("conference")
        use_test_mode = args.get("use_test_mode", False)
        
        if use_test_mode:
            return {
                "ok": True,
                "content_md": "## NFL Teams (Test Mode)\n\nTest NFL teams data",
                "data": {
                    "source": "test_mode",
                    "teams": [
                        {"team_abbr": "KC", "team_name": "Kansas City Chiefs", "division": "AFC West", "conference": "AFC"},
                        {"team_abbr": "PHI", "team_name": "Philadelphia Eagles", "division": "NFC East", "conference": "NFC"}
                    ]
                }
            }
        
        # Load teams data
        cache_key = "teams"
        if cache_key not in server.data_cache or _is_cache_expired(server, cache_key):
            logger.info("Loading NFL teams data")
            teams = nfl.import_team_desc()
            server.data_cache[cache_key] = teams
            server.cache_expiry[cache_key] = datetime.now() + timedelta(hours=24)
        else:
            teams = server.data_cache[cache_key]
        
        # Apply filters
        filtered = teams.copy()
        
        if division:
            filtered = filtered[filtered['team_division'] == division]
        
        if conference:
            filtered = filtered[filtered['team_conf'] == conference]
        
        # Convert to response format
        teams_list = []
        for idx, team in filtered.iterrows():
            teams_list.append({
                "team_abbr": team.get('team_abbr'),
                "team_name": team.get('team_name'),
                "team_id": team.get('team_id'),
                "division": team.get('team_division'),
                "conference": team.get('team_conf'),
                "colors": {
                    "primary": team.get('team_color'),
                    "secondary": team.get('team_color2'),
                    "tertiary": team.get('team_color3'),
                    "quaternary": team.get('team_color4')
                },
                "logos": {
                    "wikipedia": team.get('team_logo_wikipedia'),
                    "espn": team.get('team_logo_espn'),
                    "squared": team.get('team_logo_squared')
                }
            })
        
        content_md = f"## NFL Teams\n\n"
        if division:
            content_md += f"Division: {division}\n"
        if conference:
            content_md += f"Conference: {conference}\n"
        content_md += f"Teams found: {len(teams_list)}"
        
        return {
            "ok": True,
            "content_md": content_md,
            "data": {
                "source": "nfl_data_py",
                "filters_applied": {
                    "division": division,
                    "conference": conference
                },
                "teams": teams_list,
                "total_teams": len(teams_list)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_nfl_teams: {e}")
        return {
            "ok": False,
            "error": str(e),
            "content_md": f"## Error\n\nFailed to get NFL teams: {str(e)}"
        }

async def handle_get_nfl_player_stats(server: NFLMCPServer, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get NFL player statistics"""
    try:
        season = args.get("season", datetime.now().year)
        player_name = args.get("player_name")
        team = args.get("team")
        position = args.get("position")
        stat_type = args.get("stat_type", "passing")  # passing, rushing, receiving
        limit = args.get("limit", 50)
        use_test_mode = args.get("use_test_mode", False)
        
        if use_test_mode:
            return {
                "ok": True,
                "content_md": f"## NFL Player Stats (Test Mode)\n\nTest player statistics for {season}",
                "data": {
                    "source": "test_mode",
                    "season": season,
                    "players": [
                        {"player_name": "P.Mahomes", "team": "KC", "passing_yards": 4500, "passing_tds": 35},
                        {"player_name": "J.Hurts", "team": "PHI", "passing_yards": 4200, "passing_tds": 28}
                    ]
                }
            }
        
        # Load player stats
        cache_key = f"player_stats_{season}"
        if cache_key not in server.data_cache or _is_cache_expired(server, cache_key):
            logger.info(f"Loading NFL player stats for {season}")
            
            # Define columns based on stat type
            if stat_type == "passing":
                columns = ['player_name', 'recent_team', 'position', 'week', 'passing_yards', 'passing_tds', 'interceptions', 'passing_attempts', 'completions']
            elif stat_type == "rushing":
                columns = ['player_name', 'recent_team', 'position', 'week', 'rushing_yards', 'rushing_tds', 'carries']
            elif stat_type == "receiving":
                columns = ['player_name', 'recent_team', 'position', 'week', 'receiving_yards', 'receiving_tds', 'receptions', 'targets']
            else:
                columns = ['player_name', 'recent_team', 'position', 'week']
            
            stats = nfl.import_weekly_data([season], columns=columns)
            server.data_cache[cache_key] = stats
            server.cache_expiry[cache_key] = datetime.now() + timedelta(hours=6)
        else:
            stats = server.data_cache[cache_key]
        
        # Apply filters
        filtered = stats.copy()
        
        if player_name:
            filtered = filtered[filtered['player_name'].str.contains(player_name, case=False, na=False)]
        
        if team:
            team = team.upper()
            filtered = filtered[filtered['recent_team'] == team]
        
        if position:
            filtered = filtered[filtered['position'] == position]
        
        # Aggregate season totals
        if stat_type == "passing":
            season_stats = filtered.groupby(['player_name', 'recent_team', 'position']).agg({
                'passing_yards': 'sum',
                'passing_tds': 'sum',
                'interceptions': 'sum',
                'passing_attempts': 'sum',
                'completions': 'sum'
            }).reset_index()
            season_stats = season_stats.sort_values('passing_yards', ascending=False)
        elif stat_type == "rushing":
            season_stats = filtered.groupby(['player_name', 'recent_team', 'position']).agg({
                'rushing_yards': 'sum',
                'rushing_tds': 'sum',
                'carries': 'sum'
            }).reset_index()
            season_stats = season_stats.sort_values('rushing_yards', ascending=False)
        elif stat_type == "receiving":
            season_stats = filtered.groupby(['player_name', 'recent_team', 'position']).agg({
                'receiving_yards': 'sum',
                'receiving_tds': 'sum',
                'receptions': 'sum',
                'targets': 'sum'
            }).reset_index()
            season_stats = season_stats.sort_values('receiving_yards', ascending=False)
        
        # Convert to response format
        players = []
        for idx, player in season_stats.head(limit).iterrows():
            player_data = {
                "player_name": player.get('player_name'),
                "team": player.get('recent_team'),
                "position": player.get('position'),
                "stat_type": stat_type
            }
            
            # Add stat-specific data
            for col in season_stats.columns:
                if col not in ['player_name', 'recent_team', 'position']:
                    value = player.get(col)
                    player_data[col] = int(value) if pd.notna(value) else 0
            
            players.append(player_data)
        
        content_md = f"## NFL Player Stats\n\n"
        content_md += f"Season: {season}\n"
        content_md += f"Stat Type: {stat_type}\n"
        if player_name:
            content_md += f"Player: {player_name}\n"
        if team:
            content_md += f"Team: {team}\n"
        content_md += f"Players found: {len(players)}"
        
        return {
            "ok": True,
            "content_md": content_md,
            "data": {
                "source": "nfl_data_py",
                "season": season,
                "stat_type": stat_type,
                "filters_applied": {
                    "player_name": player_name,
                    "team": team,
                    "position": position
                },
                "players": players,
                "total_players": len(players)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_nfl_player_stats: {e}")
        return {
            "ok": False,
            "error": str(e),
            "content_md": f"## Error\n\nFailed to get NFL player stats: {str(e)}"
        }

async def handle_get_nfl_injuries(server: NFLMCPServer, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get NFL injury reports"""
    try:
        season = args.get("season", 2024)  # Injury data typically current season
        team = args.get("team")
        status = args.get("status")  # Out, Questionable, Doubtful, etc.
        position = args.get("position")
        limit = args.get("limit", 100)
        use_test_mode = args.get("use_test_mode", False)
        
        if use_test_mode:
            return {
                "ok": True,
                "content_md": f"## NFL Injuries (Test Mode)\n\nTest injury reports for {season}",
                "data": {
                    "source": "test_mode",
                    "season": season,
                    "injuries": [
                        {"player_name": "Test Player", "team": "KC", "status": "Questionable", "injury": "Ankle"},
                        {"player_name": "Test Player 2", "team": "PHI", "status": "Out", "injury": "Hamstring"}
                    ]
                }
            }
        
        # Load injury data
        cache_key = f"injuries_{season}"
        if cache_key not in server.data_cache or _is_cache_expired(server, cache_key):
            logger.info(f"Loading NFL injury data for {season}")
            injuries = nfl.import_injuries([season])
            server.data_cache[cache_key] = injuries
            server.cache_expiry[cache_key] = datetime.now() + timedelta(hours=2)  # More frequent updates
        else:
            injuries = server.data_cache[cache_key]
        
        # Apply filters
        filtered = injuries.copy()
        
        if team:
            team = team.upper()
            filtered = filtered[filtered['team'] == team]
        
        if status:
            filtered = filtered[filtered['report_status'] == status]
        
        if position:
            filtered = filtered[filtered['position'] == position]
        
        # Convert to response format
        injury_reports = []
        for idx, injury in filtered.head(limit).iterrows():
            injury_reports.append({
                "player_name": injury.get('full_name'),
                "first_name": injury.get('first_name'),
                "last_name": injury.get('last_name'),
                "team": injury.get('team'),
                "position": injury.get('position'),
                "report_status": injury.get('report_status'),
                "primary_injury": injury.get('report_primary_injury'),
                "secondary_injury": injury.get('report_secondary_injury'),
                "practice_status": injury.get('practice_status'),
                "practice_primary_injury": injury.get('practice_primary_injury'),
                "practice_secondary_injury": injury.get('practice_secondary_injury'),
                "week": injury.get('week'),
                "season": injury.get('season'),
                "date_modified": injury.get('date_modified')
            })
        
        content_md = f"## NFL Injury Reports\n\n"
        content_md += f"Season: {season}\n"
        if team:
            content_md += f"Team: {team}\n"
        if status:
            content_md += f"Status: {status}\n"
        content_md += f"Reports found: {len(injury_reports)}"
        
        return {
            "ok": True,
            "content_md": content_md,
            "data": {
                "source": "nfl_data_py",
                "season": season,
                "filters_applied": {
                    "team": team,
                    "status": status,
                    "position": position
                },
                "injuries": injury_reports,
                "total_reports": len(injury_reports)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_nfl_injuries: {e}")
        return {
            "ok": False,
            "error": str(e),
            "content_md": f"## Error\n\nFailed to get NFL injuries: {str(e)}"
        }

async def handle_get_nfl_team_stats(server: NFLMCPServer, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get NFL team statistics"""
    try:
        season = args.get("season", datetime.now().year)
        team = args.get("team")
        stat_category = args.get("stat_category", "offense")  # offense, defense, special_teams
        use_test_mode = args.get("use_test_mode", False)
        
        if use_test_mode:
            return {
                "ok": True,
                "content_md": f"## NFL Team Stats (Test Mode)\n\nTest team statistics for {season}",
                "data": {
                    "source": "test_mode",
                    "season": season,
                    "teams": [
                        {"team": "KC", "total_yards": 6500, "total_tds": 45},
                        {"team": "PHI", "total_yards": 6200, "total_tds": 42}
                    ]
                }
            }
        
        # Load seasonal team data
        cache_key = f"team_stats_{season}"
        if cache_key not in server.data_cache or _is_cache_expired(server, cache_key):
            logger.info(f"Loading NFL team stats for {season}")
            team_stats = nfl.import_seasonal_data([season])
            server.data_cache[cache_key] = team_stats
            server.cache_expiry[cache_key] = datetime.now() + timedelta(hours=6)
        else:
            team_stats = server.data_cache[cache_key]
        
        # Aggregate by team
        team_aggregated = team_stats.groupby('recent_team').agg({
            'passing_yards': 'sum',
            'passing_tds': 'sum',
            'rushing_yards': 'sum',
            'rushing_tds': 'sum',
            'receiving_yards': 'sum',
            'receiving_tds': 'sum'
        }).reset_index()
        
        # Apply team filter
        if team:
            team = team.upper()
            team_aggregated = team_aggregated[team_aggregated['recent_team'] == team]
        
        # Convert to response format
        teams_list = []
        for idx, team_data in team_aggregated.iterrows():
            teams_list.append({
                "team": team_data.get('recent_team'),
                "season": season,
                "offense": {
                    "passing_yards": int(team_data.get('passing_yards', 0)),
                    "passing_tds": int(team_data.get('passing_tds', 0)),
                    "rushing_yards": int(team_data.get('rushing_yards', 0)),
                    "rushing_tds": int(team_data.get('rushing_tds', 0)),
                    "total_yards": int(team_data.get('passing_yards', 0) + team_data.get('rushing_yards', 0)),
                    "total_tds": int(team_data.get('passing_tds', 0) + team_data.get('rushing_tds', 0))
                }
            })
        
        content_md = f"## NFL Team Stats\n\n"
        content_md += f"Season: {season}\n"
        content_md += f"Category: {stat_category}\n"
        if team:
            content_md += f"Team: {team}\n"
        content_md += f"Teams found: {len(teams_list)}"
        
        return {
            "ok": True,
            "content_md": content_md,
            "data": {
                "source": "nfl_data_py",
                "season": season,
                "stat_category": stat_category,
                "filters_applied": {
                    "team": team
                },
                "teams": teams_list,
                "total_teams": len(teams_list)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_nfl_team_stats: {e}")
        return {
            "ok": False,
            "error": str(e),
            "content_md": f"## Error\n\nFailed to get NFL team stats: {str(e)}"
        }

# Helper function
def _is_cache_expired(server: NFLMCPServer, cache_key: str) -> bool:
    """Check if cache entry is expired"""
    if cache_key not in server.cache_expiry:
        return True
    return datetime.now() > server.cache_expiry[cache_key]

# Tool definitions
TOOLS = {
    "getNFLSchedule": {
        "description": "Get NFL game schedule with optional filters for season, week, team, or date range. Includes betting odds and game details.",
        "parameters": {
            "type": "object",
            "properties": {
                "season": {
                    "type": "integer",
                    "description": "NFL season year (default: current year)"
                },
                "week": {
                    "type": "integer",
                    "description": "Specific week number (1-18 for regular season, 19+ for playoffs)"
                },
                "team": {
                    "type": "string",
                    "description": "Team abbreviation (e.g., 'KC', 'PHI') to filter games"
                },
                "date_from": {
                    "type": "string",
                    "description": "Start date filter (YYYY-MM-DD format)"
                },
                "date_to": {
                    "type": "string",
                    "description": "End date filter (YYYY-MM-DD format)"
                },
                "game_type": {
                    "type": "string",
                    "description": "Game type filter (REG, POST, WC, DIV, CON, SB)",
                    "default": "REG"
                },
                "use_test_mode": {
                    "type": "boolean",
                    "description": "Use test/mock data instead of live API"
                }
            }
        },
        "handler": handle_get_nfl_schedule
    },
    
    "getNFLTeams": {
        "description": "Get NFL teams information including divisions, conferences, and team details.",
        "parameters": {
            "type": "object",
            "properties": {
                "division": {
                    "type": "string",
                    "description": "Filter by division (e.g., 'AFC East', 'NFC West')"
                },
                "conference": {
                    "type": "string",
                    "description": "Filter by conference ('AFC' or 'NFC')"
                },
                "use_test_mode": {
                    "type": "boolean",
                    "description": "Use test/mock data instead of live API"
                }
            }
        },
        "handler": handle_get_nfl_teams
    },
    
    "getNFLPlayerStats": {
        "description": "Get NFL player statistics with filters for season, player, team, position, and stat type.",
        "parameters": {
            "type": "object",
            "properties": {
                "season": {
                    "type": "integer",
                    "description": "NFL season year (default: current year)"
                },
                "player_name": {
                    "type": "string",
                    "description": "Player name to search for (partial match supported)"
                },
                "team": {
                    "type": "string",
                    "description": "Team abbreviation to filter players"
                },
                "position": {
                    "type": "string",
                    "description": "Position to filter (QB, RB, WR, etc.)"
                },
                "stat_type": {
                    "type": "string",
                    "description": "Type of stats (passing, rushing, receiving)",
                    "default": "passing"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of players to return",
                    "default": 50
                },
                "use_test_mode": {
                    "type": "boolean",
                    "description": "Use test/mock data instead of live API"
                }
            }
        },
        "handler": handle_get_nfl_player_stats
    },
    
    "getNFLInjuries": {
        "description": "Get current NFL injury reports with filters for team, status, and position.",
        "parameters": {
            "type": "object",
            "properties": {
                "season": {
                    "type": "integer",
                    "description": "NFL season year (default: 2024)"
                },
                "team": {
                    "type": "string",
                    "description": "Team abbreviation to filter injuries"
                },
                "status": {
                    "type": "string",
                    "description": "Injury status (Out, Questionable, Doubtful, etc.)"
                },
                "position": {
                    "type": "string",
                    "description": "Position to filter (QB, RB, WR, etc.)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of injury reports to return",
                    "default": 100
                },
                "use_test_mode": {
                    "type": "boolean",
                    "description": "Use test/mock data instead of live API"
                }
            }
        },
        "handler": handle_get_nfl_injuries
    },
    
    "getNFLTeamStats": {
        "description": "Get NFL team statistics aggregated by season.",
        "parameters": {
            "type": "object",
            "properties": {
                "season": {
                    "type": "integer",
                    "description": "NFL season year (default: current year)"
                },
                "team": {
                    "type": "string",
                    "description": "Team abbreviation to filter"
                },
                "stat_category": {
                    "type": "string",
                    "description": "Category of stats (offense, defense, special_teams)",
                    "default": "offense"
                },
                "use_test_mode": {
                    "type": "boolean",
                    "description": "Use test/mock data instead of live API"
                }
            }
        },
        "handler": handle_get_nfl_team_stats
    }
}

def main():
    """Run the NFL MCP server"""
    server = NFLMCPServer()
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8080))
    
    logger.info(f"Starting NFL MCP Server on port {port}")
    logger.info(f"Available tools: {list(TOOLS.keys())}")
    
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()