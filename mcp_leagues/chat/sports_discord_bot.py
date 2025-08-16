#!/usr/bin/env python3
"""
Sports Discord Bot using OpenRouter + Discord MCP
Integrates with your sports betting platform for automated Discord interactions
"""

import asyncio
import os
import json
import httpx
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from openrouter_discord_bridge import OpenRouterDiscordBridge


class SportsDiscordBot:
    """
    Sports betting Discord bot that integrates:
    - Your sports MCPs (MLB, Soccer, CFB, Odds)
    - OpenRouter AI for analysis
    - Discord MCP for communication
    """
    
    def __init__(
        self, 
        openrouter_api_key: str,
        sports_mcp_urls: Dict[str, str],
        discord_mcp_url: str = "https://chatmcp-production.up.railway.app/mcp"
    ):
        self.bridge = OpenRouterDiscordBridge(
            openrouter_api_key=openrouter_api_key,
            discord_mcp_url=discord_mcp_url,
            default_model="anthropic/claude-3.5-sonnet"
        )
        self.sports_mcps = sports_mcp_urls
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        await self.bridge.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bridge.__aexit__(exc_type, exc_val, exc_tb)
        await self.client.aclose()

    async def get_mlb_games_today(self) -> List[Dict]:
        """Get today's MLB games from your MLB MCP"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getMLBScheduleET",
                    "arguments": {"date": today}
                }
            }
            
            response = await self.client.post(self.sports_mcps["mlb"], json=payload)
            data = response.json()
            
            if "result" in data:
                # Parse the MCP response
                content = data["result"]["content"][0]["text"]
                return json.loads(content)
            return []
        except Exception as e:
            print(f"Error getting MLB games: {e}")
            return []

    async def get_game_odds(self, sport: str = "baseball_mlb") -> List[Dict]:
        """Get betting odds from your Odds MCP"""
        try:
            payload = {
                "jsonrpc": "2.0", 
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getOdds",
                    "arguments": {
                        "sport": sport,
                        "regions": "us",
                        "markets": "h2h,spreads,totals"
                    }
                }
            }
            
            response = await self.client.post(self.sports_mcps["odds"], json=payload)
            data = response.json()
            
            if "result" in data:
                content = data["result"]["content"][0]["text"]
                return json.loads(content)
            return []
        except Exception as e:
            print(f"Error getting odds: {e}")
            return []

    async def generate_daily_mlb_picks(self, channel: str) -> Dict[str, Any]:
        """Generate and post daily MLB picks to Discord"""
        
        # Get today's games and odds
        games = await self.get_mlb_games_today()
        odds = await self.get_game_odds("baseball_mlb")
        
        if not games:
            await self.bridge.send_discord_message(
                channel, 
                "⚾ No MLB games scheduled for today."
            )
            return {"success": True, "message": "No games today"}
        
        # Create AI prompt for analysis
        prompt = f"""
        Analyze today's MLB games and provide 2-3 top betting picks:
        
        Games: {json.dumps(games[:5], indent=2)}  # Limit for token efficiency
        Odds: {json.dumps(odds[:5], indent=2)}
        
        For each pick, provide:
        1. Game (Team vs Team)
        2. Bet type (moneyline/spread/total)
        3. Pick and odds
        4. Brief reason (injury, trends, etc.)
        5. Confidence (1-5 stars)
        
        Format for Discord with emojis. Keep total under 500 characters.
        """
        
        # Get AI analysis
        messages = [
            {
                "role": "system", 
                "content": "You are a professional MLB betting analyst. Provide concise, actionable picks with reasoning."
            },
            {"role": "user", "content": prompt}
        ]
        
        picks_analysis = await self.bridge.call_openrouter(messages, max_tokens=400)
        
        # Post to Discord
        header = f"⚾ **Daily MLB Picks - {datetime.now().strftime('%B %d, %Y')}**\n\n"
        full_message = header + picks_analysis
        
        result = await self.bridge.send_discord_message(channel, full_message)
        
        return {
            "success": result["success"],
            "games_analyzed": len(games),
            "picks_posted": True if result["success"] else False,
            "message": full_message,
            "error": result.get("error")
        }

    async def handle_user_question(self, channel: str, question: str) -> Dict[str, Any]:
        """Handle user questions about sports/betting"""
        
        # Determine what data to fetch based on question
        needs_mlb = any(word in question.lower() for word in ["mlb", "baseball", "yankees", "dodgers"])
        needs_odds = any(word in question.lower() for word in ["odds", "line", "spread", "bet"])
        
        context_data = {}
        
        if needs_mlb:
            context_data["mlb_games"] = await self.get_mlb_games_today()
        
        if needs_odds:
            context_data["odds"] = await self.get_game_odds()
        
        # Build AI prompt with relevant context
        prompt = f"""
        User question: {question}
        
        Available context:
        {json.dumps(context_data, indent=2) if context_data else "No specific data needed"}
        
        Provide a helpful, accurate response about sports betting. If you need more specific data that isn't provided, say so.
        Keep response under 300 characters for Discord.
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a knowledgeable sports betting assistant. Be helpful but responsible about gambling advice."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = await self.bridge.call_openrouter(messages, max_tokens=200)
        
        # Send response to Discord
        result = await self.bridge.send_discord_message(channel, response)
        
        return {
            "question": question,
            "response": response,
            "posted": result["success"],
            "error": result.get("error")
        }

    async def post_line_movement_alert(self, channel: str, game: str, old_line: str, new_line: str):
        """Post betting line movement alert"""
        
        # Generate alert with AI context
        prompt = f"""
        Create a line movement alert:
        Game: {game}
        Line moved from {old_line} to {new_line}
        
        Brief alert with emoji, significance, and potential reason. Under 100 chars.
        """
        
        messages = [
            {"role": "system", "content": "You are a betting line movement tracker. Create urgent, concise alerts."},
            {"role": "user", "content": prompt}
        ]
        
        alert = await self.bridge.call_openrouter(messages, max_tokens=80)
        
        result = await self.bridge.send_discord_message(channel, f"🚨 LINE MOVEMENT\n{alert}")
        
        return result

    async def monitor_discord_chat(self, channel: str, check_interval: int = 60):
        """Monitor Discord chat for questions and respond"""
        print(f"🤖 Starting Discord chat monitoring for #{channel}")
        
        last_message_time = datetime.now(timezone.utc)
        
        while True:
            try:
                # Read recent messages
                messages = await self.bridge.read_discord_messages(channel, limit=5)
                
                # Check for new messages since last check
                for msg in messages:
                    msg_time = datetime.fromisoformat(msg.timestamp.replace('Z', '+00:00'))
                    
                    if msg_time > last_message_time and msg.author != "your_bot_name":
                        # Check if message is a question or mention
                        if any(word in msg.content.lower() for word in ["?", "what", "how", "when", "odds", "pick"]):
                            print(f"💬 Responding to: {msg.content}")
                            await self.handle_user_question(channel, msg.content)
                            last_message_time = msg_time
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"Error in chat monitoring: {e}")
                await asyncio.sleep(check_interval)


# Example usage and testing
async def example_daily_workflow():
    """Example: Daily automated workflow"""
    
    # Your MCP server URLs
    sports_mcps = {
        "mlb": "https://mlbmcp-production.up.railway.app/mcp",
        "soccer": "https://soccermcp-production.up.railway.app/mcp", 
        "cfb": "https://cfbmcp-production.up.railway.app/mcp",
        "odds": "https://odds-mcp-v2-production.up.railway.app/mcp"
    }
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_key:
        print("❌ Set OPENROUTER_API_KEY environment variable")
        return
    
    async with SportsDiscordBot(openrouter_key, sports_mcps) as bot:
        
        # Generate daily MLB picks
        print("📊 Generating daily MLB picks...")
        result = await bot.generate_daily_mlb_picks("aggregated-picks")
        print("Result:", result)
        
        # Handle a sample user question
        print("\n💬 Testing user question handling...")
        qa_result = await bot.handle_user_question(
            "mcp-testing", 
            "What are the best MLB bets for tonight?"
        )
        print("Q&A Result:", qa_result)


async def example_chat_monitoring():
    """Example: Start chat monitoring"""
    
    sports_mcps = {
        "mlb": "https://mlbmcp-production.up.railway.app/mcp",
        "odds": "https://odds-mcp-v2-production.up.railway.app/mcp"
    }
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    async with SportsDiscordBot(openrouter_key, sports_mcps) as bot:
        # Start monitoring (this will run continuously)
        await bot.monitor_discord_chat("chat", check_interval=30)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🤖 Sports Discord Bot")
    print("1. Daily workflow test")
    print("2. Chat monitoring")
    
    choice = input("Choose (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(example_daily_workflow())
    elif choice == "2":
        asyncio.run(example_chat_monitoring())
    else:
        print("❌ Invalid choice")