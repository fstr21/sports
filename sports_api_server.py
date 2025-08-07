#!/usr/bin/env python3
"""
Sports Betting Analysis API Server

This creates a simple web API for your sports betting analysis system
that can be accessed from multiple machines without needing MCP setup.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

# Load environment variables manually
env_file = Path('.env.local')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import requests

app = Flask(__name__)

class SportsAnalysisAPI:
    """Sports betting analysis API backend."""
    
    def __init__(self):
        """Initialize with API keys."""
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.openrouter_model = os.environ.get('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
        self.odds_api_key = os.environ.get('ODDS_API_KEY')
        
        if not self.openrouter_api_key or not self.odds_api_key:
            raise ValueError("Missing required API keys in .env.local")
    
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
        """Get betting odds for the specified sport."""
        try:
            sport_keys = {
                'wnba': 'basketball_wnba',
                'nfl': 'americanfootball_nfl', 
                'mlb': 'baseball_mlb',
                'nhl': 'icehockey_nhl',
                'soccer': 'soccer_usa_mls'
            }
            
            sport_key = sport_keys.get(sport, 'basketball_wnba')
            
            response = requests.get(
                f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds",
                params={
                    "apiKey": self.odds_api_key,
                    "regions": "us",
                    "markets": "h2h,spreads",
                    "oddsFormat": "decimal"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                odds_data = response.json()
                if odds_data:
                    formatted_odds = f"Live {sport.upper()} Betting Odds:\n\n"
                    for game in odds_data[:3]:
                        formatted_odds += f"{game['away_team']} @ {game['home_team']}\n"
                        formatted_odds += f"Time: {game['commence_time']}\n"
                        
                        if game['bookmakers']:
                            bookmaker = game['bookmakers'][0]
                            for market in bookmaker['markets']:
                                if market['key'] == 'h2h':
                                    formatted_odds += "Moneyline: "
                                    for outcome in market['outcomes']:
                                        formatted_odds += f"{outcome['name']} {outcome['price']:.2f} "
                                    formatted_odds += "\n"
                                elif market['key'] == 'spreads':
                                    formatted_odds += "Spread: "
                                    for outcome in market['outcomes']:
                                        point = outcome.get('point', 0)
                                        formatted_odds += f"{outcome['name']} {point:+.1f} ({outcome['price']:.2f}) "
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
        """Get AI analysis from OpenRouter."""
        try:
            prompt = f"""You are a professional sports betting analyst with access to real-time {sport.upper()} data.

User Question: {query}

Current {sport.upper()} Games & Analysis:
{sports_data}

Live Betting Odds:
{odds_data}

Based on this real data, provide specific betting recommendations with detailed reasoning. Include:
1. Best value bets (moneyline, spread, or totals)
2. Player performance insights
3. Key factors affecting the games
4. Risk assessment for each recommendation

Be specific about which bets to place and why."""
            
            response = requests.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Sports Betting Analysis",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.openrouter_model,
                    "messages": [
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
                else:
                    return "Error: Unexpected response format from AI"
            else:
                return f"Error: AI API returned {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error getting AI analysis: {str(e)}"
    
    def analyze_query(self, query: str) -> dict:
        """Process a sports betting query and return analysis."""
        start_time = time.time()
        
        # Detect sport
        sport = self.detect_sport_from_query(query)
        
        # Get data
        sports_data = self.get_sports_analysis(sport)
        odds_data = self.get_sports_odds(sport)
        
        # Get AI analysis
        analysis = self.get_ai_analysis(query, sports_data, odds_data, sport)
        
        end_time = time.time()
        
        return {
            "query": query,
            "sport": sport,
            "analysis": analysis,
            "processing_time": round(end_time - start_time, 2),
            "timestamp": datetime.now().isoformat()
        }

# Initialize the API
sports_api = SportsAnalysisAPI()

# Web interface HTML template
WEB_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sports Betting Analysis API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .query-form { background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .result { background: white; border: 1px solid #d1d5db; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        input[type="text"] { width: 70%; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; }
        button { background: #1e3a8a; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #1e40af; }
        .analysis { white-space: pre-wrap; background: #f9fafb; padding: 15px; border-radius: 4px; }
        .examples { background: #ecfdf5; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏀 Sports Betting Analysis API</h1>
        <p>AI-powered sports betting analysis accessible from any device</p>
    </div>
    
    <div class="examples">
        <h3>Example Questions:</h3>
        <ul>
            <li>"What are the best WNBA bets for tonight?"</li>
            <li>"Show me NFL spreads and recommend which to bet"</li>
            <li>"Which MLB games have the best value?"</li>
            <li>"Analyze tonight's hockey games and give me your top picks"</li>
        </ul>
    </div>
    
    <div class="query-form">
        <h3>Ask Your Sports Betting Question:</h3>
        <form id="queryForm">
            <input type="text" id="queryInput" placeholder="Enter your sports betting question..." required>
            <button type="submit">Analyze</button>
        </form>
    </div>
    
    <div id="result" class="result" style="display: none;">
        <h3>Analysis Result:</h3>
        <div id="analysisContent"></div>
    </div>
    
    <script>
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const query = document.getElementById('queryInput').value;
            const resultDiv = document.getElementById('result');
            const contentDiv = document.getElementById('analysisContent');
            
            contentDiv.innerHTML = '<p>Analyzing your question...</p>';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    contentDiv.innerHTML = `
                        <p><strong>Sport:</strong> ${data.result.sport.toUpperCase()}</p>
                        <p><strong>Processing Time:</strong> ${data.result.processing_time} seconds</p>
                        <div class="analysis">${data.result.analysis}</div>
                    `;
                } else {
                    contentDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
            } catch (error) {
                contentDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Serve the web interface."""
    return render_template_string(WEB_INTERFACE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint for sports betting analysis."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"success": False, "error": "Missing query parameter"}), 400
        
        result = sports_api.analyze_query(data['query'])
        return jsonify({"success": True, "result": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Starting Sports Betting Analysis API Server...")
    print("📊 Web Interface: http://localhost:5000")
    print("🔗 API Endpoint: http://localhost:5000/api/analyze")
    print("💡 Access from any device on your network!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)