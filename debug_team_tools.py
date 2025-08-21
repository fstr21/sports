#!/usr/bin/env python3
"""
Quick test of MLB team form and scoring trends tools
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_leagues.discord_bot.core.mcp_client import MCPClient

async def test_team_tools():
    """Test MLB team form and scoring trends tools"""
    
    mcp_client = MCPClient(timeout=30.0, max_retries=3)
    mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
    
    # Test teams from the Athletics vs Twins game
    athletics_id = 133
    twins_id = 142
    
    print(f"Testing MLB team tools...")
    print(f"Athletics ID: {athletics_id}")
    print(f"Twins ID: {twins_id}")
    print("=" * 60)
    
    try:
        # Test getMLBTeamForm
        print("\n1. Testing getMLBTeamForm for Athletics (133):")
        athletics_form_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBTeamForm", 
            {"team_id": athletics_id}
        )
        
        if athletics_form_response.success:
            print("Raw response:", athletics_form_response.data)
            parsed_data = await mcp_client.parse_mcp_content(athletics_form_response)
            print("Parsed data:", parsed_data)
        else:
            print("ERROR:", athletics_form_response.error)
        
        print("\n2. Testing getMLBTeamForm for Twins (142):")
        twins_form_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBTeamForm", 
            {"team_id": twins_id}
        )
        
        if twins_form_response.success:
            print("Raw response:", twins_form_response.data)
            parsed_data = await mcp_client.parse_mcp_content(twins_form_response)
            print("Parsed data:", parsed_data)
        else:
            print("ERROR:", twins_form_response.error)
            
        print("\n3. Testing getMLBTeamScoringTrends for Athletics (133):")
        athletics_trends_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBTeamScoringTrends", 
            {"team_id": athletics_id}
        )
        
        if athletics_trends_response.success:
            print("Raw response:", athletics_trends_response.data)
            parsed_data = await mcp_client.parse_mcp_content(athletics_trends_response)
            print("Parsed data:", parsed_data)
        else:
            print("ERROR:", athletics_trends_response.error)
            
    except Exception as e:
        print(f"Exception during testing: {e}")
    finally:
        await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(test_team_tools())