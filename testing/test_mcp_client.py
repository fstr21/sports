#!/usr/bin/env python3
import asyncio
import json
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Update this path to point to your comprehensive MCP server
PYTHON = r"C:\Users\fstr2\AppData\Local\Programs\Python\Python313\python.exe"
SERVER = r"C:\Users\fstr2\Desktop\sports\mcp\wnba_comprehensive_mcp.py"

OUTPUT_JSON = "wnba_mcp_output.json"

async def test_mcp_server():
    """Test the MCP server using the official client and write results to JSON"""
    print("Starting WNBA MCP server test with official client...")
    print(f"Server: {SERVER}")

    server_params = StdioServerParameters(
        command=PYTHON,
        args=[SERVER],
    )

    output = {
        "tools": [],
        "upcoming_games_call": {
            "arguments": {"days": 3},
            "result": None,
            "raw_contents": []
        }
    }

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

                tools_serialized = []
                if not tools_result.tools:
                    print("No tools found!")
                else:
                    for tool in tools_result.tools:
                        print(f"🔧 {tool.name}: {tool.description}")
                        tools_serialized.append({
                            "name": tool.name,
                            "description": tool.description
                        })
                output["tools"] = tools_serialized

                # Test the getWnbaUpcomingGames tool
                print("\n3. Testing getWnbaUpcomingGames tool...")
                result = await session.call_tool(
                    name="getWnbaUpcomingGames",
                    arguments=output["upcoming_games_call"]["arguments"]
                )
                print("✅ Successfully called getWnbaUpcomingGames!")

                print("\n" + "="*50)
                print("UPCOMING WNBA GAMES")
                print("="*50)

                # Prepare a JSON-safe structure of tool call result
                call_result_json = None
                raw_contents = []

                for content in result.content:
                    # The official client returns content objects; we extract json or text
                    if getattr(content, "type", "") == "json":
                        data = content.data
                        call_result_json = data
                        upcoming_games = data.get("upcoming_games", [])
                        days_searched = data.get("days_searched", 0)

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
                                    status = (game.get("status", {})
                                              .get("type", {})
                                              .get("shortDetail", ""))
                                    print(f"  🏀 {name} ({short_name}) - {status}")
                    elif getattr(content, "type", "") == "text":
                        raw_contents.append({"type": "text", "text": content.text})
                    else:
                        # Fallback generic serialization
                        raw_contents.append({
                            "type": getattr(content, "type", "unknown"),
                            "repr": repr(content)
                        })

                output["upcoming_games_call"]["result"] = call_result_json
                output["upcoming_games_call"]["raw_contents"] = raw_contents

                # Write the collected data to JSON
                try:
                    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                        json.dump(output, f, ensure_ascii=False, indent=2)
                    print(f"\n💾 Results written to {OUTPUT_JSON}")
                except Exception as e:
                    print(f"❌ Failed to write JSON output: {e}")

                return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        # Attempt to write whatever we have so far
        try:
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Partial results written to {OUTPUT_JSON}")
        except Exception as ew:
            print(f"❌ Also failed to write partial JSON output: {ew}")
        return False

def main():
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()