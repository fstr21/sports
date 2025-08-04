import asyncio
import json
import sys
from datetime import datetime
# Corrected import: Removed ToolCallResult
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# --- Configuration ---
# Update this path to point to your Python executable
PYTHON = r"C:\Users\fstr2\AppData\Local\Programs\Python\Python313\python.exe"
# Update this path to point to your comprehensive MCP server script
SERVER = r"C:\Users\fstr2\Desktop\sports\mcp\wnba_comprehensive_mcp.py"

OUTPUT_JSON = "wnba_mcp_exploration_results.json"

# Corrected function signature: Removed the ToolCallResult type hint
def process_tool_result(result) -> dict | None:
    """Helper function to extract the JSON data from a tool call result."""
    if result and result.content:
        for content in result.content:
            if getattr(content, "type", "") == "json":
                return content.data
    return None

async def explore_mcp_server():
    """
    Explore the WNBA MCP server by calling each available tool and saving the results.
    """
    print("🚀 Starting WNBA MCP server exploration...")
    
    server_params = StdioServerParameters(
        command=PYTHON,
        args=[SERVER],
    )

    # This dictionary will store the results from each tool call
    output = {
        "teams_data": None,
        "team_schedule_data": None,
        "scoreboard_data": None,
        "game_boxscore_data": None,
        "standings_data": None,
        "upcoming_games_data": None,
    }

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ MCP session initialized.")

                # 1. Get all WNBA Teams
                print("\n[1/6] 🏀 Calling 'getWnbaTeams'...")
                teams_result = await session.call_tool(name="getWnbaTeams")
                output["teams_data"] = process_tool_result(teams_result)
                print("✅ Success! Found team data.")

                # 2. Get a schedule for the first team found
                print("\n[2/6] 📅 Calling 'getWnbaTeamSchedule'...")
                first_team_id = None
                if output["teams_data"]:
                    try:
                        first_team_id = output["teams_data"]["sports"][0]["leagues"][0]["teams"][0]["team"]["id"]
                        print(f"   -> Found team ID: {first_team_id}. Using it to get the schedule.")
                        schedule_result = await session.call_tool(
                            name="getWnbaTeamSchedule",
                            arguments={"team_id": first_team_id}
                        )
                        output["team_schedule_data"] = process_tool_result(schedule_result)
                        print("✅ Success! Retrieved team schedule.")
                    except (KeyError, IndexError) as e:
                        print(f"   -> Could not extract a team ID from the teams data. Skipping schedule call. Error: {e}")
                else:
                    print("   -> No team data found, skipping schedule call.")

                # 3. Get the scoreboard for today
                today_str = datetime.now().strftime("%Y%m%d")
                print(f"\n[3/6] 📊 Calling 'getWnbaScoreboard' for today ({today_str})...")
                scoreboard_result = await session.call_tool(
                    name="getWnbaScoreboard",
                    arguments={"dates": today_str}
                )
                output["scoreboard_data"] = process_tool_result(scoreboard_result)
                print("✅ Success! Retrieved scoreboard.")
                
                # 4. Get the box score for the first game on the scoreboard
                print("\n[4/6] 📋 Calling 'getWnbaGameBoxScore'...")
                first_game_id = None
                if output["scoreboard_data"] and output["scoreboard_data"].get("events"):
                    try:
                        first_game_id = output["scoreboard_data"]["events"][0]["id"]
                        print(f"   -> Found game ID: {first_game_id}. Using it to get the box score.")
                        boxscore_result = await session.call_tool(
                            name="getWnbaGameBoxScore",
                            arguments={"game_id": first_game_id}
                        )
                        output["game_boxscore_data"] = process_tool_result(boxscore_result)
                        print("✅ Success! Retrieved game box score.")
                    except (KeyError, IndexError) as e:
                        print(f"   -> No games on today's scoreboard or could not find ID. Skipping box score call. Error: {e}")
                else:
                    print("   -> No games found on the scoreboard, skipping box score call.")

                # 5. Get current WNBA Standings
                print("\n[5/6] 🏆 Calling 'getWnbaStandings'...")
                standings_result = await session.call_tool(name="getWnbaStandings")
                output["standings_data"] = process_tool_result(standings_result)
                print("✅ Success! Retrieved league standings.")

                # 6. Get upcoming games for the next 2 days
                print("\n[6/6] 🗓️  Calling 'getWnbaUpcomingGames'...")
                upcoming_result = await session.call_tool(
                    name="getWnbaUpcomingGames",
                    arguments={"days": 2}
                )
                output["upcoming_games_data"] = process_tool_result(upcoming_result)
                print("✅ Success! Retrieved upcoming games.")
                
                # --- All tests complete, save the results ---
                print("\n" + "="*50)
                print(" MCP EXPLORATION COMPLETE ")
                print("="*50)

                try:
                    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                        json.dump(output, f, ensure_ascii=False, indent=2)
                    print(f"\n💾 Results successfully written to '{OUTPUT_JSON}'")
                except Exception as e:
                    print(f"❌ Failed to write JSON output: {e}")

                return True

    except Exception as e:
        print(f"\n❌ A critical error occurred during the exploration: {e}")
        import traceback
        traceback.print_exc()
        # Attempt to write whatever data was collected before the error
        try:
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Partial results have been written to '{OUTPUT_JSON}'")
        except Exception as write_error:
            print(f"❌ Additionally, failed to write partial results to JSON: {write_error}")
        return False

def main():
    success = asyncio.run(explore_mcp_server())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
