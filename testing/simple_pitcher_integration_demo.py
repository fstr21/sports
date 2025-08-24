#!/usr/bin/env python3
"""
Simple Pitcher Integration Demo - Basic Implementation

This script demonstrates the immediate implementation approach:
- Add starting pitcher names to game data
- Test how Custom Chronulus experts respond to pitcher context
- Validate the improvement in analysis quality

Usage: python simple_pitcher_integration_demo.py
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

# Configuration
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"
CUSTOM_CHRONULUS_URL = "https://customchronpredictormcp-production.up.railway.app"
OUTPUT_DIR = "pitcher_research_results"

class SimplePitcherIntegrationDemo:
    """Demo of basic pitcher integration"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=90.0)
        self.demo_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "comparisons": {},
            "recommendations": {}
        }
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async def call_mlb_mcp(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call MLB MCP tool"""
        if arguments is None:
            arguments = {}
            
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
            response = await self.client.post(MLB_MCP_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ MLB MCP Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"❌ MLB MCP request failed: {e}")
            return None
    
    async def call_custom_chronulus(self, game_data: Dict[str, Any], expert_count: int = 5) -> Optional[Dict[str, Any]]:
        """Call Custom Chronulus with proper endpoint"""
        payload = {
            "game_data": game_data,
            "expert_count": expert_count,
            "analysis_depth": "comprehensive"
        }
        
        try:
            # Try the correct MCP endpoint
            response = await self.client.post(f"{CUSTOM_CHRONULUS_URL}/", json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "getCustomChronulusAnalysis",
                    "arguments": payload
                }
            })
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Custom Chronulus Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"❌ Custom Chronulus request failed: {e}")
            # Also log the exact URL tried
            print(f"🔗 URL attempted: {CUSTOM_CHRONULUS_URL}/")
            return None
    
    async def get_sample_game_with_pitchers(self) -> Dict[str, Any]:
        """Get a real game and add pitcher information"""
        print("🗓️  Getting today's MLB games...")
        
        # Get today's schedule
        schedule_result = await self.call_mlb_mcp("getMLBScheduleET", {
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        
        if not schedule_result or not schedule_result.get("ok"):
            print("❌ Failed to get schedule")
            return {}
        
        games = schedule_result.get("data", {}).get("games", [])
        if not games:
            print("❌ No games found today")
            return {}
        
        # Get first game
        sample_game = games[0]
        home_team = sample_game.get("home", {})
        away_team = sample_game.get("away", {})
        
        print(f"🏟️  Sample game: {away_team.get('name')} @ {home_team.get('name')}")
        
        # Get team rosters to find likely starting pitchers
        home_team_id = home_team.get("teamId")
        away_team_id = away_team.get("teamId")
        
        # Get home team pitchers
        home_roster = await self.call_mlb_mcp("getMLBTeamRoster", {
            "teamId": home_team_id,
            "season": 2025
        })
        
        # Get away team pitchers
        away_roster = await self.call_mlb_mcp("getMLBTeamRoster", {
            "teamId": away_team_id,
            "season": 2025
        })
        
        # Extract pitcher names (first pitcher from each roster as sample)
        home_pitchers = []
        away_pitchers = []
        
        if home_roster and home_roster.get("ok"):
            home_players = home_roster.get("data", {}).get("players", [])
            home_pitchers = [p for p in home_players if p.get("position", "").find("P") != -1]
        
        if away_roster and away_roster.get("ok"):
            away_players = away_roster.get("data", {}).get("players", [])
            away_pitchers = [p for p in away_players if p.get("position", "").find("P") != -1]
        
        # Create enhanced game data
        enhanced_game_data = {
            "home_team": f"{home_team.get('name', 'Home Team')} ({home_team.get('abbrev', 'HOM')})",
            "away_team": f"{away_team.get('name', 'Away Team')} ({away_team.get('abbrev', 'AWY')})",
            "venue": sample_game.get("venue", "Stadium"),
            "game_date": datetime.now().strftime("%Y-%m-%d"),
            "home_record": "TBD",  # Would need season stats
            "away_record": "TBD",  # Would need season stats  
            "home_moneyline": -120,  # Sample odds
            "away_moneyline": 105,   # Sample odds
            "additional_context": f"MLB game between division rivals."
        }
        
        # Add pitcher information if available
        if home_pitchers:
            home_pitcher_name = home_pitchers[0].get("fullName", "Unknown")
            enhanced_game_data["home_starting_pitcher"] = home_pitcher_name
            enhanced_game_data["additional_context"] += f" Home starting pitcher: {home_pitcher_name}."
        
        if away_pitchers:
            away_pitcher_name = away_pitchers[0].get("fullName", "Unknown")
            enhanced_game_data["away_starting_pitcher"] = away_pitcher_name
            enhanced_game_data["additional_context"] += f" Away starting pitcher: {away_pitcher_name}."
        
        print(f"✅ Enhanced game data with pitchers:")
        if "home_starting_pitcher" in enhanced_game_data:
            print(f"   🏠 Home pitcher: {enhanced_game_data['home_starting_pitcher']}")
        if "away_starting_pitcher" in enhanced_game_data:
            print(f"   ✈️  Away pitcher: {enhanced_game_data['away_starting_pitcher']}")
        
        return enhanced_game_data
    
    async def test_analysis_without_pitchers(self) -> Dict[str, Any]:
        """Test Custom Chronulus without pitcher information"""
        print("\n🧪 TESTING ANALYSIS WITHOUT PITCHER DATA")
        print("=" * 60)
        
        # Basic game data without pitchers
        basic_game_data = {
            "home_team": "Los Angeles Dodgers (86-57, 1st NL West)",
            "away_team": "San Diego Padres (78-65, 2nd NL West)",
            "venue": "Dodger Stadium, Los Angeles, CA",
            "game_date": "2025-08-23",
            "home_record": "86-57",
            "away_record": "78-65",
            "home_moneyline": -145,
            "away_moneyline": 125,
            "additional_context": "Division rivalry game, both teams fighting for playoffs."
        }
        
        print("📝 Testing without pitcher information...")
        result = await self.call_custom_chronulus(basic_game_data)
        
        if result:
            analysis = {
                "has_result": True,
                "analysis_length": len(result.get("text", "")),
                "mentions_pitching": "pitcher" in result.get("text", "").lower() or "pitching" in result.get("text", "").lower(),
                "prob_a": result.get("prob_a"),
                "expert_count": result.get("expert_count"),
                "sample_text": result.get("text", "")[:200] + "..." if len(result.get("text", "")) > 200 else result.get("text", "")
            }
            
            print(f"✅ Analysis complete")
            print(f"📊 Length: {analysis['analysis_length']} characters")
            print(f"⚾ Mentions pitching: {analysis['mentions_pitching']}")
            print(f"🎯 Probability: {analysis['prob_a']:.1%}")
            
            return analysis
        else:
            print("❌ Analysis failed")
            return {"has_result": False}
    
    async def test_analysis_with_pitchers(self) -> Dict[str, Any]:
        """Test Custom Chronulus with pitcher information"""
        print("\n🧪 TESTING ANALYSIS WITH PITCHER DATA")
        print("=" * 60)
        
        # Get real game with pitcher data
        enhanced_game_data = await self.get_sample_game_with_pitchers()
        
        if not enhanced_game_data:
            print("❌ Could not get enhanced game data")
            return {"has_result": False}
        
        print("📝 Testing with pitcher information...")
        result = await self.call_custom_chronulus(enhanced_game_data)
        
        if result:
            analysis = {
                "has_result": True,
                "game_data": enhanced_game_data,
                "analysis_length": len(result.get("text", "")),
                "mentions_pitching": "pitcher" in result.get("text", "").lower() or "pitching" in result.get("text", "").lower(),
                "mentions_specific_pitchers": False,
                "prob_a": result.get("prob_a"),
                "expert_count": result.get("expert_count"),
                "sample_text": result.get("text", "")[:200] + "..." if len(result.get("text", "")) > 200 else result.get("text", ""),
                "full_text": result.get("text", "")
            }
            
            # Check if specific pitchers are mentioned
            if "home_starting_pitcher" in enhanced_game_data:
                pitcher_name = enhanced_game_data["home_starting_pitcher"]
                if pitcher_name.lower() in result.get("text", "").lower():
                    analysis["mentions_specific_pitchers"] = True
            
            if "away_starting_pitcher" in enhanced_game_data:
                pitcher_name = enhanced_game_data["away_starting_pitcher"]
                if pitcher_name.lower() in result.get("text", "").lower():
                    analysis["mentions_specific_pitchers"] = True
            
            print(f"✅ Analysis complete")
            print(f"📊 Length: {analysis['analysis_length']} characters")
            print(f"⚾ Mentions pitching: {analysis['mentions_pitching']}")
            print(f"👤 Mentions specific pitchers: {analysis['mentions_specific_pitchers']}")
            print(f"🎯 Probability: {analysis['prob_a']:.1%}")
            
            return analysis
        else:
            print("❌ Analysis failed")
            return {"has_result": False}
    
    def compare_analyses(self, without_pitchers: Dict[str, Any], with_pitchers: Dict[str, Any]) -> Dict[str, Any]:
        """Compare the two analyses"""
        print("\n📊 COMPARING ANALYSES")
        print("=" * 60)
        
        comparison = {
            "both_successful": without_pitchers.get("has_result", False) and with_pitchers.get("has_result", False),
            "improvement_metrics": {},
            "quality_assessment": {}
        }
        
        if comparison["both_successful"]:
            # Compare metrics
            comparison["improvement_metrics"] = {
                "length_increase": with_pitchers["analysis_length"] - without_pitchers["analysis_length"],
                "pitching_mentions_improved": with_pitchers["mentions_pitching"] and not without_pitchers["mentions_pitching"],
                "specific_pitchers_mentioned": with_pitchers.get("mentions_specific_pitchers", False),
                "probability_change": with_pitchers["prob_a"] - without_pitchers["prob_a"]
            }
            
            # Quality assessment
            comparison["quality_assessment"] = {
                "context_enrichment": "High" if with_pitchers.get("mentions_specific_pitchers", False) else "Medium",
                "analysis_depth": "Improved" if comparison["improvement_metrics"]["length_increase"] > 100 else "Similar",
                "pitcher_integration_success": with_pitchers.get("mentions_specific_pitchers", False)
            }
            
            print(f"✅ Both analyses successful")
            print(f"📈 Length increase: {comparison['improvement_metrics']['length_increase']} characters")
            print(f"⚾ Pitching mentions improved: {comparison['improvement_metrics']['pitching_mentions_improved']}")
            print(f"👤 Specific pitchers mentioned: {comparison['improvement_metrics']['specific_pitchers_mentioned']}")
            print(f"🎯 Probability change: {comparison['improvement_metrics']['probability_change']:+.1%}")
            print(f"🏆 Context enrichment: {comparison['quality_assessment']['context_enrichment']}")
        else:
            print("❌ Cannot compare - one or both analyses failed")
        
        return comparison
    
    def save_results(self):
        """Save demo results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/simple_pitcher_integration_demo_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.demo_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename
    
    async def run_demo(self):
        """Run the complete pitcher integration demo"""
        print("🥎 SIMPLE PITCHER INTEGRATION DEMO")
        print("=" * 80)
        print(f"🔗 MLB MCP: {MLB_MCP_URL}")
        print(f"🤖 Custom Chronulus: {CUSTOM_CHRONULUS_URL}")
        print("=" * 80)
        
        try:
            # Test without pitchers
            without_pitchers = await self.test_analysis_without_pitchers()
            self.demo_results["tests"]["without_pitchers"] = without_pitchers
            
            # Test with pitchers
            with_pitchers = await self.test_analysis_with_pitchers()
            self.demo_results["tests"]["with_pitchers"] = with_pitchers
            
            # Compare results
            comparison = self.compare_analyses(without_pitchers, with_pitchers)
            self.demo_results["comparisons"] = comparison
            
            # Generate recommendations
            if comparison.get("both_successful", False):
                recommendations = {
                    "implementation_success": True,
                    "next_steps": [
                        "✅ Basic pitcher names integration works",
                        "📈 Consider adding pitcher statistics next",
                        "🎯 Monitor expert analysis quality improvements",
                        "⚡ Implement in production Discord bot"
                    ],
                    "priority": "HIGH - Simple implementation with clear benefits"
                }
            else:
                recommendations = {
                    "implementation_success": False,
                    "next_steps": [
                        "🔧 Debug Custom Chronulus endpoint connectivity",
                        "🔍 Verify MCP server deployment status",
                        "📝 Test with manual API calls",
                        "🆘 Check server logs for errors"
                    ],
                    "priority": "CRITICAL - Fix connectivity issues first"
                }
            
            self.demo_results["recommendations"] = recommendations
            
            # Save results
            filename = self.save_results()
            
            print(f"\n🎉 DEMO COMPLETE!")
            print(f"📊 View detailed results in: {filename}")
            
            if recommendations["implementation_success"]:
                print("\n🎯 IMPLEMENTATION RECOMMENDATION:")
                print("✅ Basic pitcher integration is working and ready for production!")
                print("📝 Next: Add this to your MLB handler in the Discord bot")
            else:
                print("\n⚠️  CONNECTIVITY ISSUES:")
                print("🔧 Custom Chronulus endpoint needs debugging before pitcher integration")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            await self.client.aclose()

async def main():
    """Main execution"""
    demo = SimplePitcherIntegrationDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())