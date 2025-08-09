#!/usr/bin/env python3
"""
Fixed Sports Data Terminal Interface

A comprehensive terminal interface for testing and exploring your sports data system.
Tests connections to OpenRouter, Wagyu MCP, and ESPN MCP, then provides an interactive
chat interface for natural language queries including betting odds.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
import pytz

# Add clients to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clients'))

# Import our MCP and LLM functions
from clients.core_mcp import (
    scoreboard, teams, game_summary, analyze_game_strict,
    MCPError, MCPServerError, MCPValidationError, LEAGUE_MAPPING
)
from clients.core_llm import strict_answer, validate_llm_config, LLMError

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Eastern timezone
EASTERN_TZ = pytz.timezone('US/Eastern')

class ConnectionTester:
    """Tests connections to all required services."""
    
    def __init__(self):
        self.test_results = {}
    
    async def test_all_connections(self) -> Dict[str, Any]:
        """Test all service connections and return results."""
        print("🔍 Testing Service Connections...")
        print("=" * 50)
        
        try:
            # Test OpenRouter
            await self._test_openrouter()
            
            # Test ESPN MCP
            await self._test_espn_mcp()
            
            # Test Wagyu MCP with timeout protection
            try:
                await asyncio.wait_for(self._test_wagyu_mcp(), timeout=15.0)
            except asyncio.TimeoutError:
                self.test_results["wagyu_mcp"] = {
                    "status": "⚠️  TIMEOUT",
                    "error": "Overall connection test timed out after 15 seconds",
                    "note": "Skipping Wagyu MCP test to prevent terminal hang"
                }
                print("   ⚠️  Wagyu MCP test timed out - skipping to prevent hang")
            
            # Test timezone
            self._test_timezone()
            
        except Exception as e:
            print(f"   ❌ Connection testing error: {e}")
            logger.error(f"Connection testing error: {e}")
        
        return self.test_results
    
    async def _test_openrouter(self):
        """Test OpenRouter connection and configuration."""
        print("🤖 Testing OpenRouter LLM...")
        
        try:
            # Check configuration
            config = validate_llm_config()
            
            if not config["valid"]:
                self.test_results["openrouter"] = {
                    "status": "❌ FAILED",
                    "error": f"Configuration invalid: {', '.join(config['errors'])}",
                    "config": config["config"]
                }
                print(f"   ❌ Configuration Error: {', '.join(config['errors'])}")
                return
            
            # Test actual API call with a simple, clear test
            test_data = {"connection_test": True}
            success, response = await strict_answer(test_data, "Reply with exactly: 'Connection test successful'")
            
            if success:
                # Check if response contains expected text (be more flexible)
                if any(word in response.lower() for word in ['successful', 'success', 'working', 'connected']):
                    self.test_results["openrouter"] = {
                        "status": "✅ CONNECTED",
                        "model": config["config"]["model"],
                        "api_key": config["config"]["api_key_configured"],
                        "base_url": config["config"]["base_url"]
                    }
                    print(f"   ✅ Connected to {config['config']['model']}")
                    print(f"   🔑 API Key: {'Configured' if config['config']['api_key_configured'] else 'Missing'}")
                else:
                    self.test_results["openrouter"] = {
                        "status": "✅ CONNECTED",
                        "model": config["config"]["model"],
                        "note": "Connected but response format unexpected",
                        "response": response[:100]
                    }
                    print(f"   ✅ Connected to {config['config']['model']}")
                    print(f"   ℹ️  Response format unexpected but connection working")
            else:
                self.test_results["openrouter"] = {
                    "status": "❌ FAILED",
                    "error": f"API call failed: {response}",
                    "config": config["config"]
                }
                print(f"   ❌ API call failed: {response[:60]}...")
                
        except Exception as e:
            self.test_results["openrouter"] = {
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"   ❌ Connection failed: {e}")
    
    async def _test_espn_mcp(self):
        """Test ESPN MCP server connection."""
        print("🏈 Testing ESPN MCP Server...")
        
        try:
            # Test with a simple scoreboard call
            result = await scoreboard("nfl")
            
            if result.get("ok"):
                events_count = len(result.get("data", {}).get("scoreboard", {}).get("events", []))
                self.test_results["espn_mcp"] = {
                    "status": "✅ CONNECTED",
                    "events_found": events_count,
                    "url": result.get("meta", {}).get("url", "Unknown"),
                    "leagues_supported": list(LEAGUE_MAPPING.keys())
                }
                print(f"   ✅ Connected - Found {events_count} NFL events")
                print(f"   🌐 ESPN URL: {result.get('meta', {}).get('url', 'Unknown')[:60]}...")
            else:
                self.test_results["espn_mcp"] = {
                    "status": "⚠️  PARTIAL",
                    "error": result.get("message", "Unknown error"),
                    "raw_response": str(result)[:200]
                }
                print(f"   ⚠️  Connected but got error: {result.get('message', 'Unknown')}")
                
        except Exception as e:
            self.test_results["espn_mcp"] = {
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"   ❌ Connection failed: {e}")
    
    async def _test_wagyu_mcp(self):
        """Test Wagyu MCP server connection."""
        print("🎲 Testing Wagyu Odds MCP...")
        
        try:
            # Import and test the Wagyu client with timeout
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clients'))
            from wagyu_client import test_wagyu_connection
            
            # Test the connection with a timeout
            result = await asyncio.wait_for(test_wagyu_connection(), timeout=10.0)
            
            if result["status"] == "success":
                self.test_results["wagyu_mcp"] = {
                    "status": "✅ CONNECTED",
                    "sports_count": result.get("sports_count", "Unknown"),
                    "quota_info": result.get("quota_info", {}),
                    "server": "Wagyu Odds API"
                }
                print(f"   ✅ Connected - {result.get('sports_count', 'Multiple')} sports available")
                
                # Show quota info if available
                quota = result.get("quota_info", {})
                if quota.get("remaining_requests") is not None:
                    print(f"   📊 API Quota: {quota.get('remaining_requests', 'Unknown')} requests remaining")
            else:
                self.test_results["wagyu_mcp"] = {
                    "status": "❌ FAILED",
                    "error": result.get("error", "Unknown error"),
                    "message": result.get("message", "Connection failed")
                }
                print(f"   ❌ Connection failed: {result.get('error', 'Unknown error')}")
                
        except asyncio.TimeoutError:
            self.test_results["wagyu_mcp"] = {
                "status": "⚠️  TIMEOUT",
                "error": "Connection test timed out after 10 seconds",
                "note": "MCP server may be starting slowly or hanging"
            }
            print(f"   ⚠️  Connection test timed out (10s) - server may be slow to start")
        except Exception as e:
            self.test_results["wagyu_mcp"] = {
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"   ❌ Connection test failed: {e}")
    
    def _test_timezone(self):
        """Test timezone configuration."""
        print("🕐 Testing Timezone Configuration...")
        
        try:
            now_utc = datetime.now(pytz.UTC)
            now_eastern = now_utc.astimezone(EASTERN_TZ)
            
            self.test_results["timezone"] = {
                "status": "✅ CONFIGURED",
                "current_eastern_time": now_eastern.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "utc_time": now_utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "timezone_name": str(EASTERN_TZ)
            }
            print(f"   ✅ Eastern Time: {now_eastern.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"   🌍 UTC Time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
        except Exception as e:
            self.test_results["timezone"] = {
                "status": "❌ FAILED",
                "error": str(e)
            }
            print(f"   ❌ Timezone error: {e}")

class SportsTerminal:
    """Main terminal interface for sports data queries."""
    
    def __init__(self):
        self.connection_tester = ConnectionTester()
        self.connections_tested = False
        self.supported_leagues = list(LEAGUE_MAPPING.keys())
    
    def get_eastern_time(self) -> datetime:
        """Get current time in Eastern timezone."""
        return datetime.now(EASTERN_TZ)
    
    def get_eastern_date_string(self) -> str:
        """Get current date in Eastern timezone as YYYYMMDD."""
        return self.get_eastern_time().strftime("%Y%m%d")
    
    async def start(self):
        """Start the terminal interface."""
        print("🏈🏀⚾🏒 Sports Data Terminal")
        print("=" * 60)
        print(f"Current Eastern Time: {self.get_eastern_time().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print("=" * 60)
        
        # Test connections first
        await self.connection_tester.test_all_connections()
        self.connections_tested = True
        
        print("\n" + "=" * 60)
        self._show_help()
        print("=" * 60)
        
        # Start interactive loop
        await self._interactive_loop()
    
    def _show_help(self):
        """Show help information."""
        print("💡 Available Commands:")
        print("  • Ask natural language questions about sports")
        print("  • 'help' - Show this help")
        print("  • 'status' - Show detailed connection status")
        print("  • 'leagues' - Show supported leagues")
        print("  • 'time' - Show current Eastern time")
        print("  • 'quit' or 'exit' - Exit terminal")
        print("\n📝 Example Questions:")
        print("  • 'NFL scores today'")
        print("  • 'WNBA games with odds'")
        print("  • 'Storm vs Aces betting lines'")
        print("  • 'Chicago Sky moneyline odds'")
    
    async def _interactive_loop(self):
        """Main interactive loop."""
        while True:
            try:
                print(f"\n🕐 {self.get_eastern_time().strftime('%H:%M:%S ET')}")
                query = input("🤔 Your question: ").strip()
                
                if not query:
                    continue
                
                # Handle special commands
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thanks for using Sports Terminal!")
                    break
                elif query.lower() == 'help':
                    self._show_help()
                    continue
                elif query.lower() == 'status':
                    await self._show_status()
                    continue
                elif query.lower() == 'leagues':
                    self._show_leagues()
                    continue
                elif query.lower() == 'time':
                    self._show_time()
                    continue
                
                # Process sports query
                print("🔍 Processing your question...")
                await self._process_query(query)
                
            except KeyboardInterrupt:
                print("\n👋 Thanks for using Sports Terminal!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error(f"Interactive loop error: {e}")
    
    async def _show_status(self):
        """Show detailed connection status."""
        if not self.connections_tested:
            print("⚠️  Connections not tested yet. Testing now...")
            await self.connection_tester.test_all_connections()
        
        print("\n" + "=" * 60)
        print("📊 SYSTEM STATUS")
        print("=" * 60)
        
        # OpenRouter LLM Status
        openrouter = self.connection_tester.test_results.get("openrouter", {})
        print(f"🤖 OpenRouter LLM: {openrouter.get('status', 'Unknown')}")
        if openrouter.get("model"):
            print(f"   Model: {openrouter['model']}")
        if openrouter.get("base_url"):
            print(f"   URL: {openrouter['base_url']}")
        if openrouter.get("error"):
            print(f"   Error: {openrouter['error']}")
        
        print()
        
        # ESPN MCP Status
        espn = self.connection_tester.test_results.get("espn_mcp", {})
        print(f"🏈 ESPN MCP Server: {espn.get('status', 'Unknown')}")
        if espn.get("events_found") is not None:
            print(f"   Current Events: {espn['events_found']}")
        if espn.get("leagues_supported"):
            print(f"   Leagues: {len(espn['leagues_supported'])} supported")
        if espn.get("url"):
            print(f"   Last URL: {espn['url'][:50]}...")
        if espn.get("error"):
            print(f"   Error: {espn['error']}")
        
        print()
        
        # Wagyu MCP Status
        wagyu = self.connection_tester.test_results.get("wagyu_mcp", {})
        print(f"🎲 Wagyu Odds MCP: {wagyu.get('status', 'Unknown')}")
        if wagyu.get("sports_count"):
            print(f"   Sports Available: {wagyu['sports_count']}")
        if wagyu.get("quota_info"):
            quota = wagyu["quota_info"]
            if quota.get("remaining_requests"):
                print(f"   API Quota: {quota['remaining_requests']} remaining")
        if wagyu.get("error"):
            print(f"   Error: {wagyu['error']}")
        
        print()
        
        # Timezone Status
        timezone = self.connection_tester.test_results.get("timezone", {})
        print(f"🕐 Timezone: {timezone.get('status', 'Unknown')}")
        if timezone.get("current_eastern_time"):
            print(f"   Eastern Time: {timezone['current_eastern_time']}")
        if timezone.get("timezone_name"):
            print(f"   Zone: {timezone['timezone_name']}")
        
        print("=" * 60)
    
    def _show_leagues(self):
        """Show supported leagues."""
        print("\n🏆 Supported Leagues:")
        print("-" * 30)
        for league in sorted(self.supported_leagues):
            sport, league_name = LEAGUE_MAPPING[league]
            print(f"  {league.upper()}: {sport}/{league_name}")
    
    def _show_time(self):
        """Show current time information."""
        eastern_time = self.get_eastern_time()
        utc_time = datetime.now(pytz.UTC)
        
        print(f"\n🕐 Time Information:")
        print(f"  Eastern: {eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  UTC: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Date String: {self.get_eastern_date_string()}")
    
    async def _process_query(self, query: str):
        """Process a natural language sports query."""
        try:
            # Analyze the query to understand intent
            intent = await self._analyze_query(query)
            
            if not intent.get("success"):
                print(f"❌ Could not understand your question: {intent.get('error', 'Unknown error')}")
                return
            
            # Fetch the requested data
            data = await self._fetch_data(query, intent)
            
            # Generate response
            response = await self._generate_response(query, intent, data)
            
            print(f"\n💬 {response}")
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Query interrupted by user")
        except asyncio.CancelledError:
            print(f"\n⚠️  Query was cancelled")
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            logger.error(f"Query processing error: {e}")
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine what data to fetch."""
        # Skip LLM analysis to avoid timeout issues - use manual parsing directly
        try:
            return self._parse_query_manually(query)
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            return {
                "success": False,
                "error": f"Query analysis failed: {e}"
            }
    
    def _parse_query_manually(self, query: str) -> Dict[str, Any]:
        """Fallback manual query parsing."""
        query_lower = query.lower()
        
        # Detect league (check specific terms first to avoid conflicts)
        detected_league = None
        
        # Check for WNBA teams first (Storm, Aces are WNBA teams)
        wnba_teams = ['storm', 'aces', 'liberty', 'mystics', 'wings', 'lynx', 'fever', 'mercury', 'sun', 'sky', 'sparks']
        if any(team in query_lower for team in wnba_teams) or 'wnba' in query_lower:
            detected_league = 'wnba'
        elif 'ncaaf' in query_lower or 'college football' in query_lower:
            detected_league = 'ncaaf'
        elif 'ncaab' in query_lower or 'college basketball' in query_lower:
            detected_league = 'ncaab'
        elif 'nba' in query_lower:
            detected_league = 'nba'
        elif 'nfl' in query_lower:
            detected_league = 'nfl'
        elif 'mlb' in query_lower or 'baseball' in query_lower:
            detected_league = 'mlb'
        elif 'nhl' in query_lower or 'hockey' in query_lower:
            detected_league = 'nhl'
        elif 'mls' in query_lower:
            detected_league = 'mls'
        elif 'epl' in query_lower or 'premier league' in query_lower:
            detected_league = 'epl'
        elif 'laliga' in query_lower or 'la liga' in query_lower:
            detected_league = 'laliga'
        elif 'basketball' in query_lower:
            # Default basketball to NBA unless context suggests otherwise
            detected_league = 'nba'
        elif 'football' in query_lower:
            # Default football to NFL unless context suggests otherwise
            detected_league = 'nfl'
        
        # Detect intent (betting terms take priority)
        betting_terms = ['odds', 'betting', 'lines', 'line', 'spread', 'moneyline', 'money line', 'over', 'under', 'o/u', 'point line', 'take', 'would you', 'prop', 'props', 'points', 'rebounds', 'assists']
        if any(term in query_lower for term in betting_terms):
            intent_type = 'odds'
        elif any(word in query_lower for word in ['scoreboard', 'games', 'schedule', 'today', 'scores']):
            intent_type = 'scoreboard'
        elif any(word in query_lower for word in ['stats', 'game', 'vs', 'versus', 'v ']):
            intent_type = 'game'
        elif any(word in query_lower for word in ['teams', 'roster']):
            intent_type = 'teams'
        else:
            intent_type = 'scoreboard'  # Default
        
        # Detect date
        date = None
        if 'today' in query_lower:
            date = self.get_eastern_date_string()
        
        # Extract team names and players
        teams = []
        player_mentioned = None
        
        if 'storm' in query_lower and 'aces' in query_lower:
            teams = ['Storm', 'Aces']
        elif ('chicago' in query_lower or 'sky' in query_lower) and ('indiana' in query_lower or 'fever' in query_lower):
            teams = ['Chicago Sky', 'Indiana Fever']
        elif ' v ' in query_lower or ' vs ' in query_lower:
            import re
            vs_match = re.search(r'(\w+)\s+v[s]?\s+(\w+)', query_lower)
            if vs_match:
                teams = [vs_match.group(1).title(), vs_match.group(2).title()]
        
        if 'ajay wilson' in query_lower or "a'ja wilson" in query_lower:
            player_mentioned = "A'ja Wilson"
        elif 'kelsey mitchell' in query_lower:
            player_mentioned = "Kelsey Mitchell"
        elif 'caitlin clark' in query_lower:
            player_mentioned = "Caitlin Clark"
        elif 'veronica burton' in query_lower:
            player_mentioned = "Veronica Burton"
        
        return {
            "success": True,
            "intent": {
                "type": intent_type,
                "league": detected_league,
                "date": date,
                "teams": teams if teams else None,
                "player": player_mentioned,
                "betting_question": intent_type == 'odds',
                "specific_question": query
            }
        }
    
    async def _fetch_data(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data based on analyzed intent."""
        intent_data = intent.get("intent", {})
        intent_type = intent_data.get("type")
        league = intent_data.get("league")
        date = intent_data.get("date")
        
        data = {}
        
        try:
            if intent_type == "scoreboard" and league:
                logger.info(f"Fetching {league} scoreboard for {date or 'current'}")
                data["scoreboard"] = await scoreboard(league, date)
            
            elif intent_type == "teams" and league:
                logger.info(f"Fetching {league} teams")
                data["teams"] = await teams(league)
            
            elif intent_type == "game" and league:
                # Get scoreboard first to find games
                logger.info(f"Fetching {league} games")
                scoreboard_data = await scoreboard(league, date)
                data["scoreboard"] = scoreboard_data
                
                # Try to get specific game if teams mentioned
                teams_mentioned = intent_data.get("teams", [])
                if teams_mentioned and scoreboard_data.get("ok"):
                    events = scoreboard_data.get("data", {}).get("scoreboard", {}).get("events", [])
                    for event in events:
                        home = event.get("home", {}).get("displayName", "").lower()
                        away = event.get("away", {}).get("displayName", "").lower()
                        
                        if any(team.lower() in home or team.lower() in away for team in teams_mentioned):
                            event_id = event.get("event_id")
                            if event_id:
                                logger.info(f"Fetching game details for {event_id}")
                                data["game"] = await game_summary(league, event_id)
                                break
            
            elif intent_type == "odds":
                # Get live odds data using Wagyu MCP
                logger.info("Fetching odds data")
                try:
                    # Import Wagyu client
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clients'))
                    from wagyu_client import WagyuClient, get_sport_key
                    
                    # Get scoreboard data first
                    if league:
                        scoreboard_data = await scoreboard(league, date)
                        data["scoreboard"] = scoreboard_data
                    
                    # Get odds data
                    if league:
                        wagyu_client = WagyuClient()
                        sport_key = get_sport_key(league)
                        player_mentioned = intent_data.get("player")
                        query_lower = query.lower()  # Define query_lower here
                        
                        logger.info(f"Fetching odds for {sport_key}")
                        
                        # Check if this is a player prop request
                        if player_mentioned and any(prop in query_lower for prop in ['points', 'rebounds', 'assists', 'prop', 'props', 'o/u', 'over', 'under']):
                            try:
                                # First get general odds to find the event ID for the game
                                logger.info(f"Player prop request detected for {player_mentioned}")
                                general_odds = await wagyu_client.get_odds(
                                    sport=sport_key,
                                    markets="h2h"
                                )
                                
                                # Find the specific game event ID based on teams mentioned
                                event_id = None
                                teams_mentioned = intent_data.get("teams", [])
                                
                                if isinstance(general_odds, list):
                                    games_data = general_odds
                                elif isinstance(general_odds, dict) and "data" in general_odds:
                                    games_data = general_odds["data"]
                                elif isinstance(general_odds, dict) and "content" in general_odds:
                                    games_data = json.loads(general_odds["content"])
                                else:
                                    games_data = []
                                
                                # Look for matching game
                                for game in games_data:
                                    if isinstance(game, dict):
                                        home_team = game.get('home_team', '').lower()
                                        away_team = game.get('away_team', '').lower()
                                        
                                        # Check if the teams match (or if no specific teams, get first WNBA game)
                                        if teams_mentioned:
                                            if any(team.lower() in home_team or team.lower() in away_team for team in teams_mentioned):
                                                event_id = game.get('id')
                                                logger.info(f"Found event ID {event_id} for teams {teams_mentioned}")
                                                break
                                        elif 'chicago sky' in query_lower and 'fever' in query_lower:
                                            if 'chicago' in home_team or 'chicago' in away_team or 'fever' in home_team or 'fever' in away_team:
                                                event_id = game.get('id')
                                                logger.info(f"Found event ID {event_id} for Sky vs Fever")
                                                break
                                        elif 'sky' in query_lower and 'fever' in query_lower:
                                            if 'sky' in home_team or 'sky' in away_team or 'fever' in home_team or 'fever' in away_team:
                                                event_id = game.get('id')
                                                logger.info(f"Found event ID {event_id} for Sky vs Fever")
                                                break
                                
                                # Get player props if we found the event ID
                                player_props_data = None
                                if event_id:
                                    logger.info(f"Fetching player props for event {event_id}")
                                    player_props_data = await wagyu_client.get_event_odds(
                                        sport=sport_key,
                                        event_id=event_id,
                                        regions="us",
                                        markets="player_points,player_rebounds,player_assists"
                                    )
                                
                                # Get regular odds too
                                odds_data = await wagyu_client.get_odds(
                                    sport=sport_key,
                                    markets="h2h,spreads,totals"
                                )
                                
                                data["odds"] = odds_data
                                data["player_props"] = player_props_data
                                data["odds_info"] = {
                                    "note": "Live betting odds and player props retrieved" if player_props_data else "Live betting odds retrieved - player props not found",
                                    "league": league,
                                    "sport_key": sport_key,
                                    "teams": intent_data.get("teams", []),
                                    "player": player_mentioned,
                                    "event_id": event_id,
                                    "has_player_props": bool(player_props_data),
                                    "wagyu_status": "Connected and active"
                                }
                            except Exception as e:
                                logger.error(f"Error getting player props: {e}")
                                # Fall back to regular odds
                                odds_data = await wagyu_client.get_odds(
                                    sport=sport_key,
                                    markets="h2h,spreads,totals"
                                )
                                data["odds"] = odds_data
                                data["odds_info"] = {
                                    "note": f"Live betting odds retrieved - player props error: {str(e)}",
                                    "league": league,
                                    "sport_key": sport_key,
                                    "teams": intent_data.get("teams", []),
                                    "player": player_mentioned,
                                    "wagyu_status": "Connected but player props failed"
                                }
                        else:
                            # Regular odds request (no player props)
                            odds_data = await wagyu_client.get_odds(
                                sport=sport_key,
                                markets="h2h,spreads,totals"  # moneyline, spreads, over/under
                            )
                            
                            data["odds"] = odds_data
                            data["odds_info"] = {
                                "note": "Live betting odds retrieved",
                                "league": league,
                                "sport_key": sport_key,
                                "teams": intent_data.get("teams", []),
                                "player": intent_data.get("player"),
                                "wagyu_status": "Connected and active"
                            }
                    else:
                        data["odds_info"] = {
                            "note": "Betting analysis requested but no league detected",
                            "wagyu_status": "Available but need league specification"
                        }
                        
                except Exception as e:
                    logger.error(f"Error fetching odds: {e}")
                    data["odds_error"] = str(e)
                    data["odds_info"] = {
                        "note": "Betting analysis requested",
                        "league": league,
                        "teams": intent_data.get("teams", []),
                        "wagyu_status": f"Error: {str(e)}"
                    }
            
        except Exception as e:
            data["error"] = str(e)
            logger.error(f"Data fetch error: {e}")
        
        return data
    
    async def _generate_response(self, query: str, intent: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Generate natural language response."""
        if "error" in data:
            return f"I encountered an error fetching data: {data['error']}"
        
        # Handle betting/odds questions specially
        if "odds_info" in data:
            return self._format_betting_response(query, data)
        
        # For scoreboard queries, format the data directly to ensure completeness
        if "scoreboard" in data and data["scoreboard"].get("ok"):
            return self._format_scoreboard_response(query, data["scoreboard"])
        
        # For other queries, use LLM
        response_prompt = f"""
        User asked: "{query}"
        Current Eastern Time: {self.get_eastern_time().strftime('%Y-%m-%d %H:%M:%S %Z')}
        
        Here's the sports data I found:
        {json.dumps(data, indent=2)[:4000]}
        
        IMPORTANT: Include ALL games/events from the data. Do not summarize or skip any.
        Provide a helpful response using ONLY the data above.
        Include specific details like scores, team names, game status, times.
        Format as a clear list or table if there are multiple games.
        """
        
        try:
            success, response = await strict_answer(data, response_prompt)
            return response if success else f"Found data but couldn't format response: {response}"
        except Exception as e:
            return f"Found data but error generating response: {e}"
    
    def _format_scoreboard_response(self, query: str, scoreboard_data: Dict[str, Any]) -> str:
        """Format scoreboard data directly to ensure all games are shown."""
        try:
            events = scoreboard_data.get("data", {}).get("scoreboard", {}).get("events", [])
            
            if not events:
                return "No games found for your query."
            
            # Group games by status
            in_progress = []
            pre_game = []
            final = []
            
            for event in events:
                status = event.get("status", "").lower()
                home = event.get("home", {})
                away = event.get("away", {})
                
                game_info = {
                    "home_team": home.get("displayName", "Unknown"),
                    "away_team": away.get("displayName", "Unknown"),
                    "home_score": home.get("score", "0"),
                    "away_score": away.get("score", "0"),
                    "status": status,
                    "date": event.get("date", ""),
                    "event_id": event.get("event_id", "")
                }
                
                if status == "in":
                    in_progress.append(game_info)
                elif status == "pre":
                    pre_game.append(game_info)
                elif status in ["post", "final"]:
                    final.append(game_info)
            
            # Format response
            response_parts = []
            
            if in_progress:
                response_parts.append("🔴 **GAMES IN PROGRESS:**")
                for game in in_progress:
                    response_parts.append(f"  • {game['away_team']} {game['away_score']} - {game['home_score']} {game['home_team']}")
            
            if pre_game:
                response_parts.append("\n⏰ **UPCOMING GAMES:**")
                for game in pre_game:
                    # Convert UTC time to Eastern
                    try:
                        from datetime import datetime
                        import pytz
                        utc_time = datetime.fromisoformat(game['date'].replace('Z', '+00:00'))
                        eastern_time = utc_time.astimezone(EASTERN_TZ)
                        time_str = eastern_time.strftime("%I:%M %p ET")
                    except:
                        time_str = "TBD"
                    
                    response_parts.append(f"  • {game['away_team']} @ {game['home_team']} ({time_str})")
            
            if final:
                response_parts.append("\n✅ **COMPLETED GAMES:**")
                for game in final:
                    response_parts.append(f"  • {game['away_team']} {game['away_score']} - {game['home_score']} {game['home_team']} (Final)")
            
            response_parts.append(f"\n📊 **Total: {len(events)} games**")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error formatting scoreboard: {e}")
            return f"Found {len(events)} games but error formatting display: {e}"
    
    def _format_betting_response(self, query: str, data: Dict[str, Any]) -> str:
        """Format response for betting/odds questions."""
        try:
            odds_info = data.get("odds_info", {})
            league = odds_info.get("league", "Unknown")
            teams = odds_info.get("teams", [])
            player = odds_info.get("player")
            
            response_parts = []
            response_parts.append(f"🎲 **BETTING ANALYSIS - {league.upper()}**")
            
            # Show live odds if available
            if "odds" in data and data["odds"]:
                odds_data = data["odds"]
                response_parts.append(f"\n💰 **LIVE BETTING ODDS:**")
                
                # Process odds data
                games_with_odds = []
                if isinstance(odds_data, dict) and "data" in odds_data:
                    games_with_odds = odds_data["data"][:5]  # Show first 5 games
                elif isinstance(odds_data, list):
                    games_with_odds = odds_data[:5]
                elif isinstance(odds_data, dict) and "content" in odds_data:
                    try:
                        import json
                        parsed_content = json.loads(odds_data["content"])
                        if isinstance(parsed_content, list):
                            games_with_odds = parsed_content[:5]
                    except:
                        games_with_odds = []
                
                for game in games_with_odds:
                    if isinstance(game, dict):
                        home_team = game.get("home_team", "Unknown")
                        away_team = game.get("away_team", "Unknown")
                        commence_time = game.get("commence_time", "TBD")
                        
                        response_parts.append(f"\n  🏀 **{away_team} @ {home_team}**")
                        response_parts.append(f"     ⏰ {commence_time}")
                        
                        # Show bookmaker odds
                        bookmakers = game.get("bookmakers", [])
                        for book in bookmakers[:2]:  # Show first 2 bookmakers
                            book_name = book.get("title", "Unknown")
                            markets = book.get("markets", [])
                            
                            for market in markets:
                                market_key = market.get("key", "")
                                outcomes = market.get("outcomes", [])
                                
                                if market_key == "h2h":  # Moneyline
                                    response_parts.append(f"     💵 {book_name} Moneyline:")
                                    for outcome in outcomes:
                                        team = outcome.get("name", "Unknown")
                                        price = outcome.get("price", "N/A")
                                        if isinstance(price, (int, float)):
                                            response_parts.append(f"        {team}: {price:+d}")
                                        else:
                                            response_parts.append(f"        {team}: {price}")
                                
                                elif market_key == "spreads":  # Point spread
                                    response_parts.append(f"     📊 {book_name} Spread:")
                                    for outcome in outcomes:
                                        team = outcome.get("name", "Unknown")
                                        point = outcome.get("point", "N/A")
                                        price = outcome.get("price", "N/A")
                                        spread_str = f"{point:+.1f}" if isinstance(point, (int, float)) else str(point)
                                        price_str = f"{price:+d}" if isinstance(price, (int, float)) else str(price)
                                        response_parts.append(f"        {team} {spread_str}: {price_str}")
                                
                                elif market_key == "totals":  # Over/Under
                                    response_parts.append(f"     🎯 {book_name} Total:")
                                    for outcome in outcomes:
                                        name = outcome.get("name", "Unknown")
                                        point = outcome.get("point", "N/A")
                                        price = outcome.get("price", "N/A")
                                        total_str = f"{point}" if isinstance(point, (int, float)) else str(point)
                                        price_str = f"{price:+d}" if isinstance(price, (int, float)) else str(price)
                                        response_parts.append(f"        {name} {total_str}: {price_str}")
                
                # Look for specific team matchup if requested
                if teams:
                    team_names = [t.lower() for t in teams]
                    matching_odds = []
                    
                    for game in games_with_odds:
                        if isinstance(game, dict):
                            home = game.get("home_team", "").lower()
                            away = game.get("away_team", "").lower()
                            
                            if any(team in home or team in away for team in team_names):
                                matching_odds.append(game)
                    
                    if matching_odds:
                        response_parts.append(f"\n🎯 **REQUESTED MATCHUP ANALYSIS:**")
                        for game in matching_odds:
                            home_team = game.get("home_team", "Unknown")
                            away_team = game.get("away_team", "Unknown")
                            commence_time = game.get("commence_time", "TBD")
                            
                            response_parts.append(f"  🏀 **{away_team} @ {home_team}**")
                            response_parts.append(f"     ⏰ {commence_time}")
                            
                            # Show moneyline odds from multiple books
                            bookmakers = game.get("bookmakers", [])
                            for book in bookmakers[:2]:  # Show first 2 bookmakers
                                book_name = book.get("title", "Unknown")
                                markets = book.get("markets", [])
                                
                                for market in markets:
                                    if market.get("key") == "h2h":  # Moneyline
                                        outcomes = market.get("outcomes", [])
                                        response_parts.append(f"     💵 {book_name} Moneyline:")
                                        for outcome in outcomes:
                                            team = outcome.get("name", "Unknown")
                                            price = outcome.get("price", "N/A")
                                            if isinstance(price, (int, float)):
                                                response_parts.append(f"        {team}: {price:+d}")
                                            else:
                                                response_parts.append(f"        {team}: {price}")
                                        break  # Only show moneyline
                                break  # Only show first market per book
                
                # Also check for Chicago Sky specifically in the query
                elif 'chicago' in query.lower() and 'sky' in query.lower():
                    sky_games = []
                    for game in games_with_odds:
                        if isinstance(game, dict):
                            home = game.get("home_team", "").lower()
                            away = game.get("away_team", "").lower()
                            
                            if 'chicago' in home or 'chicago' in away or 'sky' in home or 'sky' in away:
                                sky_games.append(game)
                    
                    if sky_games:
                        response_parts.append(f"\n🎯 **CHICAGO SKY GAMES:**")
                        for game in sky_games:
                            home_team = game.get("home_team", "Unknown")
                            away_team = game.get("away_team", "Unknown")
                            commence_time = game.get("commence_time", "TBD")
                            
                            response_parts.append(f"  🏀 **{away_team} @ {home_team}**")
                            response_parts.append(f"     ⏰ {commence_time}")
                            
                            # Show moneyline odds
                            bookmakers = game.get("bookmakers", [])
                            for book in bookmakers[:2]:
                                book_name = book.get("title", "Unknown")
                                markets = book.get("markets", [])
                                
                                for market in markets:
                                    if market.get("key") == "h2h":
                                        outcomes = market.get("outcomes", [])
                                        response_parts.append(f"     💵 {book_name} Moneyline:")
                                        for outcome in outcomes:
                                            team = outcome.get("name", "Unknown")
                                            price = outcome.get("price", "N/A")
                                            if isinstance(price, (int, float)):
                                                response_parts.append(f"        {team}: {price:+d}")
                                            else:
                                                response_parts.append(f"        {team}: {price}")
                                        break
            
            # Show current games from scoreboard
            if "scoreboard" in data and data["scoreboard"].get("ok"):
                events = data["scoreboard"].get("data", {}).get("scoreboard", {}).get("events", [])
                
                response_parts.append(f"\n📊 **CURRENT {league.upper()} GAMES:**")
                for event in events[:3]:  # Show first 3 games
                    home = event.get("home", {}).get("displayName", "Unknown")
                    away = event.get("away", {}).get("displayName", "Unknown")
                    home_score = event.get("home", {}).get("score", "0")
                    away_score = event.get("away", {}).get("score", "0")
                    status = event.get("status", "unknown")
                    
                    if status == "in":
                        response_parts.append(f"  • {away} {away_score} - {home_score} {home} (LIVE)")
                    elif status == "pre":
                        response_parts.append(f"  • {away} @ {home} (Upcoming)")
                    else:
                        response_parts.append(f"  • {away} {away_score} - {home_score} {home} (Final)")
            
            # Player prop section
            if player:
                response_parts.append(f"\n👤 **PLAYER PROP REQUEST:**")
                response_parts.append(f"  • Player: {player}")
                
                # Check if we have actual player props data
                if data.get("player_props"):
                    player_props_data = data["player_props"]
                    
                    # Check if we have specific prop request
                    if 'points' in query.lower() and ('o/u' in query.lower() or 'over' in query.lower() or 'under' in query.lower()):
                        response_parts.append(f"  • Requested: Points Over/Under")
                    
                    # Parse and display player props
                    if isinstance(player_props_data, dict) and "bookmakers" in player_props_data:
                        bookmakers = player_props_data["bookmakers"]
                    elif isinstance(player_props_data, list):
                        bookmakers = player_props_data
                    elif isinstance(player_props_data, dict) and "content" in player_props_data:
                        try:
                            parsed_data = json.loads(player_props_data["content"])
                            bookmakers = parsed_data.get("bookmakers", [])
                        except:
                            bookmakers = []
                    else:
                        bookmakers = []
                    
                    # Display player props for the requested player
                    found_player_props = False
                    for bookmaker in bookmakers:
                        if isinstance(bookmaker, dict) and "markets" in bookmaker:
                            bookmaker_title = bookmaker.get("title", "Unknown Sportsbook")
                            for market in bookmaker["markets"]:
                                market_key = market.get("key", "")
                                for outcome in market.get("outcomes", []):
                                    outcome_player = outcome.get("description", "")
                                    if player.lower() in outcome_player.lower():
                                        found_player_props = True
                                        bet_type = outcome.get("name", "")
                                        price = outcome.get("price", "N/A")
                                        point = outcome.get("point", "")
                                        
                                        if "points" in market_key:
                                            prop_type = "Points"
                                        elif "rebounds" in market_key:
                                            prop_type = "Rebounds"
                                        elif "assists" in market_key:
                                            prop_type = "Assists"
                                        else:
                                            prop_type = market_key.replace("player_", "").title()
                                        
                                        if point:
                                            response_parts.append(f"     💰 {bookmaker_title} - {prop_type} {bet_type} {point}: {price}")
                                        else:
                                            response_parts.append(f"     💰 {bookmaker_title} - {prop_type} {bet_type}: {price}")
                    
                    if not found_player_props:
                        response_parts.append(f"  • No prop odds found for {player} at this time")
                        response_parts.append(f"  • Event ID used: {odds_info.get('event_id', 'None')}")
                
                elif odds_info.get("has_player_props") is False:
                    response_parts.append(f"  • Event ID: {odds_info.get('event_id', 'Not found')}")
                    response_parts.append(f"  • No player props available for this game")
                    
                else:
                    # Check if we have specific prop request
                    if 'points' in query.lower() and ('o/u' in query.lower() or 'over' in query.lower() or 'under' in query.lower()):
                        response_parts.append(f"  • Requested: Points Over/Under")
                        response_parts.append(f"  • Note: Player prop odds require event-specific API calls")
                        response_parts.append(f"  • Try: 'Get {player} player props for tonight's game'")
                    else:
                        response_parts.append(f"  • Note: Player prop odds (points, rebounds, etc.) require")
                        response_parts.append(f"    specialized sportsbook APIs beyond basic game odds")
            
            # Status
            response_parts.append(f"\n✅ **WAGYU STATUS:** {odds_info.get('wagyu_status', 'Unknown')}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error formatting betting response: {e}")
            return f"I found betting data but encountered an error formatting the response: {e}"

async def main():
    """Main entry point."""
    try:
        terminal = SportsTerminal()
        await terminal.start()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())