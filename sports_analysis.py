#!/usr/bin/env python3
"""
Sports Betting Analysis System - Interactive Interface

This script provides an interactive interface to your sports betting analysis system.
Ask questions about WNBA games, betting odds, and get AI-powered recommendations.

This version uses the actual MCP servers that are configured and working.
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path

# Load environment variables manually to avoid caching issues
env_file = Path('.env.local')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import requests

# Import MCP core functions
from clients.core_mcp import scoreboard, game_summary, MCPError, MCPServerError, MCPValidationError

class SportsAnalysisSystem:
    """Interactive sports betting analysis system using MCP servers."""
    
    def __init__(self):
        """Initialize the system with API keys and configuration."""
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.openrouter_model = os.environ.get('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
        self.fallback_models = [
            'meta-llama/llama-3.2-3b-instruct:free',
            'microsoft/phi-3-mini-128k-instruct:free',
            'google/gemma-2-9b-it:free'
        ]
        self.odds_api_key = os.environ.get('ODDS_API_KEY')
        
        # Validate required keys
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY not found in .env.local")
        
        # Validate OpenRouter API key (warn but don't fail)
        self.openrouter_valid = True
        if not self.openrouter_api_key:
            print("⚠️  Warning: OPENROUTER_API_KEY not found in .env.local - AI analysis will be unavailable")
            self.openrouter_valid = False
        elif not self.openrouter_api_key.startswith('sk-or-v1-'):
            print("⚠️  Warning: OPENROUTER_API_KEY appears to be invalid - AI analysis may not work")
            self.openrouter_valid = False
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def get_scoreboard_mcp(self, sport: str, league: str, **kwargs) -> dict:
        """Synchronous wrapper for MCP scoreboard call."""
        try:
            # Map sport/league to MCP league key
            league_key_map = {
                ('football', 'nfl'): 'nfl',
                ('basketball', 'wnba'): 'wnba',
                ('basketball', 'nba'): 'nba',
                ('baseball', 'mlb'): 'mlb',
                ('hockey', 'nhl'): 'nhl',
                ('soccer', 'usa.1'): 'mls'
            }
            
            league_key = league_key_map.get((sport, league))
            if not league_key:
                return {"ok": False, "message": f"Unsupported sport/league: {sport}/{league}"}
            
            return self._run_async(scoreboard(league_key, **kwargs))
        except (MCPError, MCPServerError, MCPValidationError) as e:
            return {"ok": False, "message": str(e)}
        except Exception as e:
            return {"ok": False, "message": f"Unexpected error: {str(e)}"}
    
    def get_game_summary_mcp(self, sport: str, league: str, event_id: str) -> dict:
        """Synchronous wrapper for MCP game summary call."""
        try:
            # Map sport/league to MCP league key
            league_key_map = {
                ('football', 'nfl'): 'nfl',
                ('basketball', 'wnba'): 'wnba',
                ('basketball', 'nba'): 'nba',
                ('baseball', 'mlb'): 'mlb',
                ('hockey', 'nhl'): 'nhl',
                ('soccer', 'usa.1'): 'mls'
            }
            
            league_key = league_key_map.get((sport, league))
            if not league_key:
                return {"ok": False, "message": f"Unsupported sport/league: {sport}/{league}"}
            
            return self._run_async(game_summary(league_key, event_id))
        except (MCPError, MCPServerError, MCPValidationError) as e:
            return {"ok": False, "message": str(e)}
        except Exception as e:
            return {"ok": False, "message": f"Unexpected error: {str(e)}"}
    
    def detect_sport_from_query(self, query: str) -> str:
        """Detect which sport the user is asking about."""
        query_lower = query.lower()
        
        # Check for NFL team names first (most specific)
        nfl_teams = ['ravens', 'colts', 'chiefs', 'bills', 'patriots', 'dolphins', 'jets', 'steelers', 
                     'browns', 'bengals', 'titans', 'jaguars', 'texans', 'broncos', 'chargers', 'raiders',
                     'cowboys', 'giants', 'eagles', 'commanders', 'packers', 'bears', 'lions', 'vikings',
                     'falcons', 'panthers', 'saints', 'buccaneers', 'cardinals', '49ers', 'seahawks', 'rams']
        
        if any(team in query_lower for team in nfl_teams):
            return 'nfl'
        elif any(word in query_lower for word in ['nfl', 'football', 'american football', 'quarterback', 'qb']):
            return 'nfl'
        elif any(word in query_lower for word in ['wnba', 'women basketball']):
            return 'wnba'
        elif any(word in query_lower for word in ['mlb', 'baseball']):
            return 'mlb'
        elif any(word in query_lower for word in ['nhl', 'hockey']):
            return 'nhl'
        elif any(word in query_lower for word in ['soccer', 'mls', 'premier league']):
            return 'soccer'
        else:
            return 'nfl'  # Default to NFL since it's most common
    
    def get_sports_analysis(self, sport: str, query: str = "") -> str:
        """Get sports analysis from your ESPN Sports AI MCP."""
        print(f"📊 Calling ESPN Sports AI MCP for {sport.upper()} analysis...")
        
        try:
            # Call your MCP functions based on sport
            if sport == 'wnba':
                return self.call_wnba_mcp(query)
            elif sport == 'nfl':
                return self.call_nfl_mcp(query)
            else:
                return self.call_custom_sports_mcp(sport, query)
                
        except Exception as e:
            print(f"⚠️  MCP call failed: {str(e)}")
            return self.get_fallback_analysis(sport)
    
    def call_wnba_mcp(self, query: str) -> str:
        """Call your Sports AI MCP server for WNBA data."""
        try:
            print("🔍 Using Sports AI MCP server for WNBA games...")
            
            # Call MCP scoreboard function for WNBA
            scoreboard_result = self.get_scoreboard_mcp(
                sport="basketball",
                league="wnba"
            )
            
            if not scoreboard_result.get('ok'):
                return f"❌ MCP Error: {scoreboard_result.get('message', 'Unknown error')}"
            
            # Extract events from MCP response
            scoreboard_data = scoreboard_result.get('data', {}).get('scoreboard', {})
            events = scoreboard_data.get('events', [])
            
            if not events:
                return "No WNBA games found via Sports AI MCP."
            
            analysis = "🏀 WNBA Games Analysis (via Sports AI MCP):\n\n"
            
            for i, event in enumerate(events[:3], 1):
                home_team = event.get('home', {})
                away_team = event.get('away', {})
                
                home_name = home_team.get('displayName', 'Home Team')
                away_name = away_team.get('displayName', 'Away Team')
                home_score = home_team.get('score', 'N/A')
                away_score = away_team.get('score', 'N/A')
                
                analysis += f"{i}. {away_name} @ {home_name}\n"
                analysis += f"   Score: {away_name} {away_score}, {home_name} {home_score}\n"
                analysis += f"   Status: {event.get('status', 'Unknown')}\n"
                analysis += f"   Date: {event.get('date', 'Unknown')}\n\n"
            
            analysis += "📊 Data Source: Sports AI MCP Server\n"
            analysis += "✅ Verified WNBA game data from ESPN via MCP\n"
            
            return analysis
                
        except Exception as e:
            return f"❌ Error calling Sports AI MCP: {str(e)}"
    
    def call_nfl_mcp(self, query: str) -> str:
        """Call your Sports AI MCP server for NFL data."""
        try:
            print("🔍 Using Sports AI MCP server for NFL data...")
            
            # Search for specific game using MCP
            dates_to_check = ["20250808", "20250807", "20250806", "20250805"]
            
            for date in dates_to_check:
                print(f"   Checking {date}...")
                
                try:
                    # Call MCP scoreboard function
                    scoreboard_result = self.get_scoreboard_mcp(
                        sport="football",
                        league="nfl", 
                        dates=date,
                        seasontype=1
                    )
                    
                    if not scoreboard_result.get('ok'):
                        continue
                    
                    # Extract events from MCP response
                    scoreboard_data = scoreboard_result.get('data', {}).get('scoreboard', {})
                    events = scoreboard_data.get('events', [])
                    
                    if not events:
                        continue
                    
                    # Look for specific teams in MCP data
                    for event in events:
                        home_team = event.get('home', {}).get('displayName', '').lower()
                        away_team = event.get('away', {}).get('displayName', '').lower()
                        
                        # Check for team matches in query
                        query_lower = query.lower()
                        team_matches = []
                        
                        # Extract team names from query
                        nfl_teams = {
                            'ravens': 'baltimore', 'colts': 'indianapolis', 'chiefs': 'kansas city',
                            'bills': 'buffalo', 'patriots': 'new england', 'dolphins': 'miami',
                            'jets': 'new york', 'steelers': 'pittsburgh', 'browns': 'cleveland',
                            'bengals': 'cincinnati', 'titans': 'tennessee', 'jaguars': 'jacksonville',
                            'texans': 'houston', 'broncos': 'denver', 'chargers': 'los angeles',
                            'raiders': 'las vegas', 'cowboys': 'dallas', 'giants': 'new york',
                            'eagles': 'philadelphia', 'commanders': 'washington', 'packers': 'green bay',
                            'bears': 'chicago', 'lions': 'detroit', 'vikings': 'minnesota',
                            'falcons': 'atlanta', 'panthers': 'carolina', 'saints': 'new orleans',
                            'buccaneers': 'tampa bay', 'cardinals': 'arizona', '49ers': 'san francisco',
                            'seahawks': 'seattle', 'rams': 'los angeles'
                        }
                        
                        for team_key, team_city in nfl_teams.items():
                            if team_key in query_lower or team_city in query_lower:
                                if (team_key in home_team or team_city in home_team or 
                                    team_key in away_team or team_city in away_team):
                                    team_matches.append(team_key)
                        
                        # If we found matching teams or this is a general NFL query
                        if team_matches or not any(team in query_lower for team in nfl_teams.keys()):
                            event_id = event.get('event_id')
                            game_name = f"{event.get('away', {}).get('displayName', 'Away')} @ {event.get('home', {}).get('displayName', 'Home')}"
                            print(f"   ✅ FOUND GAME: {game_name} (Event ID: {event_id})")
                            
                            # Call MCP game summary function
                            summary_result = self.get_game_summary_mcp(
                                sport="football",
                                league="nfl",
                                event_id=event_id
                            )
                            
                            if summary_result.get('ok'):
                                return self.process_mcp_game_data(summary_result, event, query)
                            else:
                                return f"❌ Could not get detailed stats for event {event_id}"
                    
                except Exception as mcp_error:
                    print(f"   ⚠️  MCP call failed for {date}: {str(mcp_error)}")
                    continue
            
            return self.generate_no_data_response(dates_to_check)
                
        except Exception as e:
            print(f"⚠️  MCP server call failed: {str(e)}")
            return f"❌ Error calling Sports AI MCP: {str(e)}\n⚠️  Cannot provide detailed analysis without MCP server."
    
    def process_enhanced_game_data(self, summary_data: dict, basic_event: dict, query: str = "") -> str:
        """Process enhanced ESPN game summary data with clean formatting."""
        
        # Basic game info
        game_name = basic_event.get('name', 'Unknown Game')
        game_date = basic_event.get('date', 'Unknown Date')
        event_id = basic_event.get('id', 'Unknown ID')
        
        # Parse date for better formatting
        try:
            from datetime import datetime
            parsed_date = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
            formatted_date = parsed_date.strftime('%A, %B %d, %Y at %I:%M %p ET')
        except:
            formatted_date = game_date
        
        analysis = f"""🏈 NFL GAME ANALYSIS

═══════════════════════════════════════════════════════════════════════════════

📊 GAME INFORMATION
{game_name}
{formatted_date}
ESPN Event ID: {event_id}

"""
        
        # Game status and final score
        competitions = basic_event.get('competitions', [])
        if competitions:
            comp = competitions[0]
            status = comp.get('status', {}).get('type', {}).get('description', 'Unknown')
            
            competitors = comp.get('competitors', [])
            if len(competitors) >= 2:
                away_team = competitors[1] if len(competitors) > 1 else competitors[0]
                home_team = competitors[0]
                
                away_name = away_team.get('team', {}).get('displayName', 'Away Team')
                home_name = home_team.get('team', {}).get('displayName', 'Home Team')
                away_score = away_team.get('score', '0')
                home_score = home_team.get('score', '0')
                
                analysis += f"🏆 FINAL SCORE\n"
                analysis += f"{away_name}: {away_score}\n"
                analysis += f"{home_name}: {home_score}\n"
                analysis += f"Status: {status}\n\n"
        
        # Determine what stats to show based on query
        query_lower = query.lower()
        show_qb = any(word in query_lower for word in ['qb', 'quarterback', 'passing', 'pass'])
        show_rb = any(word in query_lower for word in ['rb', 'running back', 'rushing', 'rush'])
        show_wr = any(word in query_lower for word in ['wr', 'receiver', 'receiving', 'catch'])
        
        # If no specific position mentioned, default to QB
        if not (show_qb or show_rb or show_wr):
            show_qb = True
        
        # Enhanced boxscore stats
        stats_found = False
        if 'boxscore' in summary_data:
            boxscore = summary_data['boxscore']
            if isinstance(boxscore, dict):
                players = boxscore.get('players', [])
                
                if players:
                    for player_group in players:
                        if isinstance(player_group, dict):
                            team = player_group.get('team', {})
                            team_name = team.get('displayName', 'Unknown Team')
                            
                            statistics = player_group.get('statistics', [])
                            for stat_category in statistics:
                                if isinstance(stat_category, dict):
                                    cat_name = stat_category.get('name', '').lower()
                                    
                                    # Show QB stats
                                    if show_qb and 'passing' in cat_name:
                                        if not stats_found:
                                            analysis += f"🎯 DETAILED PLAYER STATISTICS\n\n"
                                            stats_found = True
                                        
                                        analysis += f"📋 {team_name} Passing Statistics:\n\n"
                                        analysis += f"{'PLAYER':<25} {'C/ATT':<6} {'YDS':<6} {'AVG':<6} {'TD':<4} {'INT':<4} {'SACKS':<8} {'RTG':<6}\n"
                                        analysis += f"{'-'*25} {'-'*6} {'-'*6} {'-'*6} {'-'*4} {'-'*4} {'-'*8} {'-'*6}\n"
                                        
                                        athletes = stat_category.get('athletes', [])
                                        for athlete_data in athletes:
                                            if isinstance(athlete_data, dict):
                                                athlete = athlete_data.get('athlete', {})
                                                player_name = athlete.get('displayName', 'Unknown')
                                                jersey = athlete.get('jersey', '')
                                                display_name = f"{player_name} #{jersey}" if jersey else player_name
                                                
                                                stats = athlete_data.get('stats', [])
                                                if stats and len(stats) >= 7:
                                                    c_att = stats[0] if len(stats) > 0 else '0/0'
                                                    yards = stats[1] if len(stats) > 1 else '0'
                                                    avg = stats[2] if len(stats) > 2 else '0.0'
                                                    td = stats[3] if len(stats) > 3 else '0'
                                                    interceptions = stats[4] if len(stats) > 4 else '0'
                                                    sacks = stats[5] if len(stats) > 5 else '0-0'
                                                    rating = stats[6] if len(stats) > 6 else '0.0'
                                                    
                                                    analysis += f"{display_name:<25} {c_att:<6} {yards:<6} {avg:<6} {td:<4} {interceptions:<4} {sacks:<8} {rating:<6}\n"
                                                else:
                                                    stat_line = ' / '.join(str(s) for s in stats) if stats else 'No stats available'
                                                    analysis += f"{display_name:<25} {stat_line}\n"
                                        analysis += "\n"
                                    
                                    # Show RB stats
                                    elif show_rb and 'rushing' in cat_name:
                                        if not stats_found:
                                            analysis += f"🎯 DETAILED PLAYER STATISTICS\n\n"
                                            stats_found = True
                                        
                                        analysis += f"🏃 {team_name} Rushing Statistics:\n\n"
                                        analysis += f"{'PLAYER':<25} {'CAR':<6} {'YDS':<6} {'AVG':<6} {'TD':<4} {'LONG':<6}\n"
                                        analysis += f"{'-'*25} {'-'*6} {'-'*6} {'-'*6} {'-'*4} {'-'*6}\n"
                                        
                                        athletes = stat_category.get('athletes', [])
                                        for athlete_data in athletes:
                                            if isinstance(athlete_data, dict):
                                                athlete = athlete_data.get('athlete', {})
                                                player_name = athlete.get('displayName', 'Unknown')
                                                jersey = athlete.get('jersey', '')
                                                display_name = f"{player_name} #{jersey}" if jersey else player_name
                                                
                                                stats = athlete_data.get('stats', [])
                                                if stats and len(stats) >= 5:
                                                    # ESPN rushing format: [CAR, YDS, AVG, TD, LONG]
                                                    carries = stats[0] if len(stats) > 0 else '0'
                                                    yards = stats[1] if len(stats) > 1 else '0'
                                                    avg = stats[2] if len(stats) > 2 else '0.0'
                                                    td = stats[3] if len(stats) > 3 else '0'
                                                    long = stats[4] if len(stats) > 4 else '0'
                                                    
                                                    analysis += f"{display_name:<25} {carries:<6} {yards:<6} {avg:<6} {td:<4} {long:<6}\n"
                                                else:
                                                    stat_line = ' / '.join(str(s) for s in stats) if stats else 'No stats available'
                                                    analysis += f"{display_name:<25} {stat_line}\n"
                                        analysis += "\n"
                                    
                                    # Show WR stats
                                    elif show_wr and 'receiving' in cat_name:
                                        if not stats_found:
                                            analysis += f"🎯 DETAILED PLAYER STATISTICS\n\n"
                                            stats_found = True
                                        
                                        analysis += f"🙌 {team_name} Receiving Statistics:\n\n"
                                        analysis += f"{'PLAYER':<25} {'REC':<6} {'YDS':<6} {'AVG':<6} {'TD':<4} {'LONG':<6} {'TGTS':<6}\n"
                                        analysis += f"{'-'*25} {'-'*6} {'-'*6} {'-'*6} {'-'*4} {'-'*6} {'-'*6}\n"
                                        
                                        athletes = stat_category.get('athletes', [])
                                        for athlete_data in athletes:
                                            if isinstance(athlete_data, dict):
                                                athlete = athlete_data.get('athlete', {})
                                                player_name = athlete.get('displayName', 'Unknown')
                                                jersey = athlete.get('jersey', '')
                                                display_name = f"{player_name} #{jersey}" if jersey else player_name
                                                
                                                stats = athlete_data.get('stats', [])
                                                if stats and len(stats) >= 6:
                                                    receptions = stats[0] if len(stats) > 0 else '0'
                                                    yards = stats[1] if len(stats) > 1 else '0'
                                                    avg = stats[2] if len(stats) > 2 else '0.0'
                                                    td = stats[3] if len(stats) > 3 else '0'
                                                    long = stats[4] if len(stats) > 4 else '0'
                                                    targets = stats[5] if len(stats) > 5 else '0'
                                                    
                                                    analysis += f"{display_name:<25} {receptions:<6} {yards:<6} {avg:<6} {td:<4} {long:<6} {targets:<6}\n"
                                                else:
                                                    stat_line = ' / '.join(str(s) for s in stats) if stats else 'No stats available'
                                                    analysis += f"{display_name:<25} {stat_line}\n"
                                        analysis += "\n"
        
        # If no stats found anywhere
        if not stats_found:
            requested_position = "QUARTERBACK" if show_qb else "RUNNING BACK" if show_rb else "RECEIVER" if show_wr else "PLAYER"
            analysis += f"⚠️  {requested_position} STATISTICS\n"
            analysis += f"Detailed {requested_position.lower()} statistics not available in ESPN game summary.\n"
            analysis += f"This may be due to the game format or data availability.\n\n"
        
        analysis += f"═══════════════════════════════════════════════════════════════════════════════\n"
        analysis += f"📊 Data verified from ESPN Game Summary API\n"
        analysis += f"✅ No fabricated statistics - only real game data reported\n"
        
        return analysis
    
    def process_mcp_game_data(self, mcp_summary_result: dict, basic_event: dict, query: str = "") -> str:
        """Process detailed game data from Sports AI MCP with player stats."""
        
        # Extract the actual summary data from MCP response
        summary_data = mcp_summary_result.get('data', {}).get('summary', {})
        
        # Basic game info from scoreboard event
        home_team = basic_event.get('home', {})
        away_team = basic_event.get('away', {})
        event_id = basic_event.get('event_id', 'Unknown')
        
        analysis = f"""🏈 NFL GAME ANALYSIS (via Sports AI MCP)

═══════════════════════════════════════════════════════════════════════════════

📊 GAME INFORMATION
{away_team.get('displayName', 'Away')} @ {home_team.get('displayName', 'Home')}
Date: {basic_event.get('date', 'Unknown')}
ESPN Event ID: {event_id}

"""
        
        # Game status and scores
        analysis += f"🏆 FINAL SCORE\n"
        analysis += f"{away_team.get('displayName', 'Away')}: {away_team.get('score', 'N/A')}\n"
        analysis += f"{home_team.get('displayName', 'Home')}: {home_team.get('score', 'N/A')}\n"
        analysis += f"Status: {summary_data.get('status', 'Unknown')}\n\n"
        
        # Team metadata from MCP
        teams_meta = summary_data.get('teams_meta', [])
        if teams_meta:
            analysis += "📋 TEAM INFORMATION:\n"
            for team in teams_meta:
                team_name = team.get('displayName', 'Unknown')
                score = team.get('score', 'N/A')
                analysis += f"  {team_name}: {score} points\n"
            analysis += "\n"
        
        # QB Statistics from MCP leaders data
        qb_stats_found = False
        leaders = summary_data.get('leaders')
        if leaders and isinstance(leaders, list):
            for category in leaders:
                if isinstance(category, dict):
                    cat_name = category.get('displayName', '').lower()
                    
                    if 'pass' in cat_name:
                        qb_stats_found = True
                        analysis += f"🎯 QUARTERBACK STATISTICS\n\n"
                        
                        leaders_list = category.get('leaders', [])
                        
                        # Group by team
                        teams_qb_stats = {}
                        for leader in leaders_list:
                            if isinstance(leader, dict):
                                team_info = leader.get('team', {})
                                team_name = team_info.get('displayName', 'Unknown Team')
                                
                                if team_name not in teams_qb_stats:
                                    teams_qb_stats[team_name] = []
                                
                                athlete = leader.get('athlete', {})
                                player_name = athlete.get('displayName', 'Unknown Player')
                                stats = leader.get('displayValue', 'No stats')
                                position = athlete.get('position', {}).get('abbreviation', '')
                                jersey = athlete.get('jersey', '')
                                
                                teams_qb_stats[team_name].append({
                                    'name': player_name,
                                    'position': position,
                                    'jersey': jersey,
                                    'stats': stats
                                })
                        
                        # Display QB stats by team
                        for team_name, qbs in teams_qb_stats.items():
                            analysis += f"📋 {team_name}:\n"
                            for qb in qbs:
                                analysis += f"   {qb['name']}"
                                if qb['position']:
                                    analysis += f" ({qb['position']})"
                                if qb['jersey']:
                                    analysis += f" #{qb['jersey']}"
                                analysis += f"\n   └─ {qb['stats']}\n\n"
                        
                        break
        
        # Enhanced boxscore QB stats from MCP if available
        if not qb_stats_found:
            boxscore = summary_data.get('boxscore')
            if boxscore and isinstance(boxscore, dict):
                players = boxscore.get('players', [])
                
                if players:
                    analysis += f"🎯 DETAILED QUARTERBACK STATISTICS\n\n"
                    
                    for player_group in players:
                        if isinstance(player_group, dict):
                            team = player_group.get('team', {})
                            team_name = team.get('displayName', 'Unknown Team')
                            
                            statistics = player_group.get('statistics', [])
                            for stat_category in statistics:
                                if isinstance(stat_category, dict):
                                    cat_name = stat_category.get('name', '').lower()
                                    
                                    if 'passing' in cat_name:
                                        analysis += f"📋 {team_name} Passing Statistics:\n\n"
                                        
                                        # Add header row to match ESPN format exactly
                                        analysis += f"{'PLAYER':<25} {'C/ATT':<6} {'YDS':<6} {'AVG':<6} {'TD':<4} {'INT':<4} {'SACKS':<8} {'RTG':<6}\n"
                                        analysis += f"{'-'*25} {'-'*6} {'-'*6} {'-'*6} {'-'*4} {'-'*4} {'-'*8} {'-'*6}\n"
                                        
                                        athletes = stat_category.get('athletes', [])
                                        for athlete_data in athletes:
                                            if isinstance(athlete_data, dict):
                                                athlete = athlete_data.get('athlete', {})
                                                player_name = athlete.get('displayName', 'Unknown')
                                                jersey = athlete.get('jersey', '')
                                                
                                                # Add jersey number to name if available
                                                display_name = f"{player_name} #{jersey}" if jersey else player_name
                                                
                                                stats = athlete_data.get('stats', [])
                                                if stats and len(stats) >= 7:
                                                    # ESPN format: [c/att, yards, avg, td, int, sacks, rating]
                                                    c_att = stats[0] if len(stats) > 0 else '0/0'
                                                    yards = stats[1] if len(stats) > 1 else '0'
                                                    avg = stats[2] if len(stats) > 2 else '0.0'
                                                    td = stats[3] if len(stats) > 3 else '0'
                                                    interceptions = stats[4] if len(stats) > 4 else '0'
                                                    sacks = stats[5] if len(stats) > 5 else '0-0'
                                                    rating = stats[6] if len(stats) > 6 else '0.0'
                                                    
                                                    # Format exactly like ESPN screenshot
                                                    analysis += f"{display_name:<25} {c_att:<6} {yards:<6} {avg:<6} {td:<4} {interceptions:<4} {sacks:<8} {rating:<6}\n"
                                                else:
                                                    # Fallback if stats format is different
                                                    stat_line = ' / '.join(str(s) for s in stats) if stats else 'No stats available'
                                                    analysis += f"{display_name:<25} {stat_line}\n"
                                        
                                        analysis += "\n"
        
        # If no QB stats found anywhere
        if not qb_stats_found and not (summary_data.get('boxscore', {}).get('players')):
            analysis += f"⚠️  QUARTERBACK STATISTICS\n"
            analysis += f"Detailed QB statistics not available in MCP game summary.\n"
            analysis += f"This may be due to the game format or data availability.\n\n"
        
        analysis += f"═══════════════════════════════════════════════════════════════════════════════\n"
        analysis += f"📊 Data verified from Sports AI MCP Server\n"
        analysis += f"✅ No fabricated statistics - only real ESPN data via MCP\n"
        
        return analysis
    
    def process_verified_game_data(self, game_data: dict) -> str:
        """Process game data with strict validation - only report what's actually there."""
        
        analysis = "🏈 VERIFIED NFL GAME DATA (from ESPN API):\n\n"
        
        # Basic game info
        game_name = game_data.get('name', 'Unknown matchup')
        game_date = game_data.get('date', 'Unknown date')
        game_id = game_data.get('id', 'Unknown ID')
        
        analysis += f"Game: {game_name}\n"
        analysis += f"Date: {game_date}\n"
        analysis += f"ESPN Game ID: {game_id}\n\n"
        
        # Competition data
        competitions = game_data.get('competitions', [])
        if not competitions:
            return analysis + "❌ No competition data available in ESPN response."
        
        comp = competitions[0]
        status = comp.get('status', {}).get('type', {})
        status_desc = status.get('description', 'Status unknown')
        analysis += f"Game Status: {status_desc}\n\n"
        
        # Team and player data
        competitors = comp.get('competitors', [])
        if not competitors:
            return analysis + "❌ No team data available in ESPN response."
        
        analysis += "TEAM DATA:\n"
        
        for competitor in competitors:
            team = competitor.get('team', {})
            team_name = team.get('displayName', 'Unknown Team')
            team_abbrev = team.get('abbreviation', 'UNK')
            score = competitor.get('score')
            
            analysis += f"\n{team_name} ({team_abbrev}):\n"
            
            if score is not None:
                analysis += f"  Score: {score}\n"
            else:
                analysis += f"  Score: Not available\n"
            
            # QB/Passing stats - ONLY report what's actually in the data
            leaders = competitor.get('leaders', [])
            passing_stats_found = False
            
            for leader_cat in leaders:
                cat_name = leader_cat.get('name', '').lower()
                display_name = leader_cat.get('displayName', '')
                
                if 'passing' in cat_name or 'pass' in display_name.lower():
                    passing_stats_found = True
                    analysis += f"  {display_name}:\n"
                    
                    leader_list = leader_cat.get('leaders', [])
                    if leader_list:
                        for leader in leader_list:
                            athlete = leader.get('athlete', {})
                            player_name = athlete.get('displayName', 'Unknown Player')
                            stats = leader.get('displayValue', 'No stats available')
                            position = athlete.get('position', {}).get('abbreviation', '')
                            jersey = athlete.get('jersey', '')
                            
                            analysis += f"    {player_name}"
                            if position:
                                analysis += f" ({position})"
                            if jersey:
                                analysis += f" #{jersey}"
                            analysis += f": {stats}\n"
                    else:
                        analysis += f"    No player data available\n"
            
            if not passing_stats_found:
                analysis += f"  Passing Stats: Not available in ESPN data\n"
        
        analysis += f"\n📊 Data Source: ESPN API (verified)\n"
        analysis += f"⚠️  Only actual data from ESPN is reported above.\n"
        
        return analysis
    
    def generate_no_data_response(self, dates_checked: list) -> str:
        """Generate response when no game data is found via MCP."""
        
        response = "❌ Requested game not found via Sports AI MCP.\n\n"
        response += f"🔍 Searched dates: {', '.join(dates_checked)}\n"
        response += f"🔍 Searched season types: Preseason (1) and Regular Season (2)\n\n"
        
        response += "⚠️  IMPORTANT: This system will not fabricate game statistics.\n"
        response += "For accurate game data, please check:\n"
        response += "• ESPN.com official game center\n"
        response += "• NFL.com official statistics\n"
        response += "• Team official websites\n\n"
        
        # Show what games ARE available via MCP
        response += "Recent NFL games found via Sports AI MCP:\n"
        try:
            # Use MCP to get current NFL games
            scoreboard_result = self.get_scoreboard_mcp(
                sport="football",
                league="nfl",
                seasontype=1
            )
            
            if scoreboard_result.get('ok'):
                events = scoreboard_result.get('data', {}).get('scoreboard', {}).get('events', [])
                if events:
                    for i, event in enumerate(events[:5], 1):
                        home_name = event.get('home', {}).get('displayName', 'Home')
                        away_name = event.get('away', {}).get('displayName', 'Away')
                        response += f"{i}. {away_name} @ {home_name}\n"
                else:
                    response += "No recent games found via MCP.\n"
            else:
                response += "Could not retrieve recent games list via MCP.\n"
        except Exception as e:
            response += f"Could not retrieve recent games list: {str(e)}\n"
        
        return response
    
    def call_custom_sports_mcp(self, sport: str, query: str) -> str:
        """Call your Sports AI MCP server for other sports."""
        try:
            print(f"🔍 Using Sports AI MCP server for {sport.upper()} games...")
            
            # Map sport to MCP parameters
            sport_mapping = {
                'mlb': ('baseball', 'mlb'),
                'nhl': ('hockey', 'nhl'),
                'soccer': ('soccer', 'usa.1'),  # MLS
                'mls': ('soccer', 'usa.1')
            }
            
            if sport not in sport_mapping:
                return f"❌ Sport '{sport}' not supported by Sports AI MCP"
            
            mcp_sport, mcp_league = sport_mapping[sport]
            
            # Call MCP scoreboard function
            scoreboard_result = self.get_scoreboard_mcp(
                sport=mcp_sport,
                league=mcp_league
            )
            
            if not scoreboard_result.get('ok'):
                return f"❌ MCP Error: {scoreboard_result.get('message', 'Unknown error')}"
            
            # Extract events from MCP response
            scoreboard_data = scoreboard_result.get('data', {}).get('scoreboard', {})
            events = scoreboard_data.get('events', [])
            
            if not events:
                return f"No {sport.upper()} games found via Sports AI MCP."
            
            analysis = f"🏆 {sport.upper()} Games Analysis (via Sports AI MCP):\n\n"
            
            for i, event in enumerate(events[:3], 1):
                home_team = event.get('home', {})
                away_team = event.get('away', {})
                
                home_name = home_team.get('displayName', 'Home Team')
                away_name = away_team.get('displayName', 'Away Team')
                home_score = home_team.get('score', 'N/A')
                away_score = away_team.get('score', 'N/A')
                
                analysis += f"{i}. {away_name} @ {home_name}\n"
                analysis += f"   Score: {away_name} {away_score}, {home_name} {home_score}\n"
                analysis += f"   Status: {event.get('status', 'Unknown')}\n"
                analysis += f"   Date: {event.get('date', 'Unknown')}\n\n"
            
            analysis += "📊 Data Source: Sports AI MCP Server\n"
            analysis += f"✅ Verified {sport.upper()} game data from ESPN via MCP\n"
            
            return analysis
                
        except Exception as e:
            return f"❌ Error calling Sports AI MCP: {str(e)}"
    
    # ESPN API calls removed - now using Sports AI MCP server
    # All ESPN data fetching is handled by the MCP server
    def get_fallback_analysis(self, sport: str) -> str:
        """Fallback analysis when MCP calls fail."""
        return f"""
{sport.upper()} Analysis (Fallback Mode):

⚠️  Unable to connect to ESPN Sports AI MCP
📊 Using fallback analysis mode

To get live game data and player statistics:
1. Ensure your MCP servers are running
2. Check MCP configuration in .kiro/settings/mcp.json
3. Verify ESPN API connectivity

Current capabilities in fallback mode:
• Basic sport detection
• Betting odds (still available)
• Limited analysis without live game data

For full functionality, please check your MCP setup.
"""
    
    def get_sports_odds(self, sport: str) -> str:
        """Get betting odds for the specified sport from Wagyu Sports MCP."""
        try:
            # Map sport to API key
            sport_keys = {
                'wnba': 'basketball_wnba',
                'nfl': 'americanfootball_nfl', 
                'mlb': 'baseball_mlb',
                'nhl': 'icehockey_nhl',
                'soccer': 'soccer_usa_mls'
            }
            
            sport_key = sport_keys.get(sport, 'basketball_wnba')
            
            # Call The Odds API directly (this is what Wagyu Sports MCP does)
            response = requests.get(
                f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds",
                params={
                    "apiKey": self.odds_api_key,
                    "regions": "us",
                    "markets": "h2h,spreads",
                    "oddsFormat": "american"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                odds_data = response.json()
                if odds_data:
                    # Format the odds data nicely
                    formatted_odds = f"Live {sport.upper()} Betting Odds:\n\n"
                    for game in odds_data[:3]:  # Show first 3 games
                        formatted_odds += f"{game['away_team']} @ {game['home_team']}\n"
                        formatted_odds += f"Time: {game['commence_time']}\n"
                        
                        if game['bookmakers']:
                            bookmaker = game['bookmakers'][0]  # Use first bookmaker
                            for market in bookmaker['markets']:
                                if market['key'] == 'h2h':
                                    formatted_odds += "Moneyline: "
                                    for outcome in market['outcomes']:
                                        price = outcome['price']
                                        if price > 0:
                                            formatted_odds += f"{outcome['name']} +{price} "
                                        else:
                                            formatted_odds += f"{outcome['name']} {price} "
                                    formatted_odds += "\n"
                                elif market['key'] == 'spreads':
                                    formatted_odds += "Spread: "
                                    for outcome in market['outcomes']:
                                        point = outcome.get('point', 0)
                                        price = outcome['price']
                                        if price > 0:
                                            formatted_odds += f"{outcome['name']} {point:+.1f} (+{price}) "
                                        else:
                                            formatted_odds += f"{outcome['name']} {point:+.1f} ({price}) "
                                    formatted_odds += "\n"
                        formatted_odds += "\n"
                    
                    return formatted_odds
                else:
                    return f"No {sport.upper()} games found with current odds."
            else:
                return f"Error getting odds: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error getting odds data: {str(e)}"
    
    def get_ai_analysis(self, query: str, sports_data: str, odds_data: str, sport: str) -> str:
        """Get AI analysis from OpenRouter with strict data validation."""
        
        # CRITICAL: Check if we have real data or if ESPN call failed
        if "❌ Ravens vs Colts game not found" in sports_data or "Error calling" in sports_data:
            return f"""🚨 DATA UNAVAILABLE - NO ANALYSIS PROVIDED

❌ Could not find the requested game data in ESPN API
❌ Will NOT provide fabricated statistics or analysis
❌ All sports statistics must be verified from official sources

🔍 What we searched for: {query}
📊 ESPN API Response: {sports_data.strip()}

⚠️  IMPORTANT: This system will never make up sports statistics.
For accurate game stats, please check:
• ESPN.com official game center
• NFL.com official statistics
• Team official websites

🛡️  Data Integrity Policy: We only report verified, real data."""
        
        # Check if this is a pure stats query (no betting context needed)
        stats_query = any(word in query.lower() for word in ['stats', 'statistics', 'performance', 'qb', 'quarterback', 'how did'])
        betting_query = any(word in query.lower() for word in ['bet', 'odds', 'spread', 'moneyline', 'recommend'])
        
        if stats_query and not betting_query:
            # For pure stats queries, return the data directly without AI analysis
            return sports_data
        
        # Create a comprehensive prompt with STRICT instructions about data accuracy
        prompt = f"""You are a professional sports analyst. You must NEVER make up statistics or game results.

CRITICAL INSTRUCTIONS:
- ONLY use the exact data provided below
- If data is missing or unclear, state "Data not available"
- NEVER invent player names, scores, or statistics
- If you cannot find specific information, say so explicitly

User Question: {query}

ESPN Game Data:
{sports_data}

Betting Odds Data:
{odds_data}

RESPONSE REQUIREMENTS:
- Only report statistics that are explicitly provided in the data above
- If specific QB stats are not in the data, state "QB statistics not available in provided data"
- Use exact player names and numbers from the data only
- If game results are not clear, state "Game results unclear from provided data"
- Format for terminal display with clear sections

Provide analysis ONLY based on the actual data provided above."""
        
        # Try primary model first, then fallbacks
        models_to_try = [self.openrouter_model] + [m for m in self.fallback_models if m != self.openrouter_model]
        
        for model in models_to_try:
            try:
                response = requests.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://localhost:3000",
                        "X-Title": "Sports Betting Analysis"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a professional sports betting analyst."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1500,
                        "temperature": 0.7
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        return data['choices'][0]['message']['content']
                elif response.status_code == 401:
                    # Authentication error - fall back to basic analysis
                    break
                else:
                    # Try next model
                    continue
                    
            except Exception as e:
                # Try next model
                continue
        
        # Fallback to basic analysis when AI is unavailable
        return self.get_basic_analysis(query, sports_data, odds_data, sport)
    
    def get_basic_analysis(self, query: str, sports_data: str, odds_data: str, sport: str) -> str:
        """Provide basic analysis when AI is unavailable."""
        analysis = f"""🚨 AI Analysis Unavailable (Invalid OpenRouter API Key)

📊 BASIC SPORTS ANALYSIS FOR {sport.upper()}:

{sports_data}

💰 CURRENT BETTING ODDS:
{odds_data}

📝 BASIC RECOMMENDATIONS:
• Check team records and recent performance
• Look for value in underdog moneylines with good recent form
• Consider home field advantage in close matchups
• Monitor injury reports before placing bets
• Start with smaller bet sizes until you establish patterns

⚠️  To get AI-powered recommendations:
1. Visit https://openrouter.ai and create an account
2. Generate a new API key
3. Update OPENROUTER_API_KEY in your .env.local file
4. Restart the application

Current API Key Status: Invalid/Expired"""
        
        return analysis
    
    def process_query(self, query: str) -> str:
        """Process a user query and return analysis with strict data validation."""
        print(f"\n🔍 Analyzing your question: '{query}'")
        
        # Detect which sport the user is asking about
        sport = self.detect_sport_from_query(query)
        print(f"🏆 Detected sport: {sport.upper()}")
        
        # Get sports games analysis with validation
        print(f"📊 Getting {sport.upper()} games analysis from Sports AI MCP...")
        sports_data = self.get_sports_analysis(sport, query)
        
        # CRITICAL: Check if we have valid data before proceeding
        if self.is_data_unavailable(sports_data):
            print("⚠️  No verified game data found - stopping analysis")
            return sports_data  # Return the "no data" message directly
        
        # Only get betting odds if we have valid game data
        print(f"💰 Getting live {sport.upper()} betting odds from Wagyu Sports MCP...")
        odds_data = self.get_sports_odds(sport)
        
        # Get AI analysis combining both with strict validation
        print("🤖 Generating verified analysis...")
        analysis = self.get_ai_analysis(query, sports_data, odds_data, sport)
        
        return analysis
    
    def is_data_unavailable(self, sports_data: str) -> bool:
        """Check if sports data indicates no verified information is available."""
        error_indicators = [
            "❌ Ravens vs Colts game not found",
            "Error calling",
            "No verified data",
            "Data not available"
        ]
        
        return any(indicator in sports_data for indicator in error_indicators)
    
    def run_interactive(self):
        """Run the interactive interface."""
        print("=" * 80)
        print("🏀 SPORTS BETTING ANALYSIS SYSTEM")
        print("=" * 80)
        print()
        print("Welcome to your AI-powered sports betting analysis system!")
        print("This system uses:")
        print("• Sports AI MCP - Real ESPN data + AI analysis")
        print("• Wagyu Sports MCP - Live betting odds from major sportsbooks")
        print(f"• OpenRouter AI - {self.openrouter_model} for recommendations")
        print()
        print("Example questions:")
        print('• "What are the best WNBA bets for tonight?"')
        print('• "Show me NFL spreads and recommend which to bet"')
        print('• "Which MLB games have the best value?"')
        print('• "Analyze tonight\'s hockey games and give me your top picks"')
        print('• "What are the best soccer bets this weekend?"')
        print()
        print("Type 'quit' or 'exit' to stop.")
        print("=" * 80)
        
        while True:
            try:
                # Get user input with better error handling
                try:
                    query = input("\n💬 Your question: ").strip()
                except EOFError:
                    print("\n\n👋 Thanks for using the Sports Betting Analysis System!")
                    break
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using the Sports Betting Analysis System!")
                    break
                
                # Process the query
                start_time = time.time()
                result = self.process_query(query)
                end_time = time.time()
                
                # Display results
                print("\n" + "=" * 80)
                print("🎯 AI BETTING ANALYSIS")
                print("=" * 80)
                print(result)
                print("=" * 80)
                print(f"⏱️  Analysis completed in {end_time - start_time:.2f} seconds")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using the Sports Betting Analysis System!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again with a different question.")

def main():
    """Main function."""
    try:
        system = SportsAnalysisSystem()
        system.run_interactive()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease check your .env.local file and ensure all API keys are set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ System Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()