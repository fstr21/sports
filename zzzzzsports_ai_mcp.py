import asyncio
import os
import re
import traceback
from typing import Any, Dict, Optional
from datetime import datetime, timezone, timedelta
import zoneinfo

import httpx
from mcp.server import FastMCP

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# Proper Eastern timezone handling
try:
    EASTERN_TZ = zoneinfo.ZoneInfo("America/New_York")
except Exception:
    # Fallback for systems without zoneinfo
    import pytz
    EASTERN_TZ = pytz.timezone("America/New_York")

ESPN_BASE_URL = "http://site.api.espn.com/apis/site/v2/sports"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/horizon-beta")

date_re = re.compile(r"^\d{8}$")

server = FastMCP("sports-ai-analyzer")

async def fetch_espn_data(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Fetch data from ESPN API with comprehensive error handling"""
    url = f"{ESPN_BASE_URL}{endpoint}"
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{query_string}"
    
    print(f"[INFO] Fetching ESPN data from: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers={
                "user-agent": "sports-ai-analyzer/1.0",
                "accept": "application/json"
            })
            
            print(f"[INFO] ESPN API response status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"ESPN API error: HTTP {response.status_code}"
                try:
                    error_body = response.text
                    print(f"[ERROR] ESPN API error body: {error_body}")
                    error_msg += f" - {error_body}"
                except:
                    pass
                raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
            
            try:
                data = response.json()
                print(f"[INFO] Successfully parsed JSON response")
                return data
            except Exception as json_error:
                print(f"[ERROR] Failed to parse JSON response: {str(json_error)}")
                print(f"[ERROR] Response text: {response.text[:500]}...")
                raise ValueError(f"Invalid JSON response from ESPN API: {str(json_error)}")
                
    except httpx.TimeoutException as e:
        error_msg = f"ESPN API timeout after 15 seconds: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise TimeoutError(error_msg)
    except httpx.NetworkError as e:
        error_msg = f"ESPN API network error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise ConnectionError(error_msg)
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] ESPN API HTTP error: {str(e)}")
        raise
    except Exception as e:
        error_msg = f"Unexpected error fetching ESPN data: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise RuntimeError(error_msg)

async def analyze_with_openrouter(data: str, analysis_prompt: str) -> str:
    """Send data to OpenRouter for AI analysis with comprehensive error handling"""
    if not OPENROUTER_API_KEY:
        error_msg = "OpenRouter API key not configured - check OPENROUTER_API_KEY in .env.local"
        print(f"[ERROR] {error_msg}")
        return f"❌ {error_msg}"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a sports analytics expert. Analyze the provided sports data and give insightful, actionable analysis."
            },
            {
                "role": "user", 
                "content": f"{analysis_prompt}\n\nData to analyze:\n{data}"
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    print(f"[INFO] Sending request to OpenRouter with model: {OPENROUTER_MODEL}")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            print(f"[INFO] OpenRouter response status: {response.status_code}")
            
            if response.status_code == 401:
                error_msg = "OpenRouter API key is invalid or expired"
                print(f"[ERROR] {error_msg}")
                return f"❌ {error_msg}"
            elif response.status_code == 429:
                error_msg = "OpenRouter rate limit exceeded - try again later"
                print(f"[ERROR] {error_msg}")
                return f"❌ {error_msg}"
            elif response.status_code != 200:
                error_body = response.text
                error_msg = f"OpenRouter API error: HTTP {response.status_code} - {error_body}"
                print(f"[ERROR] {error_msg}")
                return f"❌ {error_msg}"
            
            try:
                result = response.json()
                if "choices" not in result or not result["choices"]:
                    error_msg = "OpenRouter returned empty response"
                    print(f"[ERROR] {error_msg}")
                    print(f"[ERROR] Full response: {result}")
                    return f"❌ {error_msg}"
                
                analysis = result["choices"][0]["message"]["content"]
                print(f"[INFO] Successfully received AI analysis ({len(analysis)} characters)")
                return analysis
                
            except Exception as json_error:
                error_msg = f"Failed to parse OpenRouter JSON response: {str(json_error)}"
                print(f"[ERROR] {error_msg}")
                print(f"[ERROR] Response text: {response.text[:500]}...")
                return f"❌ {error_msg}"
                
    except httpx.TimeoutException as e:
        error_msg = f"OpenRouter API timeout after 30 seconds: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return f"❌ {error_msg}"
    except httpx.NetworkError as e:
        error_msg = f"OpenRouter API network error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error with OpenRouter API: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return f"❌ {error_msg}"

@server.tool(
    name="analyzeWnbaGames",
    description="Fetch WNBA games and provide AI-powered analysis and insights"
)
async def analyze_wnba_games(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch WNBA scoreboard and analyze with AI"""
    args = args or {}
    dates = args.get("dates")
    limit = args.get("limit")
    analysis_type = args.get("analysis_type", "general")
    
    # Build ESPN API parameters
    params = {}
    
    # Force Eastern timezone date handling
    if dates:
        if not isinstance(dates, str) or not date_re.match(dates):
            raise ValueError("dates must be a string in YYYYMMDD format")
        params["dates"] = dates
    else:
        # Default to current date in Eastern timezone
        try:
            eastern_now = datetime.now(EASTERN_TZ)
            current_date = eastern_now.strftime("%Y%m%d")
            params["dates"] = current_date
            print(f"[INFO] Using Eastern timezone date: {current_date} (Eastern time: {eastern_now.strftime('%Y-%m-%d %H:%M:%S %Z')})")
        except Exception as tz_error:
            # Fallback to UTC if timezone fails
            utc_now = datetime.now(timezone.utc)
            current_date = utc_now.strftime("%Y%m%d")
            params["dates"] = current_date
            print(f"[WARNING] Timezone error, using UTC date: {current_date} - Error: {str(tz_error)}")
    
    if limit:
        try:
            n = float(limit)
            if not (n > 0 and n == int(n)):
                raise ValueError("limit must be a positive integer")
            params["limit"] = int(n)
        except Exception:
            raise ValueError("limit must be a number")
    
    # Fetch WNBA data with error handling
    print(f"[INFO] Calling ESPN API with params: {params}")
    try:
        espn_data = await fetch_espn_data("/basketball/wnba/scoreboard", params)
        events_count = len(espn_data.get('events', []))
        print(f"[INFO] ESPN API returned {events_count} events")
        
        if events_count == 0:
            print(f"[WARNING] No WNBA games found for the requested date/parameters")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"## WNBA Games Analysis\n\n❌ No WNBA games found for the requested parameters.\n\n**Parameters used:** {params}\n\n**Suggestion:** Try a different date or check if WNBA is in season."
                    }
                ]
            }
    except Exception as api_error:
        error_msg = f"Failed to fetch WNBA data: {str(api_error)}"
        print(f"[ERROR] {error_msg}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## WNBA Games Analysis - Error\n\n❌ {error_msg}\n\n**Parameters attempted:** {params}\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
                }
            ]
        }
    
    # Create analysis prompt based on type
    analysis_prompts = {
        "general": "Provide a general analysis of these WNBA games including key matchups, standout performances, and notable trends. When discussing players, use SPECIFIC PLAYER NAMES from the roster data provided, not generic descriptions.",
        "betting": "Analyze these WNBA games from a betting perspective. Look for value bets, upset potential, and key factors that could influence outcomes. Use specific player names when making predictions.",
        "performance": "Focus on individual and team performance metrics. Highlight standout players by NAME, team strengths/weaknesses, and statistical trends.",
        "predictions": "Based on the current data, provide predictions for upcoming games and identify which teams are trending up or down. Use specific player names for scoring and rebounding predictions."
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
    
    # Convert data to readable format for AI analysis
    games_summary = []
    try:
        if "events" in espn_data:
            print(f"[INFO] Processing {len(espn_data['events'])} events from ESPN")
            for i, event in enumerate(espn_data["events"][:5]):  # Limit to 5 games for analysis
                game_info = {
                    "matchup": event.get("name", "Unknown matchup"),
                    "date": event.get("date", "Unknown date"),
                    "competitors": []
                }
            
                print(f"[INFO] Event {i+1}: {game_info['matchup']} on {game_info['date']}")
                
                if "competitions" in event and event["competitions"]:
                    comp = event["competitions"][0]
                    if "competitors" in comp:
                        for competitor in comp["competitors"]:
                            team_info = {
                                "team": competitor["team"]["displayName"],
                                "team_id": competitor["team"].get("id"),
                                "abbreviation": competitor["team"].get("abbreviation"),
                                "score": competitor.get("score", "0"),
                                "record": competitor.get("records", [{}])[0].get("summary", "Unknown"),
                                "leaders": {}
                            }
                        
                            # Extract player leaders
                            if "leaders" in competitor:
                                for leader_category in competitor["leaders"]:
                                    category_name = leader_category.get("name", "unknown")
                                    category_leaders = []
                                    
                                    for leader in leader_category.get("leaders", []):
                                        if "athlete" in leader:
                                            athlete = leader["athlete"]
                                            leader_info = {
                                                "name": athlete.get("fullName", "Unknown"),
                                                "value": leader.get("displayValue", "N/A")
                                            }
                                            category_leaders.append(leader_info)
                                    
                                    if category_leaders:
                                        team_info["leaders"][category_name] = category_leaders
                            
                            game_info["competitors"].append(team_info)
                
                games_summary.append(game_info)
                
            print(f"[INFO] Successfully extracted data for {len(games_summary)} games")
                            
        else:
            print("[WARNING] No 'events' key found in ESPN data")
            
    except Exception as processing_error:
        error_msg = f"Error processing ESPN data: {str(processing_error)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## WNBA Games Analysis - Processing Error\n\n❌ {error_msg}\n\n**Raw ESPN Data (first 1000 chars):**\n```\n{str(espn_data)[:1000]}...\n```\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
                }
            ]
        }
    
    # Analyze with OpenRouter
    try:
        data_for_analysis = str(games_summary)
        print(f"[INFO] Sending {len(data_for_analysis)} characters to AI for analysis")
        ai_analysis = await analyze_with_openrouter(data_for_analysis, prompt)
    except Exception as ai_error:
        error_msg = f"Error during AI analysis: {str(ai_error)}"
        print(f"[ERROR] {error_msg}")
        ai_analysis = f"❌ AI analysis failed: {error_msg}"
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"## WNBA Games Analysis ({analysis_type.title()})\n\n{ai_analysis}\n\n---\n\n**Raw Data Summary:**\n{data_for_analysis}"
            }
        ]
    }

@server.tool(
    name="analyzeNflGames", 
    description="Fetch NFL games and provide AI-powered analysis and insights"
)
async def analyze_nfl_games(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch NFL scoreboard and analyze with AI"""
    args = args or {}
    analysis_type = args.get("analysis_type", "general")
    week = args.get("week")
    
    # Build ESPN API parameters
    params = {}
    if week:
        params["week"] = week
    
    # Fetch NFL data with error handling
    try:
        espn_data = await fetch_espn_data("/football/nfl/scoreboard", params)
        events_count = len(espn_data.get('events', []))
        print(f"[INFO] ESPN API returned {events_count} NFL events")
        
        if events_count == 0:
            print(f"[WARNING] No NFL games found for the requested parameters")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"## NFL Games Analysis\n\n❌ No NFL games found for the requested parameters.\n\n**Parameters used:** {params}\n\n**Suggestion:** Try specifying a different week or check if NFL is in season."
                    }
                ]
            }
    except Exception as api_error:
        error_msg = f"Failed to fetch NFL data: {str(api_error)}"
        print(f"[ERROR] {error_msg}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## NFL Games Analysis - Error\n\n❌ {error_msg}\n\n**Parameters attempted:** {params}\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
                }
            ]
        }
    
    # Analysis prompts
    analysis_prompts = {
        "general": "Provide a general analysis of these NFL games including key matchups, standout performances, and notable trends.",
        "betting": "Analyze these NFL games from a betting perspective. Look for value bets, upset potential, spread analysis, and key factors.",
        "fantasy": "Focus on fantasy football implications. Highlight players to start/sit, breakout candidates, and matchup advantages.",
        "predictions": "Based on current data and trends, provide predictions for upcoming games and identify which teams are hot or cold."
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
    
    # Convert data to readable format with error handling
    games_summary = []
    try:
        if "events" in espn_data:
            for event in espn_data["events"][:5]:  # Limit for analysis
                game_info = {
                    "matchup": event.get("name", "Unknown matchup"),
                    "date": event.get("date", "Unknown date"),
                    "week": event.get("week", {}).get("number", "Unknown"),
                    "competitors": []
                }
                
                if "competitions" in event and event["competitions"]:
                    comp = event["competitions"][0]
                    if "competitors" in comp:
                        for competitor in comp["competitors"]:
                            team_info = {
                                "team": competitor["team"]["displayName"],
                                "score": competitor.get("score", "0"),
                                "record": competitor.get("records", [{}])[0].get("summary", "Unknown")
                            }
                            game_info["competitors"].append(team_info)
                
                games_summary.append(game_info)
                
        print(f"[INFO] Successfully processed {len(games_summary)} NFL games")
        
    except Exception as processing_error:
        error_msg = f"Error processing NFL data: {str(processing_error)}"
        print(f"[ERROR] {error_msg}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## NFL Games Analysis - Processing Error\n\n❌ {error_msg}\n\n**Raw ESPN Data (first 1000 chars):**\n```\n{str(espn_data)[:1000]}...\n```\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
                }
            ]
        }
    
    # Analyze with OpenRouter
    try:
        data_for_analysis = str(games_summary)
        print(f"[INFO] Sending {len(data_for_analysis)} characters to AI for NFL analysis")
        ai_analysis = await analyze_with_openrouter(data_for_analysis, prompt)
    except Exception as ai_error:
        error_msg = f"Error during NFL AI analysis: {str(ai_error)}"
        print(f"[ERROR] {error_msg}")
        ai_analysis = f"❌ AI analysis failed: {error_msg}"
    
    return {
        "content": [
            {
                "type": "text", 
                "text": f"## NFL Games Analysis ({analysis_type.title()})\n\n{ai_analysis}\n\n---\n\n**Raw Data Summary:**\n{data_for_analysis}"
            }
        ]
    }

@server.tool(
    name="customSportsAnalysis",
    description="Fetch any sports data and analyze it with custom prompts using AI"
)
async def custom_sports_analysis(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch custom sports data and analyze with user-defined prompts"""
    args = args or {}
    sport = args.get("sport", "basketball")  # basketball, football, etc.
    league = args.get("league", "wnba")      # wnba, nfl, nba, etc.
    endpoint = args.get("endpoint", "scoreboard")  # scoreboard, standings, etc.
    custom_prompt = args.get("prompt", "Analyze this sports data and provide insights")
    
    # Build endpoint URL
    api_endpoint = f"/{sport}/{league}/{endpoint}"
    print(f"[INFO] Custom analysis endpoint: {api_endpoint}")
    
    # Fetch data with error handling
    try:
        espn_data = await fetch_espn_data(api_endpoint)
        print(f"[INFO] Successfully fetched custom sports data")
    except Exception as api_error:
        error_msg = f"Failed to fetch custom sports data from {api_endpoint}: {str(api_error)}"
        print(f"[ERROR] {error_msg}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## Custom Sports Analysis - API Error\n\n❌ {error_msg}\n\n**Endpoint attempted:** {api_endpoint}\n\n**Parameters:** sport={sport}, league={league}, endpoint={endpoint}\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
                }
            ]
        }
    
    # Analyze with custom prompt and better data handling
    try:
        # Smart data limiting instead of arbitrary truncation
        if isinstance(espn_data, dict):
            # Keep important keys, limit others
            important_keys = ['events', 'standings', 'teams', 'athletes']
            filtered_data = {}
            for key in important_keys:
                if key in espn_data:
                    filtered_data[key] = espn_data[key]
            
            if not filtered_data:
                # If no important keys found, use first 3000 chars as fallback
                data_for_analysis = str(espn_data)[:3000]
            else:
                data_for_analysis = str(filtered_data)
        else:
            data_for_analysis = str(espn_data)[:3000]
            
        print(f"[INFO] Sending {len(data_for_analysis)} characters for custom analysis")
        ai_analysis = await analyze_with_openrouter(data_for_analysis, custom_prompt)
        
    except Exception as ai_error:
        error_msg = f"Error during custom AI analysis: {str(ai_error)}"
        print(f"[ERROR] {error_msg}")
        ai_analysis = f"❌ Custom AI analysis failed: {error_msg}"
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"## Custom Sports Analysis\n\n**Query:** {sport}/{league}/{endpoint}\n**Prompt:** {custom_prompt}\n\n**Analysis:**\n{ai_analysis}"
            }
        ]
    }

async def amain():
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(amain())