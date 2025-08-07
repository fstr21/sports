import asyncio
import os
import re
from typing import Any, Dict, Optional

import httpx
from mcp.server import FastMCP

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

ESPN_BASE_URL = "http://site.api.espn.com/apis/site/v2/sports"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/horizon-beta")

date_re = re.compile(r"^\d{8}$")

server = FastMCP("sports-ai-analyzer")

async def fetch_espn_data(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Fetch data from ESPN API"""
    url = f"{ESPN_BASE_URL}{endpoint}"
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{query_string}"
    
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers={
            "user-agent": "sports-ai-analyzer/1.0",
            "accept": "application/json"
        })
        response.raise_for_status()
        return response.json()

async def analyze_with_openrouter(data: str, analysis_prompt: str) -> str:
    """Send data to OpenRouter for AI analysis"""
    if not OPENROUTER_API_KEY:
        return "OpenRouter API key not configured"
    
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
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

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
    if dates:
        if not isinstance(dates, str) or not date_re.match(dates):
            raise ValueError("dates must be a string in YYYYMMDD format")
        params["dates"] = dates
    
    if limit:
        try:
            n = float(limit)
            if not (n > 0 and n == int(n)):
                raise ValueError("limit must be a positive integer")
            params["limit"] = int(n)
        except Exception:
            raise ValueError("limit must be a number")
    
    # Fetch WNBA data
    espn_data = await fetch_espn_data("/basketball/wnba/scoreboard", params)
    
    # Create analysis prompt based on type
    analysis_prompts = {
        "general": "Provide a general analysis of these WNBA games including key matchups, standout performances, and notable trends.",
        "betting": "Analyze these WNBA games from a betting perspective. Look for value bets, upset potential, and key factors that could influence outcomes.",
        "performance": "Focus on individual and team performance metrics. Highlight standout players, team strengths/weaknesses, and statistical trends.",
        "predictions": "Based on the current data, provide predictions for upcoming games and identify which teams are trending up or down."
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
    
    # Convert data to readable format for AI analysis
    games_summary = []
    if "events" in espn_data:
        for event in espn_data["events"][:5]:  # Limit to 5 games for analysis
            game_info = {
                "matchup": event.get("name", "Unknown matchup"),
                "date": event.get("date", "Unknown date"),
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
    
    # Analyze with OpenRouter
    data_for_analysis = str(games_summary)
    ai_analysis = await analyze_with_openrouter(data_for_analysis, prompt)
    
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
    
    # Fetch NFL data
    espn_data = await fetch_espn_data("/football/nfl/scoreboard", params)
    
    # Analysis prompts
    analysis_prompts = {
        "general": "Provide a general analysis of these NFL games including key matchups, standout performances, and notable trends.",
        "betting": "Analyze these NFL games from a betting perspective. Look for value bets, upset potential, spread analysis, and key factors.",
        "fantasy": "Focus on fantasy football implications. Highlight players to start/sit, breakout candidates, and matchup advantages.",
        "predictions": "Based on current data and trends, provide predictions for upcoming games and identify which teams are hot or cold."
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
    
    # Convert data to readable format
    games_summary = []
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
    
    # Analyze with OpenRouter
    data_for_analysis = str(games_summary)
    ai_analysis = await analyze_with_openrouter(data_for_analysis, prompt)
    
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
    
    # Fetch data
    espn_data = await fetch_espn_data(api_endpoint)
    
    # Analyze with custom prompt
    data_for_analysis = str(espn_data)[:3000]  # Limit data size
    ai_analysis = await analyze_with_openrouter(data_for_analysis, custom_prompt)
    
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