#!/usr/bin/env python3
"""
Interactive Sports Chat - Ask any question about sports and get ESPN data!
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from mcp import ClientSession
from mcp.client.sse import sse_client

class SportsChatBot:
    def __init__(self):
        self.proxy_url = "http://127.0.0.1:8080/servers/espn/sse"
        self.headers = {}
        
    def parse_question(self, question):
        """Parse the user's question to determine what ESPN endpoint to call"""
        question = question.lower()
        
        # Determine sport (check WNBA FIRST to avoid NBA matching first)
        sport = None
        league = None
        if any(word in question for word in ['wnba', 'liberty', 'sparks', 'sky', 'fever']):
            sport = 'basketball' 
            league = 'wnba'
        elif any(word in question for word in ['nba', 'basketball', 'lakers', 'warriors', 'bulls', 'heat']):
            sport = 'basketball'
            league = 'nba'
        elif any(word in question for word in ['nfl', 'football', 'patriots', 'cowboys', 'packers']):
            sport = 'football'
            league = 'nfl'
        elif any(word in question for word in ['mlb', 'baseball', 'yankees', 'dodgers', 'red sox']):
            sport = 'baseball'
            league = 'mlb'
        
        # Determine date
        date_str = None
        if any(word in question for word in ['today', 'tonight']):
            date_str = datetime.now().strftime("%Y%m%d")
        elif any(word in question for word in ['tomorrow']):
            date_str = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        elif any(word in question for word in ['yesterday']):
            date_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        elif 'this week' in question:
            # We'll handle this differently - check multiple days
            pass
        
        # Determine what type of data they want
        endpoint_type = 'scoreboard'  # Default
        if any(word in question for word in ['standings', 'ranking', 'records']):
            endpoint_type = 'standings'
        elif any(word in question for word in ['stats', 'leaders', 'top players']):
            endpoint_type = 'leaders'
        elif any(word in question for word in ['news', 'articles']):
            endpoint_type = 'news'
        
        return {
            'sport': sport,
            'league': league,
            'date': date_str,
            'endpoint_type': endpoint_type,
            'original_question': question
        }
    
    def build_endpoint(self, parsed):
        """Build the ESPN API endpoint based on parsed question"""
        if not parsed['sport'] or not parsed['league']:
            return f"/basketball/nba/scoreboard"  # Default fallback
            
        base = f"/{parsed['sport']}/{parsed['league']}/{parsed['endpoint_type']}"
        
        if parsed['date'] and parsed['endpoint_type'] == 'scoreboard':
            base += f"?dates={parsed['date']}"
            
        return base
    
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
    
    def format_games_response(self, data, question):
        """Format game data into a readable response"""
        if "error" in data:
            return f"❌ Sorry, I couldn't get the data: {data['error']}"
            
        response = []
        
        if "events" in data and len(data["events"]) > 0:
            games = data["events"]
            league_name = data.get("leagues", [{}])[0].get("name", "Games")
            
            response.append(f"🏀 Found {len(games)} {league_name} games:")
            response.append("=" * 50)
            
            for i, game in enumerate(games, 1):
                try:
                    # Get teams
                    competitors = game["competitions"][0]["competitors"]
                    home_team = next(c for c in competitors if c["homeAway"] == "home")["team"]["displayName"]
                    away_team = next(c for c in competitors if c["homeAway"] == "away")["team"]["displayName"]
                    
                    # Get status
                    status = game["status"]["type"]["description"]
                    game_time = game.get("date", "TBD")
                    
                    response.append(f"\n{i}. {away_team} @ {home_team}")
                    response.append(f"   Status: {status}")
                    
                    # Add scores if game is complete or in progress
                    if game["status"]["type"]["completed"] or "in progress" in status.lower():
                        try:
                            home_score = next(c for c in competitors if c["homeAway"] == "home")["score"]
                            away_score = next(c for c in competitors if c["homeAway"] == "away")["score"]
                            response.append(f"   Score: {away_team} {away_score} - {home_team} {home_score}")
                        except:
                            pass
                    else:
                        response.append(f"   Time: {game_time}")
                        
                except Exception as e:
                    response.append(f"   Error parsing game {i}: {e}")
                    
        elif "events" in data:
            response.append("❌ No games found for your query.")
        else:
            response.append("❌ Unexpected data format from ESPN.")
            
        return "\n".join(response)
    
    async def answer_question(self, question):
        """Main method to answer a sports question"""
        print(f"\n🤔 Thinking about: '{question}'")
        
        # Check if they're asking about betting/moneylines
        betting_disclaimer = ""
        if any(word in question.lower() for word in ['moneyline', 'odds', 'betting', 'spread', 'over/under']):
            betting_disclaimer = "\n⚠️  Note: ESPN doesn't provide betting odds/moneylines. I can only show game schedules and scores.\n"
        
        parsed = self.parse_question(question)
        endpoint = self.build_endpoint(parsed)
        
        print(f"🌐 Fetching from ESPN: {endpoint}")
        print(f"🏀 Detected sport: {parsed['league']}")
        
        data = await self.fetch_espn_data(endpoint)
        
        response = ""
        if parsed['endpoint_type'] == 'scoreboard':
            response = self.format_games_response(data, question)
        else:
            # For other types, just return raw data for now
            response = f"📊 Here's the data from ESPN:\n{json.dumps(data, indent=2)[:1000]}..."
            
        return betting_disclaimer + response

async def main():
    print("🏀 Welcome to Sports Chat!")
    print("Ask me any sports question and I'll fetch the data from ESPN.")
    print("Examples:")
    print("  - 'What NBA games are today?'")
    print("  - 'Show me WNBA games tomorrow'") 
    print("  - 'Any NFL games this week?'")
    print("  - 'What basketball games are tonight?'")
    print("\nType 'quit' to exit.\n")
    
    bot = SportsChatBot()
    
    while True:
        try:
            question = input("🏈 Ask me about sports: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for using Sports Chat!")
                break
                
            if not question:
                continue
                
            answer = await bot.answer_question(question)
            print(f"\n{answer}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using Sports Chat!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())