#!/usr/bin/env python3
"""
Direct Test of /textonly Command Logic
Test Custom Chronulus MCP with Red Sox @ Yankees data and export to markdown
"""
import asyncio
import json
import httpx
import os
from datetime import datetime

# Custom Chronulus MCP Server URL
CUSTOM_CHRONULUS_MCP_URL = "https://customchronpredictormcp-production.up.railway.app/mcp"

async def test_textonly_direct():
    """Test the exact same logic as /textonly command"""
    
    print("DIRECT /textonly TEST - Red Sox @ Yankees")
    print("=" * 60)
    print("Testing the exact same logic as Discord /textonly command")
    print()
    
    # Hard-coded game data from the image (exact same as Discord command)
    game_data = {
        "home_team": "New York Yankees (69-60, .535 win%, AL East)",
        "away_team": "Boston Red Sox (71-59, .546 win%, AL East)", 
        "sport": "Baseball",
        "venue": "Yankee Stadium (49,642 capacity, Bronx, NY)",
        "game_date": "August 24, 2025 - 7:10 PM ET",
        "home_record": "69-60 (.535), +96 run diff, Allowed/Game: 4.36, L10 Form: 6-4",
        "away_record": "71-59 (.546), +105 run diff, Allowed/Game: 4.20, L10 Form: 6-4",
        "home_moneyline": -162,
        "away_moneyline": +136,
        "additional_context": (
            "BETTING LINES: Yankees -162 (61.8% implied), Red Sox +136 (42.4% implied). "
            "Run Line: Red Sox +1.5 (-152), Yankees -1.5 (+126). "
            "Over/Under: Over 8.5 (-115), Under 8.5 (-105). "
            "TEAM PERFORMANCE: Yankees 69-60, +96 run differential, 4.36 ERA allowed. "
            "Red Sox 71-59, +105 run differential, 4.20 ERA allowed. "
            "Both teams 6-4 in last 10 games showing good recent form. "
            "VENUE: Yankee Stadium, iconic venue with short right field (314 ft). "
            "RIVALRY: Historic AL East matchup with playoff implications. "
            "Weather conditions and other factors favorable for baseball."
        )
    }
    
    print("GAME DATA INPUT:")
    print(f"  Game: {game_data['away_team']} @ {game_data['home_team']}")
    print(f"  Date: {game_data['game_date']}")
    print(f"  Venue: {game_data['venue']}")
    print(f"  Moneylines: Yankees {game_data['home_moneyline']}, Red Sox {game_data['away_moneyline']}")
    print(f"  Context Length: {len(game_data['additional_context'])} characters")
    print()
    
    # MCP request (exact same as Discord command)
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": game_data,
                "expert_count": 3,
                "analysis_depth": "comprehensive"
            }
        }
    }
    
    try:
        print(f"CALLING CUSTOM CHRONULUS MCP")
        print("-" * 40)
        print(f"URL: {CUSTOM_CHRONULUS_MCP_URL}")
        print(f"Expert Count: 3")
        print(f"Analysis Depth: comprehensive")
        print()
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("Sending request...")
            response = await client.post(CUSTOM_CHRONULUS_MCP_URL, json=mcp_request)
            response.raise_for_status()
            result = response.json()
            
            print(f"SUCCESS: Received response from Custom Chronulus MCP")
            print(f"Response type: {type(result)}")
            print()
            
            if "result" not in result:
                error_msg = result.get('error', 'Unknown error')
                print(f"MCP Error: {error_msg}")
                return None
            
            # Extract analysis text
            mcp_result = result["result"]
            analysis_text = mcp_result["content"][0]["text"] if "content" in mcp_result and mcp_result["content"] else "No analysis returned"
            
            print(f"ANALYSIS RECEIVED:")
            print(f"  Analysis length: {len(analysis_text)} characters")
            print(f"  First 200 chars: {analysis_text[:200]}...")
            print()
            
            # Export to markdown
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_file = f"C:\\Users\\fstr2\\Desktop\\sports\\textonly_direct_{timestamp}.md"
            
            print(f"EXPORTING TO MARKDOWN:")
            print(f"  Target file: {md_file}")
            
            try:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write("# /textonly Direct Test - Raw MCP Results\\n\\n")
                    f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\\n")
                    f.write(f"**Test**: Direct /textonly command logic\\n")
                    f.write(f"**Game**: {game_data['away_team']} @ {game_data['home_team']}\\n\\n")
                    
                    f.write("## Game Data Input\\n\\n")
                    f.write("```json\\n")
                    f.write(json.dumps(game_data, indent=2))
                    f.write("\\n```\\n\\n")
                    
                    f.write("## MCP Request\\n\\n")
                    f.write("```json\\n")
                    f.write(json.dumps(mcp_request, indent=2))
                    f.write("\\n```\\n\\n")
                    
                    f.write("## Raw MCP Response\\n\\n")
                    f.write("```json\\n")
                    f.write(json.dumps(result, indent=2))
                    f.write("\\n```\\n\\n")
                    
                    f.write("## Analysis Text\\n\\n")
                    f.write("```\\n")
                    f.write(analysis_text)
                    f.write("\\n```\\n\\n")
                    
                    # Try to parse as JSON for additional details
                    try:
                        analysis_data = json.loads(analysis_text)
                        f.write("## Parsed Analysis Data\\n\\n")
                        if "analysis" in analysis_data:
                            analysis = analysis_data["analysis"]
                            
                            if "away_team_win_probability" in analysis and "home_team_win_probability" in analysis:
                                away_prob = analysis["away_team_win_probability"] * 100
                                home_prob = analysis["home_team_win_probability"] * 100
                                f.write(f"**Win Probabilities**:\\n")
                                f.write(f"- Red Sox: {away_prob:.1f}%\\n")
                                f.write(f"- Yankees: {home_prob:.1f}%\\n\\n")
                            
                            if "betting_recommendation" in analysis:
                                f.write(f"**Recommendation**: {analysis['betting_recommendation']}\\n\\n")
                            
                            if "expert_analysis" in analysis:
                                f.write("**Expert Analysis**:\\n")
                                f.write("```\\n")
                                f.write(analysis["expert_analysis"])
                                f.write("\\n```\\n\\n")
                    except json.JSONDecodeError:
                        f.write("## Analysis Format\\n\\n")
                        f.write("Analysis returned as text (not JSON)\\n\\n")
                    
                    f.write("---\\n\\n")
                    f.write("*This is a direct test of the /textonly command logic to verify Custom Chronulus MCP integration.*\\n")
                
                # Verify file was created
                if os.path.exists(md_file):
                    file_size = os.path.getsize(md_file)
                    print(f"SUCCESS: Markdown file created!")
                    print(f"  File: {md_file}")
                    print(f"  Size: {file_size} bytes")
                    
                    # Show a preview of what would go to Discord
                    try:
                        analysis_data = json.loads(analysis_text)
                        if "analysis" in analysis_data:
                            analysis = analysis_data["analysis"]
                            print(f"\\nDISCORD PREVIEW:")
                            print("-" * 20)
                            if "away_team_win_probability" in analysis:
                                away_prob = analysis["away_team_win_probability"] * 100
                                home_prob = analysis["home_team_win_probability"] * 100
                                print(f"Red Sox Win Probability: {away_prob:.1f}%")
                                print(f"Yankees Win Probability: {home_prob:.1f}%")
                            if "betting_recommendation" in analysis:
                                print(f"Recommendation: {analysis['betting_recommendation']}")
                    except:
                        print("\\nAnalysis returned as text format")
                    
                    return md_file
                else:
                    print(f"ERROR: File was not created")
                    return None
                    
            except Exception as file_error:
                print(f"ERROR: Failed to create markdown file: {file_error}")
                return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    async def main():
        print("DIRECT /textonly COMMAND TEST")
        print("Red Sox @ Yankees - Custom Chronulus Analysis")
        print("=" * 70)
        
        result = await test_textonly_direct()
        
        if result:
            print(f"\\nSUCCESS!")
            print(f"Complete analysis exported to: {result}")
            print(f"This shows exactly what the MCP returned vs what Discord should display.")
        else:
            print(f"\\nTest failed - check MCP server status")
    
    asyncio.run(main())