#!/usr/bin/env python3
"""
Soccer Schedule Finder
Enter a date and get upcoming matches across 5 major leagues with betting lines
"""
import asyncio
import json
import httpx
from datetime import datetime, timedelta
import sys

# Your MCP server URL
MCP_URL = "https://soccermcp-production.up.railway.app/mcp"

# League configurations - only leagues supported by your MCP server
LEAGUES = {
    "EPL": {"id": 228, "name": "Premier League", "country": "England"},
    "La Liga": {"id": 297, "name": "La Liga", "country": "Spain"}, 
    "MLS": {"id": 168, "name": "MLS", "country": "USA"}
}

async def mcp_call(tool_name: str, arguments: dict):
    """Make MCP call to get betting matches"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(MCP_URL, json=payload)
            result = response.json()
            
            if "result" in result and "content" in result["result"]:
                return json.loads(result["result"]["content"][0]["text"])
            else:
                return {"error": f"Unexpected response format: {result}"}
                
    except Exception as e:
        return {"error": f"Request failed: {e}"}

def validate_date_format(date_string):
    """Validate and convert date to proper format (DD-MM-YYYY)"""
    # Try different formats
    formats_to_try = [
        "%d-%m-%Y",    # DD-MM-YYYY
        "%d/%m/%Y",    # DD/MM/YYYY
        "%Y-%m-%d",    # YYYY-MM-DD
        "%m/%d/%Y",    # MM/DD/YYYY
        "%m-%d-%Y"     # MM-DD-YYYY
    ]
    
    for date_format in formats_to_try:
        try:
            parsed_date = datetime.strptime(date_string, date_format)
            return parsed_date.strftime("%d-%m-%Y")  # Return in DD-MM-YYYY format
        except ValueError:
            continue
    
    return None

def print_match_details(match, league_name):
    """Print detailed match information"""
    teams = match.get('teams', {})
    home_team = teams.get('home', {}).get('name', 'TBD')
    away_team = teams.get('away', {}).get('name', 'TBD')
    
    print(f"  {home_team} vs {away_team}")
    print(f"    Time: {match.get('time', 'TBD')}")
    print(f"    Status: {match.get('status', 'scheduled')}")
    print(f"    Match ID: {match.get('id', 'N/A')}")
    
    # Show betting odds if available
    odds = match.get('odds', {})
    if odds and isinstance(odds, dict):
        home_odds = odds.get('home')
        away_odds = odds.get('away') 
        draw_odds = odds.get('draw')
        
        if home_odds or away_odds or draw_odds:
            print(f"    Betting Lines:")
            if home_odds:
                print(f"      {home_team}: {home_odds}")
            if draw_odds:
                print(f"      Draw: {draw_odds}")
            if away_odds:
                print(f"      {away_team}: {away_odds}")
        else:
            print(f"    Betting Lines: Not available")
    else:
        print(f"    Betting Lines: Not available")
    
    # Check if real data or placeholder
    if home_team in ['None', 'TBD'] or away_team in ['None', 'TBD']:
        print(f"    Note: Placeholder data - real fixtures pending")
    else:
        print(f"    Note: Real match data")

async def get_matches_for_date(date_string):
    """Get matches for all leagues for the specified date"""
    print(f"\nSearching for matches on {date_string}...")
    print("=" * 60)
    
    total_matches = 0
    leagues_with_matches = 0
    
    for league_code, league_info in LEAGUES.items():
        print(f"\n{league_info['name']} ({league_info['country']}):")
        print("-" * 40)
        
        # Call MCP tool for this league
        result = await mcp_call("get_betting_matches", {
            "date": date_string,
            "league_filter": league_code
        })
        
        if "error" in result:
            print(f"  Error: {result['error']}")
            continue
        
        # Extract matches for this league
        matches_by_league = result.get('matches_by_league', {})
        league_matches = matches_by_league.get(league_code, [])
        
        if not league_matches:
            print(f"  No matches found")
            continue
        
        leagues_with_matches += 1
        total_matches += len(league_matches)
        
        print(f"  Found {len(league_matches)} matches:")
        
        for i, match in enumerate(league_matches, 1):
            print(f"\n  Match {i}:")
            print_match_details(match, league_info['name'])
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY FOR {date_string}")
    print(f"{'=' * 60}")
    print(f"Total matches found: {total_matches}")
    print(f"Leagues with matches: {leagues_with_matches}/{len(LEAGUES)}")
    
    if total_matches == 0:
        print(f"\nNo matches found for {date_string}")
        print("This could mean:")
        print("- No matches scheduled for this date")
        print("- Fixtures not yet released for current season")
        print("- Try a different date")

def print_help():
    """Print usage instructions"""
    print("Soccer Schedule Finder")
    print("=" * 50)
    print("Enter a date to find upcoming matches across 3 major leagues")
    print("\nSupported Leagues:")
    for code, info in LEAGUES.items():
        print(f"  - {info['name']} ({info['country']})")
    
    print(f"\nSupported Date Formats:")
    print(f"  - DD-MM-YYYY (e.g., 19-08-2025)")
    print(f"  - DD/MM/YYYY (e.g., 19/08/2025)")
    print(f"  - YYYY-MM-DD (e.g., 2025-08-19)")
    print(f"  - MM/DD/YYYY (e.g., 08/19/2025)")
    print(f"  - MM-DD-YYYY (e.g., 08-19-2025)")
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    print(f"\nSuggested Dates to Try:")
    print(f"  - Today: {today.strftime('%d-%m-%Y')}")
    print(f"  - Tomorrow: {tomorrow.strftime('%d-%m-%Y')}")
    print(f"  - Next Week: {next_week.strftime('%d-%m-%Y')}")

async def main():
    """Main function"""
    print_help()
    
    while True:
        print(f"\n" + "=" * 50)
        user_input = input("Enter date (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            print("Please enter a date")
            continue
        
        # Validate date format
        formatted_date = validate_date_format(user_input)
        if not formatted_date:
            print(f"Invalid date format: {user_input}")
            print("Please use one of the supported formats (see above)")
            continue
        
        print(f"Searching for matches on {formatted_date}...")
        
        try:
            await get_matches_for_date(formatted_date)
        except Exception as e:
            print(f"Error getting matches: {e}")
        
        # Ask if user wants to continue
        print(f"\n" + "-" * 50)
        continue_search = input("Search another date? (y/n): ").strip().lower()
        if continue_search not in ['y', 'yes']:
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)