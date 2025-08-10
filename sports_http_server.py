#!/usr/bin/env python3
"""
Sports HTTP Server - Simple HTTP wrapper for Sports MCPs

This server provides HTTP endpoints that wrap your existing MCP functionality,
solving the deployment consistency issues across different machines.

Usage:
    python sports_http_server.py

Environment Variables:
    OPENROUTER_API_KEY - Required for ESPN analysis
    ODDS_API_KEY - Required for odds data (optional, will use test mode if missing)
    SPORTS_API_KEY - Required for authentication (set to any secure string)
    SERVER_PORT - Server port (default: 8000)
    SERVER_HOST - Server host (default: 0.0.0.0)
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pytz

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Load environment variables from .env.local file if it exists
try:
    from dotenv import load_dotenv
    # Try .env.local first, then fall back to .env
    if os.path.exists('.env.local'):
        load_dotenv('.env.local')
        print("[INFO] Loaded environment variables from .env.local file")
    else:
        load_dotenv()
        print("[INFO] Loaded environment variables from .env file")
except ImportError:
    print("[WARNING] python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"[WARNING] Could not load environment file: {e}")

# Add the current directory and sports_mcp to the path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "sports_mcp"))

# Import the MCP wrapper functions
try:
    from mcp_wrappers import (
        get_scoreboard_wrapper, get_teams_wrapper, 
        get_game_summary_wrapper, analyze_game_wrapper
    )
    SPORTS_AI_AVAILABLE = True
    print("[OK] Sports AI MCP wrappers imported")
except ImportError as e:
    print(f"[WARNING] Could not import Sports AI MCP wrappers: {e}")
    SPORTS_AI_AVAILABLE = False

try:
    # Import the wagyu odds server
    from sports_mcp.wagyu_sports.mcp_server.odds_client_server import OddsMcpServer
    ODDS_AVAILABLE = True
    print("[OK] Wagyu Odds MCP imported successfully")
except ImportError as e:
    print(f"[WARNING] Could not import Wagyu Odds MCP: {e}")
    ODDS_AVAILABLE = False

# Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8000")))  # Railway uses PORT env var
SPORTS_API_KEY = os.getenv("SPORTS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

if not SPORTS_API_KEY:
    print("ERROR: SPORTS_API_KEY environment variable is required!")
    print("Set it to any secure string, e.g.:")
    print("export SPORTS_API_KEY=your-secure-api-key-here")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Sports Data HTTP Server",
    description="HTTP wrapper for Sports AI and Odds MCPs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key authentication"""
    if credentials.credentials != SPORTS_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials

# Initialize Odds MCP server if available
odds_server = None
odds_client = None

if ODDS_AVAILABLE:
    try:
        if ODDS_API_KEY:
            # Import the OddsClient directly
            try:
                from sports_mcp.wagyu_sports.odds_client import OddsClient
                odds_client = OddsClient(ODDS_API_KEY)
                print("[OK] Odds Client initialized directly with API key")
            except ImportError:
                print("[WARNING] Could not import OddsClient directly")
            
            # Also try MCP server initialization - NEVER test mode
            try:
                odds_server = OddsMcpServer(api_key=ODDS_API_KEY, test_mode=False)
                print("[OK] Odds MCP server initialized with REAL API")
            except Exception as e:
                print(f"[WARNING] Odds MCP server initialization failed: {e}")
        else:
            # NO API KEY = NO ODDS SERVICE
            print("[ERROR] No ODDS_API_KEY provided - odds service will be unavailable")
            print("[INFO] Set ODDS_API_KEY environment variable to enable real odds data")
    except Exception as e:
        print(f"[ERROR] Odds initialization failed: {e}")

# Determine which odds system to use
ODDS_DIRECT_CLIENT = odds_client is not None
ODDS_MCP_SERVER = odds_server is not None

print(f"[INFO] Odds systems available:")
print(f"   Direct Client: {'Yes' if ODDS_DIRECT_CLIENT else 'No'}")
print(f"   MCP Server: {'Yes' if ODDS_MCP_SERVER else 'No'}")

# Request/Response Models
class ScoreboardRequest(BaseModel):
    sport: str
    league: str
    dates: Optional[str] = None
    limit: Optional[int] = None
    week: Optional[int] = None
    seasontype: Optional[int] = None

class TeamsRequest(BaseModel):
    sport: str
    league: str

class GameSummaryRequest(BaseModel):
    sport: str
    league: str
    event_id: str

class GameAnalysisRequest(BaseModel):
    sport: str
    league: str
    event_id: str
    question: str

class ProbeRequest(BaseModel):
    sport: str
    league: str
    date: Optional[str] = None

class OddsRequest(BaseModel):
    sport: str
    regions: Optional[str] = None
    markets: Optional[str] = None
    odds_format: Optional[str] = None
    date_format: Optional[str] = None

class EventOddsRequest(BaseModel):
    sport: str
    event_id: str
    regions: Optional[str] = None
    markets: Optional[str] = None
    odds_format: Optional[str] = None
    date_format: Optional[str] = None

class PlayerPropsRequest(BaseModel):
    sport: str
    date: Optional[str] = None  # YYYY-MM-DD format, defaults to today
    player_markets: Optional[str] = "player_points,player_rebounds,player_assists"
    regions: Optional[str] = "us"
    odds_format: Optional[str] = "american"

class DailyIntelligenceRequest(BaseModel):
    leagues: List[str]
    include_odds: bool = True
    include_analysis: bool = False
    date: Optional[str] = None

class NaturalLanguageRequest(BaseModel):
    question: str
    model: Optional[str] = "openai/gpt-4o-mini"

# Timezone conversion utilities
def convert_utc_to_eastern(utc_datetime_str: str) -> str:
    """Convert UTC datetime string to Eastern time"""
    try:
        # Parse the UTC datetime
        if utc_datetime_str.endswith('Z'):
            utc_datetime_str = utc_datetime_str[:-1] + '+00:00'
        
        utc_dt = datetime.fromisoformat(utc_datetime_str)
        
        # Convert to Eastern time
        eastern = pytz.timezone('US/Eastern')
        utc = pytz.timezone('UTC')
        
        if utc_dt.tzinfo is None:
            utc_dt = utc.localize(utc_dt)
        
        eastern_dt = utc_dt.astimezone(eastern)
        return eastern_dt.strftime('%Y-%m-%d %I:%M %p %Z')
    except:
        return utc_datetime_str

def convert_timestamps_in_data(data: Any) -> Any:
    """Recursively convert UTC timestamps to Eastern in nested data structures"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == 'date' and isinstance(value, str) and ('T' in value or 'Z' in value):
                result[key] = value  # Keep original UTC
                result[key + '_eastern'] = convert_utc_to_eastern(value)  # Add Eastern version
            elif key == 'generated_at' and isinstance(value, str):
                result[key] = value  # Keep original UTC
                result[key + '_eastern'] = convert_utc_to_eastern(value)  # Add Eastern version
            else:
                result[key] = convert_timestamps_in_data(value)
        return result
    elif isinstance(data, list):
        return [convert_timestamps_in_data(item) for item in data]
    else:
        return data

# Natural Language Processing Functions
async def ask_openrouter_query(question: str, model: str = "openai/gpt-4o-mini") -> Tuple[bool, str, Dict[str, Any]]:
    """Ask OpenRouter to process a natural language sports query"""
    if not OPENROUTER_API_KEY:
        return False, "OpenRouter API key not configured", {}
    
    # Create the system prompt for sports query understanding
    system_prompt = """You are a sports data assistant that converts natural language questions into API calls.
    
Available endpoints (use ONLY these exact endpoint names):
1. scoreboard - Get games for a sport/league (params: sport, league, dates optional)
2. teams - Get teams for a sport/league (params: sport, league) 
3. game-summary - Get detailed game info (params: sport, league, event_id)
4. daily-intelligence - Get comprehensive daily data (params: leagues list, include_odds)

Supported leagues:
- basketball/nba, basketball/wnba
- football/nfl, football/college-football  
- baseball/mlb
- hockey/nhl
- soccer/eng.1 (Premier League), soccer/esp.1 (La Liga), soccer/usa.1 (MLS)

Return JSON with:
{
  "endpoint": "endpoint_name",
  "params": {...},
  "explanation": "brief explanation of what you're doing"
}

IMPORTANT: 
- Use only these endpoint names: scoreboard, teams, game-summary, daily-intelligence
- For "today's games" questions, use scoreboard endpoint with NO dates parameter at all
- NEVER use dates:"today" - omit the dates field entirely for today's games
- Only include dates parameter for specific dates like "yesterday", "2024-08-09", etc.
- For questions about multiple sports or daily summaries, use daily-intelligence
- If you need a specific event_id, explain that more info is needed

Example for today's games:
{"endpoint": "scoreboard", "params": {"sport": "baseball", "league": "mlb"}}"""

    try:
        import httpx
        client = httpx.AsyncClient()
        
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "X-Title": "Sports AI MCP"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
        )
        
        if response.status_code != 200:
            return False, f"OpenRouter error: {response.status_code}", {}
            
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Try to parse the JSON response
        try:
            import json
            parsed_response = json.loads(content)
            return True, content, parsed_response
        except json.JSONDecodeError:
            # If not valid JSON, return as explanation
            return True, content, {"explanation": content}
            
    except Exception as e:
        return False, f"Error calling OpenRouter: {str(e)}", {}

async def execute_parsed_query(parsed_query: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the parsed query against the appropriate endpoint"""
    
    endpoint = parsed_query.get("endpoint")
    params = parsed_query.get("params", {})
    
    try:
        if endpoint == "scoreboard" or "scoreboard" in endpoint:
            result = await get_scoreboard_wrapper(
                sport=params.get("sport", ""),
                league=params.get("league", ""),
                dates=params.get("dates"),
                limit=params.get("limit"),
                week=params.get("week"),
                seasontype=params.get("seasontype")
            )
            # Convert timestamps to Eastern time
            if result.get("ok") and "data" in result:
                result["data"] = convert_timestamps_in_data(result["data"])
            return result
        
        elif endpoint == "teams" or "teams" in endpoint:
            return await get_teams_wrapper(
                sport=params.get("sport", ""),
                league=params.get("league", "")
            )
        
        elif endpoint == "game-summary" or "game-summary" in endpoint:
            return await get_game_summary_wrapper(
                sport=params.get("sport", ""),
                league=params.get("league", ""),
                event_id=params.get("event_id", "")
            )
        
        elif endpoint == "daily-intelligence" or "daily-intelligence" in endpoint:
            leagues = params.get("leagues", [])
            if isinstance(leagues, str):
                leagues = [leagues]
            
            # Simulate the daily intelligence call
            results = {}
            for league_spec in leagues:
                if "/" not in league_spec:
                    continue
                sport, league = league_spec.split("/", 1)
                
                # Get scoreboard data
                scoreboard_data = await get_scoreboard_wrapper(sport=sport, league=league)
                
                results[league_spec] = {
                    "sport": sport,
                    "league": league,
                    "games": scoreboard_data.get("data", {}).get("scoreboard") if scoreboard_data.get("ok") else None,
                    "error": None if scoreboard_data.get("ok") else scoreboard_data.get("message")
                }
            
            return {
                "ok": True,
                "status": "success",
                "data": results
            }
        
        else:
            return {
                "ok": False,
                "message": f"Unknown endpoint: {endpoint}",
                "explanation": parsed_query.get("explanation", "")
            }
            
    except Exception as e:
        return {
            "ok": False,
            "message": f"Error executing query: {str(e)}",
            "parsed_query": parsed_query
        }

# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "sports_ai": SPORTS_AI_AVAILABLE,
            "odds": odds_server is not None,
            "openrouter": OPENROUTER_API_KEY is not None
        }
    }

# Sports AI MCP Endpoints
@app.post("/espn/scoreboard")
async def espn_scoreboard(request: ScoreboardRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get scoreboard data for a specific league"""
    if not SPORTS_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sports AI MCP not available")
    
    try:
        result = await get_scoreboard_wrapper(
            sport=request.sport,
            league=request.league,
            dates=request.dates,
            limit=request.limit,
            week=request.week,
            seasontype=request.seasontype
        )
        # Convert timestamps to Eastern time
        if result.get("ok") and "data" in result:
            result["data"] = convert_timestamps_in_data(result["data"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scoreboard: {str(e)}")

@app.post("/espn/teams")
async def espn_teams(request: TeamsRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get teams for a specific league"""
    if not SPORTS_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sports AI MCP not available")
    
    try:
        result = await get_teams_wrapper(sport=request.sport, league=request.league)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting teams: {str(e)}")

@app.post("/espn/game-summary")
async def espn_game_summary(request: GameSummaryRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get detailed game summary/boxscore"""
    if not SPORTS_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sports AI MCP not available")
    
    try:
        result = await get_game_summary_wrapper(
            sport=request.sport,
            league=request.league,
            event_id=request.event_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting game summary: {str(e)}")

@app.post("/espn/analyze-game")
async def espn_analyze_game(request: GameAnalysisRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Analyze a game using AI"""
    if not SPORTS_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sports AI MCP not available")
    
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=503, detail="OpenRouter API key required for analysis")
    
    try:
        result = await analyze_game_wrapper(
            sport=request.sport,
            league=request.league,
            event_id=request.event_id,
            question=request.question
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing game: {str(e)}")

@app.post("/espn/probe")
async def espn_probe(request: ProbeRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Probe league support capabilities"""
    if not SPORTS_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sports AI MCP not available")
    
    # For now, return a simple capability check
    return {
        "ok": True,
        "content_md": f"## Probe {request.sport}/{request.league}\\n\\nBasic support available",
        "data": {
            "capability": {
                "scoreboard": True,
                "summary": True,
                "game_player_stats": False
            }
        }
    }

# Odds API Endpoints
@app.get("/odds/sports")
async def odds_sports(all_sports: bool = False, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get available sports from odds API"""
    if not (ODDS_DIRECT_CLIENT or ODDS_MCP_SERVER):
        raise HTTPException(status_code=503, detail="Odds API not available")
    
    try:
        if ODDS_DIRECT_CLIENT:
            # Use direct client
            result = odds_client.get_sports(all_sports=all_sports)
            return result.get("data", result)  # Extract data if wrapped
        elif ODDS_MCP_SERVER and hasattr(odds_server, 'get_sports_http'):
            # Use MCP server HTTP helper
            result = await odds_server.get_sports_http(all_sports=all_sports)
            return json.loads(result)
        else:
            raise HTTPException(status_code=503, detail="No working odds implementation available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sports: {str(e)}")

@app.post("/odds/get-odds")
async def odds_get_odds(request: OddsRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get odds for a specific sport"""
    if not (ODDS_DIRECT_CLIENT or ODDS_MCP_SERVER):
        raise HTTPException(status_code=503, detail="Odds API not available")
    
    try:
        if ODDS_DIRECT_CLIENT:
            # Use direct client
            options = {}
            if request.regions:
                options["regions"] = request.regions
            if request.markets:
                options["markets"] = request.markets
            if request.odds_format:
                options["oddsFormat"] = request.odds_format
            if request.date_format:
                options["dateFormat"] = request.date_format
                
            result = odds_client.get_odds(request.sport, options=options)
            return result.get("data", result)  # Extract data if wrapped
        elif ODDS_MCP_SERVER and hasattr(odds_server, 'get_odds_http'):
            # Use MCP server HTTP helper
            result = await odds_server.get_odds_http(
                sport=request.sport,
                regions=request.regions,
                markets=request.markets,
                odds_format=request.odds_format,
                date_format=request.date_format
            )
            return json.loads(result)
        else:
            raise HTTPException(status_code=503, detail="No working odds implementation available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting odds: {str(e)}")

@app.post("/odds/event-odds")
async def odds_event_odds(request: EventOddsRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get odds for a specific event (required for player props)"""
    if not (ODDS_DIRECT_CLIENT or ODDS_MCP_SERVER):
        raise HTTPException(status_code=503, detail="Odds API not available")
    
    try:
        if ODDS_DIRECT_CLIENT:
            # Use direct client
            options = {}
            if request.regions:
                options["regions"] = request.regions
            if request.markets:
                options["markets"] = request.markets
            if request.odds_format:
                options["oddsFormat"] = request.odds_format
            if request.date_format:
                options["dateFormat"] = request.date_format
                
            result = odds_client.get_event_odds(request.sport, request.event_id, options=options)
            return result.get("data", result)  # Extract data if wrapped
        elif ODDS_MCP_SERVER and hasattr(odds_server, 'get_event_odds_http'):
            # Use MCP server HTTP helper
            result = await odds_server.get_event_odds_http(
                sport=request.sport,
                event_id=request.event_id,
                regions=request.regions,
                markets=request.markets,
                odds_format=request.odds_format,
                date_format=request.date_format
            )
            return json.loads(result)
        else:
            raise HTTPException(status_code=503, detail="No working odds implementation available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting event odds: {str(e)}")

@app.get("/odds/quota")
async def odds_quota(_: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get API quota information"""
    if not (ODDS_DIRECT_CLIENT or ODDS_MCP_SERVER):
        raise HTTPException(status_code=503, detail="Odds API not available")
    
    try:
        if ODDS_DIRECT_CLIENT:
            # Use direct client quota info
            return {
                "remaining_requests": odds_client.remaining_requests,
                "used_requests": odds_client.used_requests
            }
        elif ODDS_MCP_SERVER and hasattr(odds_server, 'get_quota_info_http'):
            # Use MCP server HTTP helper
            result = await odds_server.get_quota_info_http()
            return json.loads(result)
        else:
            raise HTTPException(status_code=503, detail="No working odds implementation available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quota: {str(e)}")

@app.post("/odds/player-props")
async def odds_player_props(request: PlayerPropsRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get player props for all games on a specific date (based on oddstest.py implementation)"""
    if not odds_server:
        raise HTTPException(status_code=503, detail="Odds MCP not available")
    
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # Timezone setup
        eastern = pytz.timezone("US/Eastern")
        utc = pytz.UTC
        
        # Parse target date
        if request.date:
            try:
                target_date_et = eastern.localize(datetime.strptime(request.date, "%Y-%m-%d"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")
        else:
            # Default to today
            target_date_et = datetime.now(eastern).replace(hour=0, minute=0, second=0, microsecond=0)
        
        next_day_et = target_date_et + timedelta(days=1)
        
        # Convert to UTC for filtering
        target_date_utc = target_date_et.astimezone(utc)
        next_day_utc = next_day_et.astimezone(utc)
        
        # Step 1: Get all games to get event IDs
        if ODDS_DIRECT_CLIENT:
            options = {
                "regions": request.regions,
                "markets": "h2h",
                "oddsFormat": request.odds_format
            }
            games_result = odds_client.get_odds(request.sport, options=options)
            games = games_result.get("data", games_result)
        elif ODDS_MCP_SERVER and hasattr(odds_server, 'get_odds_http'):
            games_result = await odds_server.get_odds_http(
                sport=request.sport,
                regions=request.regions,
                markets="h2h",
                odds_format=request.odds_format
            )
            games = json.loads(games_result)
        else:
            raise HTTPException(status_code=503, detail="No working odds implementation available")
        if not isinstance(games, list):
            return {"error": "Failed to get games list", "details": games}
        
        # Step 2: For each game on target date, get player props
        player_props_data = []
        
        for game in games:
            commence_time_str = game.get("commence_time", "")
            if not commence_time_str:
                continue
                
            # Parse commence time
            try:
                commence_time_utc = datetime.fromisoformat(commence_time_str.replace("Z", "+00:00"))
                if target_date_utc <= commence_time_utc < next_day_utc:
                    commence_time_et = commence_time_utc.astimezone(eastern)
                    event_id = game.get("id", "")
                    
                    if event_id:
                        # Get player props for this specific event
                        if ODDS_DIRECT_CLIENT:
                            event_options = {
                                "regions": request.regions,
                                "markets": request.player_markets,
                                "oddsFormat": request.odds_format
                            }
                            event_result = odds_client.get_event_odds(request.sport, event_id, options=event_options)
                            event_data = event_result.get("data", event_result)
                        elif ODDS_MCP_SERVER and hasattr(odds_server, 'get_event_odds_http'):
                            event_result = await odds_server.get_event_odds_http(
                                sport=request.sport,
                                event_id=event_id,
                                regions=request.regions,
                                markets=request.player_markets,
                                odds_format=request.odds_format
                            )
                            event_data = json.loads(event_result)
                        else:
                            continue  # Skip this game if no odds system available
                        
                        game_props = {
                            "event_id": event_id,
                            "home_team": game.get("home_team", ""),
                            "away_team": game.get("away_team", ""),
                            "commence_time_et": commence_time_et.strftime('%Y-%m-%d %I:%M %p ET'),
                            "commence_time_utc": commence_time_str,
                            "player_props": []
                        }
                        
                        # Parse player props data
                        if isinstance(event_data, dict) and event_data.get("bookmakers"):
                            for bookmaker in event_data.get("bookmakers", []):
                                bookmaker_data = {
                                    "bookmaker": bookmaker.get("title", "Unknown"),
                                    "markets": []
                                }
                                
                                for market in bookmaker.get("markets", []):
                                    market_data = {
                                        "market": market.get("key", ""),
                                        "outcomes": []
                                    }
                                    
                                    for outcome in market.get("outcomes", []):
                                        outcome_data = {
                                            "player": outcome.get('description', 'Unknown Player'),
                                            "bet_type": outcome.get('name', 'Unknown'),
                                            "price": outcome.get('price', 'N/A'),
                                            "point": outcome.get('point', '')
                                        }
                                        market_data["outcomes"].append(outcome_data)
                                    
                                    bookmaker_data["markets"].append(market_data)
                                
                                game_props["player_props"].append(bookmaker_data)
                        
                        player_props_data.append(game_props)
            except Exception as e:
                # Skip games with parsing errors
                continue
        
        return {
            "status": "success",
            "target_date": target_date_et.strftime('%Y-%m-%d'),
            "sport": request.sport,
            "player_markets": request.player_markets,
            "games_with_props": len(player_props_data),
            "data": player_props_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting player props: {str(e)}")

# High-level orchestration endpoint
@app.post("/daily-intelligence")
async def daily_intelligence(request: DailyIntelligenceRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """
    Get comprehensive daily sports intelligence for multiple leagues.
    This is the high-level endpoint that orchestrates multiple MCP calls.
    """
    if not SPORTS_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sports AI MCP not available")
    
    results = {}
    
    try:
        for league_spec in request.leagues:
            # Parse league spec (format: "sport/league" e.g., "basketball/nba")
            if "/" not in league_spec:
                raise HTTPException(status_code=400, detail=f"Invalid league format: {league_spec}. Use 'sport/league' format")
            
            sport, league = league_spec.split("/", 1)
            
            league_data = {
                "sport": sport,
                "league": league,
                "games": None,
                "teams": None,
                "odds": None,
                "error": None
            }
            
            try:
                # Get today's games
                scoreboard_result = await get_scoreboard_wrapper(
                    sport=sport,
                    league=league,
                    dates=request.date
                )
                
                if scoreboard_result.get("ok"):
                    league_data["games"] = scoreboard_result["data"]["scoreboard"]
                    
                    # Get teams
                    teams_result = await get_teams_wrapper(sport=sport, league=league)
                    if teams_result.get("ok"):
                        league_data["teams"] = teams_result["data"]["teams"]
                    
                    # Get odds if requested and available
                    if request.include_odds and (ODDS_DIRECT_CLIENT or ODDS_MCP_SERVER):
                        try:
                            # Map league to odds sport key
                            odds_sport_map = {
                                "basketball/nba": "basketball_nba",
                                "basketball/wnba": "basketball_wnba",
                                "football/nfl": "americanfootball_nfl",
                                "baseball/mlb": "baseball_mlb",
                                "hockey/nhl": "icehockey_nhl"
                            }
                            
                            odds_sport = odds_sport_map.get(league_spec)
                            if odds_sport:
                                if ODDS_DIRECT_CLIENT:
                                    options = {
                                        "regions": "us",
                                        "markets": "h2h,spreads,totals"
                                    }
                                    odds_result = odds_client.get_odds(odds_sport, options=options)
                                    league_data["odds"] = odds_result.get("data", odds_result)
                                elif ODDS_MCP_SERVER and hasattr(odds_server, 'get_odds_http'):
                                    odds_result = await odds_server.get_odds_http(
                                        sport=odds_sport,
                                        regions="us",
                                        markets="h2h,spreads,totals"
                                    )
                                    league_data["odds"] = json.loads(odds_result)
                        except Exception as e:
                            league_data["odds_error"] = str(e)
                else:
                    league_data["error"] = scoreboard_result.get("message", "Unknown error")
                    
            except Exception as e:
                league_data["error"] = str(e)
            
            results[league_spec] = league_data
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "requested_leagues": request.leagues,
            "include_odds": request.include_odds,
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting daily intelligence: {str(e)}")

# Natural Language Query Endpoint
@app.post("/ask")
async def natural_language_query(request: NaturalLanguageRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """
    Ask a natural language question about sports data.
    
    Examples:
    - "What NBA games are today?"
    - "Show me all NBA teams"
    - "Give me today's sports summary"
    - "What games are happening in the Premier League?"
    """
    
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=503, detail="OpenRouter API key required for natural language queries")
    
    try:
        # Step 1: Parse the natural language question
        success, raw_response, parsed_query = await ask_openrouter_query(request.question, request.model)
        
        if not success:
            return {
                "ok": False,
                "error": "Failed to parse question",
                "message": raw_response,
                "question": request.question
            }
        
        # Step 2: Execute the parsed query
        if "endpoint" in parsed_query:
            result = await execute_parsed_query(parsed_query)
            
            return {
                "ok": True,
                "question": request.question,
                "interpretation": parsed_query.get("explanation", ""),
                "parsed_query": parsed_query,
                "result": result,
                "model_used": request.model
            }
        else:
            # If no endpoint was identified, return the explanation
            return {
                "ok": True,
                "question": request.question,
                "explanation": parsed_query.get("explanation", raw_response),
                "model_used": request.model
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing natural language query: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    print("[INFO] Starting Sports HTTP Server...")
    print(f"[INFO] Server will run on http://{SERVER_HOST}:{SERVER_PORT}")
    print("[INFO] Authentication required - use 'Authorization: Bearer YOUR_API_KEY' header")
    print(f"[INFO] Sports AI MCP: {'Available' if SPORTS_AI_AVAILABLE else 'NOT AVAILABLE'}")
    print(f"[INFO] Odds MCP: {'Available' if odds_server else 'NOT AVAILABLE'}")
    print(f"[INFO] OpenRouter: {'Configured' if OPENROUTER_API_KEY else 'NOT CONFIGURED'}")
    print("\n[EXAMPLE] Example usage:")
    print(f'curl -H "Authorization: Bearer {SPORTS_API_KEY}" http://localhost:{SERVER_PORT}/health')
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )