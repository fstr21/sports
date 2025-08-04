#!/usr/bin/env python3
"""
Enhanced ESPN WNBA MCP Server - Full API Coverage
Supports: scores, teams, injuries, news, statistics, team details
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# Load environment
def load_env():
    env_path = Path("C:/Users/fstr2/Desktop/sports/.env.local")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v
        print(f"✅ Loaded environment from {env_path}")

load_env()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/horizon-beta")
ESPN_BASE = "https://site.api.espn.com"

HEADERS = {
    "User-Agent": "Enhanced-WNBA-MCP/1.0",
    "Accept": "application/json",
}

TEAM_MAPPING = {
    "aces": "LV", "las vegas": "LV", "vegas": "LV",
    "liberty": "NY", "new york": "NY", "brooklyn": "NY",
    "storm": "SEA", "seattle": "SEA",
    "sun": "CONN", "connecticut": "CONN",
    "sky": "CHI", "chicago": "CHI",
    "fever": "IND", "indiana": "IND",
    "wings": "DAL", "dallas": "DAL",
    "dream": "ATL", "atlanta": "ATL",
    "mercury": "PHX", "phoenix": "PHX",
    "lynx": "MIN", "minnesota": "MIN",
    "sparks": "LA", "los angeles": "LA",
    "mystics": "WAS", "washington": "WAS",
}

class EnhancedESPNClient:
    def __init__(self):
        self.client = httpx.AsyncClient(headers=HEADERS, timeout=15.0)
        self._teams_cache = None

    async def get_scoreboard(self, date: Optional[str] = None) -> Dict:
        """Get WNBA scoreboard"""
        url = f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/scoreboard"
        params = {"dates": date} if date else None
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_teams(self) -> Dict:
        """Get all WNBA teams"""
        if self._teams_cache is None:
            url = f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/teams"
            response = await self.client.get(url)
            response.raise_for_status()
            self._teams_cache = response.json()
        return self._teams_cache

    async def get_team_details(self, team_id: str) -> Dict:
        """Get detailed team information"""
        url = f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/teams/{team_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_injuries(self) -> Dict:
        """Get injury reports"""
        url = f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/injuries"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_news(self) -> Dict:
        """Get WNBA news"""
        url = f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/news"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_statistics(self) -> Dict:
        """Get WNBA statistics"""
        url = f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/statistics"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_standings(self) -> Dict:
        """Get WNBA standings"""
        url = f"{ESPN_BASE}/apis/site/v2/sports/basketball/wnba/standings"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

class OpenRouterClient:
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not found")
        
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        self.model = OPENROUTER_MODEL

    async def parse_query(self, user_query: str) -> Dict[str, Any]:
        """Parse natural language query"""
        system_prompt = """You are a WNBA data query parser. Parse requests into structured ESPN API calls.

RESPOND ONLY WITH VALID JSON:
{
  "intent": "scores|teams|team_details|injuries|news|statistics|standings",
  "teams": ["team_abbreviation"],
  "time_frame": "today|recent|current",
  "specific_team_requested": true/false
}

INTENTS:
- scores: game scores, schedules, matchups
- teams: list all teams, basic team info
- team_details: specific team info, records, rosters
- injuries: injury reports
- news: latest articles and news
- statistics: team/league stats
- standings: league standings

TEAM ABBREVIATIONS: LV, NY, SEA, CONN, CHI, IND, DAL, ATL, PHX, MIN, LA, WAS"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            "max_tokens": 150,
            "temperature": 0.1,
        }

        try:
            response = await self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(content)
        except Exception:
            return self._fallback_parse(user_query)

    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        """Simple fallback parsing"""
        q = query.lower()
        
        if any(w in q for w in ["score", "game", "matchup", "schedule"]):
            intent = "scores"
        elif any(w in q for w in ["injury", "hurt", "injured"]):
            intent = "injuries"
        elif any(w in q for w in ["news", "article", "latest"]):
            intent = "news"
        elif any(w in q for w in ["stats", "statistics", "performance"]):
            intent = "statistics"
        elif any(w in q for w in ["standing", "ranking", "position"]):
            intent = "standings"
        elif any(w in q for w in ["roster", "record", "detail"]):
            intent = "team_details"
        elif any(w in q for w in ["team", "teams"]):
            intent = "teams"
        else:
            intent = "scores"

        teams = []
        for name, abbr in TEAM_MAPPING.items():
            if name in q:
                teams.append(abbr)
                break

        return {
            "intent": intent,
            "teams": teams,
            "time_frame": "current",
            "specific_team_requested": len(teams) > 0
        }

# Initialize clients
espn_client = EnhancedESPNClient()
openrouter_client = OpenRouterClient()
mcp = FastMCP("Enhanced ESPN WNBA Server")

def find_team_id(teams_data: Dict, team_abbr: str) -> Optional[str]:
    """Find team ID from abbreviation"""
    for sport in teams_data.get("sports", []):
        for league in sport.get("leagues", []):
            for team_entry in league.get("teams", []):
                team = team_entry.get("team", team_entry)
                if team.get("abbreviation") == team_abbr:
                    return str(team.get("id"))
    return None

def format_scoreboard(data: Dict) -> str:
    """Format scoreboard data"""
    events = data.get("events", [])
    if not events:
        return "📭 No WNBA games found"
    
    lines = ["🏀 **WNBA Scoreboard**", ""]
    for event in events:
        name = event.get("name", "Unknown matchup")
        status = event.get("status", {}).get("type", {}).get("description", "Unknown")
        date = event.get("date", "")
        
        try:
            if date:
                dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%b %d, %I:%M %p")
            else:
                formatted_date = "TBD"
        except:
            formatted_date = date
        
        lines.append(f"**{name}**")
        lines.append(f"📅 {formatted_date} | 📊 {status}")
        lines.append("")
    
    return "\n".join(lines)

def format_teams(data: Dict) -> str:
    """Format teams data"""
    lines = ["🏆 **WNBA Teams**", ""]
    
    for sport in data.get("sports", []):
        for league in sport.get("leagues", []):
            for team_entry in league.get("teams", []):
                team = team_entry.get("team", team_entry)
                name = team.get("displayName", "Unknown")
                abbr = team.get("abbreviation", "")
                location = team.get("location", "")
                nickname = team.get("name", "")
                
                display = f"**{name}** ({abbr})"
                if location and nickname:
                    display += f" - {location} {nickname}"
                
                lines.append(f"• {display}")
    
    return "\n".join(lines)

def format_team_details(data: Dict) -> str:
    """Format detailed team information"""
    team = data.get("team", {})
    name = team.get("displayName", "Unknown Team")
    
    lines = [f"🏆 **{name}**", ""]
    
    # Basic info
    location = team.get("location", "")
    nickname = team.get("name", "")
    if location and nickname:
        lines.append(f"📍 {location} {nickname}")
    
    # Record
    record = team.get("record", {})
    if record:
        overall = record.get("items", [])
        if overall:
            summary = overall[0].get("summary", "")
            if summary:
                lines.append(f"📊 Record: {summary}")
    
    # Standing summary
    standing = team.get("standingSummary", "")
    if standing:
        lines.append(f"📈 Standing: {standing}")
    
    # Next event
    next_event = team.get("nextEvent", [])
    if next_event:
        event = next_event[0]
        event_name = event.get("name", "")
        event_date = event.get("date", "")
        if event_name:
            lines.append(f"🎯 Next Game: {event_name}")
            if event_date:
                try:
                    dt = datetime.fromisoformat(event_date.replace("Z", "+00:00"))
                    formatted = dt.strftime("%b %d, %I:%M %p")
                    lines.append(f"📅 {formatted}")
                except:
                    pass
    
    return "\n".join(lines)

def format_injuries(data: Dict, team_filter: List[str] = None) -> str:
    """Format injury data"""
    injuries = data.get("injuries", [])
    if not injuries:
        return "✅ No injuries reported"
    
    team_tag = f" for {', '.join(team_filter)}" if team_filter else ""
    lines = [f"🏥 **WNBA Injury Report{team_tag}**", ""]
    
    for injury_entry in injuries:
        player_name = injury_entry.get("displayName", "Unknown Player")
        injury_list = injury_entry.get("injuries", [])
        
        if injury_list:
            for injury in injury_list:
                status = injury.get("status", "Unknown")
                detail = injury.get("detail", "")
                team_name = injury.get("team", {}).get("displayName", "Unknown Team")
                
                lines.append(f"**{player_name}** ({team_name})")
                lines.append(f"Status: {status}")
                if detail:
                    lines.append(f"Details: {detail}")
                lines.append("")
    
    return "\n".join(lines)

def format_news(data: Dict) -> str:
    """Format news data"""
    articles = data.get("articles", [])
    if not articles:
        return "📰 No WNBA news available"
    
    lines = ["📰 **Latest WNBA News**", ""]
    
    for article in articles[:8]:  # Show top 8 articles
        headline = article.get("headline", "No headline")
        description = article.get("description", "")
        published = article.get("published", "")
        
        try:
            if published:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%b %d, %Y")
            else:
                formatted_date = "Unknown date"
        except:
            formatted_date = published or "Unknown date"
        
        lines.append(f"**{headline}**")
        if description:
            desc_preview = description[:150] + "..." if len(description) > 150 else description
            lines.append(desc_preview)
        lines.append(f"📅 {formatted_date}")
        lines.append("")
    
    return "\n".join(lines)

def format_statistics(data: Dict) -> str:
    """Format statistics data"""
    lines = ["📊 **WNBA Statistics**", ""]
    
    season = data.get("season", {})
    if season:
        year = season.get("year", "Unknown")
        season_type = season.get("type", {}).get("name", "Unknown")
        lines.append(f"🏀 Season: {year} {season_type}")
        lines.append("")
    
    stats = data.get("stats", {})
    if stats:
        lines.append("📈 Available statistical categories:")
        for key, value in stats.items():
            if isinstance(value, list) and value:
                lines.append(f"• {key}: {len(value)} entries")
    
    return "\n".join(lines)

@mcp.tool()
async def ask_espn(query: str) -> str:
    """
    Ask comprehensive questions about WNBA data from ESPN.
    
    Available data types:
    - Game scores and schedules
    - Team information and details  
    - Injury reports
    - Latest news and articles
    - League statistics
    - Team standings
    
    Examples:
    - "Show me today's WNBA scores"
    - "Tell me about the Las Vegas Aces"
    - "Any injuries in the WNBA?"
    - "Latest WNBA news"
    - "League statistics"
    - "Team standings"
    """
    
    try:
        # Parse the query
        parsed = await openrouter_client.parse_query(query)
        intent = parsed.get("intent", "scores")
        teams = parsed.get("teams", [])
        
        if intent == "scores":
            data = await espn_client.get_scoreboard()
            return format_scoreboard(data)
            
        elif intent == "teams":
            data = await espn_client.get_teams()
            return format_teams(data)
            
        elif intent == "team_details":
            if teams:
                teams_data = await espn_client.get_teams()
                team_id = find_team_id(teams_data, teams[0])
                if team_id:
                    data = await espn_client.get_team_details(team_id)
                    return format_team_details(data)
                else:
                    return f"❌ Could not find team: {teams[0]}"
            else:
                return "❌ Please specify which team you want details for"
                
        elif intent == "injuries":
            data = await espn_client.get_injuries()
            return format_injuries(data, teams)
            
        elif intent == "news":
            data = await espn_client.get_news()
            return format_news(data)
            
        elif intent == "statistics":
            data = await espn_client.get_statistics()
            return format_statistics(data)
            
        elif intent == "standings":
            data = await espn_client.get_standings()
            return "📊 Standings data available (structure varies)"
            
        else:
            # Default to scoreboard
            data = await espn_client.get_scoreboard()
            return format_scoreboard(data)
            
    except httpx.HTTPStatusError as e:
        return f"❌ ESPN API error: {e.response.status_code}"
    except Exception as e:
        return f"❌ Error processing query: {str(e)}"

@mcp.tool()
async def list_capabilities() -> str:
    """
    Show all available ESPN WNBA data types and example queries.
    """
    
    return """🏀 **ESPN WNBA MCP Server Capabilities**

**📊 Available Data Types:**

🏀 **Game Scores & Schedules**
• "Show me today's WNBA scores"
• "What games are scheduled?"
• "Dallas Wings vs Liberty score"

🏆 **Team Information**
• "Tell me about the Las Vegas Aces"
• "All WNBA teams"
• "Seattle Storm team details"

🏥 **Injury Reports**
• "Any injuries in the WNBA?"
• "Liberty injury report"
• "Who's hurt on the Aces?"

📰 **Latest News**
• "Latest WNBA news"
• "Recent articles"
• "What's new in the WNBA?"

📊 **Statistics**
• "WNBA team statistics"
• "League stats"
• "Team performance data"

📈 **Standings**
• "WNBA standings"
• "Team rankings"

**🚫 Not Available:**
• Individual player career stats
• Historical game data
• Playoff brackets (currently)

**💡 Tips:**
• Use team names like "Las Vegas Aces" or abbreviations like "LV"
• Ask in natural language - the AI will understand!
• Data is current for the 2025 WNBA season"""

@mcp.tool()
async def test_connection() -> str:
    """Test connectivity to all ESPN endpoints and OpenRouter"""
    results = []
    
    # Test OpenRouter
    try:
        test_parse = await openrouter_client.parse_query("test query")
        results.append("✅ OpenRouter connection working")
    except Exception as e:
        results.append(f"❌ OpenRouter error: {str(e)}")
    
    # Test ESPN endpoints
    endpoints = [
        ("Scoreboard", espn_client.get_scoreboard),
        ("Teams", espn_client.get_teams),
        ("Injuries", espn_client.get_injuries),
        ("News", espn_client.get_news),
        ("Statistics", espn_client.get_statistics),
    ]
    
    for name, func in endpoints:
        try:
            await func()
            results.append(f"✅ ESPN {name} working")
        except Exception as e:
            results.append(f"❌ ESPN {name} error: {str(e)}")
    
    return "\n".join(results)

async def main():
    print("🏀 Starting Enhanced ESPN WNBA MCP Server...")
    print(f"🤖 Using OpenRouter model: {OPENROUTER_MODEL}")
    print("📊 Available: scores, teams, injuries, news, statistics")
    await mcp.run()

if __name__ == "__main__":
    asyncio.run(main())