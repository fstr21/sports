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
    """Get recent matches for a specific team using matches endpoint - improved version"""
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
                all_matches = []
                
                # Extract matches from the API response structure
                if isinstance(data, list) and data:
                    for league_data in data:
                        if isinstance(league_data, dict):
                            # Check for direct matches
                            if 'matches' in league_data:
                                all_matches.extend(league_data['matches'])
                            # Check for stage-based matches
                            elif 'stage' in league_data:
                                for stage in league_data['stage']:
                                    if 'matches' in stage:
                                        all_matches.extend(stage['matches'])
                
                # Filter for matches involving this team and completed games
                team_matches = []
                for match in all_matches:
                    teams = match.get('teams', {})
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    
                    home_id = home_team.get('id')
                    away_id = away_team.get('id')
                    
                    # Check if this match involves our team
                    if home_id == team_id or away_id == team_id:
                        # Only include finished matches
                        if match.get('status') in ['finished', 'complete', 'full-time']:
                            is_home = (home_id == team_id)
                            opponent = away_team if is_home else home_team
                            
                            # Calculate result for this team
                            goals = match.get('goals', {})
                            home_goals = goals.get('home_ft_goals', 0)
                            away_goals = goals.get('away_ft_goals', 0)
                            
                            if is_home:
                                team_goals = home_goals
                                opponent_goals = away_goals
                            else:
                                team_goals = away_goals
                                opponent_goals = home_goals
                            
                            if team_goals > opponent_goals:
                                result = 'W'
                            elif team_goals < opponent_goals:
                                result = 'L'
                            else:
                                result = 'D'
                            
                            team_matches.append({
                                'match': match,
                                'is_home': is_home,
                                'opponent': opponent,
                                'result': result,
                                'team_goals': team_goals,
                                'opponent_goals': opponent_goals,
                                'date': match.get('date', ''),
                                'events': match.get('events', [])
                            })
                
                # Sort by date (most recent first) and limit
                from datetime import datetime
                def parse_date(date_str):
                    try:
                        return datetime.strptime(date_str, "%d/%m/%Y")
                    except:
                        return datetime.min
                
                team_matches.sort(key=lambda x: parse_date(x['date']), reverse=True)
                return team_matches[:limit]
            else:
                print(f"Error getting matches: {response.status_code}")
                return []
                
    except Exception as e:
        print(f"Error getting recent matches: {e}")
        return []

async def find_recent_h2h_meetings_improved(team_1_id, team_2_id, league_id, max_meetings=5):
    """Find recent H2H meetings using the original proven methodology"""
    import os
    from datetime import datetime, timedelta
    
    AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")
    h2h_meetings = []
    
    # Search recent dates systematically (your original approach)
    end_date = datetime.now()
    search_days = 365  # Search last year
    
    for i in range(0, search_days, 7):  # Check weekly to be more efficient
        if len(h2h_meetings) >= max_meetings:
            break
            
        search_date = (end_date - timedelta(days=i)).strftime("%d-%m-%Y")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    "https://api.soccerdataapi.com/matches/",
                    params={
                        "league_id": league_id,
                        "date": search_date,
                        "auth_token": AUTH_KEY
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract matches from response
                    matches = []
                    if isinstance(data, list) and data:
                        for league_data in data:
                            if isinstance(league_data, dict):
                                if 'matches' in league_data:
                                    matches.extend(league_data['matches'])
                                elif 'stage' in league_data:
                                    for stage in league_data['stage']:
                                        if 'matches' in stage:
                                            matches.extend(stage['matches'])
                    
                    # Look for H2H meetings
                    for match in matches:
                        teams = match.get('teams', {})
                        home_team = teams.get('home', {})
                        away_team = teams.get('away', {})
                        
                        home_id = home_team.get('id')
                        away_id = away_team.get('id')
                        
                        # Check if this is a meeting between our two teams
                        if ((home_id == team_1_id and away_id == team_2_id) or 
                            (home_id == team_2_id and away_id == team_1_id)):
                            
                            if match.get('status') in ['finished', 'complete', 'full-time']:
                                team_1_is_home = (home_id == team_1_id)
                                
                                h2h_meetings.append({
                                    'date': search_date,
                                    'match': match,
                                    'team_1_is_home': team_1_is_home
                                })
                                
                                print(f"    Found H2H meeting: {search_date}")
        
        except Exception as e:
            continue  # Skip failed requests
    
    # Sort by date (most recent first)
    from datetime import datetime
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y")
        except:
            return datetime.min
    
    h2h_meetings.sort(key=lambda x: parse_date(x['date']), reverse=True)
    return h2h_meetings[:max_meetings]

# Import comprehensive data extraction functions
from comprehensive_data_extractor import (
    extract_comprehensive_match_data,
    get_comprehensive_team_matches,
    print_comprehensive_match_summary
)

async def get_custom_h2h_analysis(home_team_id, away_team_id, home_team_name, away_team_name, league_id):
    """Create custom H2H analysis using comprehensive data extraction"""
    print("  Fetching comprehensive match data...")
    
    # Get comprehensive recent matches for both teams
    print(f"    Getting {home_team_name} comprehensive match data...")
    home_comprehensive = await get_comprehensive_team_matches(home_team_id, league_id, 10)
    
    print(f"    Getting {away_team_name} comprehensive match data...")
    away_comprehensive = await get_comprehensive_team_matches(away_team_id, league_id, 10)
    
    # Find recent H2H meetings using date-by-date search
    print("    Searching for recent H2H meetings...")
    h2h_meetings = await find_recent_h2h_meetings_improved(home_team_id, away_team_id, league_id, 5)
    
    return {
        'home_team_name': home_team_name,
        'away_team_name': away_team_name,
        'home_team_id': home_team_id,
        'away_team_id': away_team_id,
        'home_comprehensive_matches': home_comprehensive,
        'away_comprehensive_matches': away_comprehensive,
        'h2h_recent_meetings': h2h_meetings,
        'league_id': league_id
    }

def print_custom_h2h_analysis(custom_data):
    """Print comprehensive custom H2H analysis with ALL available data"""
    print(f"\n{'='*70}")
    print("COMPREHENSIVE CUSTOM H2H ANALYSIS (All Available Data)")
    print(f"{'='*70}")
    
    home_name = custom_data.get('home_team_name', 'Home Team')
    away_name = custom_data.get('away_team_name', 'Away Team')
    
    home_comprehensive = custom_data.get('home_comprehensive_matches', [])
    away_comprehensive = custom_data.get('away_comprehensive_matches', [])
    h2h_meetings = custom_data.get('h2h_recent_meetings', [])
    
    print(f"[COMPREHENSIVE DATA SOURCES]:")
    print(f"  {home_name}: {len(home_comprehensive)} matches with full event data")
    print(f"  {away_name}: {len(away_comprehensive)} matches with full event data") 
    print(f"  Recent H2H meetings found: {len(h2h_meetings)}")
    print(f"  Data includes: goals, assists, cards, substitutions, timing, odds, insights")
    
    # Show recent H2H meetings with full details
    if h2h_meetings:
        print(f"\n[RECENT HEAD-TO-HEAD MEETINGS] (Date Search Method):")
        print("-" * 50)
        
        for i, meeting in enumerate(h2h_meetings, 1):
            match = meeting['match']
            date = meeting['date']
            
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            goals = match.get('goals', {})
            
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            
            print(f"  {i}. {date}: {home_team.get('name')} {home_goals}-{away_goals} {away_team.get('name')}")
            
            # Show detailed match events
            events = match.get('events', [])
            if events:
                goal_events = [e for e in events if 'goal' in e.get('type', '').lower()]
                card_events = [e for e in events if 'card' in e.get('type', '').lower()]
                sub_events = [e for e in events if 'substitution' in e.get('type', '').lower()]
                
                print(f"     Match Events: {len(goal_events)} goals, {len(card_events)} cards, {len(sub_events)} subs")
                
                # Show goal scorers if available
                if goal_events:
                    goal_info = []
                    for goal in goal_events[:3]:  # Show first 3 goals
                        player = goal.get('player', {}).get('name', 'Unknown')
                        minute = goal.get('minute', '?')
                        goal_info.append(f"{player} {minute}'")
                    if goal_info:
                        print(f"     Goal scorers: {', '.join(goal_info)}")
            
            # Show odds if available
            odds = match.get('odds', {})
            if odds:
                match_winner = odds.get('match_winner', {})
                if match_winner:
                    home_odds = match_winner.get('home', 'N/A')
                    away_odds = match_winner.get('away', 'N/A')
                    print(f"     Historical odds: {home_odds} - {away_odds}")
    
    # COMPREHENSIVE TEAM ANALYSIS WITH ALL AVAILABLE DATA
    print(f"\n[COMPREHENSIVE TEAM ANALYSIS] - All Available Data:")
    print("=" * 70)
    
    def analyze_team_comprehensive_data(comprehensive_matches, team_name):
        if not comprehensive_matches:
            print(f"\n{team_name}: No comprehensive match data found")
            return
        
        print(f"\n{team_name.upper()} - COMPLETE DATA BREAKDOWN:")
        print("-" * 50)
        
        # Basic form analysis
        recent_5 = comprehensive_matches[:5]
        wins = draws = losses = 0
        goals_for = goals_against = 0
        ht_goals_for = ht_goals_against = 0
        form_string = []
        
        # Advanced metrics
        total_cards = home_wins = away_wins = 0
        early_goals = late_goals = clean_sheets = 0
        comebacks = both_scored = high_scoring = 0
        total_yellow_cards = total_red_cards = 0
        early_subs = late_subs = 0
        
        print("\n  RECENT MATCHES (Last 5 with ALL data):")
        for i, match_data in enumerate(recent_5, 1):
            basic = match_data['basic_info']
            teams = match_data['teams']
            goals = match_data['goals']
            events = match_data['events_breakdown']
            timing = match_data['goal_timing']
            cards = match_data['card_discipline']
            subs = match_data['substitution_analysis']
            insights = match_data['insights']
            context = match_data['team_context']
            
            # Basic match info
            opponent_name = context['opponent']['name']
            venue = "vs" if context['is_home'] else "@"
            result = context['result_from_team_perspective']
            
            home_score = goals['fulltime']['home']
            away_score = goals['fulltime']['away']
            ht_home = goals['halftime']['home']
            ht_away = goals['halftime']['away']
            
            print(f"    {i}. {basic['date']}: {venue} {opponent_name} {result} {home_score}-{away_score}")
            print(f"       HT: {ht_home}-{ht_away} | Events: {events['total_events']} | Cards: {cards['total_cards']}")
            
            # Show goal details if available
            if events['goals']:
                goal_times = [str(g['minute']) for g in events['goals']]
                print(f"       Goals at: {', '.join(goal_times)} min")
            
            # Show key insights
            key_insights = []
            if insights['clean_sheet']['home'] or insights['clean_sheet']['away']:
                key_insights.append("Clean sheet")
            if insights['comeback_win']:
                key_insights.append(f"Comeback: {insights['comeback_win']}")
            if insights['early_goal']:
                key_insights.append("Early goal")
            if insights['late_drama']:
                key_insights.append("Late drama")
            if insights['both_teams_scored']:
                key_insights.append("BTTS")
            if insights['high_scoring']:
                key_insights.append("High scoring")
            
            if key_insights:
                print(f"       Insights: {', '.join(key_insights)}")
            
            # Update aggregated stats
            if result == 'W':
                wins += 1
                if context['is_home']:
                    home_wins += 1
                else:
                    away_wins += 1
            elif result == 'D':
                draws += 1
            else:
                losses += 1
            
            # Goals stats (from team perspective)
            if context['is_home']:
                goals_for += home_score
                goals_against += away_score
                ht_goals_for += ht_home
                ht_goals_against += ht_away
            else:
                goals_for += away_score
                goals_against += home_score
                ht_goals_for += ht_away
                ht_goals_against += ht_home
            
            form_string.append(result)
            
            # Advanced metrics
            total_cards += cards['total_cards']
            total_yellow_cards += (cards['home_yellow_cards'] + cards['away_yellow_cards'])
            total_red_cards += (cards['home_red_cards'] + cards['away_red_cards'])
            early_subs += subs['early_subs']
            late_subs += subs['late_subs']
            
            if timing['early_goals'] > 0:
                early_goals += 1
            if timing['late_goals'] > 0:
                late_goals += 1
            if context['is_home'] and insights['clean_sheet']['home']:
                clean_sheets += 1
            elif not context['is_home'] and insights['clean_sheet']['away']:
                clean_sheets += 1
            if insights['comeback_win']:
                comebacks += 1
            if insights['both_teams_scored']:
                both_scored += 1
            if insights['high_scoring']:
                high_scoring += 1
        
        # COMPREHENSIVE SUMMARY STATISTICS
        total_games = len(recent_5)
        if total_games > 0:
            print(f"\n  [BASIC FORM SUMMARY]:")
            win_pct = (wins / total_games) * 100
            avg_goals_for = goals_for / total_games
            avg_goals_against = goals_against / total_games
            avg_ht_for = ht_goals_for / total_games
            avg_ht_against = ht_goals_against / total_games
            
            print(f"    Record: {wins}W-{draws}D-{losses}L ({win_pct:.1f}% win rate)")
            print(f"    Form: {'-'.join(form_string)}")
            print(f"    Goals per game: {avg_goals_for:.1f} for, {avg_goals_against:.1f} against")
            print(f"    Halftime goals: {avg_ht_for:.1f} for, {avg_ht_against:.1f} against")
            
            print(f"\n  [ADVANCED METRICS] (Data you can analyze):")
            print(f"    Home vs Away: {home_wins}W at home, {away_wins}W away")
            print(f"    Clean sheets: {clean_sheets}/{total_games} ({clean_sheets/total_games*100:.1f}%)")
            print(f"    Early goals (0-15min): {early_goals}/{total_games} games")
            print(f"    Late drama (75+min): {late_goals}/{total_games} games")
            print(f"    Both teams scored: {both_scored}/{total_games} games")
            print(f"    High scoring (3+ goals): {high_scoring}/{total_games} games")
            print(f"    Comeback wins: {comebacks}")
            
            print(f"\n  [DISCIPLINARY DATA]:")
            print(f"    Total cards per game: {total_cards/total_games:.1f}")
            print(f"    Yellow cards per game: {total_yellow_cards/total_games:.1f}")
            print(f"    Red cards total: {total_red_cards}")
            
            print(f"\n  [SUBSTITUTION PATTERNS]:")
            print(f"    Early subs per game: {early_subs/total_games:.1f} (injuries/tactical)")
            print(f"    Late subs per game: {late_subs/total_games:.1f} (time management)")
            
            print(f"\n  [BETTING INSIGHTS FROM COMPREHENSIVE DATA]:")
            if avg_goals_for > 2.0:
                print("    [STRONG ATTACK] Excellent goal scoring form")
            elif avg_goals_for < 1.0:
                print("    [WEAK ATTACK] Struggling to find the net")
            
            if avg_goals_against < 1.0:
                print("    [SOLID DEFENSE] Very tight at the back")
            elif avg_goals_against > 2.0:
                print("    [LEAKY DEFENSE] Conceding too easily")
            
            if both_scored / total_games > 0.6:
                print("    [BTTS YES] Both teams score frequently")
            elif both_scored / total_games < 0.3:
                print("    [BTTS NO] Often one-sided games")
            
            if high_scoring / total_games > 0.6:
                print("    [OVER 2.5] Frequently involved in high-scoring games")
            elif high_scoring / total_games < 0.3:
                print("    [UNDER 2.5] Often involved in low-scoring affairs")
            
            if late_goals / total_games > 0.6:
                print("    [LATE DRAMA] Frequent late goals - good for in-play betting")
            
            if total_cards / total_games > 4:
                print("    [CARDS MARKET] High card count team")
    
    analyze_team_comprehensive_data(home_comprehensive, home_name)
    analyze_team_comprehensive_data(away_comprehensive, away_name)
    
    # Enhanced betting insights based on comprehensive data
    print(f"\n[ENHANCED BETTING RECOMMENDATIONS]:")
    print("=" * 50)
    
    if home_comprehensive and away_comprehensive:
        # Calculate comprehensive attacking/defensive trends using all available data
        home_matches = home_comprehensive[:5]
        away_matches = away_comprehensive[:5]
        
        # Extract goals data from comprehensive format
        home_goals_for = home_goals_against = 0
        away_goals_for = away_goals_against = 0
        home_btts = away_btts = 0
        home_high_scoring = away_high_scoring = 0
        
        for match in home_matches:
            context = match['team_context']
            goals = match['goals']
            insights = match['insights']
            
            if context['is_home']:
                home_goals_for += goals['fulltime']['home']
                home_goals_against += goals['fulltime']['away']
            else:
                home_goals_for += goals['fulltime']['away']
                home_goals_against += goals['fulltime']['home']
                
            if insights['both_teams_scored']:
                home_btts += 1
            if insights['high_scoring']:
                home_high_scoring += 1
        
        for match in away_matches:
            context = match['team_context']
            goals = match['goals']
            insights = match['insights']
            
            if context['is_home']:
                away_goals_for += goals['fulltime']['home']
                away_goals_against += goals['fulltime']['away']
            else:
                away_goals_for += goals['fulltime']['away']
                away_goals_against += goals['fulltime']['home']
                
            if insights['both_teams_scored']:
                away_btts += 1
            if insights['high_scoring']:
                away_high_scoring += 1
        
        home_avg_for = home_goals_for / len(home_matches)
        home_avg_against = home_goals_against / len(home_matches)
        away_avg_for = away_goals_for / len(away_matches)
        away_avg_against = away_goals_against / len(away_matches)
        
        expected_goals = (home_avg_for + away_avg_against + away_avg_for + home_avg_against) / 2
        btts_probability = (home_btts + away_btts) / (len(home_matches) + len(away_matches))
        high_scoring_prob = (home_high_scoring + away_high_scoring) / (len(home_matches) + len(away_matches))
        
        print(f"Expected total goals (comprehensive): {expected_goals:.2f}")
        print(f"BTTS probability: {btts_probability:.1%}")
        print(f"High scoring probability: {high_scoring_prob:.1%}")
        
        # Enhanced recommendations
        if expected_goals > 2.8:
            print("[STRONG] Over 2.5 Goals - High-scoring teams")
        elif expected_goals < 2.2:
            print("[STRONG] Under 2.5 Goals - Low-scoring affair likely")
        else:
            print("[NEUTRAL] Goals market balanced")
            
        if btts_probability > 0.6:
            print("[STRONG] Both Teams to Score YES")
        elif btts_probability < 0.3:
            print("[STRONG] Both Teams to Score NO")
        else:
            print("[NEUTRAL] BTTS market balanced")
        
        # Form momentum using comprehensive data
        home_form = [match['team_context']['result_from_team_perspective'] for match in home_matches[:3]]
        away_form = [match['team_context']['result_from_team_perspective'] for match in away_matches[:3]]
        
        home_momentum = home_form.count('W') - home_form.count('L')
        away_momentum = away_form.count('W') - away_form.count('L')
        
        if home_momentum > away_momentum + 1:
            print(f"[MOMENTUM] {home_name} has better recent momentum")
        elif away_momentum > home_momentum + 1:
            print(f"[MOMENTUM] {away_name} has better recent momentum")
        else:
            print("[NEUTRAL] Similar recent momentum for both teams")
    
    print(f"\n[COMPREHENSIVE DATA METHODOLOGY]:")
    print("[OK] Complete match data extraction with ALL available fields")
    print("[OK] Halftime/fulltime scores for HT/FT betting analysis")
    print("[OK] Goal timing patterns (early/late goal trends)")
    print("[OK] Card discipline tracking (yellow/red cards per game)")
    print("[OK] Substitution timing analysis (tactical vs injury subs)")
    print("[OK] Clean sheet, comeback, and BTTS pattern analysis")
    print("[OK] Home vs away performance breakdowns")
    print("[OK] Advanced betting market insights (Over/Under, BTTS, Cards)")
    print("[OK] Historical H2H combined with comprehensive recent form")
    print("[OK] All data available for custom filtering and analysis")
    
    print(f"\n{'='*70}")

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
    
    print(f"[OVERALL HISTORICAL RECORD] ({total_meetings} meetings)")
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
        
        print(f"\n[HOME vs AWAY PERFORMANCE BREAKDOWN]")
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
        print(f"\n[GOALS ANALYSIS]")
        print("=" * 50)
        print(f"  Average total goals per game: {avg_goals:.2f}")
        print(f"  {team1_record.get('name', home_team)} total goals: {goals.get('team_1_total', 0)} ({goals.get('team_1_total', 0)/total_meetings:.1f} per game)")
        print(f"  {team2_record.get('name', away_team)} total goals: {goals.get('team_2_total', 0)} ({goals.get('team_2_total', 0)/total_meetings:.1f} per game)")
    
    # Enhanced betting insights
    betting_insights = h2h_data.get('betting_insights', {})
    print(f"\n[BETTING INSIGHTS & RECOMMENDATIONS]")
    print("=" * 50)
    
    if betting_insights:
        print(f"  Historical trend: {betting_insights.get('goals_trend', 'Unknown')}")
        
        avg_goals = goals.get('average_per_game', 0) if goals else 0
        if avg_goals > 2.8:
            print(f"  [STRONG BET] 'Over 2.5 Goals' (Historical avg: {avg_goals:.2f})")
        elif avg_goals < 2.2:
            print(f"  [STRONG BET] 'Under 2.5 Goals' (Historical avg: {avg_goals:.2f})")
        else:
            print(f"  [NEUTRAL] Goals market unpredictable (Historical avg: {avg_goals:.2f})")
    
    # Dominance and venue analysis
    if team1_record and team2_record:
        team1_wins = team1_record.get('wins', 0)
        team2_wins = team2_record.get('wins', 0)
        overall_win_rate = team1_record.get('win_rate', 0)
        
        print(f"\n[DOMINANCE & VENUE ANALYSIS]")
        print("=" * 50)
        
        if team1_wins > team2_wins * 2:
            print(f"  [DOMINANCE] {team1_record.get('name', home_team)} DOMINATES this matchup ({overall_win_rate:.1f}% win rate)")
        elif team2_wins > team1_wins * 2:
            print(f"  [DOMINANCE] {team2_record.get('name', away_team)} DOMINATES this matchup")
        else:
            print(f"  [BALANCED] Competitive matchup - no clear historical dominance")
        
        # Venue advantage analysis
        if enhanced_data and "stats" in enhanced_data:
            stats = enhanced_data["stats"]
            team1_home = stats.get("team1_at_home", {})
            
            if team1_home:
                home_win_rate = (team1_home.get("team1_wins_at_home", 0) / team1_home.get("team1_games_played_at_home", 1) * 100)
                if home_win_rate > overall_win_rate + 10:
                    print(f"  [VENUE ADVANTAGE] {team1_record.get('name', home_team)} much stronger at home ({home_win_rate:.1f}% vs {overall_win_rate:.1f}% overall)")
                elif home_win_rate < overall_win_rate - 10:
                    print(f"  [VENUE DISADVANTAGE] {team1_record.get('name', home_team)} weaker at home than overall")
                else:
                    print(f"  [NEUTRAL] No significant home advantage pattern")
    
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