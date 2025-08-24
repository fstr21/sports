#!/usr/bin/env python3
"""
Pitcher Integration Test Script - Custom Chronulus Enhancement

This script explores how pitcher data can be integrated with Custom Chronulus analysis:
- Available pitcher statistics and formats
- Data structure for integration
- Sample integration scenarios
- Performance metrics suitable for betting analysis

Usage: python pitcher_integration_test.py
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

# Configuration
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"
CUSTOM_CHRONULUS_URL = "https://customchronpredictormcp-production.up.railway.app/tools/call"
OUTPUT_DIR = "pitcher_research_results"
TARGET_SEASON = 2025

class PitcherIntegrationTester:
    """Test pitcher data integration with Custom Chronulus"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.integration_data = {
            "timestamp": datetime.now().isoformat(),
            "season": TARGET_SEASON,
            "pitcher_data_fields": {},
            "integration_scenarios": {},
            "custom_chronulus_tests": {},
            "recommendations": {}
        }
        
        # Ensure output directory exists
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
    
    async def call_custom_chronulus(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call Custom Chronulus MCP tool"""
        if arguments is None:
            arguments = {}
            
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        try:
            response = await self.client.post(CUSTOM_CHRONULUS_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Custom Chronulus Error: {result['error']}")
                return None
            
            return result
            
        except Exception as e:
            print(f"❌ Custom Chronulus request failed: {e}")
            return None
    
    async def explore_pitcher_data_structure(self) -> Dict[str, Any]:
        """Explore the structure of pitcher data available"""
        print("🔍 EXPLORING PITCHER DATA STRUCTURE")
        print("=" * 60)
        
        # Get a sample team and pitcher
        teams_result = await self.call_mlb_mcp("getMLBTeams", {"season": TARGET_SEASON})
        if not teams_result or not teams_result.get("ok"):
            print("❌ Failed to get teams")
            return {}
        
        teams = teams_result.get("data", {}).get("teams", [])
        if not teams:
            print("❌ No teams found")
            return {}
        
        # Get first team's roster
        sample_team = teams[0]
        team_id = sample_team.get("teamId")
        team_name = sample_team.get("name", "Unknown")
        
        print(f"📊 Using sample team: {team_name} (ID: {team_id})")
        
        roster_result = await self.call_mlb_mcp("getMLBTeamRoster", {
            "teamId": team_id,
            "season": TARGET_SEASON
        })
        
        if not roster_result or not roster_result.get("ok"):
            print("❌ Failed to get roster")
            return {}
        
        players = roster_result.get("data", {}).get("players", [])
        pitchers = [p for p in players if p.get("position", "").find("P") != -1]
        
        if not pitchers:
            print("❌ No pitchers found")
            return {}
        
        # Get detailed analysis for first pitcher
        sample_pitcher = pitchers[0]
        pitcher_id = sample_pitcher.get("playerId")
        pitcher_name = sample_pitcher.get("fullName", "Unknown")
        
        print(f"🥎 Analyzing sample pitcher: {pitcher_name} (ID: {pitcher_id})")
        
        pitcher_result = await self.call_mlb_mcp("getMLBPitcherMatchup", {
            "pitcher_id": pitcher_id,
            "season": TARGET_SEASON,
            "count": 5
        })
        
        if not pitcher_result or not pitcher_result.get("ok"):
            print("❌ Failed to get pitcher analysis")
            return {}
        
        pitcher_data = pitcher_result.get("data", {})
        
        # Analyze data structure
        data_structure = {
            "pitcher_info_fields": list(sample_pitcher.keys()),
            "recent_starts_fields": list(pitcher_data.get("recent_starts", [{}])[0].keys()) if pitcher_data.get("recent_starts") else [],
            "aggregates_fields": list(pitcher_data.get("aggregates", {}).keys()),
            "sample_pitcher": sample_pitcher,
            "sample_recent_start": pitcher_data.get("recent_starts", [{}])[0] if pitcher_data.get("recent_starts") else {},
            "sample_aggregates": pitcher_data.get("aggregates", {}),
            "data_availability": {
                "has_recent_starts": bool(pitcher_data.get("recent_starts")),
                "has_aggregates": bool(pitcher_data.get("aggregates")),
                "recent_starts_count": len(pitcher_data.get("recent_starts", []))
            }
        }
        
        self.integration_data["pitcher_data_fields"] = data_structure
        
        print("✅ Data structure analysis complete")
        print(f"📋 Pitcher info fields: {len(data_structure['pitcher_info_fields'])}")
        print(f"📊 Recent starts fields: {len(data_structure['recent_starts_fields'])}")
        print(f"📈 Aggregates fields: {len(data_structure['aggregates_fields'])}")
        
        return data_structure
    
    async def test_current_chronulus_without_pitchers(self) -> Dict[str, Any]:
        """Test current Custom Chronulus analysis without pitcher data"""
        print("\n🧪 TESTING CURRENT CUSTOM CHRONULUS (No Pitcher Data)")
        print("=" * 60)
        
        # Sample game data without pitcher information
        sample_game_data = {
            "home_team": "Los Angeles Dodgers (86-57, 1st NL West)",
            "away_team": "San Diego Padres (78-65, 2nd NL West)",
            "venue": "Dodger Stadium, Los Angeles, CA",
            "game_date": "2025-08-23",
            "home_record": "86-57",
            "away_record": "78-65",
            "home_moneyline": -145,
            "away_moneyline": 125,
            "additional_context": "Division rivalry game, both teams fighting for playoffs"
        }
        
        print("📝 Testing with sample game data (no pitcher info)...")
        
        result = await self.call_custom_chronulus("getCustomChronulusAnalysis", {
            "game_data": sample_game_data,
            "expert_count": 5,
            "analysis_depth": "comprehensive"
        })
        
        if result:
            print("✅ Custom Chronulus analysis successful")
            
            # Extract key information
            analysis_data = {
                "analysis_length": len(result.get("text", "")),
                "prob_a": result.get("prob_a"),
                "expert_count": result.get("expert_count"),
                "has_confidence_levels": "Confidence Level:" in result.get("text", ""),
                "has_unit_sizing": "Unit Size:" in result.get("text", "") or "units" in result.get("text", ""),
                "has_risk_levels": "Risk Level:" in result.get("text", ""),
                "mentions_pitching": "pitcher" in result.get("text", "").lower() or "pitching" in result.get("text", "").lower(),
                "sample_text_snippet": result.get("text", "")[:300] + "..." if len(result.get("text", "")) > 300 else result.get("text", "")
            }
            
            self.integration_data["custom_chronulus_tests"]["without_pitchers"] = {
                "request_data": sample_game_data,
                "response_analysis": analysis_data,
                "full_response": result
            }
            
            print(f"📊 Analysis length: {analysis_data['analysis_length']} characters")
            print(f"🎯 Probability: {analysis_data['prob_a']:.1%}")
            print(f"👥 Experts: {analysis_data['expert_count']}")
            print(f"📈 Has confidence levels: {analysis_data['has_confidence_levels']}")
            print(f"🎲 Has unit sizing: {analysis_data['has_unit_sizing']}")
            print(f"⚠️  Has risk levels: {analysis_data['has_risk_levels']}")
            print(f"⚾ Mentions pitching: {analysis_data['mentions_pitching']}")
            
            return analysis_data
        else:
            print("❌ Custom Chronulus analysis failed")
            return {}
    
    async def design_pitcher_integration_scenarios(self, data_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design scenarios for integrating pitcher data"""
        print("\n🎯 DESIGNING PITCHER INTEGRATION SCENARIOS")
        print("=" * 60)
        
        scenarios = []
        
        # Scenario 1: Basic Pitcher Info
        scenarios.append({
            "name": "Basic Pitcher Names",
            "description": "Add starting pitcher names to game data",
            "integration_level": "simple",
            "required_fields": ["fullName", "position"],
            "implementation": "Add home_starting_pitcher and away_starting_pitcher fields to game_data",
            "example_data": {
                "home_starting_pitcher": "Clayton Kershaw",
                "away_starting_pitcher": "Yu Darvish"
            },
            "effort": "Low - Just add names",
            "value": "Medium - Basic context"
        })
        
        # Scenario 2: Recent Performance
        scenarios.append({
            "name": "Recent Pitcher Performance",
            "description": "Include recent performance metrics",
            "integration_level": "moderate",
            "required_fields": ["era", "whip", "k_per_9", "innings_pitched"],
            "implementation": "Fetch pitcher stats and include in additional_context",
            "example_data": {
                "home_pitcher_stats": "ERA: 3.21, WHIP: 1.15, K/9: 9.8, Last 5 starts",
                "away_pitcher_stats": "ERA: 4.05, WHIP: 1.32, K/9: 8.4, Last 5 starts"
            },
            "effort": "Medium - API calls needed",
            "value": "High - Statistical context"
        })
        
        # Scenario 3: Head-to-Head History
        scenarios.append({
            "name": "Head-to-Head Pitcher History",
            "description": "Include pitcher vs opponent team history",
            "integration_level": "advanced",
            "required_fields": ["recent_starts", "opponent_team_id", "vs_opponent_stats"],
            "implementation": "Filter recent starts by opponent, calculate specific matchup stats",
            "example_data": {
                "home_pitcher_vs_opponent": "vs Padres: 2-1 record, 2.45 ERA in 3 starts",
                "away_pitcher_vs_opponent": "vs Dodgers: 1-2 record, 5.12 ERA in 4 starts"
            },
            "effort": "High - Complex filtering and calculation",
            "value": "Very High - Specific matchup insights"
        })
        
        # Scenario 4: Comprehensive Pitcher Analysis
        scenarios.append({
            "name": "Comprehensive Pitcher Context",
            "description": "Full pitcher analysis integration",
            "integration_level": "comprehensive",
            "required_fields": ["all pitcher data"],
            "implementation": "Create detailed pitcher section in game_data with recent form, matchup history, and key metrics",
            "example_data": {
                "pitcher_analysis": {
                    "home": {
                        "name": "Clayton Kershaw",
                        "recent_form": "3.21 ERA, 1.15 WHIP in last 5 starts",
                        "vs_opponent": "2.45 ERA vs SD in 3 career starts",
                        "key_stats": "9.8 K/9, 65% first-strike rate"
                    },
                    "away": {
                        "name": "Yu Darvish",
                        "recent_form": "4.05 ERA, 1.32 WHIP in last 5 starts",
                        "vs_opponent": "5.12 ERA vs LAD in 4 career starts",
                        "key_stats": "8.4 K/9, 58% first-strike rate"
                    }
                }
            },
            "effort": "Very High - Multiple API calls and data processing",
            "value": "Maximum - Complete context for experts"
        })
        
        self.integration_data["integration_scenarios"] = scenarios
        
        print(f"📋 Designed {len(scenarios)} integration scenarios:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i}. {scenario['name']} - {scenario['effort']} effort, {scenario['value']} value")
        
        return scenarios
    
    def generate_implementation_recommendations(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate recommendations for pitcher integration"""
        print("\n💡 GENERATING IMPLEMENTATION RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = {
            "immediate_implementation": {
                "scenario": "Basic Pitcher Names",
                "reason": "Quick wins with minimal effort",
                "steps": [
                    "1. Modify game_data structure to include pitcher names",
                    "2. Update MLB game data collection to fetch starting lineups",
                    "3. Add pitcher names to additional_context field",
                    "4. Test with Custom Chronulus to ensure experts mention pitchers"
                ],
                "estimated_effort": "2-4 hours"
            },
            "medium_term_implementation": {
                "scenario": "Recent Pitcher Performance",
                "reason": "High value for betting analysis",
                "steps": [
                    "1. Implement pitcher stats fetching in game data collection",
                    "2. Format pitcher stats for expert consumption",
                    "3. Include in additional_context with clear labeling",
                    "4. Test expert analysis quality improvement",
                    "5. Monitor Custom Chronulus token usage"
                ],
                "estimated_effort": "1-2 days"
            },
            "advanced_implementation": {
                "scenario": "Head-to-Head Pitcher History",
                "reason": "Maximum betting edge for matchup analysis",
                "steps": [
                    "1. Implement head-to-head filtering logic",
                    "2. Create pitcher matchup analysis module",
                    "3. Cache frequent matchup data for performance",
                    "4. Integrate with Custom Chronulus input structure",
                    "5. Validate expert analysis quality vs effort"
                ],
                "estimated_effort": "3-5 days"
            },
            "data_requirements": {
                "mlb_mcp_tools_needed": [
                    "getMLBScheduleET (for game identification)",
                    "getMLBTeamRoster (for pitcher identification)",
                    "getMLBPitcherMatchup (for pitcher stats)",
                    "Potentially: getMLBPlayerLastN (for recent performance)"
                ],
                "data_processing": [
                    "Pitcher identification from lineups",
                    "Recent performance aggregation",
                    "Head-to-head filtering",
                    "Statistical calculation and formatting"
                ]
            },
            "integration_points": {
                "discord_bot": "Update game data collection in mlb_handler.py",
                "custom_chronulus": "Enhance game_data structure passed to experts",
                "data_flow": "Schedule -> Teams -> Rosters -> Pitchers -> Stats -> Analysis"
            },
            "risks_and_considerations": [
                "API rate limiting with additional pitcher calls",
                "Custom Chronulus token limit with more data",
                "Data freshness - starting lineups may change",
                "Performance impact on analysis speed",
                "Complexity vs value trade-off"
            ]
        }
        
        self.integration_data["recommendations"] = recommendations
        
        print("✅ Recommendations generated:")
        print(f"🚀 Immediate: {recommendations['immediate_implementation']['scenario']} ({recommendations['immediate_implementation']['estimated_effort']})")
        print(f"📈 Medium-term: {recommendations['medium_term_implementation']['scenario']} ({recommendations['medium_term_implementation']['estimated_effort']})")
        print(f"🎯 Advanced: {recommendations['advanced_implementation']['scenario']} ({recommendations['advanced_implementation']['estimated_effort']})")
        
        return recommendations
    
    def save_results(self):
        """Save integration analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/pitcher_integration_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.integration_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename
    
    async def run_integration_analysis(self):
        """Run complete pitcher integration analysis"""
        print("🥎 PITCHER INTEGRATION ANALYSIS FOR CUSTOM CHRONULUS")
        print("=" * 80)
        print(f"🔗 MLB MCP: {MLB_MCP_URL}")
        print(f"🤖 Custom Chronulus: {CUSTOM_CHRONULUS_URL}")
        print(f"📅 Season: {TARGET_SEASON}")
        print("=" * 80)
        
        try:
            # Step 1: Explore data structure
            data_structure = await self.explore_pitcher_data_structure()
            
            # Step 2: Test current Chronulus
            current_analysis = await self.test_current_chronulus_without_pitchers()
            
            # Step 3: Design integration scenarios
            scenarios = await self.design_pitcher_integration_scenarios(data_structure)
            
            # Step 4: Generate recommendations
            recommendations = self.generate_implementation_recommendations(scenarios)
            
            # Step 5: Save results
            filename = self.save_results()
            
            print(f"\n🎉 INTEGRATION ANALYSIS COMPLETE!")
            print(f"📊 View detailed results in: {filename}")
            print("\n🎯 NEXT STEPS:")
            print(f"1. Implement: {recommendations['immediate_implementation']['scenario']}")
            print(f"2. Plan: {recommendations['medium_term_implementation']['scenario']}")
            print(f"3. Evaluate: {recommendations['advanced_implementation']['scenario']}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
        finally:
            await self.client.aclose()

async def main():
    """Main execution"""
    tester = PitcherIntegrationTester()
    await tester.run_integration_analysis()

if __name__ == "__main__":
    asyncio.run(main())