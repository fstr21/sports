#!/usr/bin/env python3
"""
Sports AI Agent - Intelligent sports data retrieval using OpenRouter + ESPN API
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

class SportsAIAgent:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'openrouter/horizon-beta')
        self.espn_base_url = "http://site.api.espn.com"
        
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    def ask_openrouter(self, prompt, system_message=None):
        """Send a request to OpenRouter AI"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Sports Data Analyzer"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.openrouter_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Debug: Print the response structure
            print(f"🔍 OpenRouter Response: {json.dumps(response_data, indent=2)[:500]}...")
            
            # Handle different response formats
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content']
            elif 'response' in response_data:
                return response_data['response']
            elif 'text' in response_data:
                return response_data['text']
            else:
                return f"Unexpected response format: {response_data}"
                
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}"
        except KeyError as e:
            return f"Response format error - missing key: {e}"
        except Exception as e:
            return f"Error calling OpenRouter: {e}"
    
    def call_espn_api(self, endpoint, params=None):
        """Call ESPN API directly"""
        url = f"{self.espn_base_url}{endpoint}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "ESPN-Research/1.0"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_date_range(self, days=3):
        """Get date range for the next N days"""
        dates = []
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            dates.append(date.strftime("%Y%m%d"))
        return dates
    
    def get_wnba_schedule(self, days=3):
        """Get WNBA schedule for the next N days"""
        dates = self.get_date_range(days)
        all_games = []
        
        for date in dates:
            print(f"Fetching WNBA games for {date}...")
            endpoint = "/apis/site/v2/sports/basketball/wnba/scoreboard"
            params = {"dates": date}
            
            data = self.call_espn_api(endpoint, params)
            
            if "events" in data and data["events"]:
                for event in data["events"]:
                    game_info = {
                        "date": date,
                        "game_id": event.get("id"),
                        "name": event.get("name"),
                        "short_name": event.get("shortName"),
                        "time_utc": event.get("date"),
                        "venue": event["competitions"][0]["venue"]["fullName"] if event.get("competitions") else "TBD"
                    }
                    
                    # Extract team info and stats
                    if event.get("competitions") and event["competitions"][0].get("competitors"):
                        competitors = event["competitions"][0]["competitors"]
                        competition = event["competitions"][0]
                        
                        # Extract odds if available
                        odds = competition.get("odds", [])
                        if odds:
                            game_info["odds"] = {
                                "spread": odds[0].get("spread"),
                                "over_under": odds[0].get("overUnder"),
                                "provider": odds[0].get("provider", {}).get("name"),
                                "home_odds": odds[0].get("homeTeamOdds", {}),
                                "away_odds": odds[0].get("awayTeamOdds", {})
                            }
                        
                        for comp in competitors:
                            team = comp["team"]
                            team_data = {
                                "id": team["id"],
                                "name": team["displayName"],
                                "abbreviation": team["abbreviation"],
                                "record": None,
                                "stats": {},
                                "leaders": {}
                            }
                            
                            # Extract team records
                            if comp.get("records"):
                                for record in comp["records"]:
                                    if record.get("name") == "overall":
                                        team_data["record"] = record.get("summary")
                            
                            # Extract team stats
                            if comp.get("statistics"):
                                for stat in comp["statistics"]:
                                    team_data["stats"][stat["name"]] = stat["displayValue"]
                            
                            # Extract team leaders
                            if comp.get("leaders"):
                                for leader in comp["leaders"]:
                                    if leader.get("leaders"):
                                        player = leader["leaders"][0]["athlete"]
                                        team_data["leaders"][leader["name"]] = {
                                            "player": player.get("displayName"),
                                            "value": leader["leaders"][0].get("displayValue")
                                        }
                            
                            if comp["homeAway"] == "home":
                                game_info["home_team"] = team_data
                            else:
                                game_info["away_team"] = team_data
                    
                    all_games.append(game_info)
        
        return all_games
    
    def format_games_for_ai(self, games):
        """Format games data for AI analysis"""
        if not games:
            return "No games found for the requested dates."
        
        formatted = "WNBA Games Schedule:\n\n"
        current_date = None
        
        for game in games:
            # Group by date
            if game["date"] != current_date:
                current_date = game["date"]
                date_obj = datetime.strptime(game["date"], "%Y%m%d")
                formatted += f"\n📅 {date_obj.strftime('%A, %B %d, %Y')}:\n"
                formatted += "-" * 50 + "\n"
            
            # Format game info
            away_team = game.get("away_team", {}).get("name", "TBD")
            home_team = game.get("home_team", {}).get("name", "TBD")
            venue = game.get("venue", "TBD")
            
            formatted += f"🏀 {away_team} @ {home_team}\n"
            formatted += f"   📍 {venue}\n"
            formatted += f"   🆔 Game ID: {game.get('game_id', 'N/A')}\n\n"
        
        return formatted
    
    def analyze_specific_game(self, team1, team2, games):
        """Analyze a specific game matchup"""
        # Find the game
        target_game = None
        for game in games:
            home_name = game.get("home_team", {}).get("name", "").lower()
            away_name = game.get("away_team", {}).get("name", "").lower()
            
            if (team1.lower() in home_name or team1.lower() in away_name) and \
               (team2.lower() in home_name or team2.lower() in away_name):
                target_game = game
                break
        
        if not target_game:
            return f"Could not find a game between {team1} and {team2}"
        
        # Format detailed game analysis
        analysis = f"🏀 GAME ANALYSIS: {target_game['name']}\n"
        analysis += "=" * 60 + "\n\n"
        
        # Game details
        analysis += f"📅 Date: {target_game['date']}\n"
        analysis += f"🏟️ Venue: {target_game['venue']}\n"
        analysis += f"🆔 Game ID: {target_game['game_id']}\n\n"
        
        # Team records
        home_team = target_game.get("home_team", {})
        away_team = target_game.get("away_team", {})
        
        analysis += f"📊 TEAM RECORDS:\n"
        analysis += f"🏠 {home_team.get('name', 'Home')}: {home_team.get('record', 'N/A')}\n"
        analysis += f"✈️ {away_team.get('name', 'Away')}: {away_team.get('record', 'N/A')}\n\n"
        
        # Odds analysis
        if target_game.get("odds"):
            odds = target_game["odds"]
            analysis += f"💰 BETTING ODDS ({odds.get('provider', 'Unknown')}):\n"
            analysis += f"📈 Spread: {odds.get('spread', 'N/A')}\n"
            analysis += f"🎯 Over/Under: {odds.get('over_under', 'N/A')}\n"
            
            home_odds = odds.get("home_odds", {})
            away_odds = odds.get("away_odds", {})
            
            if home_odds.get("moneyLine") or away_odds.get("moneyLine"):
                analysis += f"💵 Moneyline:\n"
                analysis += f"   🏠 {home_team.get('name', 'Home')}: {home_odds.get('moneyLine', 'N/A')}\n"
                analysis += f"   ✈️ {away_team.get('name', 'Away')}: {away_odds.get('moneyLine', 'N/A')}\n"
            
            analysis += "\n🎲 BETTING RECOMMENDATIONS:\n"
            
            # Simple betting analysis based on available data
            if odds.get("spread"):
                spread = odds["spread"]
                if spread < -5:
                    analysis += f"• Large spread ({spread}) suggests a mismatch - consider the underdog +{abs(spread)}\n"
                elif spread > -3:
                    analysis += f"• Close spread ({spread}) indicates even matchup - look for value bets\n"
            
            if odds.get("over_under"):
                ou = odds["over_under"]
                analysis += f"• Over/Under {ou} - check recent team scoring trends\n"
            
            analysis += "\n"
        else:
            analysis += "💰 No betting odds available for this game\n\n"
        
        # Team stats comparison
        analysis += "📈 TEAM STATS COMPARISON:\n"
        
        home_stats = home_team.get("stats", {})
        away_stats = away_team.get("stats", {})
        
        key_stats = ["avgPoints", "avgRebounds", "avgAssists", "fieldGoalPct"]
        for stat in key_stats:
            if stat in home_stats or stat in away_stats:
                analysis += f"• {stat}: {home_team.get('name', 'Home')} {home_stats.get(stat, 'N/A')} vs {away_team.get('name', 'Away')} {away_stats.get(stat, 'N/A')}\n"
        
        # Team leaders
        analysis += f"\n⭐ KEY PLAYERS:\n"
        home_leaders = home_team.get("leaders", {})
        away_leaders = away_team.get("leaders", {})
        
        if home_leaders.get("pointsPerGame"):
            analysis += f"🏠 {home_team.get('name', 'Home')} Leading Scorer: {home_leaders['pointsPerGame']['player']} ({home_leaders['pointsPerGame']['value']} PPG)\n"
        
        if away_leaders.get("pointsPerGame"):
            analysis += f"✈️ {away_team.get('name', 'Away')} Leading Scorer: {away_leaders['pointsPerGame']['player']} ({away_leaders['pointsPerGame']['value']} PPG)\n"
        
        return analysis

    def process_request(self, user_request):
        """Process a natural language request"""
        print(f"\n🤖 Processing request: '{user_request}'")
        
        # Check for specific game analysis - broader keyword matching
        request_lower = user_request.lower()
        
        # Common team name patterns
        team_patterns = [
            "dallas wings", "dallas", "wings",
            "new york liberty", "new york", "liberty", "ny",
            "las vegas aces", "las vegas", "aces", "lv",
            "seattle storm", "seattle", "storm",
            "chicago sky", "chicago", "sky",
            "indiana fever", "indiana", "fever",
            "phoenix mercury", "phoenix", "mercury",
            "minnesota lynx", "minnesota", "lynx",
            "atlanta dream", "atlanta", "dream",
            "washington mystics", "washington", "mystics",
            "connecticut sun", "connecticut", "sun",
            "los angeles sparks", "los angeles", "sparks", "la sparks"
        ]
        
        found_teams = []
        for pattern in team_patterns:
            if pattern in request_lower:
                found_teams.append(pattern)
        
        # Check if this looks like a game analysis request
        game_analysis_keywords = ["analyze", "odds", "bet", "betting", "game", "matchup", "vs", "v", "at", "against"]
        has_analysis_intent = any(keyword in request_lower for keyword in game_analysis_keywords)
        
        # If we found teams and it looks like game analysis
        if len(found_teams) >= 2 and has_analysis_intent:
            # Map team names to full names
            team_mapping = {
                "dallas": "Dallas Wings", "wings": "Dallas Wings", "dallas wings": "Dallas Wings",
                "new york": "New York Liberty", "liberty": "New York Liberty", "ny": "New York Liberty", "new york liberty": "New York Liberty",
                "las vegas": "Las Vegas Aces", "aces": "Las Vegas Aces", "lv": "Las Vegas Aces", "las vegas aces": "Las Vegas Aces",
                "seattle": "Seattle Storm", "storm": "Seattle Storm", "seattle storm": "Seattle Storm",
                "chicago": "Chicago Sky", "sky": "Chicago Sky", "chicago sky": "Chicago Sky",
                "indiana": "Indiana Fever", "fever": "Indiana Fever", "indiana fever": "Indiana Fever",
                "phoenix": "Phoenix Mercury", "mercury": "Phoenix Mercury", "phoenix mercury": "Phoenix Mercury",
                "minnesota": "Minnesota Lynx", "lynx": "Minnesota Lynx", "minnesota lynx": "Minnesota Lynx",
                "atlanta": "Atlanta Dream", "dream": "Atlanta Dream", "atlanta dream": "Atlanta Dream",
                "washington": "Washington Mystics", "mystics": "Washington Mystics", "washington mystics": "Washington Mystics",
                "connecticut": "Connecticut Sun", "sun": "Connecticut Sun", "connecticut sun": "Connecticut Sun",
                "los angeles": "Los Angeles Sparks", "sparks": "Los Angeles Sparks", "la sparks": "Los Angeles Sparks", "los angeles sparks": "Los Angeles Sparks"
            }
            
            # Get the full team names
            team1 = team_mapping.get(found_teams[0], found_teams[0].title())
            team2 = team_mapping.get(found_teams[1], found_teams[1].title()) if len(found_teams) > 1 else None
            
            if team2 and team1 != team2:  # Make sure we have two different teams
                print(f"\n📊 Analyzing matchup: {team1} vs {team2}")
                games = self.get_wnba_schedule(3)  # Get next 3 days
                analysis = self.analyze_specific_game(team1, team2, games)
                
                # Try to get AI enhancement, but return analysis if AI fails
                ai_response = self.ask_openrouter(f"Enhance this game analysis with additional betting insights: {analysis}")
                
                if "Error calling OpenRouter" in ai_response or "Request error" in ai_response or "502" in ai_response:
                    return analysis + "\n\n(AI enhancement unavailable - OpenRouter server issues)"
                else:
                    return ai_response
        
        # Check if we should fetch WNBA data (simple keyword matching as fallback)
        elif "wnba" in user_request.lower() and ("game" in user_request.lower() or "schedule" in user_request.lower()):
            # Extract number of days if mentioned
            days = 3  # default
            if "3 days" in user_request.lower():
                days = 3
            elif "week" in user_request.lower():
                days = 7
            elif "tomorrow" in user_request.lower():
                days = 2
            elif "today" in user_request.lower():
                days = 1
            
            print(f"\n📊 Fetching WNBA schedule for next {days} days...")
            games = self.get_wnba_schedule(days)
            formatted_games = self.format_games_for_ai(games)
            
            # Try to get AI analysis, but fallback to raw data if it fails
            ai_response = self.ask_openrouter(f"Analyze this WNBA schedule: {formatted_games}")
            
            # If AI fails, return the formatted data directly
            if "Error calling OpenRouter" in ai_response or "Request error" in ai_response:
                return f"Here's the WNBA schedule data (AI analysis unavailable - OpenRouter server issues):\n\n{formatted_games}"
            else:
                return ai_response
        
        else:
            # For other requests, try AI or provide helpful message
            ai_response = self.ask_openrouter(user_request)
            
            if "Error calling OpenRouter" in ai_response or "Request error" in ai_response:
                return "OpenRouter is currently experiencing server issues (502 Bad Gateway). I can still help you with WNBA schedule data and game analysis. Try asking: 'analyze dallas wings vs new york liberty'"
            else:
                return ai_response

def main():
    """Main interactive loop"""
    print("🏀 Sports AI Agent - Powered by OpenRouter + ESPN API")
    print("=" * 60)
    print("Ask me about sports data! Examples:")
    print("- 'Give me the WNBA games for the next 3 days'")
    print("- 'What WNBA games are happening this week?'")
    print("- 'Show me tomorrow's WNBA schedule'")
    print("Type 'quit' to exit.\n")
    
    try:
        agent = SportsAIAgent()
        
        while True:
            user_input = input("🎯 Your request: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                response = agent.process_request(user_input)
                print(f"\n🤖 AI Response:\n{response}\n")
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ Error processing request: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize Sports AI Agent: {e}")
        print("Make sure your OPENROUTER_API_KEY is set in .env.local")

if __name__ == "__main__":
    main()