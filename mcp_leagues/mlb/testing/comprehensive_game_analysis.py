#!/usr/bin/env python3
"""
Comprehensive game analysis for a specific MLB game
Shows exactly what data should appear in Discord embeds for verification
"""
import asyncio
import json
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from discord_bot.core.mcp_client import MCPClient

async def analyze_specific_game():
    """Analyze a specific game with all available tools"""
    
    mcp_client = MCPClient(timeout=30.0, max_retries=3)
    mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
    
    # Test specific game: Athletics @ Minnesota Twins
    game_date = "2025-08-21"
    athletics_id = 133  # Away team
    twins_id = 142     # Home team
    
    print("=" * 80)
    print(f"COMPREHENSIVE MLB GAME ANALYSIS")
    print(f"Date: {game_date}")
    print(f"Matchup: Athletics (ID: {athletics_id}) @ Minnesota Twins (ID: {twins_id})")
    print("=" * 80)
    
    try:
        # 1. Get schedule to confirm game details
        print("\n1. GAME SCHEDULE DETAILS")
        print("-" * 40)
        schedule_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBScheduleET", 
            {"date": game_date}
        )
        
        if schedule_response.success:
            schedule_data = await mcp_client.parse_mcp_content(schedule_response)
            games = schedule_data.get("data", {}).get("games", [])
            
            # Find our specific game
            target_game = None
            for game in games:
                if (game.get("away", {}).get("teamId") == athletics_id and 
                    game.get("home", {}).get("teamId") == twins_id):
                    target_game = game
                    break
            
            if target_game:
                print(f"FOUND Game: {target_game.get('away', {}).get('name')} @ {target_game.get('home', {}).get('name')}")
                print(f"  Game ID: {target_game.get('gamePk')}")
                print(f"  Start Time: {target_game.get('start_et')}")
                print(f"  Status: {target_game.get('status')}")
                print(f"  Venue: {target_game.get('venue')}")
            else:
                print("ERROR: Game not found in schedule")
                return
        else:
            print(f"ERROR: Schedule error: {schedule_response.error}")
            return
        
        # 2. Team Form Analysis
        print("\n2. TEAM FORM ANALYSIS")
        print("-" * 40)
        
        # Athletics form
        athletics_form_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBTeamForm", 
            {"team_id": athletics_id}
        )
        
        if athletics_form_response.success:
            athletics_form_data = await mcp_client.parse_mcp_content(athletics_form_response)
            athletics_form = athletics_form_data.get("data", {}).get("form", {})
            
            print(f"AWAY - Athletics:")
            print(f"   Record: {athletics_form.get('wins', 0)}-{athletics_form.get('losses', 0)}")
            print(f"   Win %: {athletics_form.get('win_percentage', 'N/A')}")
            print(f"   Streak: {athletics_form.get('streak', 'N/A')}")
            print(f"   Games Back: {athletics_form.get('games_back', 'N/A')}")
            print(f"   Last 10: {athletics_form.get('last_10', 'N/A')}")
            print(f"   Home Record: {athletics_form.get('home_record', 'N/A')}")
            print(f"   Away Record: {athletics_form.get('away_record', 'N/A')}")
        else:
            print(f"ERROR: Athletics form error: {athletics_form_response.error}")
        
        # Twins form
        twins_form_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBTeamForm", 
            {"team_id": twins_id}
        )
        
        if twins_form_response.success:
            twins_form_data = await mcp_client.parse_mcp_content(twins_form_response)
            twins_form = twins_form_data.get("data", {}).get("form", {})
            
            print(f"\nHOME - Minnesota Twins:")
            print(f"   Record: {twins_form.get('wins', 0)}-{twins_form.get('losses', 0)}")
            print(f"   Win %: {twins_form.get('win_percentage', 'N/A')}")
            print(f"   Streak: {twins_form.get('streak', 'N/A')}")
            print(f"   Games Back: {twins_form.get('games_back', 'N/A')}")
            print(f"   Last 10: {twins_form.get('last_10', 'N/A')}")
            print(f"   Home Record: {twins_form.get('home_record', 'N/A')}")
            print(f"   Away Record: {twins_form.get('away_record', 'N/A')}")
        else:
            print(f"ERROR: Twins form error: {twins_form_response.error}")
        
        # 3. Scoring Trends Analysis
        print("\n3. SCORING TRENDS ANALYSIS")
        print("-" * 40)
        
        # Athletics trends
        athletics_trends_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBTeamScoringTrends", 
            {"team_id": athletics_id}
        )
        
        if athletics_trends_response.success:
            athletics_trends_data = await mcp_client.parse_mcp_content(athletics_trends_response)
            athletics_trends = athletics_trends_data.get("data", {}).get("trends", {})
            
            print(f"AWAY - Athletics Offense:")
            print(f"   Runs/Game: {athletics_trends.get('runs_per_game', 0):.1f}")
            print(f"   Allowed/Game: {athletics_trends.get('runs_allowed_per_game', 0):.1f}")
            print(f"   Run Differential: {athletics_trends.get('run_differential', 0):+d}")
            print(f"   Games Played: {athletics_trends.get('games_played', 0)}")
            print(f"   Total Runs Scored: {athletics_trends.get('total_runs_scored', 0)}")
            print(f"   Total Runs Allowed: {athletics_trends.get('total_runs_allowed', 0)}")
            print(f"   Run Diff/Game: {athletics_trends.get('run_differential_per_game', 0):.1f}")
        else:
            print(f"ERROR: Athletics trends error: {athletics_trends_response.error}")
        
        # Twins trends
        twins_trends_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBTeamScoringTrends", 
            {"team_id": twins_id}
        )
        
        if twins_trends_response.success:
            twins_trends_data = await mcp_client.parse_mcp_content(twins_trends_response)
            twins_trends = twins_trends_data.get("data", {}).get("trends", {})
            
            print(f"\nHOME - Minnesota Twins Offense:")
            print(f"   Runs/Game: {twins_trends.get('runs_per_game', 0):.1f}")
            print(f"   Allowed/Game: {twins_trends.get('runs_allowed_per_game', 0):.1f}")
            print(f"   Run Differential: {twins_trends.get('run_differential', 0):+d}")
            print(f"   Games Played: {twins_trends.get('games_played', 0)}")
            print(f"   Total Runs Scored: {twins_trends.get('total_runs_scored', 0)}")
            print(f"   Total Runs Allowed: {twins_trends.get('total_runs_allowed', 0)}")
            print(f"   Run Diff/Game: {twins_trends.get('run_differential_per_game', 0):.1f}")
        else:
            print(f"ERROR: Twins trends error: {twins_trends_response.error}")
        
        # 4. Team Information
        print("\n4. TEAM INFORMATION")
        print("-" * 40)
        
        teams_response = await mcp_client.call_mcp(mcp_url, "getMLBTeams", {})
        if teams_response.success:
            teams_data = await mcp_client.parse_mcp_content(teams_response)
            teams = teams_data.get("data", {}).get("teams", [])
            
            athletics_info = next((t for t in teams if t.get("id") == athletics_id), None)
            twins_info = next((t for t in teams if t.get("id") == twins_id), None)
            
            if athletics_info:
                print(f"Athletics Full Info: {athletics_info.get('name')} ({athletics_info.get('abbreviation')})")
                print(f"   Division: {athletics_info.get('division', 'N/A')}")
                print(f"   League: {athletics_info.get('league', 'N/A')}")
                print(f"   Venue: {athletics_info.get('venue', 'N/A')}")
            
            if twins_info:
                print(f"Twins Full Info: {twins_info.get('name')} ({twins_info.get('abbreviation')})")
                print(f"   Division: {twins_info.get('division', 'N/A')}")
                print(f"   League: {twins_info.get('league', 'N/A')}")
                print(f"   Venue: {twins_info.get('venue', 'N/A')}")
                
            # Check for division rivalry
            if athletics_info and twins_info:
                athletics_division = athletics_info.get('division', '')
                twins_division = twins_info.get('division', '')
                if athletics_division == twins_division and athletics_division:
                    print(f"\nDIVISION RIVALRY: Both teams in {athletics_division}")
                else:
                    print(f"\nINTER-DIVISION: {athletics_info.get('division', 'Unknown')} vs {twins_info.get('division', 'Unknown')}")
        
        # 5. Pitcher Matchup Analysis
        print("\n5. PITCHER MATCHUP ANALYSIS")
        print("-" * 40)
        
        pitcher_response = await mcp_client.call_mcp(
            mcp_url, 
            "getMLBPitcherMatchup", 
            {"teams": [athletics_id, twins_id], "starts": 3}
        )
        
        if pitcher_response.success:
            pitcher_data = await mcp_client.parse_mcp_content(pitcher_response)
            team_rosters = pitcher_data.get("data", {}).get("team_rosters", {})
            
            # Athletics pitchers
            athletics_roster = team_rosters.get(str(athletics_id), {})
            if athletics_roster:
                print(f"Athletics Pitching Staff:")
                print(f"   Total Pitchers: {athletics_roster.get('pitchers', 0)}")
                pitchers = athletics_roster.get('pitcher_list', [])[:5]
                for i, pitcher in enumerate(pitchers, 1):
                    name = pitcher.get('fullName', 'Unknown')
                    number = pitcher.get('primaryNumber', '')
                    status = pitcher.get('status', '')
                    print(f"   {i}. #{number} {name} ({status})")
            
            # Twins pitchers  
            twins_roster = team_rosters.get(str(twins_id), {})
            if twins_roster:
                print(f"\nTwins Pitching Staff:")
                print(f"   Total Pitchers: {twins_roster.get('pitchers', 0)}")
                pitchers = twins_roster.get('pitcher_list', [])[:5]
                for i, pitcher in enumerate(pitchers, 1):
                    name = pitcher.get('fullName', 'Unknown')
                    number = pitcher.get('primaryNumber', '')
                    status = pitcher.get('status', '')
                    print(f"   {i}. #{number} {name} ({status})")
        else:
            print(f"ERROR: Pitcher matchup error: {pitcher_response.error}")
        
        # 6. Summary for Discord Embed Verification
        print("\n6. DISCORD EMBED VERIFICATION")
        print("=" * 80)
        print("This is what should appear in Discord:")
        print()
        
        print("EMBED 1: Enhanced Basic Game Analysis")
        print(f"Title: Athletics @ Minnesota Twins")
        print(f"Game Info: Time: {target_game.get('start_et', 'TBD')}, Venue: {target_game.get('venue', 'TBD')}, League: MLB")
        if athletics_info and twins_info:
            athletics_division = athletics_info.get('division', 'Unknown')
            twins_division = twins_info.get('division', 'Unknown')
            if athletics_division == twins_division and athletics_division != 'Unknown':
                print(f"Division Context: DIVISION RIVALRY - {athletics_division}")
            else:
                print(f"Division Context: Away: {athletics_division}, Home: {twins_division}")
        print(f"Status: {target_game.get('status', 'Scheduled')}")
        print()
        
        if athletics_form_response.success and twins_form_response.success:
            print("EMBED 2: Team Form Analysis")
            print(f"Title: Team Form: Athletics vs Minnesota Twins")
            athletics_form = athletics_form_data.get("data", {}).get("form", {})
            twins_form = twins_form_data.get("data", {}).get("form", {})
            print(f"Athletics (Away): Record {athletics_form.get('wins')}-{athletics_form.get('losses')}, Win% {athletics_form.get('win_percentage')}, Streak {athletics_form.get('streak')}, GB {athletics_form.get('games_back')}")
            print(f"Twins (Home): Record {twins_form.get('wins')}-{twins_form.get('losses')}, Win% {twins_form.get('win_percentage')}, Streak {twins_form.get('streak')}, GB {twins_form.get('games_back')}")
            print()
        
        if athletics_trends_response.success and twins_trends_response.success:
            print("EMBED 3: Scoring Trends Analysis")
            print(f"Title: Scoring Trends: Athletics vs Minnesota Twins")
            athletics_trends = athletics_trends_data.get("data", {}).get("trends", {})
            twins_trends = twins_trends_data.get("data", {}).get("trends", {})
            print(f"Athletics Offense: {athletics_trends.get('runs_per_game'):.1f} runs/game, {athletics_trends.get('runs_allowed_per_game'):.1f} allowed/game, {athletics_trends.get('run_differential'):+d} run diff, {athletics_trends.get('games_played')} games")
            print(f"Twins Offense: {twins_trends.get('runs_per_game'):.1f} runs/game, {twins_trends.get('runs_allowed_per_game'):.1f} allowed/game, {twins_trends.get('run_differential'):+d} run diff, {twins_trends.get('games_played')} games")
            print()
        
        if pitcher_response.success:
            print("EMBED 4: Pitcher Matchup Analysis")
            print(f"Title: Pitching Matchup: Athletics vs Minnesota Twins")
            if athletics_roster:
                print(f"Athletics Rotation: Top 3 pitchers from {athletics_roster.get('pitchers', 0)} total")
                pitchers = athletics_roster.get('pitcher_list', [])[:3]
                for pitcher in pitchers:
                    name = pitcher.get('fullName', 'Unknown')
                    number = pitcher.get('primaryNumber', '')
                    print(f"  #{number} {name}")
            if twins_roster:
                print(f"Twins Rotation: Top 3 pitchers from {twins_roster.get('pitchers', 0)} total")
                pitchers = twins_roster.get('pitcher_list', [])[:3]
                for pitcher in pitchers:
                    name = pitcher.get('fullName', 'Unknown')
                    number = pitcher.get('primaryNumber', '')
                    print(f"  #{number} {name}")
            print(f"Pitching Depth: Athletics {athletics_roster.get('pitchers', 0)} vs Twins {twins_roster.get('pitchers', 0)} pitchers")
        
        print("\n" + "=" * 80)
        print("Analysis complete! Compare this with your Discord bot output.")
        print("=" * 80)
            
    except Exception as e:
        print(f"Exception during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(analyze_specific_game())