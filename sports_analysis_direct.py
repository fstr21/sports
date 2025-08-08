#!/usr/bin/env python3
"""
Sports Betting Analysis System - Direct API Version

This script provides sports betting analysis using The Odds API directly,
without MCP servers. This serves as the truth test for MCP implementations.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Load environment variables
env_file = Path('.env.local')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class DirectSportsAnalysis:
    """Sports betting analysis using direct API calls only."""
    
    def __init__(self):
        """Initialize with API keys."""
        self.odds_api_key = os.environ.get('ODDS_API_KEY')
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.openrouter_model = os.environ.get('OPENROUTER_MODEL', 'openai/gpt-oss-20b:free')
        
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY not found in .env.local")
        
        # Sport mappings for The Odds API
        self.sport_keys = {
            'nfl': ['americanfootball_nfl', 'americanfootball_nfl_preseason'],  # Check both
            'nba': ['basketball_nba', 'basketball_nba_preseason'],
            'wnba': ['basketball_wnba'],
            'mlb': ['baseball_mlb', 'baseball_mlb_preseason'],
            'nhl': ['icehockey_nhl'],
            'soccer': ['soccer_usa_mls'],
            'mls': ['soccer_usa_mls'],
            'premier': ['soccer_epl'],
            'ncaaf': ['americanfootball_ncaaf'],
            'ncaab': ['basketball_ncaab', 'basketball_ncaab_preseason']
        }
    
    def get_available_sports(self):
        """Get list of available sports from The Odds API."""
        try:
            response = requests.get(
                "https://api.the-odds-api.com/v4/sports",
                params={"apiKey": self.odds_api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                sports_data = response.json()
                return sports_data
            else:
                return f"Error getting sports: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_odds_for_sport(self, sport_keys, regions="us", markets="h2h,spreads,totals", odds_format="american"):
        """Get odds for a sport, checking multiple endpoints if needed."""
        all_games = []
        
        # If sport_keys is a string, convert to list
        if isinstance(sport_keys, str):
            sport_keys = [sport_keys]
        
        for sport_key in sport_keys:
            try:
                print(f"   Checking {sport_key}...")
                response = requests.get(
                    f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds",
                    params={
                        "apiKey": self.odds_api_key,
                        "regions": regions,
                        "markets": markets,
                        "oddsFormat": odds_format
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    games = response.json()
                    if games:
                        print(f"   ✅ Found {len(games)} games in {sport_key}")
                        all_games.extend(games)
                    else:
                        print(f"   📭 No games in {sport_key}")
                else:
                    print(f"   ❌ Error in {sport_key}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error in {sport_key}: {str(e)}")
        
        if not all_games:
            return {"error": "No games found in any endpoint"}
        
        # Sort games by commence_time
        all_games.sort(key=lambda x: x['commence_time'])
        return all_games
    
    def format_odds_display(self, odds_data, sport_name, filter_date=None):
        """Format odds data for display."""
        if isinstance(odds_data, dict) and "error" in odds_data:
            return f"❌ Error getting {sport_name} odds: {odds_data['error']}"
        
        if not odds_data:
            return f"📭 No {sport_name} games found with current odds."
        
        # Filter for specific date if requested
        if filter_date:
            filtered_games = []
            for game in odds_data:
                game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                game_date = game_time.strftime('%Y-%m-%d')
                if game_date == filter_date:
                    filtered_games.append(game)
            odds_data = filtered_games
            
            if not odds_data:
                return f"📭 No {sport_name} games found for {filter_date}."
        
        formatted = f"🏆 {sport_name.upper()} PRESEASON BETTING ODDS\n"
        if filter_date:
            formatted = f"🏆 {sport_name.upper()} PRESEASON ODDS - {filter_date}\n"
        formatted += "=" * 60 + "\n\n"
        
        for i, game in enumerate(odds_data[:10], 1):  # Show up to 10 games
            formatted += f"{i}. {game['away_team']} @ {game['home_team']}\n"
            
            # Format game time
            game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            formatted += f"   🕐 {game_time.strftime('%A, %B %d at %I:%M %p ET')}\n"
            
            if game['bookmakers']:
                bookmaker = game['bookmakers'][0]  # Use first bookmaker
                formatted += f"   📊 {bookmaker['title']}\n"
                
                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':
                        formatted += "   💰 Moneyline: "
                        for outcome in market['outcomes']:
                            price = outcome['price']
                            if price > 0:
                                formatted += f"{outcome['name']} +{price}  "
                            else:
                                formatted += f"{outcome['name']} {price}  "
                        formatted += "\n"
                    
                    elif market['key'] == 'spreads':
                        formatted += "   📈 Spread: "
                        for outcome in market['outcomes']:
                            point = outcome.get('point', 0)
                            price = outcome['price']
                            if price > 0:
                                formatted += f"{outcome['name']} {point:+.1f} (+{price})  "
                            else:
                                formatted += f"{outcome['name']} {point:+.1f} ({price})  "
                        formatted += "\n"
                    
                    elif market['key'] == 'totals':
                        formatted += "   🎯 Total: "
                        for outcome in market['outcomes']:
                            point = outcome.get('point', 0)
                            price = outcome['price']
                            if price > 0:
                                formatted += f"{outcome['name']} {point} (+{price})  "
                            else:
                                formatted += f"{outcome['name']} {point} ({price})  "
                        formatted += "\n"
            
            formatted += "\n"
        
        return formatted
    
    def detect_sport_from_query(self, query):
        """Detect sport from user query."""
        query_lower = query.lower()
        
        # Check WNBA first since it contains "nba"
        if any(word in query_lower for word in ['wnba', 'women basketball', 'womens basketball']):
            return 'wnba'
        elif any(word in query_lower for word in ['nfl', 'football', 'american football', 'preseason']):
            return 'nfl'
        elif any(word in query_lower for word in ['nba', 'basketball', 'lakers', 'warriors']):
            return 'nba'
        elif any(word in query_lower for word in ['mlb', 'baseball', 'yankees', 'dodgers']):
            return 'mlb'
        elif any(word in query_lower for word in ['nhl', 'hockey']):
            return 'nhl'
        elif any(word in query_lower for word in ['soccer', 'mls', 'premier league']):
            return 'soccer'
        elif any(word in query_lower for word in ['ncaaf', 'college football']):
            return 'ncaaf'
        elif any(word in query_lower for word in ['ncaab', 'college basketball']):
            return 'ncaab'
        else:
            return 'nfl'  # Default to NFL preseason
    
    def get_ai_analysis(self, query, odds_data, sport_name):
        """Get AI analysis using OpenRouter."""
        if not self.openrouter_api_key:
            return self.get_basic_analysis(odds_data, sport_name)
        
        # Create prompt with real odds data
        if isinstance(odds_data, list) and odds_data:
            odds_sample = json.dumps(odds_data[:3], indent=2)
        else:
            odds_sample = "No games available"
            
        prompt = f"""You are a professional sports betting analyst. Analyze these real {sport_name.upper()} betting odds and provide specific recommendations.

User Question: {query}

Current {sport_name.upper()} Odds Data:
{odds_sample}

Provide specific betting recommendations with clear reasoning. Format your response for terminal display:
- Use simple text formatting, NO markdown tables
- Use bullet points (•) and dashes (-) for lists  
- Keep lines under 80 characters
- Include specific bet recommendations with reasoning

Include these sections:
🎯 TOP BETTING RECOMMENDATIONS
💰 BEST VALUE BETS
📊 KEY INSIGHTS
⚠️ RISK FACTORS"""

        try:
            response = requests.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://localhost:3000",
                    "X-Title": "Sports Betting Analysis"
                },
                json={
                    "model": self.openrouter_model,
                    "messages": [
                        {"role": "system", "content": "You are a professional sports betting analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
            
        except Exception as e:
            pass
        
        return self.get_basic_analysis(odds_data, sport_name)
    
    def get_basic_analysis(self, odds_data, sport_name):
        """Provide basic analysis when AI is unavailable."""
        if not odds_data:
            return f"No {sport_name} games available for analysis."
        
        analysis = f"""📊 BASIC {sport_name.upper()} ANALYSIS

🎯 GENERAL RECOMMENDATIONS:
• Look for value in underdog moneylines with reasonable odds
• Consider home field advantage in close spread bets
• Check for totals that seem off based on team averages
• Monitor line movement before placing bets

💰 BETTING STRATEGY:
• Start with smaller bet sizes to test your analysis
• Focus on games you know the teams well
• Avoid betting on every game - be selective
• Consider bankroll management (1-3% per bet)

⚠️ RISK FACTORS:
• Injury reports can significantly impact odds
• Weather conditions for outdoor sports
• Back-to-back games may affect performance
• Public betting can skew lines

📈 CURRENT MARKET:
• {len(odds_data)} games available with odds
• Multiple sportsbooks offering competitive lines
• Various bet types available (moneyline, spread, totals)

Note: For AI-powered analysis, ensure OPENROUTER_API_KEY is set in .env.local"""
        
        return analysis
    
    def process_query(self, query):
        """Process user query and return analysis."""
        print(f"\n🔍 Processing: '{query}'")
        
        # Detect sport
        sport = self.detect_sport_from_query(query)
        sport_keys = self.sport_keys.get(sport, ['americanfootball_nfl'])
        
        print(f"🏆 Detected sport: {sport.upper()}")
        print(f"📡 Will check endpoints: {', '.join(sport_keys)}")
        
        # Check if user is asking about a specific date
        filter_date = None
        if 'august 8' in query.lower() or '8/8' in query.lower():
            filter_date = '2025-08-08'
            print(f"📅 Filtering for date: {filter_date}")
        
        # Get odds data from all relevant endpoints
        print("💰 Fetching live odds from The Odds API...")
        odds_data = self.get_odds_for_sport(sport_keys)
        
        # Format odds display
        odds_display = self.format_odds_display(odds_data, sport, filter_date)
        
        # Get AI analysis
        print("🤖 Generating analysis...")
        ai_analysis = self.get_ai_analysis(query, odds_data, sport)
        
        return f"{odds_display}\n{ai_analysis}"
    
    def run_interactive(self):
        """Run interactive interface."""
        print("=" * 80)
        print("🏈 DIRECT SPORTS BETTING ANALYSIS")
        print("=" * 80)
        print()
        print("This system uses The Odds API directly (no MCP servers)")
        print("Available sports: NFL, NBA, WNBA, MLB, NHL, MLS, NCAAF, NCAAB")
        print()
        print("Example queries:")
        print('• "Show me NFL odds and best bets"')
        print('• "What are the best NBA value plays tonight?"')
        print('• "Analyze WNBA games for today"')
        print('• "Give me MLB betting recommendations"')
        print()
        print("Type 'sports' to see available sports")
        print("Type 'quit' to exit")
        print("=" * 80)
        
        while True:
            try:
                query = input("\n💬 Your question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using Direct Sports Analysis!")
                    break
                
                if query.lower() == 'sports':
                    print("\n📋 Getting available sports...")
                    sports = self.get_available_sports()
                    if isinstance(sports, list):
                        print("\n🏆 AVAILABLE SPORTS:")
                        for sport in sports:
                            if sport.get('active', True):
                                print(f"• {sport['title']} ({sport['key']})")
                    else:
                        print(f"Error: {sports}")
                    continue
                
                # Process query
                start_time = time.time()
                result = self.process_query(query)
                end_time = time.time()
                
                # Display results
                print("\n" + "=" * 80)
                print("📊 ANALYSIS RESULTS")
                print("=" * 80)
                print(result)
                print("=" * 80)
                print(f"⏱️ Completed in {end_time - start_time:.2f} seconds")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using Direct Sports Analysis!")
                break
            except EOFError:
                print("\n\n👋 Thanks for using Direct Sports Analysis!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                # Don't continue the loop if there's a persistent error
                if "EOF" in str(e):
                    break

def main():
    """Main function."""
    try:
        system = DirectSportsAnalysis()
        system.run_interactive()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease check your .env.local file and ensure ODDS_API_KEY is set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ System Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()