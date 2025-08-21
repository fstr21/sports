#!/usr/bin/env python3
"""
Debug the pitcher matchup tool specifically
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_leagues.discord_bot.core.mcp_client import MCPClient

async def debug_pitcher_matchup():
    """Debug getMLBPitcherMatchup tool"""
    
    mcp_client = MCPClient(timeout=30.0, max_retries=3)
    mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
    
    print("Debugging getMLBPitcherMatchup...")
    print("=" * 50)
    
    try:
        # Test different parameter formats
        test_cases = [
            {"teams": [133, 142]},
            {"teams": [133, 142], "starts": 3},
            {"team_id": 133},
            {"team_ids": [133, 142]},
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n{i}. Testing with params: {params}")
            
            response = await mcp_client.call_mcp(mcp_url, "getMLBPitcherMatchup", params)
            
            if response.success:
                print("✓ Raw response received")
                print("Response data type:", type(response.data))
                print("Response data:", response.data)
                
                # Try to parse
                try:
                    parsed_data = await mcp_client.parse_mcp_content(response)
                    print("✓ Parsed successfully")
                    print("Parsed data type:", type(parsed_data))
                    print("Parsed data keys:", list(parsed_data.keys()) if isinstance(parsed_data, dict) else "Not a dict")
                    
                    if isinstance(parsed_data, dict) and "data" in parsed_data:
                        data_section = parsed_data["data"]
                        print("Data section keys:", list(data_section.keys()) if isinstance(data_section, dict) else "Not a dict")
                        
                        if "team_rosters" in data_section:
                            team_rosters = data_section["team_rosters"]
                            print("Team rosters keys:", list(team_rosters.keys()) if isinstance(team_rosters, dict) else "Not a dict")
                            
                except Exception as parse_error:
                    print("✗ Parse error:", parse_error)
                    print("Parse error type:", type(parse_error))
                    import traceback
                    traceback.print_exc()
                
                break  # Stop on first successful response
                
            else:
                print(f"✗ Error: {response.error}")
                
    except Exception as e:
        print(f"Exception during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(debug_pitcher_matchup())