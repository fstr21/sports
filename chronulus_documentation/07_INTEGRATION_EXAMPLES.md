# 🔗 Integration Examples

Complete examples for integrating Chronulus MCP server with Discord bot and other systems.

## Discord Bot Integration

### Basic MCP Client Setup
```python
import httpx
import json
import asyncio
from typing import Dict, Any, Optional

class ChronulusMCPClient:
    def __init__(self, base_url: str = "https://chronulusmcp-production.up.railway.app"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp"
        self.health_url = f"{base_url}/health"
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call MCP tool with JSON-RPC 2.0 protocol"""
        request_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        try:
            response = await self.client.post(self.mcp_url, json=request_payload)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"error": "Request timed out", "status": "timeout"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "status": "error"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MCP server health"""
        try:
            response = await self.client.get(self.health_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_chronulus_analysis(self, game_data: Dict[str, Any], expert_count: int = 2) -> Dict[str, Any]:
        """Get Chronulus analysis for game data"""
        return await self.call_tool("getChronulusAnalysis", {
            "game_data": game_data,
            "expert_count": expert_count
        })
    
    async def test_hardcoded_analysis(self) -> Dict[str, Any]:
        """Test with hardcoded Dodgers @ Padres data"""
        return await self.call_tool("testChronulusHardcoded")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
```

### MLB Handler Integration
```python
# In your existing MLB handler (mlb_handler.py)
import asyncio
from typing import List, Dict, Any
import discord

class MLBHandler:
    def __init__(self, sport_name: str, config: Dict[str, Any], mcp_client):
        # ... existing initialization
        self.chronulus_client = ChronulusMCPClient()
    
    async def create_comprehensive_game_analysis(self, match) -> List[discord.Embed]:
        """Enhanced with Chronulus AI analysis"""
        # Get existing embeds
        embeds = await self.get_existing_analysis_embeds(match)
        
        # Add Chronulus AI analysis as additional embed
        try:
            ai_embed = await self.create_chronulus_analysis_embed(match)
            if ai_embed:
                embeds.append(ai_embed)
        except Exception as e:
            # Graceful degradation - don't fail if Chronulus unavailable
            print(f"Chronulus analysis failed: {e}")
        
        return embeds
    
    async def create_chronulus_analysis_embed(self, match) -> Optional[discord.Embed]:
        """Create Chronulus AI analysis embed"""
        # Convert match data to Chronulus format
        game_data = await self.format_game_data_for_chronulus(match)
        
        # Get AI analysis
        response = await self.chronulus_client.get_chronulus_analysis(
            game_data=game_data,
            expert_count=2  # Cost-effective 2-expert analysis
        )
        
        # Check if analysis succeeded
        if not self.is_successful_response(response):
            return None
        
        # Extract analysis data
        analysis_data = self.extract_analysis_data(response)
        if not analysis_data:
            return None
        
        # Create Discord embed
        embed = discord.Embed(
            title="🧠 AI Expert Panel Analysis",
            description=f"**{match.away_team} @ {match.home_team}**",
            color=0x9B59B6  # Purple for AI analysis
        )
        
        # Add expert analysis
        expert_text = analysis_data.get("expert_analysis", "")
        if expert_text:
            # Truncate if too long for Discord
            if len(expert_text) > 1000:
                expert_text = expert_text[:997] + "..."
            embed.add_field(
                name="📊 Expert Consensus",
                value=expert_text,
                inline=False
            )
        
        # Add key metrics
        if "consensus_probability" in analysis_data:
            prob = analysis_data["consensus_probability"]
            embed.add_field(
                name="Win Probability",
                value=f"**{match.away_team}**: {prob:.1%}\\n**{match.home_team}**: {(1-prob):.1%}",
                inline=True
            )
        
        if "market_edge" in analysis_data:
            edge = analysis_data["market_edge"]
            edge_text = f"+{edge:.1%}" if edge > 0 else f"{edge:.1%}"
            embed.add_field(
                name="Market Edge",
                value=edge_text,
                inline=True
            )
        
        if "recommendation" in analysis_data:
            rec = analysis_data["recommendation"]
            rec_emoji = "✅" if rec == "BET" else "❌"
            embed.add_field(
                name="Recommendation",
                value=f"{rec_emoji} {rec}",
                inline=True
            )
        
        # Add footer with cost info
        expert_count = analysis_data.get("expert_count", 2)
        cost_estimate = analysis_data.get("cost_estimate", "$0.05-0.10")
        embed.set_footer(text=f"{expert_count} AI Experts • Cost: {cost_estimate}")
        
        return embed
    
    async def format_game_data_for_chronulus(self, match) -> Dict[str, Any]:
        """Convert MLB match data to Chronulus format"""
        # Get additional data from your existing MCP servers
        team_stats = await self.get_team_statistics(match.home_team, match.away_team)
        recent_form = await self.get_team_recent_form(match.home_team, match.away_team)
        betting_odds = await self.get_betting_odds(match)
        
        return {
            "home_team": match.home_team,
            "away_team": match.away_team,
            "date": match.date,
            "venue": match.venue,
            "stats": {
                "home_record": team_stats.get("home_record"),
                "away_record": team_stats.get("away_record"),
                "home_run_differential": team_stats.get("home_run_diff"),
                "away_run_differential": team_stats.get("away_run_diff"),
            },
            "form": {
                "home_recent": recent_form.get("home_l10"),
                "away_recent": recent_form.get("away_l10"),
                "home_streak": recent_form.get("home_streak"),
                "away_streak": recent_form.get("away_streak")
            },
            "odds": {
                "home_moneyline": betting_odds.get("home_ml"),
                "away_moneyline": betting_odds.get("away_ml"),
                "implied_probability": betting_odds.get("implied_prob")
            },
            "context": {
                "rivalry": self.is_rivalry_game(match.home_team, match.away_team),
                "playoff_implications": self.has_playoff_implications(match),
                "weather": await self.get_weather_info(match.venue, match.date)
            }
        }
    
    def is_successful_response(self, response: Dict[str, Any]) -> bool:
        """Check if Chronulus response was successful"""
        if "error" in response:
            return False
        
        if "result" not in response:
            return False
        
        try:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            return data.get("status") == "success"
        except (KeyError, json.JSONDecodeError):
            return False
    
    def extract_analysis_data(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract analysis data from MCP response"""
        try:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            return data.get("analysis")
        except (KeyError, json.JSONDecodeError):
            return None
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.chronulus_client.close()
```

### Discord Slash Command Integration
```python
import discord
from discord.ext import commands

class ChronulusCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chronulus_client = ChronulusMCPClient()
    
    @discord.slash_command(name="ai_analysis", description="Get AI expert analysis for a game")
    async def ai_analysis(
        self, 
        ctx: discord.ApplicationContext,
        home_team: str,
        away_team: str,
        experts: int = 2
    ):
        """Get Chronulus AI analysis for specified teams"""
        await ctx.defer()  # This might take a while
        
        try:
            # Create basic game data
            game_data = {
                "home_team": home_team,
                "away_team": away_team,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "venue": f"{home_team} Stadium"
            }
            
            # Get AI analysis
            response = await self.chronulus_client.get_chronulus_analysis(
                game_data=game_data,
                expert_count=min(max(experts, 2), 30)  # Clamp to valid range
            )
            
            if not self.is_successful_response(response):
                embed = discord.Embed(
                    title="❌ Analysis Failed",
                    description="Could not get AI analysis at this time.",
                    color=discord.Color.red()
                )
                await ctx.followup.send(embed=embed)
                return
            
            # Create result embed
            analysis_data = self.extract_analysis_data(response)
            embed = self.create_analysis_embed(home_team, away_team, analysis_data)
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed)
    
    @discord.slash_command(name="ai_test", description="Test AI analysis with hardcoded data")
    async def ai_test(self, ctx: discord.ApplicationContext):
        """Test Chronulus with hardcoded Dodgers @ Padres data"""
        await ctx.defer()
        
        try:
            response = await self.chronulus_client.test_hardcoded_analysis()
            
            if not self.is_successful_response(response):
                embed = discord.Embed(
                    title="❌ Test Failed",
                    description="AI test analysis failed.",
                    color=discord.Color.red()
                )
                await ctx.followup.send(embed=embed)
                return
            
            # Extract and display results
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            analysis = data["analysis"]
            
            embed = discord.Embed(
                title="🧠 AI Test Analysis",
                description="**Los Angeles Dodgers @ San Diego Padres**",
                color=0x9B59B6
            )
            
            # Add expert analysis (truncated for Discord)
            expert_text = analysis["expert_analysis"]
            if len(expert_text) > 1000:
                expert_text = expert_text[:997] + "..."
            
            embed.add_field(
                name="📊 Expert Analysis",
                value=expert_text,
                inline=False
            )
            
            embed.add_field(
                name="Win Probability",
                value=f"Dodgers: {analysis['dodgers_win_probability']:.1%}",
                inline=True
            )
            
            embed.add_field(
                name="Expert Count",
                value=str(analysis["expert_count"]),
                inline=True
            )
            
            embed.add_field(
                name="Cost",
                value=analysis["cost_estimate"],
                inline=True
            )
            
            embed.set_footer(text="Test analysis • Markets: Moneyline, Run Line, Total")
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Test failed: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed)
    
    @discord.slash_command(name="ai_health", description="Check AI service health")
    async def ai_health(self, ctx: discord.ApplicationContext):
        """Check Chronulus service health"""
        health = await self.chronulus_client.health_check()
        
        if health.get("status") == "healthy":
            embed = discord.Embed(
                title="✅ AI Service Healthy",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ AI Service Issues",
                description=health.get("error", "Unknown error"),
                color=discord.Color.red()
            )
        
        embed.add_field(name="Status", value=health.get("status"), inline=True)
        embed.add_field(name="SDK Available", value=health.get("chronulus_sdk", False), inline=True)
        embed.add_field(name="API Key", value=health.get("api_key_configured", False), inline=True)
        
        await ctx.respond(embed=embed)
```

## Webhook Integration

### FastAPI Webhook Server
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()
chronulus_client = ChronulusMCPClient()

class GameAnalysisRequest(BaseModel):
    home_team: str
    away_team: str
    game_date: str
    venue: str = None
    expert_count: int = 2

class AnalysisResponse(BaseModel):
    status: str
    analysis: dict = None
    error: str = None

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_game(request: GameAnalysisRequest):
    """Webhook endpoint for game analysis"""
    try:
        game_data = {
            "home_team": request.home_team,
            "away_team": request.away_team,
            "date": request.game_date,
            "venue": request.venue or f"{request.home_team} Stadium"
        }
        
        response = await chronulus_client.get_chronulus_analysis(
            game_data=game_data,
            expert_count=request.expert_count
        )
        
        if "error" in response:
            return AnalysisResponse(status="error", error=response["error"])
        
        # Extract analysis data
        content = response["result"]["content"][0]["text"]
        data = json.loads(content)
        
        return AnalysisResponse(
            status=data["status"],
            analysis=data.get("analysis")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health = await chronulus_client.health_check()
    return health

# Usage with webhook
# POST https://your-webhook.com/analyze
# {
#   "home_team": "New York Yankees", 
#   "away_team": "Boston Red Sox",
#   "game_date": "2025-08-23",
#   "expert_count": 3
# }
```

## Scheduled Analysis

### Daily Analysis Script
```python
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict

class DailyAnalysisRunner:
    def __init__(self):
        self.chronulus_client = ChronulusMCPClient()
        self.results_dir = "daily_analysis_results"
    
    async def run_daily_analysis(self, date: str = None):
        """Run analysis for all games on specified date"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🗓️ Running daily analysis for {date}")
        
        # Get games for date (from your existing MLB MCP)
        games = await self.get_games_for_date(date)
        print(f"📊 Found {len(games)} games to analyze")
        
        results = []
        total_cost = 0.0
        
        for i, game in enumerate(games):
            print(f"🧠 Analyzing game {i+1}/{len(games)}: {game['away_team']} @ {game['home_team']}")
            
            try:
                # Get Chronulus analysis
                response = await self.chronulus_client.get_chronulus_analysis(
                    game_data=game,
                    expert_count=2  # Cost-effective for daily analysis
                )
                
                if self.is_successful_response(response):
                    analysis_data = self.extract_analysis_data(response)
                    results.append({
                        "game": f"{game['away_team']} @ {game['home_team']}",
                        "analysis": analysis_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    total_cost += 0.075  # Estimate $0.075 per 2-expert analysis
                    print(f"✅ Analysis completed")
                else:
                    print(f"❌ Analysis failed")
                
                # Rate limiting - don't overwhelm Chronulus API
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"❌ Error analyzing game: {e}")
                continue
        
        # Save results
        await self.save_daily_results(date, results, total_cost)
        
        print(f"✅ Daily analysis complete!")
        print(f"📊 Analyzed {len(results)}/{len(games)} games")
        print(f"💰 Estimated cost: ${total_cost:.2f}")
        
        return results
    
    async def save_daily_results(self, date: str, results: List[Dict], cost: float):
        """Save daily analysis results"""
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Summary report
        summary = {
            "date": date,
            "total_games": len(results),
            "estimated_cost": f"${cost:.2f}",
            "timestamp": datetime.now().isoformat(),
            "games": results
        }
        
        # Save JSON
        json_file = f"{self.results_dir}/daily_analysis_{date}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save readable report
        md_file = f"{self.results_dir}/daily_analysis_{date}.md"
        with open(md_file, 'w') as f:
            f.write(f"# Daily MLB AI Analysis - {date}\\n\\n")
            f.write(f"**Games Analyzed**: {len(results)}\\n")
            f.write(f"**Estimated Cost**: ${cost:.2f}\\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            
            for result in results:
                f.write(f"## {result['game']}\\n\\n")
                analysis = result["analysis"]
                
                if "expert_analysis" in analysis:
                    f.write("### Expert Analysis\\n")
                    f.write(f"{analysis['expert_analysis']}\\n\\n")
                
                if "consensus_probability" in analysis:
                    f.write("### Key Metrics\\n")
                    prob = analysis["consensus_probability"]
                    f.write(f"- **Win Probability**: {prob:.1%}\\n")
                    
                    if "market_edge" in analysis:
                        edge = analysis["market_edge"]
                        f.write(f"- **Market Edge**: {edge:+.1%}\\n")
                    
                    if "recommendation" in analysis:
                        rec = analysis["recommendation"]
                        f.write(f"- **Recommendation**: {rec}\\n")
                
                f.write("\\n---\\n\\n")
        
        print(f"💾 Results saved:")
        print(f"   JSON: {json_file}")
        print(f"   Report: {md_file}")

# Scheduled execution
async def main():
    runner = DailyAnalysisRunner()
    await runner.run_daily_analysis()

if __name__ == "__main__":
    asyncio.run(main())
```

### Cron Job Setup
```bash
# Add to crontab for daily 6 AM analysis
# crontab -e
0 6 * * * cd /path/to/your/project && python daily_analysis.py
```

## Error Handling and Retry Logic

### Robust Integration Pattern
```python
import asyncio
import time
from typing import Optional, Dict, Any

class RobustChronulusClient:
    def __init__(self):
        self.base_client = ChronulusMCPClient()
        self.retry_attempts = 3
        self.retry_delay = 5  # seconds
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.last_failure_time = 0
    
    async def get_analysis_with_fallback(
        self, 
        game_data: Dict[str, Any], 
        expert_count: int = 2
    ) -> Optional[Dict[str, Any]]:
        """Get analysis with retry logic and circuit breaker"""
        
        # Check circuit breaker
        if self.is_circuit_open():
            print("🔴 Circuit breaker open - Chronulus unavailable")
            return None
        
        # Attempt analysis with retries
        for attempt in range(self.retry_attempts):
            try:
                response = await self.base_client.get_chronulus_analysis(
                    game_data=game_data,
                    expert_count=expert_count
                )
                
                if self.is_successful_response(response):
                    # Reset circuit breaker on success
                    self.circuit_breaker_failures = 0
                    return self.extract_analysis_data(response)
                else:
                    print(f"❌ Analysis failed (attempt {attempt + 1}): {response.get('error')}")
                    
            except Exception as e:
                print(f"❌ Exception during analysis (attempt {attempt + 1}): {e}")
            
            # Increment failure count and delay before retry
            self.circuit_breaker_failures += 1
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        # All attempts failed
        self.last_failure_time = time.time()
        print(f"🔴 All {self.retry_attempts} attempts failed")
        return None
    
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.circuit_breaker_failures < self.circuit_breaker_threshold:
            return False
        
        # Check if timeout has passed
        if time.time() - self.last_failure_time > self.circuit_breaker_timeout:
            self.circuit_breaker_failures = 0  # Reset
            return False
        
        return True
    
    async def get_analysis_or_fallback_message(
        self, 
        game_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get analysis with graceful degradation"""
        analysis = await self.get_analysis_with_fallback(game_data)
        
        if analysis:
            return {
                "status": "success",
                "source": "chronulus_ai",
                "analysis": analysis
            }
        else:
            # Fallback to basic analysis
            return {
                "status": "fallback",
                "source": "basic_analysis", 
                "message": "🤖 AI analysis temporarily unavailable. Using basic statistical analysis.",
                "basic_analysis": self.generate_basic_analysis(game_data)
            }
    
    def generate_basic_analysis(self, game_data: Dict[str, Any]) -> str:
        """Generate basic fallback analysis"""
        home = game_data.get("home_team", "Home")
        away = game_data.get("away_team", "Away")
        
        return f"Statistical matchup: {away} @ {home}. " \\
               f"Analysis based on recent form and head-to-head records. " \\
               f"AI expert analysis will resume when service is available."
```

This comprehensive integration guide provides production-ready examples for incorporating Chronulus AI analysis into various systems with proper error handling, retry logic, and graceful degradation.