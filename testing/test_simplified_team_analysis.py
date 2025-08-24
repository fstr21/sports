#!/usr/bin/env python3
"""
Test Simplified Team-Focused Analysis
Validate the team-level context without pitcher complexity
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the discord bot path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mcp_leagues', 'discord_bot'))

from sports.mlb_handler import MLBHandler
from core.mcp_client import MCPClient

async def test_simplified_team_analysis():
    """Test the simplified team-focused analysis"""
    
    print("TESTING SIMPLIFIED TEAM-FOCUSED ANALYSIS")
    print("=" * 50)
    
    # Create mock MCP client and configuration
    mcp_client = MCPClient()
    config = {
        'mcp_url': 'https://mlbmcp-production.up.railway.app/mcp',
        'embed_color': 0x0066cc
    }
    
    # Create MLB handler
    mlb_handler = MLBHandler("mlb", config, mcp_client)
    
    try:
        print("Testing simplified team context method...")
        
        # Test with real teams
        test_teams = [
            ("New York Yankees", "Boston Red Sox"),
            ("Los Angeles Dodgers", "San Diego Padres"),
        ]
        
        for home_team, away_team in test_teams:
            print(f"\nTesting: {away_team} @ {home_team}")
            print("-" * 30)
            
            # Test simplified team context
            team_context = await mlb_handler._get_team_context(home_team, away_team)
            
            if team_context:
                print(f"SUCCESS: Team context generated: {len(team_context)} characters")
                print(f"Context: {team_context}")
                
                # Test with Custom Chronulus
                print(f"\nTesting with Custom Chronulus...")
                
                game_data = {
                    "home_team": f"{home_team} (Season Record TBD)",
                    "away_team": f"{away_team} (Season Record TBD)",
                    "venue": "Stadium TBD",
                    "game_date": datetime.now().strftime("%B %d, %Y"),
                    "additional_context": f"MLB Game Analysis with Team-Level Intelligence: {team_context}"
                }
                
                # Call Custom Chronulus
                chronulus_result = await test_chronulus_with_context(game_data)
                
                if chronulus_result:
                    print("SUCCESS: Custom Chronulus analysis successful!")
                    
                    # Analyze team intelligence in response
                    analysis_text = chronulus_result.get('analysis', {}).get('expert_analysis', '')
                    
                    team_intelligence = {
                        "Team mentions": sum(analysis_text.lower().count(team.lower().split()[-1]) for team in [home_team, away_team]),
                        "Form mentions": sum(analysis_text.lower().count(term) for term in ['form', 'recent', 'momentum']),
                        "Offense mentions": sum(analysis_text.lower().count(term) for term in ['offense', 'scoring', 'runs']),
                        "Bullpen mentions": sum(analysis_text.lower().count(term) for term in ['bullpen', 'relief']),
                        "Home field mentions": sum(analysis_text.lower().count(term) for term in ['home', 'venue', 'field'])
                    }
                    
                    print("Team Intelligence Detected:")
                    total_mentions = sum(team_intelligence.values())
                    for metric, count in team_intelligence.items():
                        print(f"  {metric}: {count} mentions")
                    
                    print(f"\nTotal Team Intelligence Score: {total_mentions} mentions")
                    
                    if total_mentions >= 10:
                        print("EXCELLENT! Rich team intelligence detected in analysis")
                    elif total_mentions >= 5:
                        print("GOOD! Some team intelligence present")
                    else:
                        print("LIMITED! Team intelligence may need enhancement")
                
                else:
                    print("ERROR: Custom Chronulus analysis failed")
                
            else:
                print(f"ERROR: No team context generated for {away_team} @ {home_team}")
    
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_chronulus_with_context(game_data):
    """Test Custom Chronulus with team context"""
    
    try:
        import httpx
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getCustomChronulusAnalysis",
                "arguments": {
                    "game_data": game_data,
                    "expert_count": 5,
                    "analysis_depth": "comprehensive"
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://customchronpredictormcp-production.up.railway.app/mcp", 
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    content = result["result"]["content"][0]["text"]
                    analysis_data = json.loads(content)
                    return analysis_data
                else:
                    print(f"ERROR: Custom Chronulus error: {result}")
                    return None
            else:
                print(f"ERROR: HTTP {response.status_code}: {response.text}")
                return None
                
    except Exception as e:
        print(f"ERROR: Error testing with Custom Chronulus: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_simplified_team_analysis())