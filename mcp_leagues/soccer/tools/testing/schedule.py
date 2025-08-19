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

# League configurations - all leagues supported by your MCP server
LEAGUES = {
    "EPL": {"id": 228, "name": "Premier League", "country": "England"},
    "La Liga": {"id": 297, "name": "La Liga", "country": "Spain"}, 
    "MLS": {"id": 168, "name": "MLS", "country": "USA"},
    "Bundesliga": {"id": 241, "name": "Bundesliga", "country": "Germany"},
    "Serie A": {"id": 253, "name": "Serie A", "country": "Italy"},
    "UEFA": {"id": 310, "name": "UEFA Champions League", "country": "Europe"}
}

def convert_to_american_odds(decimal_odds):
    """Convert decimal odds to American format"""
    try:
        decimal = float(decimal_odds)
        if decimal >= 2.0:
            # Positive American odds
            american = int((decimal - 1) * 100)
            return f"+{american}"
        else:
            # Negative American odds  
            american = int(-100 / (decimal - 1))
            return str(american)
    except (ValueError, ZeroDivisionError, TypeError):
        return str(decimal_odds)

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
        # Check for match_winner odds format
        match_winner = odds.get('match_winner', {})
        if match_winner:
            home_odds = match_winner.get('home')
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
            
            print(f"    Betting Lines:")
            if home_odds:
                american_home = convert_to_american_odds(home_odds)
                print(f"      {home_team}: {home_odds} ({american_home})")
            if draw_odds:
                american_draw = convert_to_american_odds(draw_odds)
                print(f"      Draw: {draw_odds} ({american_draw})")
            if away_odds:
                american_away = convert_to_american_odds(away_odds)
                print(f"      {away_team}: {away_odds} ({american_away})")
            
            # Show over/under if available
            over_under = odds.get('over_under', {})
            if over_under:
                total = over_under.get('total')
                over = over_under.get('over')
                under = over_under.get('under')
                if total and over and under:
                    american_over = convert_to_american_odds(over)
                    american_under = convert_to_american_odds(under)
                    print(f"      Over/Under {total}: Over {over} ({american_over}), Under {under} ({american_under})")
        else:
            # Try old format
            home_odds = odds.get('home')
            away_odds = odds.get('away') 
            draw_odds = odds.get('draw')
            
            if home_odds or away_odds or draw_odds:
                print(f"    Betting Lines:")
                if home_odds:
                    american_home = convert_to_american_odds(home_odds)
                    print(f"      {home_team}: {home_odds} ({american_home})")
                if draw_odds:
                    american_draw = convert_to_american_odds(draw_odds)
                    print(f"      Draw: {draw_odds} ({american_draw})")
                if away_odds:
                    american_away = convert_to_american_odds(away_odds)
                    print(f"      {away_team}: {away_odds} ({american_away})")
            else:
                print(f"    Betting Lines: Not available")
    else:
        print(f"    Betting Lines: Not available")
    
    # Check if real data or placeholder
    if home_team in ['None', 'TBD'] or away_team in ['None', 'TBD']:
        print(f"    Note: Placeholder data - real fixtures pending")
    else:
        print(f"    Note: Real match data")

async def get_h2h_analysis(home_team_id, away_team_id, home_team_name, away_team_name):
    """Get head-to-head analysis between two teams"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_h2h_betting_analysis",
            "arguments": {
                "team_1_id": home_team_id,
                "team_2_id": away_team_id,
                "team_1_name": home_team_name,
                "team_2_name": away_team_name
            }
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

async def get_enhanced_h2h_data(home_team_id, away_team_id):
    """Get raw H2H data directly from SoccerDataAPI for enhanced analysis"""
    import os
    AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.soccerdataapi.com/head-to-head/",
                params={
                    "team_1_id": home_team_id,
                    "team_2_id": away_team_id,
                    "auth_token": AUTH_KEY
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
                
    except Exception as e:
        return {"error": f"Request failed: {e}"}

async def get_team_recent_matches(team_id, league_id, limit=10):
    """Get recent matches for a specific team using matches endpoint"""
    import os
    AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.soccerdataapi.com/matches/",
                params={
                    "team_id": team_id,
                    "league_id": league_id,
                    "season": "2024-2025",  # Get recent completed season
                    "auth_token": AUTH_KEY
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract matches from the response structure
                matches = []
                if isinstance(data, list) and data:
                    for league_data in data:
                        if 'stage' in league_data:
                            for stage in league_data['stage']:
                                if 'matches' in stage:
                                    matches.extend(stage['matches'])
                
                # Filter for completed matches and limit
                completed_matches = [
                    match for match in matches 
                    if match.get('status') in ['complete', 'finished', 'full-time']
                ]
                
                # Sort by date (most recent first) and limit
                completed_matches.sort(key=lambda x: x.get('date', ''), reverse=True)
                return completed_matches[:limit]
            else:
                return []
                
    except Exception as e:
        print(f"Error getting recent matches: {e}")
        return []

async def get_custom_h2h_analysis(home_team_id, away_team_id, home_team_name, away_team_name, league_id):
    """Create custom H2H analysis using recent matches approach"""
    print("  Fetching recent matches for both teams...")
    
    # Get recent matches for both teams
    home_recent = await get_team_recent_matches(home_team_id, league_id, 15)
    away_recent = await get_team_recent_matches(away_team_id, league_id, 15)
    
    # Find matches where they played each other
    h2h_matches = []
    
    for home_match in home_recent:
        teams = home_match.get('teams', {})
        home_in_match = teams.get('home', {}).get('id')
        away_in_match = teams.get('away', {}).get('id')
        
        # Check if this match involved both teams
        if ((home_in_match == home_team_id and away_in_match == away_team_id) or
            (home_in_match == away_team_id and away_in_match == home_team_id)):
            h2h_matches.append(home_match)
    
    # Also check away team's matches (to catch any missed)
    for away_match in away_recent:
        teams = away_match.get('teams', {})
        home_in_match = teams.get('home', {}).get('id')
        away_in_match = teams.get('away', {}).get('id')
        
        # Check if this match involved both teams and isn't already added
        if ((home_in_match == home_team_id and away_in_match == away_team_id) or
            (home_in_match == away_team_id and away_in_match == home_team_id)):
            # Check if not already in list
            match_id = away_match.get('id')
            if not any(m.get('id') == match_id for m in h2h_matches):
                h2h_matches.append(away_match)
    
    # Sort H2H matches by date (most recent first)
    h2h_matches.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return {
        'home_team_name': home_team_name,
        'away_team_name': away_team_name,
        'home_recent_matches': home_recent[:10],  # Last 10 games each team
        'away_recent_matches': away_recent[:10],
        'h2h_recent_matches': h2h_matches[:5],  # Last 5 H2H meetings
        'total_recent_h2h': len(h2h_matches)
    }

def print_custom_h2h_analysis(custom_data):
    """Print custom H2H analysis based on recent matches"""
    print(f"\n{'='*50}")
    print("CUSTOM H2H ANALYSIS (Recent Matches Approach)")
    print(f"{'='*50}")
    
    home_name = custom_data.get('home_team_name', 'Home Team')
    away_name = custom_data.get('away_team_name', 'Away Team')
    
    home_recent = custom_data.get('home_recent_matches', [])
    away_recent = custom_data.get('away_recent_matches', [])
    h2h_recent = custom_data.get('h2h_recent_matches', [])
    
    print(f"🔍 RECENT FORM ANALYSIS:")
    print(f"  {home_name}: {len(home_recent)} recent matches analyzed")
    print(f"  {away_name}: {len(away_recent)} recent matches analyzed") 
    print(f"  Recent H2H meetings found: {len(h2h_recent)}")
    
    if h2h_recent:
        print(f"\n⚔️ RECENT HEAD-TO-HEAD MEETINGS:")
        print("-" * 40)
        
        home_wins = 0
        away_wins = 0
        draws = 0
        total_goals = 0
        
        for i, match in enumerate(h2h_recent, 1):
            date = match.get('date', 'Unknown')
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            goals = match.get('goals', {})
            
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            total_goals += home_goals + away_goals
            
            # Determine who was home/away in this specific match
            match_home_name = home_team.get('name', 'Unknown')
            match_away_name = away_team.get('name', 'Unknown')
            
            print(f"  {i}. {date}: {match_home_name} {home_goals}-{away_goals} {match_away_name}")
            
            # Track wins from perspective of our current home/away teams
            if home_team.get('id') == custom_data.get('home_team_id'):
                # Home team was home in this match
                if home_goals > away_goals:
                    home_wins += 1
                elif away_goals > home_goals:
                    away_wins += 1
                else:
                    draws += 1
            else:
                # Home team was away in this match
                if away_goals > home_goals:
                    home_wins += 1
                elif home_goals > away_goals:
                    away_wins += 1
                else:
                    draws += 1
            
            # Show match events if available
            events = match.get('events', [])
            if events:
                goals_events = [e for e in events if e.get('type') == 'goal']
                cards_events = [e for e in events if e.get('type') in ['yellow_card', 'red_card']]
                print(f"     Events: {len(goals_events)} goals, {len(cards_events)} cards")
        
        if len(h2h_recent) > 0:
            avg_goals = total_goals / len(h2h_recent)
            print(f"\n📊 RECENT H2H SUMMARY:")
            print(f"  {home_name}: {home_wins} wins")
            print(f"  {away_name}: {away_wins} wins") 
            print(f"  Draws: {draws}")
            print(f"  Average goals per game: {avg_goals:.2f}")
            
            if avg_goals > 2.8:
                print(f"  🔥 High-scoring recent meetings - consider Over 2.5")
            elif avg_goals < 2.0:
                print(f"  🛡️ Low-scoring recent meetings - consider Under 2.5")
    
    # Recent form summary
    print(f"\n📈 RECENT FORM SUMMARY:")
    print("-" * 25)
    
    def analyze_team_form(matches, team_name):
        if not matches:
            return
        
        wins = 0
        draws = 0 
        losses = 0
        goals_for = 0
        goals_against = 0
        
        for match in matches[:5]:  # Last 5 games
            teams = match.get('teams', {})
            goals = match.get('goals', {})
            
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            
            # Determine if team was home or away
            home_team_id = teams.get('home', {}).get('id')
            if home_team_id == (home_recent[0].get('teams', {}).get('home', {}).get('id') if home_recent else None):
                # This logic needs team ID - simplified for now
                goals_for += home_goals
                goals_against += away_goals
                if home_goals > away_goals:
                    wins += 1
                elif home_goals < away_goals:
                    losses += 1
                else:
                    draws += 1
        
        form = f"{wins}W-{draws}D-{losses}L"
        print(f"  {team_name}: {form} (last 5 games)")
        if len(matches) >= 5:
            avg_goals_for = goals_for / 5
            avg_goals_against = goals_against / 5
            print(f"    Avg goals scored: {avg_goals_for:.1f}")
            print(f"    Avg goals conceded: {avg_goals_against:.1f}")
    
    analyze_team_form(home_recent, home_name)
    analyze_team_form(away_recent, away_name)
    
    print(f"\n💡 CUSTOM ANALYSIS BENEFITS:")
    print("  ✅ Based on recent actual match data")
    print("  ✅ Includes detailed match events")
    print("  ✅ Shows recent form context")
    print("  ✅ More granular than overall H2H stats")
    
    print(f"\n{'='*50}")

def print_h2h_summary(h2h_data, home_team, away_team, enhanced_data=None):
    """Print comprehensive H2H analysis summary"""
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE HEAD-TO-HEAD ANALYSIS: {home_team} vs {away_team}")
    print(f"{'='*80}")
    
    if "error" in h2h_data:
        print(f"No historical data available: {h2h_data['error']}")
        return
    
    # Basic stats
    total_meetings = h2h_data.get('total_meetings', 0)
    if total_meetings == 0:
        print("No historical meetings found between these teams")
        return
    
    print(f"📊 OVERALL HISTORICAL RECORD ({total_meetings} meetings)")
    print("=" * 50)
    
    # Team records
    team1_record = h2h_data.get('team_1_record', {})
    team2_record = h2h_data.get('team_2_record', {})
    draws = h2h_data.get('draws', {})
    
    if team1_record and team2_record:
        print(f"  {team1_record.get('name', home_team)}: {team1_record.get('wins', 0)} wins ({team1_record.get('win_rate', 0):.1f}%)")
        print(f"  {team2_record.get('name', away_team)}: {team2_record.get('wins', 0)} wins ({team2_record.get('win_rate', 0):.1f}%)")
        print(f"  Draws: {draws.get('count', 0)} ({draws.get('rate', 0):.1f}%)")
    
    # Enhanced home/away analysis
    if enhanced_data and "stats" in enhanced_data:
        stats = enhanced_data["stats"]
        team1_home = stats.get("team1_at_home", {})
        team2_home = stats.get("team2_at_home", {})
        
        print(f"\n🏠 HOME vs AWAY PERFORMANCE BREAKDOWN")
        print("=" * 50)
        
        # Team 1 (home team) at home performance
        if team1_home:
            home_games = team1_home.get("team1_games_played_at_home", 0)
            home_wins = team1_home.get("team1_wins_at_home", 0)
            home_losses = team1_home.get("team1_losses_at_home", 0) 
            home_draws = team1_home.get("team1_draws_at_home", 0)
            home_scored = team1_home.get("team1_scored_at_home", 0)
            home_conceded = team1_home.get("team1_conceded_at_home", 0)
            
            home_win_rate = (home_wins / home_games * 100) if home_games > 0 else 0
            home_avg_scored = home_scored / home_games if home_games > 0 else 0
            home_avg_conceded = home_conceded / home_games if home_games > 0 else 0
            
            print(f"  {team1_record.get('name', home_team)} AT HOME:")
            print(f"    Record: {home_wins}W-{home_draws}D-{home_losses}L ({home_win_rate:.1f}% win rate)")
            print(f"    Goals: {home_scored} scored, {home_conceded} conceded ({home_avg_scored:.1f} per game)")
        
        # Team 2 (away team) at home performance  
        if team2_home:
            away_home_games = team2_home.get("team2_games_played_at_home", 0)
            away_home_wins = team2_home.get("team2_wins_at_home", 0)
            away_home_losses = team2_home.get("team2_losses_at_home", 0)
            away_home_draws = team2_home.get("team2_draws_at_home", 0)
            away_home_scored = team2_home.get("team2_scored_at_home", 0)
            away_home_conceded = team2_home.get("team2_conceded_at_home", 0)
            
            away_home_win_rate = (away_home_wins / away_home_games * 100) if away_home_games > 0 else 0
            away_home_avg_scored = away_home_scored / away_home_games if away_home_games > 0 else 0
            away_home_avg_conceded = away_home_conceded / away_home_games if away_home_games > 0 else 0
            
            print(f"\n  {team2_record.get('name', away_team)} AT HOME:")
            print(f"    Record: {away_home_wins}W-{away_home_draws}D-{away_home_losses}L ({away_home_win_rate:.1f}% win rate)")
            print(f"    Goals: {away_home_scored} scored, {away_home_conceded} conceded ({away_home_avg_scored:.1f} per game)")
    
    # Goals analysis
    goals = h2h_data.get('goals', {})
    if goals:
        avg_goals = goals.get('average_per_game', 0)
        print(f"\n⚽ GOALS ANALYSIS")
        print("=" * 50)
        print(f"  Average total goals per game: {avg_goals:.2f}")
        print(f"  {team1_record.get('name', home_team)} total goals: {goals.get('team_1_total', 0)} ({goals.get('team_1_total', 0)/total_meetings:.1f} per game)")
        print(f"  {team2_record.get('name', away_team)} total goals: {goals.get('team_2_total', 0)} ({goals.get('team_2_total', 0)/total_meetings:.1f} per game)")
    
    # Enhanced betting insights
    betting_insights = h2h_data.get('betting_insights', {})
    print(f"\n💰 BETTING INSIGHTS & RECOMMENDATIONS")
    print("=" * 50)
    
    if betting_insights:
        print(f"  Historical trend: {betting_insights.get('goals_trend', 'Unknown')}")
        
        avg_goals = goals.get('average_per_game', 0) if goals else 0
        if avg_goals > 2.8:
            print(f"  ✅ STRONG BET: 'Over 2.5 Goals' (Historical avg: {avg_goals:.2f})")
        elif avg_goals < 2.2:
            print(f"  ✅ STRONG BET: 'Under 2.5 Goals' (Historical avg: {avg_goals:.2f})")
        else:
            print(f"  ⚠️ NEUTRAL: Goals market unpredictable (Historical avg: {avg_goals:.2f})")
    
    # Dominance and venue analysis
    if team1_record and team2_record:
        team1_wins = team1_record.get('wins', 0)
        team2_wins = team2_record.get('wins', 0)
        overall_win_rate = team1_record.get('win_rate', 0)
        
        print(f"\n🏆 DOMINANCE & VENUE ANALYSIS")
        print("=" * 50)
        
        if team1_wins > team2_wins * 2:
            print(f"  🔥 {team1_record.get('name', home_team)} DOMINATES this matchup ({overall_win_rate:.1f}% win rate)")
        elif team2_wins > team1_wins * 2:
            print(f"  🔥 {team2_record.get('name', away_team)} DOMINATES this matchup")
        else:
            print(f"  ⚖️ Competitive matchup - no clear historical dominance")
        
        # Venue advantage analysis
        if enhanced_data and "stats" in enhanced_data:
            stats = enhanced_data["stats"]
            team1_home = stats.get("team1_at_home", {})
            
            if team1_home:
                home_win_rate = (team1_home.get("team1_wins_at_home", 0) / team1_home.get("team1_games_played_at_home", 1) * 100)
                if home_win_rate > overall_win_rate + 10:
                    print(f"  🏠 VENUE ADVANTAGE: {team1_record.get('name', home_team)} much stronger at home ({home_win_rate:.1f}% vs {overall_win_rate:.1f}% overall)")
                elif home_win_rate < overall_win_rate - 10:
                    print(f"  🛫 VENUE DISADVANTAGE: {team1_record.get('name', home_team)} weaker at home than overall")
                else:
                    print(f"  🏠 No significant home advantage pattern")
    
    print(f"\n" + "=" * 80)

async def get_matches_for_date(date_string):
    """Get matches for all leagues for the specified date"""
    print(f"\nSearching for matches on {date_string}...")
    print("=" * 60)
    
    total_matches = 0
    leagues_with_matches = 0
    all_matches = []  # Store all matches with numbers
    
    for league_code, league_info in LEAGUES.items():
        print(f"\n{league_info['name']} ({league_info['country']}):")
        print("-" * 40)
        
        # Call MCP tool for this league
        print(f"  Calling MCP with league_filter: '{league_code}'")
        result = await mcp_call("get_betting_matches", {
            "date": date_string,
            "league_filter": league_code
        })
        print(f"  Response: {result.get('error', 'Success')}")
        
        if "error" in result:
            print(f"  Error: {result['error']}")
            continue
        
        # Debug: show the actual response data
        print(f"  DEBUG: Total matches in response: {result.get('total_matches', 'N/A')}")
        matches_by_league = result.get('matches_by_league', {})
        print(f"  DEBUG: Leagues in response: {list(matches_by_league.keys())}")
        
        # Extract matches for this league
        matches_by_league = result.get('matches_by_league', {})
        # Try both the original league code and uppercase version
        league_matches = matches_by_league.get(league_code, [])
        if not league_matches:
            league_matches = matches_by_league.get(league_code.upper(), [])
        
        if not league_matches:
            print(f"  No matches found")
            continue
        
        leagues_with_matches += 1
        total_matches += len(league_matches)
        
        print(f"  Found {len(league_matches)} matches:")
        
        for match in league_matches:
            match_number = len(all_matches) + 1
            all_matches.append({
                'match': match,
                'league': league_info,
                'number': match_number
            })
            
            print(f"\n  [{match_number}] Match:")
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
        return []
    else:
        print(f"\nTo analyze any match, enter its number when prompted.")
        return all_matches

def print_help():
    """Print usage instructions"""
    print("Soccer Schedule Finder")
    print("=" * 50)
    print("Enter a date to find upcoming matches across 6 major leagues")
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
            matches = await get_matches_for_date(formatted_date)
            
            # If matches found, offer H2H analysis
            if matches:
                print(f"\n" + "-" * 50)
                while True:
                    choice = input("Enter match number for H2H analysis (or 'skip' to continue): ").strip()
                    
                    if choice.lower() in ['skip', 's', '']:
                        break
                    
                    try:
                        match_num = int(choice)
                        if 1 <= match_num <= len(matches):
                            selected_match = matches[match_num - 1]
                            match_data = selected_match['match']
                            
                            # Extract team data
                            teams = match_data.get('teams', {})
                            home_team = teams.get('home', {})
                            away_team = teams.get('away', {})
                            
                            home_team_id = home_team.get('id')
                            away_team_id = away_team.get('id')
                            home_team_name = home_team.get('name', 'Unknown')
                            away_team_name = away_team.get('name', 'Unknown')
                            
                            if home_team_id and away_team_id:
                                print(f"\nAnalyzing {home_team_name} vs {away_team_name}...")
                                print("Fetching comprehensive H2H data...")
                                
                                # Get league ID for custom analysis
                                match_league_id = selected_match['league']['id']
                                
                                # METHOD 1: Standard H2H endpoint analysis
                                h2h_data = await get_h2h_analysis(home_team_id, away_team_id, home_team_name, away_team_name)
                                enhanced_data = await get_enhanced_h2h_data(home_team_id, away_team_id)
                                
                                print_h2h_summary(h2h_data, home_team_name, away_team_name, enhanced_data)
                                
                                # METHOD 2: Custom matches-based analysis
                                print(f"\n{'='*50}")
                                print("CUSTOM H2H ANALYSIS")
                                print(f"{'='*50}")
                                
                                custom_h2h_data = await get_custom_h2h_analysis(
                                    home_team_id, away_team_id, home_team_name, away_team_name, match_league_id
                                )
                                print_custom_h2h_analysis(custom_h2h_data)
                            else:
                                print("Cannot analyze: Missing team ID data")
                        else:
                            print(f"Invalid choice. Please enter a number between 1 and {len(matches)}")
                    except ValueError:
                        print("Please enter a valid number or 'skip'")
            
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