#!/usr/bin/env python3
"""
Test script using the official MCP client library
"""
import asyncio
import subprocess
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Update this path to point to your comprehensive MCP server
PYTHON = r"C:\Users\fstr2\AppData\Local\Programs\Python\Python313\python.exe"
SERVER = r"C:\Users\fstr2\Desktop\sports\mcp\wnba_comprehensive_mcp.py"

async def test_mcp_server():
    """Test the MCP server using the official client"""
    
    print("Starting WNBA MCP server test with official client...")
    print(f"Server: {SERVER}")
    
    # Create server parameters
    server_params = StdioServerParameters(
        command=PYTHON,
        args=[SERVER],
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                print("1. Initializing MCP session...")
                await session.initialize()
                print("✅ MCP session initialized successfully")
                
                # List available tools
                print("2. Listing available tools...")
                tools_result = await session.list_tools()
                print("✅ Successfully retrieved tools list!")
                
                print("\n" + "="*50)
                print("AVAILABLE TOOLS")
                print("="*50)
                
                if not tools_result.tools:
                    print("No tools found!")
                else:
                    for tool in tools_result.tools:
                        print(f"🔧 {tool.name}: {tool.description}")
                
                # Test the getWnbaUpcomingGames tool
                print("\n3. Testing getWnbaUpcomingGames tool...")
                
                # Find the tool
                upcoming_games_tool = None
                for tool in tools_result.tools:
                    if tool.name == "getWnbaUpcomingGames":
                        upcoming_games_tool = tool
                        break
                
                if not upcoming_games_tool:
                    print("❌ getWnbaUpcomingGames tool not found!")
                    return False
                
                # Call the tool
                result = await session.call_tool(
                    name="getWnbaUpcomingGames",
                    arguments={"days": 3}
                )
                
                print("✅ Successfully called getWnbaUpcomingGames!")
                
                print("\n" + "="*50)
                print("UPCOMING WNBA GAMES")
                print("="*50)
                
                # Process the result
                for content in result.content:
                    if hasattr(content, 'type') and content.type == "json":
                        games_data = content.data
                        upcoming_games = games_data.get("upcoming_games", [])
                        days_searched = games_data.get("days_searched", 0)
                        
                        print(f"\nSearched {days_searched} days ahead:")
                        
                        if not upcoming_games:
                            print("No games found in the next few days.")
                        else:
                            for day in upcoming_games:
                                date = day.get("date", "")
                                games = day.get("games", [])
                                
                                print(f"\n📅 {date}:")
                                for game in games:
                                    name = game.get("name", "Unknown matchup")
                                    short_name = game.get("shortName", "")
                                    status = game.get("status", {}).get("type", {}).get("shortDetail", "")
                                    print(f"  🏀 {name} ({short_name}) - {status}")
                    
                    elif hasattr(content, 'type') and content.type == "text":
                        print(content.text)
                
                return True
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()