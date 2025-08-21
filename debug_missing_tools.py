#!/usr/bin/env python3
"""
Debug the missing team info and pitcher matchup tools
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_leagues.discord_bot.core.mcp_client import MCPClient

async def debug_tools():
    """Debug the problematic tools"""
    
    mcp_client = MCPClient(timeout=30.0, max_retries=3)
    mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
    
    print("Debugging MLB Tools...")
    print("=" * 50)
    
    try:
        # Test getMLBTeams
        print("\n1. Testing getMLBTeams:")
        teams_response = await mcp_client.call_mcp(mcp_url, "getMLBTeams", {})
        
        if teams_response.success:
            print("Raw response:", teams_response.data)
            parsed_data = await mcp_client.parse_mcp_content(teams_response)
            print("Parsed data keys:", list(parsed_data.keys()) if parsed_data else "None")
            if parsed_data:
                teams = parsed_data.get("data", {}).get("teams", [])
                print(f"Found {len(teams)} teams")
                if teams:
                    athletics = next((t for t in teams if t.get("id") == 133), None)
                    if athletics:
                        print(f"Athletics info: {athletics}")
        else:
            print("ERROR:", teams_response.error)
        
        # Test getMLBPitcherMatchup with simpler parameters
        print("\n2. Testing getMLBPitcherMatchup:")
        pitcher_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBPitcherMatchup", 
            {"teams": [133, 142]}  # Simplified - no "starts" parameter
        )
        
        if pitcher_response.success:
            print("Raw response:", pitcher_response.data)
            parsed_data = await mcp_client.parse_mcp_content(pitcher_response)
            print("Parsed data keys:", list(parsed_data.keys()) if parsed_data else "None")
        else:
            print("ERROR:", pitcher_response.error)
            
    except Exception as e:
        print(f"Exception during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(debug_tools())