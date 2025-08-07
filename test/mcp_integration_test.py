#!/usr/bin/env python3
"""
MCP Integration Test Script

Tests both Sports AI MCP and Wagyu Sports MCP working together with OpenRouter LLM.
Provides detailed logging to troubleshoot data flow and integration.
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

class MCPIntegrationTester:
    """Test script for MCP integration with OpenRouter LLM."""
    
    def __init__(self):
        """Initialize the tester with API keys and configuration."""
        self.log_entries = []  # Initialize log_entries first
        
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'openrouter/horizon-beta')
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        
        # Log the configuration for debugging
        self.log(f"OpenRouter API Key: {self.openrouter_api_key[:20]}..." if self.openrouter_api_key else "None")
        self.log(f"OpenRouter Base URL: {self.openrouter_base_url}")
        self.log(f"OpenRouter Model: {self.openrouter_model}")
        self.log(f"Odds API Key: {self.odds_api_key[:20]}..." if self.odds_api_key else "None")
        
        # Validate required keys
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY not found in environment")
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.log_entries.append(log_entry)
        
    def detect_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the user query to determine what data is needed."""
        self.log("Analyzing user query for intent...")
        
        intent = {
            'sports': [],
            'timeframe': 'today',
            'bet_types': [],
            'needs_odds': False,
            'needs_games': False,
            'needs_analysis': False
        }
        
        query_lower = query.lower()
        
        # Detect sports - be more specific to avoid conflicts
        if 'wnba' in query_lower:
            intent['sports'].append('basketball_wnba')
        elif 'nba' in query_lower:  # Only add NBA if WNBA not mentioned
            intent['sports'].append('basketball_nba')
        if 'nfl' in query_lower:
            intent['sports'].append('americanfootball_nfl')
        if 'mlb' in query_lower:
            intent['sports'].append('baseball_mlb')
            
        # Detect timeframe
        if 'tomorrow' in query_lower:
            intent['timeframe'] = 'tomorrow'
        elif 'today' in query_lower:
            intent['timeframe'] = 'today'
        elif 'tonight' in query_lower:
            intent['timeframe'] = 'today'
            
        # Detect bet types
        if 'spread' in query_lower:
            intent['bet_types'].append('spreads')
        if 'moneyline' in query_lower or 'money line' in query_lower:
            intent['bet_types'].append('h2h')
        if 'total' in query_lower or 'over' in query_lower or 'under' in query_lower:
            intent['bet_types'].append('totals')
            
        # Determine what data is needed
        if any(word in query_lower for word in ['odds', 'bet', 'spread', 'line', 'moneyline']):
            intent['needs_odds'] = True
        if any(word in query_lower for word in ['game', 'match', 'team', 'player']):
            intent['needs_games'] = True
        if any(word in query_lower for word in ['analyze', 'recommend', 'predict', 'why', 'should']):
            intent['needs_analysis'] = True
            
        self.log(f"Query intent detected: {json.dumps(intent, indent=2)}")
        return intent
        
    async def call_sports_ai_mcp(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Sports AI MCP to get game data and analysis."""
        self.log("Calling Sports AI MCP...")
        
        # For now, we'll simulate the MCP call since we need to integrate with actual MCP protocol
        # In a real implementation, this would use the MCP client to call the sports_ai_mcp.py
        
        try:
            # Import and use the sports AI MCP functions directly for testing
            sys.path.append('mcp')
            from sports_ai_mcp import analyze_wnba_games, analyze_nfl_games, custom_sports_analysis
            
            sports_data = {}
            
            for sport in intent['sports']:
                self.log(f"Getting {sport} data from Sports AI MCP...")
                
                if sport == 'basketball_wnba':
                    self.log(f"Calling analyze_wnba_games() for {sport}...")
                    result = await analyze_wnba_games({})
                    self.log(f"Raw result type: {type(result)}")
                    self.log(f"Raw result length: {len(str(result))}")
                    
                    # Log the raw result for debugging
                    self.log("RAW SPORTS AI MCP RESULT:")
                    self.log(str(result)[:2000] + "..." if len(str(result)) > 2000 else str(result))
                    
                    sports_data['wnba'] = json.loads(result) if isinstance(result, str) else result
                    self.log(f"Parsed sports_data keys: {list(sports_data['wnba'].keys()) if isinstance(sports_data['wnba'], dict) else 'Not a dict'}")
                elif sport == 'americanfootball_nfl':
                    result = await analyze_nfl_games({})
                    sports_data['nfl'] = json.loads(result) if isinstance(result, str) else result
                else:
                    # Use custom analysis for other sports
                    result = await custom_sports_analysis({
                        'sport': sport,
                        'prompt': f"Get current games and analysis for {sport}"
                    })
                    sports_data[sport] = json.loads(result) if isinstance(result, str) else result
                    
            self.log(f"Sports AI MCP returned data for {len(sports_data)} sports")
            return sports_data
            
        except Exception as e:
            self.log(f"Error calling Sports AI MCP: {str(e)}", "ERROR")
            self.log(f"Python path: {sys.path}", "DEBUG")
            self.log(f"Current working directory: {os.getcwd()}", "DEBUG")
            
            # Try alternative import paths
            try:
                self.log("Trying alternative import path...", "DEBUG")
                import importlib.util
                spec = importlib.util.spec_from_file_location("sports_ai_mcp", "mcp/sports_ai_mcp.py")
                sports_ai_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(sports_ai_module)
                
                # Now try calling the functions
                sports_data = {}
                for sport in intent['sports']:
                    if sport == 'basketball_wnba':
                        result = await sports_ai_module.analyze_wnba_games({})
                        sports_data['wnba'] = json.loads(result) if isinstance(result, str) else result
                        
                self.log(f"Alternative import successful, got data for {len(sports_data)} sports")
                return sports_data
                
            except Exception as e2:
                self.log(f"Alternative import also failed: {str(e2)}", "ERROR")
                return {}
            
    async def call_wagyu_sports_mcp(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Wagyu Sports MCP to get betting odds."""
        self.log("Calling Wagyu Sports MCP...")
        
        try:
            # Import the wagyu sports MCP
            sys.path.append('mcp/wagyu_sports/mcp_server')
            from odds_client_server import OddsMcpServer
            
            # Initialize the MCP server with REAL API calls
            server = OddsMcpServer(api_key=self.odds_api_key, test_mode=False)  # Use REAL API data
            
            odds_data = {}
            
            for sport in intent['sports']:
                self.log(f"Getting REAL odds for {sport} from Wagyu Sports MCP...")
                
                # Use the real odds client directly
                try:
                    if server.client:  # Make sure we have a real client (not test mode)
                        markets = "h2h,spreads,totals"  # Get all market types
                        regions = "us"  # US region
                        
                        self.log(f"Calling real API for {sport} with markets: {markets}")
                        
                        # Call the client directly
                        options = {
                            "regions": regions,
                            "markets": markets,
                            "oddsFormat": "american",
                            "dateFormat": "iso"
                        }
                        
                        result = server.client.get_odds(sport, options=options)
                        odds_data[sport] = result
                        
                        # Log the full raw data for debugging
                        self.log(f"RAW ODDS DATA for {sport}:")
                        self.log(json.dumps(result, indent=2))
                        
                        self.log(f"Successfully got real odds data for {sport}: {len(result.get('data', []))} games")
                        
                        # Log API usage
                        if hasattr(server.client, 'remaining_requests'):
                            self.log(f"API requests remaining: {server.client.remaining_requests}")
                    else:
                        self.log(f"No real client available (test mode enabled)", "ERROR")
                        
                except Exception as e:
                    self.log(f"Error getting real odds for {sport}: {str(e)}", "ERROR")
                    # Don't fallback to mock data - just skip this sport
                    continue
                
            self.log(f"Wagyu Sports MCP returned odds for {len(odds_data)} sports")
            return odds_data
            
        except Exception as e:
            self.log(f"Error calling Wagyu Sports MCP: {str(e)}", "ERROR")
            return {}
            
    def combine_data(self, sports_data: Dict[str, Any], odds_data: Dict[str, Any]) -> str:
        """Combine data from both MCPs into a formatted prompt."""
        self.log("Combining data from both MCPs...")
        
        combined_prompt = "Here is the current sports data and betting odds:\n\n"
        
        # Add sports data
        if sports_data:
            combined_prompt += "=== GAME DATA & ANALYSIS ===\n"
            for sport, data in sports_data.items():
                combined_prompt += f"\n{sport.upper()} Data:\n"
                combined_prompt += json.dumps(data, indent=2) + "\n"  # Don't truncate - send full data
                
        # Add odds data
        if odds_data:
            combined_prompt += "\n=== BETTING ODDS ===\n"
            for sport, data in odds_data.items():
                combined_prompt += f"\n{sport.upper()} Odds:\n"
                combined_prompt += json.dumps(data, indent=2) + "\n"  # Don't truncate - send full data
                
        self.log(f"Combined data length: {len(combined_prompt)} characters")
        return combined_prompt
        
    async def query_openrouter(self, user_question: str, combined_data: str) -> str:
        """Send the combined data and user question to OpenRouter LLM."""
        self.log("Sending query to OpenRouter LLM...")
        
        # Construct the full prompt
        full_prompt = f"""You are a sports betting analyst. Based on the following sports data and betting odds, please answer the user's question with detailed analysis and reasoning.

{combined_data}

User Question: {user_question}

Please provide specific recommendations with clear reasoning based on the data provided."""

        self.log(f"Sending {len(full_prompt)} characters to OpenRouter")
        self.log(f"Using model: {self.openrouter_model}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.openrouter_model,
                    "messages": [
                        {"role": "user", "content": full_prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            
            response_time = time.time() - start_time
            self.log(f"OpenRouter response received in {response_time:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                
                # Log usage statistics
                if 'usage' in result:
                    usage = result['usage']
                    self.log(f"Token usage - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                           f"Completion: {usage.get('completion_tokens', 'N/A')}, "
                           f"Total: {usage.get('total_tokens', 'N/A')}")
                
                answer = result['choices'][0]['message']['content']
                self.log(f"OpenRouter returned {len(answer)} characters")
                return answer
                
            else:
                error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                self.log(error_msg, "ERROR")
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Error calling OpenRouter: {str(e)}"
            self.log(error_msg, "ERROR")
            return f"Error: {error_msg}"
            
    def save_log(self):
        """Save the log entries to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"test/logs/mcp_test_{timestamp}.log"
        
        # Create logs directory if it doesn't exist
        os.makedirs("test/logs", exist_ok=True)
        
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.log_entries))
            
        self.log(f"Log saved to {log_file}")
        
    async def run_test(self):
        """Run the complete integration test."""
        print("=" * 80)
        print("MCP Integration Test - Sports AI + Wagyu Sports + OpenRouter")
        print("=" * 80)
        print()
        
        try:
            # Get user question
            user_question = input("Enter your sports betting question: ").strip()
            if not user_question:
                user_question = "Based on the odds for the WNBA games tomorrow can you tell me which spread bets to place and why?"
                print(f"Using default question: {user_question}")
                
            print()
            self.log("Starting MCP integration test...")
            self.log(f"User question: {user_question}")
            
            # Step 1: Analyze query intent
            intent = self.detect_query_intent(user_question)
            
            # Step 2: Get data from both MCPs
            sports_data = {}
            odds_data = {}
            
            if intent['needs_games'] or intent['needs_analysis']:
                sports_data = await self.call_sports_ai_mcp(intent)
                
            if intent['needs_odds']:
                self.log("SKIPPING Wagyu Sports MCP to preserve API quota", "INFO")
                # odds_data = await self.call_wagyu_sports_mcp(intent)
                
            # Step 3: Combine the data
            combined_data = self.combine_data(sports_data, odds_data)
            
            # Step 4: Query OpenRouter
            answer = await self.query_openrouter(user_question, combined_data)
            
            # Step 5: Display results
            print("\n" + "=" * 80)
            print("AI RESPONSE")
            print("=" * 80)
            print(answer)
            print("=" * 80)
            
            # Save log
            self.save_log()
            
        except Exception as e:
            self.log(f"Test failed with error: {str(e)}", "ERROR")
            print(f"\nTest failed: {str(e)}")
            
        print(f"\nTest completed. Check test/logs/ for detailed logs.")

async def main():
    """Main function to run the test."""
    try:
        tester = MCPIntegrationTester()
        await tester.run_test()
    except Exception as e:
        print(f"Failed to initialize tester: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)