#!/usr/bin/env python3
"""
Minimal Data Test - Just Team Names
Test what Custom Chronulus MCP can do with absolute minimum information
"""
import asyncio
import json
import httpx
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for .env access
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# Custom Chronulus MCP Server URL
CUSTOM_CHRONULUS_MCP_URL = "https://customchronpredictormcp-production.up.railway.app/mcp"

async def test_minimal_data():
    """Test with just team names - see what the AI can generate"""
    
    print("🧪 MINIMAL DATA TEST - JUST TEAM NAMES")
    print("=" * 50)
    print("Goal: See what analysis is possible with minimal input")
    print("Input: Just 'Yankees' and 'Red Sox' - nothing else")
    print()
    
    # ABSOLUTE MINIMUM - just team names
    minimal_game_data = {
        "home_team": "Yankees",
        "away_team": "Red Sox",
        "venue": "Stadium",
        "game_date": "Today"
    }
    
    print("📊 MINIMAL INPUT DATA:")
    print(f"  Home Team: {minimal_game_data['home_team']}")
    print(f"  Away Team: {minimal_game_data['away_team']}")
    print(f"  Venue: {minimal_game_data['venue']}")
    print(f"  Date: {minimal_game_data['game_date']}")
    print("  Records: Not provided")
    print("  Odds: Not provided")
    print("  Context: Not provided")
    print()
    
    # MCP request with minimal data
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": minimal_game_data,
                "expert_count": 3,
                "analysis_depth": "standard"
            }
        }
    }
    
    try:
        print("🚀 SENDING MINIMAL REQUEST TO CUSTOM CHRONULUS MCP")
        print("-" * 50)
        print("Testing: What can AI generate from team names alone?")
        print("Expected: AI should fill in reasonable defaults or indicate missing data")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\n⏳ Requesting analysis with minimal data...")
            response = await client.post(CUSTOM_CHRONULUS_MCP_URL, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ MCP Error: {error_msg}")
                return None
            
            # Parse response
            mcp_result = result["result"]
            if "content" not in mcp_result or not isinstance(mcp_result["content"], list):
                print(f"❌ Unexpected response format: {mcp_result}")
                return None
            
            analysis_text = mcp_result["content"][0]["text"]
            
            print("\n📈 MINIMAL DATA ANALYSIS RESULTS")
            print("=" * 60)
            
            try:
                # Try to parse as JSON
                analysis_data = json.loads(analysis_text)
                
                print("✅ SUCCESS: AI generated structured analysis from minimal input!")
                print()
                
                # Check what the AI generated
                if "analysis" in analysis_data:
                    analysis = analysis_data["analysis"]
                    
                    # Probabilities
                    away_prob = analysis.get("away_team_win_probability", 0) * 100
                    home_prob = analysis.get("home_team_win_probability", 0) * 100
                    
                    print(f"🎯 WIN PROBABILITIES (AI Generated):")
                    print(f"  {minimal_game_data['away_team']}: {away_prob:.1f}%")
                    print(f"  {minimal_game_data['home_team']}: {home_prob:.1f}%")
                    
                    # Expert analysis
                    if "expert_analysis" in analysis:
                        expert_text = analysis["expert_analysis"]
                        
                        print(f"\n📝 AI-GENERATED ANALYSIS:")
                        print("-" * 40)
                        
                        # Check for key indicators of what AI filled in
                        indicators = {
                            "Generated Records": any(record in expert_text for record in ["win%", "record", "games"]),
                            "Generated Stats": any(stat in expert_text for stat in ["ERA", "runs", "differential"]),
                            "Generated Context": any(context in expert_text for context in ["rivalry", "recent", "season"]),
                            "Mentioned Missing Data": any(missing in expert_text.lower() for missing in ["unknown", "unavailable", "limited", "tbd"]),
                            "Made Assumptions": any(assume in expert_text.lower() for assume in ["assume", "typically", "historically", "generally"])
                        }
                        
                        print("🔍 AI RESPONSE ANALYSIS:")
                        for indicator, found in indicators.items():
                            status = "YES" if found else "NO"
                            print(f"  {status:3} | {indicator}")
                        
                        print(f"\n📖 FULL ANALYSIS (first 500 chars):")
                        print("-" * 50)
                        print(expert_text[:500] + "..." if len(expert_text) > 500 else expert_text)
                        
                        # Check analysis quality
                        word_count = len(expert_text.split())
                        quality_score = 0
                        
                        if word_count > 100:
                            quality_score += 1
                        if "Yankees" in expert_text and "Red Sox" in expert_text:
                            quality_score += 1
                        if any(num in expert_text for num in ["%", "probability", "win"]):
                            quality_score += 1
                        if not any(missing in expert_text.lower() for missing in ["unknown", "unavailable"]):
                            quality_score += 1
                        
                        print(f"\n📊 QUALITY ASSESSMENT:")
                        print(f"  Word Count: {word_count}")
                        print(f"  Quality Score: {quality_score}/4")
                        print(f"  Assessment: {'EXCELLENT' if quality_score >= 3 else 'GOOD' if quality_score >= 2 else 'BASIC'}")
                
            except json.JSONDecodeError:
                # Handle text response
                print("📝 TEXT RESPONSE (not JSON):")
                print("-" * 40)
                print(analysis_text[:1000] + "..." if len(analysis_text) > 1000 else analysis_text)
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"c:/Users/fstr2/Desktop/sports/chronulus/results/minimal_test_{timestamp}.txt"
            
            os.makedirs("c:/Users/fstr2/Desktop/sports/chronulus/results", exist_ok=True)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write("Minimal Data Test - Yankees vs Red Sox\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")
                f.write("INPUT DATA:\n")
                f.write(f"Home Team: {minimal_game_data['home_team']}\n")
                f.write(f"Away Team: {minimal_game_data['away_team']}\n")
                f.write(f"Venue: {minimal_game_data['venue']}\n")
                f.write(f"Date: {minimal_game_data['game_date']}\n")
                f.write("Records: Not provided\n")
                f.write("Odds: Not provided\n")
                f.write("Context: Not provided\n\n")
                f.write("AI RESPONSE:\n")
                f.write(analysis_text)
                f.write("\n\nCONCLUSION:\n")
                f.write("Test demonstrates what Custom Chronulus MCP can generate from minimal input.\n")
            
            print(f"\n💾 Results saved to: {results_file}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_team_names_only():
    """Even more minimal - see if we can get away with just required fields"""
    
    print("\n🔬 ULTRA-MINIMAL TEST - REQUIRED FIELDS ONLY")
    print("=" * 50)
    
    # Just the required fields from the schema
    ultra_minimal = {
        "home_team": "Yankees",
        "away_team": "Red Sox", 
        "venue": "Ballpark",
        "game_date": "2025-08-23"
    }
    
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call", 
        "id": 2,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": ultra_minimal,
                "expert_count": 1,  # Just one expert for speed
                "analysis_depth": "brief"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("⚡ Quick test with absolute minimum data...")
            response = await client.post(CUSTOM_CHRONULUS_MCP_URL, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result and "content" in result["result"]:
                analysis_text = result["result"]["content"][0]["text"]
                
                print("✅ SUCCESS: AI works with just team names!")
                print(f"📄 Quick Preview (first 200 chars):")
                print("-" * 40)
                print(analysis_text[:200] + "...")
                
                return True
            else:
                print(f"❌ Failed: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Ultra-minimal test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🧪 CUSTOM CHRONULUS MCP - MINIMAL DATA TESTING")
        print("Question: What's the minimum data needed for baseball predictions?")
        print("=" * 70)
        
        # Test 1: Minimal but complete
        success1 = await test_minimal_data()
        
        if success1:
            # Test 2: Ultra-minimal
            success2 = await test_team_names_only()
            
            print(f"\n🎉 CONCLUSIONS:")
            print(f"✅ Standard minimal test: {'PASSED' if success1 else 'FAILED'}")
            print(f"✅ Ultra-minimal test: {'PASSED' if success2 else 'FAILED'}")
            print(f"\n💡 FINDING:")
            if success1 and success2:
                print("Custom Chronulus MCP can generate meaningful analysis from just team names!")
                print("The AI fills in reasonable defaults and provides structured output.")
                print("For real use: Team names + venue + date = sufficient for basic analysis")
                print("For better analysis: Add records, odds, and context when available")
            else:
                print("Some required fields are necessary for analysis to work.")
                print("Check the specific error messages above for details.")
        else:
            print("\n❌ Basic test failed - check server configuration")
    
    asyncio.run(main())