#!/usr/bin/env python3
"""
Integrated Custom Chronulus Test
Tests custom chronulus predictor using real game data from Discord bot's MLB handler
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp_leagues', 'discord_bot'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp_leagues', 'discord_bot', 'sports'))

from mlb_handler_enhanced import EnhancedMLBHandler

class IntegratedChronulusTest:
    """Test custom Chronulus with real MLB data from Discord bot"""
    
    def __init__(self):
        self.mlb_mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
        self.custom_chronulus_url = "https://custom-chronulus-mcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # MLB Handler config (mimicking Discord bot setup)
        self.mlb_config = {
            'mcp_url': self.mlb_mcp_url,
            'channel_creation_delay': 2.0
        }
        
        # Create MLB handler instance
        self.mlb_handler = EnhancedMLBHandler(
            sport_name="mlb",
            config=self.mlb_config,
            mcp_client=self  # Use self as mock MCP client
        )
        
        # Mock MCP client properties for MLB handler
        self._client = self.client
    
    async def call_custom_chronulus(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call custom chronulus MCP tool"""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.client.post(self.custom_chronulus_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                return {"ok": False, "error": result["error"]}
            
            return result.get("result", {})
            
        except Exception as e:
            return {"ok": False, "error": f"Custom Chronulus call failed: {str(e)}"}
    
    async def get_today_games(self) -> List[Dict[str, Any]]:
        """Get today's MLB games using Discord bot's enhanced handler"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            print(f"🔍 Getting MLB games for {today}...")
            
            # Use the enhanced MLB handler to get games
            matches = await self.mlb_handler.get_enhanced_matches(today)
            
            if not matches:
                # Try tomorrow if no games today
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                print(f"📅 No games today, trying {tomorrow}...")
                matches = await self.mlb_handler.get_enhanced_matches(tomorrow)
            
            return matches
            
        except Exception as e:
            print(f"❌ Error getting games: {e}")
            return []
    
    def convert_match_to_chronulus_format(self, match) -> Dict[str, Any]:
        """Convert Discord bot Match object to Custom Chronulus format"""
        try:
            # Extract enhanced data
            basic_info = match.additional_data.get("basic_game_info", {})
            team_forms = match.additional_data.get("team_forms", {})
            scoring_trends = match.additional_data.get("scoring_trends", {})
            
            # Build comprehensive game context
            home_context = f"{match.home_team}"
            away_context = f"{match.away_team}"
            
            # Add team form data if available
            home_form = team_forms.get("home", {})
            away_form = team_forms.get("away", {})
            
            if home_form:
                form_data = home_form.get("form", {})
                wins = form_data.get("wins", 0)
                losses = form_data.get("losses", 0)
                win_pct = form_data.get("win_percentage", "N/A")
                home_context += f" ({wins}-{losses}, .{win_pct if isinstance(win_pct, str) and win_pct != 'N/A' else f'{win_pct:.3f}' if isinstance(win_pct, float) else 'N/A'} win%)"
            
            if away_form:
                form_data = away_form.get("form", {})
                wins = form_data.get("wins", 0)
                losses = form_data.get("losses", 0)
                win_pct = form_data.get("win_percentage", "N/A")
                away_context += f" ({wins}-{losses}, .{win_pct if isinstance(win_pct, str) and win_pct != 'N/A' else f'{win_pct:.3f}' if isinstance(win_pct, float) else 'N/A'} win%)"
            
            # Add scoring trends if available
            additional_context_parts = []
            
            home_scoring = scoring_trends.get("home", {})
            away_scoring = scoring_trends.get("away", {})
            
            if home_scoring:
                trends = home_scoring.get("trends", {})
                rpg = trends.get("runs_per_game", "N/A")
                rapg = trends.get("runs_allowed_per_game", "N/A")
                additional_context_parts.append(f"{match.home_team}: {rpg} R/G, {rapg} RA/G")
            
            if away_scoring:
                trends = away_scoring.get("trends", {})
                rpg = trends.get("runs_per_game", "N/A")
                rapg = trends.get("runs_allowed_per_game", "N/A")
                additional_context_parts.append(f"{match.away_team}: {rpg} R/G, {rapg} RA/G")
            
            # Get venue and time info
            venue = basic_info.get("venue", "Unknown Venue")
            start_time = basic_info.get("start_et", "TBD")
            
            return {
                "home_team": home_context,
                "away_team": away_context,
                "venue": f"{venue} ({start_time} ET)",
                "game_date": datetime.now().strftime("%Y-%m-%d"),
                "home_record": home_form.get("form", {}).get("record", "Unknown") if home_form else "Unknown",
                "away_record": away_form.get("form", {}).get("record", "Unknown") if away_form else "Unknown",
                "home_moneyline": 100,  # Default - would need odds integration
                "away_moneyline": -100, # Default - would need odds integration
                "additional_context": "; ".join(additional_context_parts) if additional_context_parts else "Enhanced MCP data analysis"
            }
            
        except Exception as e:
            print(f"❌ Error converting match: {e}")
            # Fallback to basic format
            return {
                "home_team": match.home_team,
                "away_team": match.away_team,
                "venue": "Unknown Venue",
                "game_date": datetime.now().strftime("%Y-%m-%d"),
                "home_record": "Unknown",
                "away_record": "Unknown", 
                "home_moneyline": 100,
                "away_moneyline": -100,
                "additional_context": "Basic game data"
            }
    
    async def test_single_game_analysis(self) -> Dict[str, Any]:
        """Test custom chronulus on a single real game"""
        try:
            print("🚀 Starting Integrated Custom Chronulus Test")
            print("=" * 50)
            
            # 1. Get real games from Discord bot
            matches = await self.get_today_games()
            
            if not matches:
                return {
                    "status": "error",
                    "message": "No MLB games found for testing",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 2. Use first game for testing
            test_match = matches[0]
            print(f"🎯 Testing: {test_match.away_team} @ {test_match.home_team}")
            
            # 3. Convert to Custom Chronulus format
            game_data = self.convert_match_to_chronulus_format(test_match)
            
            print(f"📊 Game Data Preview:")
            print(f"  Away: {game_data['away_team']}")
            print(f"  Home: {game_data['home_team']}")
            print(f"  Venue: {game_data['venue']}")
            print(f"  Context: {game_data['additional_context']}")
            
            # 4. Call Custom Chronulus with real data
            print("\n🤖 Calling Custom Chronulus with 3 experts...")
            chronulus_result = await self.call_custom_chronulus(
                "getCustomChronulusAnalysis",
                {
                    "game_data": game_data,
                    "expert_count": 3,
                    "analysis_depth": "comprehensive"
                }
            )
            
            if not chronulus_result or chronulus_result.get("ok") == False:
                return {
                    "status": "error",
                    "message": f"Custom Chronulus analysis failed: {chronulus_result.get('error', 'Unknown error')}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 5. Parse and format results
            analysis_data = json.loads(chronulus_result.get("content", [{}])[0].get("text", "{}"))
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "test_game": {
                    "away_team": test_match.away_team,
                    "home_team": test_match.home_team,
                    "enhanced_data_available": bool(test_match.additional_data)
                },
                "chronulus_analysis": analysis_data,
                "comparison_notes": [
                    "Uses real MLB MCP data instead of hardcoded stats",
                    "Enhanced with team forms, scoring trends, and venue info", 
                    "Cost: ~$0.06-0.15 vs Paid Chronulus ~$0.75-1.50",
                    "Ready for Discord bot integration testing"
                ]
            }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Test failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def save_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"integrated_chronulus_test_{timestamp}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📄 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    async def run_test(self):
        """Run the integrated test"""
        try:
            results = await self.test_single_game_analysis()
            
            # Print summary
            print("\n" + "=" * 50)
            print("📋 TEST SUMMARY")
            print("=" * 50)
            
            if results["status"] == "success":
                analysis = results["chronulus_analysis"]
                print(f"✅ Status: {results['status'].upper()}")
                print(f"🎮 Game: {results['test_game']['away_team']} @ {results['test_game']['home_team']}")
                
                if analysis.get("analysis"):
                    prob_data = analysis["analysis"]
                    away_prob = prob_data.get("away_team_win_probability", "N/A")
                    home_prob = prob_data.get("home_team_win_probability", "N/A")
                    expert_count = prob_data.get("expert_count", "N/A")
                    cost = prob_data.get("cost_estimate", "N/A")
                    
                    print(f"📊 Away Win Probability: {away_prob:.1%}" if isinstance(away_prob, (int, float)) else f"📊 Away Win Probability: {away_prob}")
                    print(f"🏠 Home Win Probability: {home_prob:.1%}" if isinstance(home_prob, (int, float)) else f"🏠 Home Win Probability: {home_prob}")
                    print(f"👥 Experts Used: {expert_count}")
                    print(f"💰 Estimated Cost: {cost}")
                
            else:
                print(f"❌ Status: {results['status'].upper()}")
                print(f"📝 Message: {results['message']}")
            
            # Save results
            await self.save_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            await self.client.aclose()

async def main():
    """Run the integrated test"""
    tester = IntegratedChronulusTest()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())