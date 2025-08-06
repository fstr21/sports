#!/usr/bin/env python3
"""
Smart Sports Chat - AI-powered sports analysis with ESPN data
Uses OpenRouter API for real AI analysis
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

class SmartSportsBot:
    def __init__(self):
        self.proxy_url = "http://127.0.0.1:8080/servers/espn/sse"
        self.headers = {}
        
        # OpenRouter API configuration
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'openrouter/horizon-beta')
        
        if not self.openrouter_api_key:
            print("⚠️ Warning: No OpenRouter API key found in .env.local")
    
    async def check_proxy_status(self):
        """Check if the MCP proxy is running"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get("http://127.0.0.1:8080/")
                return "🟢 Online" if response.status_code in [200, 404] else "🔴 Error"
        except:
            return "🔴 Offline"
    
    async def check_openrouter_status(self):
        """Check if OpenRouter API is accessible"""
        if not self.openrouter_api_key:
            return "🔴 No API Key"
        
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(
                    f"{self.openrouter_base_url}/models",
                    headers={"Authorization": f"Bearer {self.openrouter_api_key}"}
                )
                return "🟢 Connected" if response.status_code == 200 else "🟡 Limited"
        except:
            return "🔴 Error"
        
    async def fetch_espn_data(self, endpoint):
        """Fetch data from ESPN via our MCP proxy"""
        try:
            async with sse_client(self.proxy_url, headers=self.headers) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    args = {
                        "method": "GET",
                        "endpoint": endpoint
                    }
                    
                    result = await session.call_tool("test_request", args)
                    
                    if result.content:
                        response_text = result.content[0].text
                        response_data = json.loads(response_text)
                        
                        if "response" in response_data and "body" in response_data["response"]:
                            body_data = response_data["response"]["body"]
                            
                            if isinstance(body_data, str):
                                return json.loads(body_data)
                            else:
                                return body_data
                        
        except Exception as e:
            return {"error": str(e)}
    
    def determine_endpoints(self, question):
        """Determine what ESPN endpoints to call based on the question"""
        question = question.lower()
        endpoints = []
        
        print(f"🔍 Debug: Analyzing question - '{question}'")
        
        # Check if this is a general team/league question vs game schedule question
        general_questions = ['tell me about', 'who are', 'what is', 'how are', 'season start', 'when does']
        is_general_question = any(phrase in question for phrase in general_questions)
        
        print(f"🔍 Debug: Is general question? {is_general_question}")
        
        # For pure general questions (not game-related), don't fetch ESPN data at all
        game_related_words = ['games', 'playing', 'schedule', 'tonight', 'today', 'tomorrow']
        has_game_context = any(word in question for word in game_related_words)
        
        print(f"🔍 Debug: Has game context? {has_game_context}")
        
        if is_general_question and not has_game_context:
            print("🔍 Debug: Pure general question - no ESPN data needed")
            return []  # Return empty - rely on AI knowledge only
        
        # For general questions with some game context, just get today's context
        if is_general_question:
            today = datetime.now().strftime("%Y%m%d")
            dates_to_check = [today]
        else:
            # For game schedule questions, determine date range
            today = datetime.now()
            dates_to_check = []
            
            if any(phrase in question for phrase in ['this week', 'upcoming', 'week']):
                # Check today through next 6 days (7 total)
                for i in range(7):
                    date = today + timedelta(days=i)
                    dates_to_check.append(date.strftime("%Y%m%d"))
            elif 'tomorrow' in question:
                dates_to_check = [(today + timedelta(days=1)).strftime("%Y%m%d")]
            elif 'yesterday' in question:
                dates_to_check = [(today - timedelta(days=1)).strftime("%Y%m%d")]
            else:
                # Default to today for game questions
                dates_to_check = [today.strftime("%Y%m%d")]
        
        # Determine sport/league - check specific teams first
        sport_league = "/basketball/wnba/scoreboard"  # Default
        
        # WNBA teams
        wnba_teams = ['aces', 'liberty', 'sparks', 'sky', 'fever', 'sun', 'mercury', 'storm', 'lynx', 'wings', 'mystics', 'dream']
        if any(team in question for team in wnba_teams):
            sport_league = "/basketball/wnba/scoreboard"
        elif 'wnba' in question:
            sport_league = "/basketball/wnba/scoreboard"
        elif 'nba' in question:
            sport_league = "/basketball/nba/scoreboard"
        elif 'nfl' in question:
            sport_league = "/football/nfl/scoreboard"
        elif 'mlb' in question:
            sport_league = "/baseball/mlb/scoreboard"
        
        # Create endpoints for each date
        for date_str in dates_to_check:
            endpoints.append(f"{sport_league}?dates={date_str}")
            
        return endpoints
    
    def format_espn_data_for_llm(self, data):
        """Format ESPN data into a clean summary for the LLM"""
        if "error" in data:
            return f"Error getting ESPN data: {data['error']}"
            
        summary = []
        
        if "events" in data and len(data["events"]) > 0:
            league_name = data.get("leagues", [{}])[0].get("name", "Games")
            summary.append(f"Current {league_name} Games:")
            
            for i, game in enumerate(data["events"], 1):
                try:
                    competitors = game["competitions"][0]["competitors"]
                    home_team = next(c for c in competitors if c["homeAway"] == "home")["team"]["displayName"]
                    away_team = next(c for c in competitors if c["homeAway"] == "away")["team"]["displayName"]
                    
                    status = game["status"]["type"]["description"]
                    game_time = game.get("date", "TBD")
                    
                    game_summary = f"{i}. {away_team} @ {home_team} - {status}"
                    
                    # Add scores if available
                    if game["status"]["type"]["completed"] or "in progress" in status.lower():
                        try:
                            home_score = next(c for c in competitors if c["homeAway"] == "home").get("score", "0")
                            away_score = next(c for c in competitors if c["homeAway"] == "away").get("score", "0")
                            game_summary += f" (Score: {away_team} {away_score} - {home_team} {home_score})"
                        except:
                            pass
                    else:
                        game_summary += f" (Time: {game_time})"
                        
                    summary.append(game_summary)
                    
                except Exception as e:
                    summary.append(f"{i}. Error parsing game: {e}")
                    
        return "\n".join(summary)
    
    def create_llm_prompt(self, user_question, espn_data):
        """Create a prompt for the LLM with context"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_year = datetime.now().year
        
        return f"""You are a knowledgeable sports analyst who loves discussing games, betting lines, player matchups, and giving opinions on sports.

IMPORTANT CONTEXT:
- Current date: {current_date}
- Current year: {current_year}
- This is the {current_year} sports season

Current ESPN Data:
{espn_data}

User Question: "{user_question}"

Please provide a thoughtful, engaging response that:
1. Answers their specific question using the CURRENT year ({current_year})
2. Uses the ESPN data when relevant
3. For general team questions, provide current info about the team based on your knowledge and any available data
4. For schedule questions, use the ESPN game data provided
5. Gives your analysis/opinion when asked
6. Discusses betting aspects if mentioned (totals, spreads, moneylines)
7. Shows enthusiasm for sports discussion
8. If betting lines are mentioned but you don't have that data, acknowledge it and give your analysis based on team performance

Be conversational and knowledgeable, like a sports expert friend would be. Remember it's currently {current_year}!"""

    async def get_llm_response(self, prompt):
        """Get response from OpenRouter API"""
        if not self.openrouter_api_key:
            return "❌ Error: OpenRouter API key not configured in .env.local"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8080",
                        "X-Title": "Sports Chat Bot"
                    },
                    json={
                        "model": self.openrouter_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a knowledgeable sports analyst and betting expert who loves discussing games, matchups, and giving opinions on betting lines. Be conversational, enthusiastic, and provide detailed analysis."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"❌ OpenRouter API error: {response.status_code} - {response.text}"
                    
        except Exception as e:
            return f"❌ Error calling OpenRouter: {str(e)}"

    async def chat(self, user_question):
        """Main chat method"""
        print(f"\n🤔 Analyzing: '{user_question}'")
        
        # Get ESPN data
        endpoints = self.determine_endpoints(user_question)
        all_data = []
        
        print(f"🗓️ Checking {len(endpoints)} date(s) for games...")
        
        for endpoint in endpoints:
            print(f"🌐 Fetching: {endpoint}")
            data = await self.fetch_espn_data(endpoint)
            formatted_data = self.format_espn_data_for_llm(data)
            if formatted_data and "No games found" not in formatted_data and "Error" not in formatted_data:
                all_data.append(formatted_data)
            
            # Small delay to be nice to ESPN servers
            await asyncio.sleep(0.3)
        
        if not all_data:
            espn_summary = "No games found for the requested time period."
        else:
            espn_summary = "\n\n".join(all_data)
        
        # Create LLM prompt
        prompt = self.create_llm_prompt(user_question, espn_summary)
        
        # Get LLM response
        response = await self.get_llm_response(prompt)
        
        return response

async def main():
    print("🏀 Smart Sports Chat - AI Powered!")
    
    bot = SmartSportsBot()
    
    # Check system status
    print("\n📊 System Status:")
    print("=" * 60)
    
    proxy_status = await bot.check_proxy_status()
    openrouter_status = await bot.check_openrouter_status()
    
    print(f"ESPN Proxy (localhost:8080): {proxy_status}")
    print(f"OpenRouter API: {openrouter_status}")
    print(f"AI Model: {bot.openrouter_model}")
    print("=" * 60)
    
    print("\nAsk me anything about sports and I'll analyze it for you.")
    print("Examples:")
    print("  - 'What WNBA games are tonight and how do you feel about the Lynx-Storm total being 156.5?'")
    print("  - 'Should I bet the over on the Liberty game?'")
    print("  - 'How are the Fever looking tonight?'")
    print("\nType 'quit' to exit.\n")
    
    while True:
        try:
            question = input("🏈 Ask your sports question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for chatting sports!")
                break
                
            if not question:
                continue
                
            answer = await bot.chat(question)
            print(f"\n🏀 {answer}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for chatting sports!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())