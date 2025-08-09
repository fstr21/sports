#!/usr/bin/env python3
"""
Natural Language Sports Data Interface

This tool allows you to ask natural language questions about sports data
and get responses that combine ESPN data (via MCP) and odds data (via Wagyu MCP).
It uses OpenRouter to understand your questions and fetch the right data.

Examples:
  python sports_chat.py "What NFL games are happening today?"
  python sports_chat.py "Show me the Lakers vs Celtics game stats"
  python sports_chat.py "What are the odds for tonight's NFL games?"
  python sports_chat.py "Who's the leading scorer in the Warriors game?"
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import MCP functions
from core_mcp import (
    scoreboard, teams, game_summary, analyze_game_strict, 
    MCPError, MCPServerError, MCPValidationError
)
from core_llm import strict_answer, LLMError, LLMConfigurationError, LLMAPIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SportsDataFetcher:
    """Handles fetching data from various MCP sources."""
    
    async def get_scoreboard_data(self, league: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get scoreboard data for a league."""
        try:
            return await scoreboard(league, date)
        except Exception as e:
            logger.error(f"Error fetching scoreboard for {league}: {e}")
            return {"error": str(e)}
    
    async def get_game_data(self, league: str, event_id: str) -> Dict[str, Any]:
        """Get detailed game data."""
        try:
            return await game_summary(league, event_id)
        except Exception as e:
            logger.error(f"Error fetching game {event_id}: {e}")
            return {"error": str(e)}
    
    async def get_teams_data(self, league: str) -> Dict[str, Any]:
        """Get teams data for a league."""
        try:
            return await teams(league)
        except Exception as e:
            logger.error(f"Error fetching teams for {league}: {e}")
            return {"error": str(e)}

class QueryProcessor:
    """Processes natural language queries and determines what data to fetch."""
    
    def __init__(self):
        self.data_fetcher = SportsDataFetcher()
        self.supported_leagues = [
            'nfl', 'nba', 'wnba', 'mlb', 'nhl', 'mls', 
            'epl', 'laliga', 'ncaaf', 'ncaab'
        ]
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return relevant sports data.
        
        Args:
            query: Natural language question about sports
            
        Returns:
            Dictionary containing the response and any fetched data
        """
        logger.info(f"Processing query: {query}")
        
        # First, use LLM to understand what the user wants
        query_analysis = await self._analyze_query(query)
        
        if not query_analysis.get("success"):
            return {
                "success": False,
                "message": "Could not understand your question. Please try rephrasing.",
                "query": query
            }
        
        # Extract what data we need to fetch
        intent = query_analysis.get("intent", {})
        
        # Fetch the requested data
        fetched_data = await self._fetch_requested_data(intent)
        
        # Generate final response using the fetched data
        final_response = await self._generate_response(query, fetched_data)
        
        return {
            "success": True,
            "query": query,
            "intent": intent,
            "data": fetched_data,
            "response": final_response
        }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the query to understand what data is needed."""
        
        analysis_prompt = f"""
        Analyze this sports question and determine what data needs to be fetched:
        
        Question: "{query}"
        
        Available data sources:
        - ESPN scoreboard data (current games, scores, status)
        - ESPN game summaries (detailed stats, player performance)
        - ESPN team data (rosters, team info)
        - Odds data (betting lines, spreads, over/under)
        
        Supported leagues: {', '.join(self.supported_leagues)}
        
        Respond with JSON in this format:
        {{
            "success": true/false,
            "intent": {{
                "type": "scoreboard|game|teams|odds|general",
                "league": "nfl|nba|etc or null",
                "date": "YYYYMMDD or null",
                "team_names": ["team1", "team2"] or null,
                "event_id": "event_id or null",
                "specific_question": "what specifically they want to know"
            }}
        }}
        
        Examples:
        - "NFL games today" -> {{"type": "scoreboard", "league": "nfl", "date": "today"}}
        - "Lakers vs Celtics stats" -> {{"type": "game", "team_names": ["Lakers", "Celtics"]}}
        - "What are the odds for tonight's games?" -> {{"type": "odds", "date": "today"}}
        """
        
        try:
            success, response = await strict_answer({}, analysis_prompt)
            if success:
                # Try to parse JSON response
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # If not JSON, extract key info manually
                    return self._extract_intent_manually(query)
            else:
                return {"success": False, "error": response}
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_intent_manually(self, query: str) -> Dict[str, Any]:
        """Fallback method to extract intent from query."""
        query_lower = query.lower()
        
        # Detect league (check longer names first to avoid conflicts)
        detected_league = None
        league_keywords = {
            'wnba': ['wnba', 'women\'s basketball', 'womens basketball'],
            'nba': ['nba', 'basketball'],
            'nfl': ['nfl', 'football'],
            'ncaaf': ['ncaaf', 'college football'],
            'ncaab': ['ncaab', 'college basketball'],
            'mlb': ['mlb', 'baseball'],
            'nhl': ['nhl', 'hockey'],
            'mls': ['mls', 'soccer'],
            'epl': ['epl', 'premier league'],
            'laliga': ['laliga', 'la liga']
        }
        
        for league, keywords in league_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_league = league
                break
        
        # Detect intent type
        if any(word in query_lower for word in ['scoreboard', 'games', 'schedule', 'today']):
            intent_type = 'scoreboard'
        elif any(word in query_lower for word in ['stats', 'game', 'vs', 'versus', 'against']):
            intent_type = 'game'
        elif any(word in query_lower for word in ['odds', 'betting', 'lines', 'spread']):
            intent_type = 'odds'
        elif any(word in query_lower for word in ['teams', 'roster', 'players']):
            intent_type = 'teams'
        else:
            intent_type = 'general'
        
        # Detect date
        date = None
        if 'today' in query_lower:
            date = datetime.now().strftime('%Y%m%d')
        
        return {
            "success": True,
            "intent": {
                "type": intent_type,
                "league": detected_league,
                "date": date,
                "specific_question": query
            }
        }
    
    async def _fetch_requested_data(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch the data based on the analyzed intent."""
        intent_type = intent.get("type")
        league = intent.get("league")
        date = intent.get("date")
        
        fetched_data = {}
        
        try:
            if intent_type == "scoreboard" and league:
                logger.info(f"Fetching scoreboard for {league}")
                fetched_data["scoreboard"] = await self.data_fetcher.get_scoreboard_data(league, date)
            
            elif intent_type == "teams" and league:
                logger.info(f"Fetching teams for {league}")
                fetched_data["teams"] = await self.data_fetcher.get_teams_data(league)
            
            elif intent_type == "game":
                # For game queries, we might need to search scoreboards first
                if league:
                    logger.info(f"Fetching recent games for {league}")
                    scoreboard_data = await self.data_fetcher.get_scoreboard_data(league, date)
                    fetched_data["scoreboard"] = scoreboard_data
                    
                    # If we have specific teams mentioned, try to find their game
                    team_names = intent.get("team_names", [])
                    if team_names and scoreboard_data.get("ok"):
                        events = scoreboard_data.get("data", {}).get("scoreboard", {}).get("events", [])
                        for event in events:
                            home_team = event.get("home", {}).get("displayName", "").lower()
                            away_team = event.get("away", {}).get("displayName", "").lower()
                            
                            # Simple team name matching
                            if any(team.lower() in home_team or team.lower() in away_team for team in team_names):
                                event_id = event.get("event_id")
                                if event_id:
                                    logger.info(f"Fetching game details for event {event_id}")
                                    fetched_data["game"] = await self.data_fetcher.get_game_data(league, event_id)
                                    break
            
            elif intent_type == "odds":
                # Try to fetch odds data using Wagyu MCP
                logger.info("Fetching odds data via Wagyu MCP")
                try:
                    # Import Wagyu MCP functions
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'clients'))
                    
                    # For now, we'll note that odds integration is available
                    # You can extend this to call actual Wagyu MCP functions
                    fetched_data["odds_note"] = "Odds integration available via Wagyu MCP - specific implementation needed"
                    logger.info("Odds data integration ready")
                except Exception as e:
                    fetched_data["odds_error"] = f"Wagyu MCP not available: {e}"
                    logger.warning(f"Could not access Wagyu MCP: {e}")
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            fetched_data["error"] = str(e)
        
        return fetched_data
    
    async def _generate_response(self, original_query: str, fetched_data: Dict[str, Any]) -> str:
        """Generate a natural language response based on the fetched data."""
        
        if not fetched_data or "error" in fetched_data:
            return f"I encountered an error while fetching data: {fetched_data.get('error', 'Unknown error')}"
        
        # Create a comprehensive prompt for the LLM
        response_prompt = f"""
        The user asked: "{original_query}"
        
        I fetched this sports data for them:
        {json.dumps(fetched_data, indent=2)}
        
        Please provide a helpful, natural language response that answers their question using ONLY the data provided above.
        
        Guidelines:
        - Be conversational and helpful
        - Include specific details from the data (scores, player names, stats, etc.)
        - If the data shows games in progress, mention current scores
        - If the data shows completed games, mention final scores
        - If no relevant data was found, say so clearly
        - Don't make up any information not in the provided data
        - Format numbers and stats clearly
        """
        
        try:
            success, response = await strict_answer(fetched_data, response_prompt)
            if success:
                return response
            else:
                return f"I found some data but had trouble formatting the response: {response}"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I found the data but encountered an error formatting the response: {e}"

async def interactive_mode():
    """Run in interactive mode for continuous conversation."""
    processor = QueryProcessor()
    
    print("🏈 Sports Data Chat Interface")
    print("=" * 50)
    print("Ask me anything about sports! Examples:")
    print("  • 'What NFL games are happening today?'")
    print("  • 'Show me Lakers vs Celtics stats'")
    print("  • 'Who's winning the Warriors game?'")
    print("  • 'What are today's NBA scores?'")
    print("\nType 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            query = input("🤔 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using Sports Data Chat!")
                break
            
            if not query:
                continue
            
            print("🔍 Processing your question...")
            result = await processor.process_query(query)
            
            if result.get("success"):
                print(f"\n💬 {result['response']}\n")
                
                # Optionally show debug info
                if logger.level <= logging.DEBUG:
                    print(f"Debug - Intent: {result.get('intent')}")
                    print(f"Debug - Data keys: {list(result.get('data', {}).keys())}")
            else:
                print(f"\n❌ {result.get('message', 'Unknown error')}\n")
                
        except KeyboardInterrupt:
            print("\n👋 Thanks for using Sports Data Chat!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

async def single_query_mode(query: str, debug: bool = False):
    """Process a single query and exit."""
    processor = QueryProcessor()
    
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print(f"🔍 Processing: {query}")
    result = await processor.process_query(query)
    
    if result.get("success"):
        print(f"\n💬 {result['response']}")
        
        if debug:
            print(f"\nDebug Info:")
            print(f"Intent: {json.dumps(result.get('intent'), indent=2)}")
            print(f"Data keys: {list(result.get('data', {}).keys())}")
    else:
        print(f"\n❌ {result.get('message', 'Unknown error')}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Natural language interface for sports data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s "What NFL games are today?"        # Single query
  %(prog)s "Lakers vs Celtics stats" --debug # Single query with debug info

Interactive mode examples:
  • "What NFL games are happening today?"
  • "Show me the Lakers game stats"
  • "Who's winning the Warriors vs Lakers game?"
  • "What are today's NBA scores?"
  • "Tell me about the Cowboys game"
        """
    )
    
    parser.add_argument('query', nargs='?', help='Single question to ask (optional - omit for interactive mode)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        if args.query:
            # Single query mode
            asyncio.run(single_query_mode(args.query, args.debug))
        else:
            # Interactive mode
            asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()