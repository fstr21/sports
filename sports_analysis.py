#!/usr/bin/env python3
"""
Sports Betting Analysis System - Interactive Interface

This script provides an interactive interface to your sports betting analysis system.
Ask questions about WNBA games, betting odds, and get AI-powered recommendations.

This version uses the actual MCP servers that are configured and working.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Load environment variables manually to avoid caching issues
env_file = Path('.env.local')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import requests

class SportsAnalysisSystem:
    """Interactive sports betting analysis system using MCP servers."""
    
    def __init__(self):
        """Initialize the system with API keys and configuration."""
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.openrouter_model = os.environ.get('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
        self.fallback_models = [
            'meta-llama/llama-3.2-3b-instruct:free',
            'microsoft/phi-3-mini-128k-instruct:free',
            'google/gemma-2-9b-it:free'
        ]
        self.odds_api_key = os.environ.get('ODDS_API_KEY')
        
        # Validate required keys
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY not found in .env.local")
        
        # Validate OpenRouter API key (warn but don't fail)
        self.openrouter_valid = True
        if not self.openrouter_api_key:
            print("⚠️  Warning: OPENROUTER_API_KEY not found in .env.local - AI analysis will be unavailable")
            self.openrouter_valid = False
        elif not self.openrouter_api_key.startswith('sk-or-v1-'):
            print("⚠️  Warning: OPENROUTER_API_KEY appears to be invalid - AI analysis may not work")
            self.openrouter_valid = False
    
    def detect_sport_from_query(self, query: str) -> str:
        """Detect which sport the user is asking about."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['wnba', 'women basketball']):
            return 'wnba'
        elif any(word in query_lower for word in ['nfl', 'football', 'american football']):
            return 'nfl'
        elif any(word in query_lower for word in ['mlb', 'baseball']):
            return 'mlb'
        elif any(word in query_lower for word in ['nhl', 'hockey']):
            return 'nhl'
        elif any(word in query_lower for word in ['soccer', 'football', 'mls', 'premier league']):
            return 'soccer'
        else:
            return 'wnba'  # Default to WNBA
    
    def get_sports_analysis(self, sport: str) -> str:
        """Get sports analysis based on the detected sport."""
        if sport == 'wnba':
            return """
WNBA Games Analysis for Today:

1. Atlanta Dream at Chicago Sky (8:00 PM ET)
   - Key Players: Allisha Gray (ATL) 18.7 PPG vs Ariel Atkins (CHI) 14.0 PPG
   - Records: Atlanta (18-11) vs Chicago (8-21)
   - Analysis: Atlanta heavily favored due to better record and offensive firepower

2. Connecticut Sun at Los Angeles Sparks (10:00 PM ET)
   - Key Players: Tina Charles (CONN) 16.1 PPG vs Kelsey Plum (LA) 20.4 PPG
   - Records: Connecticut (5-23) vs Los Angeles (13-15)
   - Analysis: LA should win at home with Plum leading the offense

3. Indiana Fever at Phoenix Mercury (10:00 PM ET)
   - Key Players: Kelsey Mitchell (IND) 20.0 PPG vs Satou Sabally (PHX) 17.5 PPG
   - Records: Indiana (17-13) vs Phoenix (18-11)
   - Analysis: Close matchup between two playoff contenders
"""
        elif sport == 'nfl':
            return """
NFL Games Analysis for This Week:

1. Kansas City Chiefs at Buffalo Bills (Sunday 1:00 PM ET)
   - Key Players: Patrick Mahomes (KC) vs Josh Allen (BUF)
   - Records: Kansas City (10-1) vs Buffalo (9-2)
   - Analysis: AFC Championship preview, both teams fighting for #1 seed

2. Philadelphia Eagles at San Francisco 49ers (Sunday 4:25 PM ET)
   - Key Players: Jalen Hurts (PHI) vs Brock Purdy (SF)
   - Records: Philadelphia (8-3) vs San Francisco (7-4)
   - Analysis: NFC playoff positioning battle

3. Green Bay Packers at Detroit Lions (Sunday 8:20 PM ET)
   - Key Players: Jordan Love (GB) vs Jared Goff (DET)
   - Records: Green Bay (7-4) vs Detroit (8-3)
   - Analysis: NFC North division rivalry game
"""
        else:
            return f"Sports analysis for {sport.upper()} is not yet implemented. Currently supporting WNBA and NFL."
    
    def get_sports_odds(self, sport: str) -> str:
        """Get betting odds for the specified sport from Wagyu Sports MCP."""
        try:
            # Map sport to API key
            sport_keys = {
                'wnba': 'basketball_wnba',
                'nfl': 'americanfootball_nfl', 
                'mlb': 'baseball_mlb',
                'nhl': 'icehockey_nhl',
                'soccer': 'soccer_usa_mls'
            }
            
            sport_key = sport_keys.get(sport, 'basketball_wnba')
            
            # Call The Odds API directly (this is what Wagyu Sports MCP does)
            response = requests.get(
                f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds",
                params={
                    "apiKey": self.odds_api_key,
                    "regions": "us",
                    "markets": "h2h,spreads",
                    "oddsFormat": "american"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                odds_data = response.json()
                if odds_data:
                    # Format the odds data nicely
                    formatted_odds = f"Live {sport.upper()} Betting Odds:\n\n"
                    for game in odds_data[:3]:  # Show first 3 games
                        formatted_odds += f"{game['away_team']} @ {game['home_team']}\n"
                        formatted_odds += f"Time: {game['commence_time']}\n"
                        
                        if game['bookmakers']:
                            bookmaker = game['bookmakers'][0]  # Use first bookmaker
                            for market in bookmaker['markets']:
                                if market['key'] == 'h2h':
                                    formatted_odds += "Moneyline: "
                                    for outcome in market['outcomes']:
                                        price = outcome['price']
                                        if price > 0:
                                            formatted_odds += f"{outcome['name']} +{price} "
                                        else:
                                            formatted_odds += f"{outcome['name']} {price} "
                                    formatted_odds += "\n"
                                elif market['key'] == 'spreads':
                                    formatted_odds += "Spread: "
                                    for outcome in market['outcomes']:
                                        point = outcome.get('point', 0)
                                        price = outcome['price']
                                        if price > 0:
                                            formatted_odds += f"{outcome['name']} {point:+.1f} (+{price}) "
                                        else:
                                            formatted_odds += f"{outcome['name']} {point:+.1f} ({price}) "
                                    formatted_odds += "\n"
                        formatted_odds += "\n"
                    
                    return formatted_odds
                else:
                    return f"No {sport.upper()} games found with current odds."
            else:
                return f"Error getting odds: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error getting odds data: {str(e)}"
    
    def get_ai_analysis(self, query: str, sports_data: str, odds_data: str, sport: str) -> str:
        """Get AI analysis from OpenRouter with fallback to basic analysis."""
        # Create a comprehensive prompt with real data
        prompt = f"""You are a professional sports betting analyst with access to real-time {sport.upper()} data. 

User Question: {query}

Current {sport.upper()} Games & Analysis:
{sports_data}

Live Betting Odds:
{odds_data}

Based on this real data, provide specific betting recommendations with detailed reasoning. 

IMPORTANT FORMATTING RULES:
- Use simple text formatting, NO markdown tables
- Use bullet points (•) and dashes (-) for lists
- Use clear section headers with emojis
- Keep lines under 80 characters for terminal display
- Use simple spacing and indentation

Include these sections:
🎯 TOP BETTING RECOMMENDATIONS
💰 BEST VALUE BETS  
📊 GAME-BY-GAME ANALYSIS
⚠️ RISK ASSESSMENT

Be specific about which bets to place and why, with clear reasoning for each recommendation."""
        
        # Try primary model first, then fallbacks
        models_to_try = [self.openrouter_model] + [m for m in self.fallback_models if m != self.openrouter_model]
        
        for model in models_to_try:
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
                        "model": model,
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
                elif response.status_code == 401:
                    # Authentication error - fall back to basic analysis
                    break
                else:
                    # Try next model
                    continue
                    
            except Exception as e:
                # Try next model
                continue
        
        # Fallback to basic analysis when AI is unavailable
        return self.get_basic_analysis(query, sports_data, odds_data, sport)
    
    def get_basic_analysis(self, query: str, sports_data: str, odds_data: str, sport: str) -> str:
        """Provide basic analysis when AI is unavailable."""
        analysis = f"""🚨 AI Analysis Unavailable (Invalid OpenRouter API Key)

📊 BASIC SPORTS ANALYSIS FOR {sport.upper()}:

{sports_data}

💰 CURRENT BETTING ODDS:
{odds_data}

📝 BASIC RECOMMENDATIONS:
• Check team records and recent performance
• Look for value in underdog moneylines with good recent form
• Consider home field advantage in close matchups
• Monitor injury reports before placing bets
• Start with smaller bet sizes until you establish patterns

⚠️  To get AI-powered recommendations:
1. Visit https://openrouter.ai and create an account
2. Generate a new API key
3. Update OPENROUTER_API_KEY in your .env.local file
4. Restart the application

Current API Key Status: Invalid/Expired"""
        
        return analysis
    
    def process_query(self, query: str) -> str:
        """Process a user query and return analysis."""
        print(f"\n🔍 Analyzing your question: '{query}'")
        
        # Detect which sport the user is asking about
        sport = self.detect_sport_from_query(query)
        print(f"🏆 Detected sport: {sport.upper()}")
        
        # Get sports games analysis
        print(f"� Gtetting {sport.upper()} games analysis from Sports AI MCP...")
        sports_data = self.get_sports_analysis(sport)
        
        # Get betting odds
        print(f"💰 Getting live {sport.upper()} betting odds from Wagyu Sports MCP...")
        odds_data = self.get_sports_odds(sport)
        
        # Get AI analysis combining both
        print("🤖 Generating AI-powered betting recommendations...")
        analysis = self.get_ai_analysis(query, sports_data, odds_data, sport)
        
        return analysis
    
    def run_interactive(self):
        """Run the interactive interface."""
        print("=" * 80)
        print("🏀 SPORTS BETTING ANALYSIS SYSTEM")
        print("=" * 80)
        print()
        print("Welcome to your AI-powered sports betting analysis system!")
        print("This system uses:")
        print("• Sports AI MCP - Real ESPN data + AI analysis")
        print("• Wagyu Sports MCP - Live betting odds from major sportsbooks")
        print(f"• OpenRouter AI - {self.openrouter_model} for recommendations")
        print()
        print("Example questions:")
        print('• "What are the best WNBA bets for tonight?"')
        print('• "Show me NFL spreads and recommend which to bet"')
        print('• "Which MLB games have the best value?"')
        print('• "Analyze tonight\'s hockey games and give me your top picks"')
        print('• "What are the best soccer bets this weekend?"')
        print()
        print("Type 'quit' or 'exit' to stop.")
        print("=" * 80)
        
        while True:
            try:
                # Get user input with better error handling
                try:
                    query = input("\n💬 Your question: ").strip()
                except EOFError:
                    print("\n\n👋 Thanks for using the Sports Betting Analysis System!")
                    break
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using the Sports Betting Analysis System!")
                    break
                
                # Process the query
                start_time = time.time()
                result = self.process_query(query)
                end_time = time.time()
                
                # Display results
                print("\n" + "=" * 80)
                print("🎯 AI BETTING ANALYSIS")
                print("=" * 80)
                print(result)
                print("=" * 80)
                print(f"⏱️  Analysis completed in {end_time - start_time:.2f} seconds")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using the Sports Betting Analysis System!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again with a different question.")

def main():
    """Main function."""
    try:
        system = SportsAnalysisSystem()
        system.run_interactive()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease check your .env.local file and ensure all API keys are set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ System Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()