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
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[INFO] Loaded environment variables from .env file")
except ImportError:
    print("[WARNING] python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"[WARNING] Could not load .env file: {e}")

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
    from sports_mcp.wagyu_sports.mcp_server.odds_client_server import OddsMcpServer
    ODDS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Wagyu Odds MCP: {e}")
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
if ODDS_AVAILABLE and ODDS_API_KEY:
    try:
        odds_server = OddsMcpServer(api_key=ODDS_API_KEY, test_mode=False)
        print("[OK] Odds MCP initialized with API key")
    except Exception as e:
        print(f"[WARNING] Odds MCP initialization failed: {e}")
        odds_server = None
elif ODDS_AVAILABLE:
    try:
        odds_server = OddsMcpServer(test_mode=True)
        print("[WARNING] Odds MCP initialized in TEST MODE (no API key)")
    except Exception as e:
        print(f"[ERROR] Odds MCP failed to initialize even in test mode: {e}")
        odds_server = None

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

class DailyIntelligenceRequest(BaseModel):
    leagues: List[str]
    include_odds: bool = True
    include_analysis: bool = False
    date: Optional[str] = None

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
    if not odds_server:
        raise HTTPException(status_code=503, detail="Odds MCP not available")
    
    try:
        # Call the odds server method directly
        result = await odds_server.server._tools["get_sports"].handler(all_sports=all_sports)
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sports: {str(e)}")

@app.post("/odds/get-odds")
async def odds_get_odds(request: OddsRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get odds for a specific sport"""
    if not odds_server:
        raise HTTPException(status_code=503, detail="Odds MCP not available")
    
    try:
        result = await odds_server.server._tools["get_odds"].handler(
            sport=request.sport,
            regions=request.regions,
            markets=request.markets,
            odds_format=request.odds_format,
            date_format=request.date_format
        )
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting odds: {str(e)}")

@app.post("/odds/event-odds")
async def odds_event_odds(request: EventOddsRequest, _: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get odds for a specific event (required for player props)"""
    if not odds_server:
        raise HTTPException(status_code=503, detail="Odds MCP not available")
    
    try:
        result = await odds_server.server._tools["get_event_odds"].handler(
            sport=request.sport,
            event_id=request.event_id,
            regions=request.regions,
            markets=request.markets,
            odds_format=request.odds_format,
            date_format=request.date_format
        )
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting event odds: {str(e)}")

@app.get("/odds/quota")
async def odds_quota(_: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get API quota information"""
    if not odds_server:
        raise HTTPException(status_code=503, detail="Odds MCP not available")
    
    try:
        result = await odds_server.server._tools["get_quota_info"].handler()
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quota: {str(e)}")

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
                    if request.include_odds and odds_server:
                        try:
                            # Map league to odds sport key
                            odds_sport_map = {
                                "basketball/nba": "basketball_nba",
                                "football/nfl": "americanfootball_nfl",
                                "baseball/mlb": "baseball_mlb",
                                "hockey/nhl": "icehockey_nhl"
                            }
                            
                            odds_sport = odds_sport_map.get(league_spec)
                            if odds_sport:
                                odds_result = await odds_server.server._tools["get_odds"].handler(
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