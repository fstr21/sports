#!/usr/bin/env python3
"""
Sports AI Chat Interface

Interactive CLI for asking natural language questions to your Sports MCP API.

Usage:
    python ask_sports.py

Examples:
    - "What NBA games are today?"
    - "Show me all NBA teams" 
    - "Give me today's sports summary"
    - "What Premier League games happened this week?"
"""

import requests
import json
import sys
import os
from typing import Dict, Any

class SportsAI:
    def __init__(self, base_url: str = None, api_key: str = None):
        # Default to Railway URL or localhost
        self.base_url = base_url or os.getenv("SPORTS_API_URL", "https://web-production-b939f.up.railway.app")
        self.api_key = api_key or os.getenv("SPORTS_API_KEY", "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Available models
        self.models = [
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-pro"
        ]
        
        self.current_model = self.models[0]  # Default model
    
    def ask(self, question: str, model: str = None) -> Dict[str, Any]:
        """Ask a natural language question"""
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                json={
                    "question": question,
                    "model": model or self.current_model
                },
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "ok": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "ok": False,
                "error": "Connection error",
                "message": str(e)
            }
    
    def test_connection(self) -> bool:
        """Test if the API is working"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def change_model(self, model: str):
        """Change the AI model"""
        if model in self.models:
            self.current_model = model
            return True
        return False
    
    def list_models(self) -> list:
        """Get available models"""
        return self.models

def format_response(response: Dict[str, Any]) -> str:
    """Format the API response for display"""
    if not response.get("ok"):
        return f"Error: {response.get('message', 'Unknown error')}"
    
    output = []
    
    # Show what the AI understood
    if response.get("interpretation"):
        output.append(f"[AI Understanding]: {response['interpretation']}")
    
    # Show the result
    result = response.get("result", {})
    if result.get("ok"):
        data = result.get("data", {})
        
        # Format different types of results
        if "scoreboard" in data:
            scoreboard = data["scoreboard"]
            events = scoreboard.get("events", [])
            output.append(f"\nFound {len(events)} games:")
            for event in events[:5]:  # Show first 5 games
                home = event.get("home", {})
                away = event.get("away", {})
                status = event.get("status", "unknown")
                
                if home.get("score") and away.get("score"):
                    output.append(f"  {away.get('displayName', 'Team')} {away.get('score')} - {home.get('score')} {home.get('displayName', 'Team')} ({status})")
                else:
                    output.append(f"  {away.get('displayName', 'Team')} @ {home.get('displayName', 'Team')} ({status})")
            
            if len(events) > 5:
                output.append(f"  ... and {len(events) - 5} more games")
        
        elif "teams" in data:
            teams = data["teams"]
            output.append(f"\nFound {len(teams)} teams:")
            for team in teams[:10]:  # Show first 10 teams
                output.append(f"  {team.get('displayName', 'Team')} ({team.get('abbrev', 'N/A')})")
            
            if len(teams) > 10:
                output.append(f"  ... and {len(teams) - 10} more teams")
        
        elif isinstance(data, dict) and any(k.count("/") for k in data.keys()):
            # Daily intelligence format
            output.append("\nDaily Sports Summary:")
            for league, league_data in data.items():
                if "/" in league:
                    games = league_data.get("games", {}).get("events", []) if league_data.get("games") else []
                    output.append(f"  {league.upper()}: {len(games)} games")
        
        else:
            # Generic data display
            output.append(f"\nResult: {json.dumps(data, indent=2)}")
    
    else:
        output.append(f"\nData Error: {result.get('message', 'No data available')}")
    
    return "\n".join(output)

def main():
    print("Sports AI Chat Interface")
    print("=" * 40)
    print("Ask me anything about sports!")
    print("Type 'help' for examples, 'models' to change AI model, 'quit' to exit")
    print()
    
    # Initialize the Sports AI client
    sports_ai = SportsAI()
    
    # Test connection
    print("Testing connection to API...")
    if sports_ai.test_connection():
        print("[OK] Connected to Sports API")
    else:
        print("[ERROR] Cannot connect to Sports API")
        print("Make sure your server is running or check your URL/API key")
        return
    
    print(f"[INFO] Using model: {sports_ai.current_model}")
    print()
    
    # Main chat loop
    while True:
        try:
            question = input("Ask about sports > ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            elif question.lower() == 'help':
                print("""
Example questions you can ask:
- "What NBA games are today?"
- "Show me all NBA teams"
- "Give me today's sports summary"
- "What Premier League games happened this week?"
- "How many NFL teams are there?"
- "What basketball games are scheduled?"
- "Show me hockey teams"

Commands:
- 'models' - Change AI model
- 'quit' - Exit the program
""")
                continue
            
            elif question.lower() == 'models':
                print("\nAvailable AI models:")
                for i, model in enumerate(sports_ai.list_models(), 1):
                    current = " (current)" if model == sports_ai.current_model else ""
                    print(f"{i}. {model}{current}")
                
                try:
                    choice = input("\nSelect model (1-{}): ".format(len(sports_ai.models))).strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(sports_ai.models):
                        new_model = sports_ai.models[int(choice) - 1]
                        sports_ai.change_model(new_model)
                        print(f"[OK] Switched to {new_model}")
                    else:
                        print("[ERROR] Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("[ERROR] Invalid selection")
                continue
            
            # Ask the question
            print(f"[AI] Thinking...")
            response = sports_ai.ask(question)
            
            # Display the formatted response
            formatted_response = format_response(response)
            print("\n" + formatted_response + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {str(e)}\n")

if __name__ == "__main__":
    main()