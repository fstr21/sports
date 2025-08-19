#!/usr/bin/env python3
"""
Comprehensive Match Data Extractor
Extracts ALL available data from matches endpoint in clean, structured format
"""
import asyncio
import json
import httpx
import os
from datetime import datetime, timedelta

AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")

def extract_comprehensive_match_data(match):
    """Extract ALL available data from a single match in structured format"""
    
    # Basic match info
    basic_info = {
        'match_id': match.get('id'),
        'date': match.get('date'),
        'time': match.get('time'),
        'status': match.get('status'),
        'minute': match.get('minute'),
        'winner': match.get('winner'),  # 'home', 'away', 'draw', or None
        'has_extra_time': match.get('has_extra_time', False),
        'has_penalties': match.get('has_penalties', False)
    }
    
    # Team information
    teams = match.get('teams', {})
    team_info = {
        'home_team': {
            'id': teams.get('home', {}).get('id'),
            'name': teams.get('home', {}).get('name')
        },
        'away_team': {
            'id': teams.get('away', {}).get('id'),
            'name': teams.get('away', {}).get('name')
        }
    }
    
    # Complete goal breakdown
    goals = match.get('goals', {})
    goal_info = {
        'halftime': {
            'home': goals.get('home_ht_goals', 0),
            'away': goals.get('away_ht_goals', 0)
        },
        'fulltime': {
            'home': goals.get('home_ft_goals', 0),
            'away': goals.get('away_ft_goals', 0)
        },
        'extra_time': {
            'home': goals.get('home_et_goals', -1),
            'away': goals.get('away_et_goals', -1)
        },
        'penalties': {
            'home': goals.get('home_pen_goals', -1),
            'away': goals.get('away_pen_goals', -1)
        }
    }
    
    # Detailed events breakdown
    events = match.get('events', [])
    events_breakdown = {
        'total_events': len(events),
        'goals': [],
        'yellow_cards': [],
        'red_cards': [],
        'substitutions': [],
        'other_events': []
    }
    
    # Goal timing analysis
    goal_timing = {
        'first_half_goals': 0,
        'second_half_goals': 0,
        'early_goals': 0,      # 0-15 min
        'late_goals': 0,       # 75-90+ min
        'goal_minutes': []
    }
    
    # Card discipline tracking
    card_discipline = {
        'home_yellow_cards': 0,
        'away_yellow_cards': 0,
        'home_red_cards': 0,
        'away_red_cards': 0,
        'total_cards': 0,
        'card_minutes': []
    }
    
    # Substitution analysis
    substitution_analysis = {
        'home_subs': 0,
        'away_subs': 0,
        'early_subs': 0,       # Before 60 min (injury/tactical)
        'late_subs': 0,        # After 75 min (time wasting/fresh legs)
        'substitution_minutes': []
    }
    
    # Process all events
    for event in events:
        if not isinstance(event, dict):
            continue
            
        event_type = event.get('event_type', '')
        minute_str = event.get('event_minute', '0')
        
        try:
            minute = int(minute_str) if minute_str.isdigit() else 0
        except:
            minute = 0
            
        team = event.get('team', '')
        player_data = event.get('player', {})
        player_name = player_data.get('name', 'Unknown') if isinstance(player_data, dict) else str(player_data)
        
        # Goal events
        if event_type == 'goal':
            assist_data = event.get('assist_player')
            assist_name = None
            if assist_data and isinstance(assist_data, dict):
                assist_name = assist_data.get('name')
            
            goal_event = {
                'minute': minute,
                'team': team,
                'player': player_name,
                'assist': assist_name
            }
            events_breakdown['goals'].append(goal_event)
            
            # Goal timing analysis
            goal_timing['goal_minutes'].append(minute)
            if minute <= 45:
                goal_timing['first_half_goals'] += 1
            else:
                goal_timing['second_half_goals'] += 1
                
            if minute <= 15:
                goal_timing['early_goals'] += 1
            elif minute >= 75:
                goal_timing['late_goals'] += 1
        
        # Card events
        elif 'card' in event_type:
            card_event = {
                'minute': minute,
                'team': team,
                'player': player_name,
                'card_type': event_type
            }
            
            if event_type == 'yellow_card':
                events_breakdown['yellow_cards'].append(card_event)
                if team == 'home':
                    card_discipline['home_yellow_cards'] += 1
                else:
                    card_discipline['away_yellow_cards'] += 1
            elif event_type == 'red_card':
                events_breakdown['red_cards'].append(card_event)
                if team == 'home':
                    card_discipline['home_red_cards'] += 1
                else:
                    card_discipline['away_red_cards'] += 1
            
            card_discipline['total_cards'] += 1
            card_discipline['card_minutes'].append(minute)
        
        # Substitution events
        elif event_type == 'substitution':
            player_in_data = event.get('player_in', {})
            player_out_data = event.get('player_out', {})
            
            player_in = player_in_data.get('name', 'Unknown') if isinstance(player_in_data, dict) else str(player_in_data)
            player_out = player_out_data.get('name', 'Unknown') if isinstance(player_out_data, dict) else str(player_out_data)
            
            sub_event = {
                'minute': minute,
                'team': team,
                'player_in': player_in,
                'player_out': player_out
            }
            events_breakdown['substitutions'].append(sub_event)
            
            # Substitution timing analysis
            if team == 'home':
                substitution_analysis['home_subs'] += 1
            else:
                substitution_analysis['away_subs'] += 1
                
            if minute < 60:
                substitution_analysis['early_subs'] += 1
            elif minute > 75:
                substitution_analysis['late_subs'] += 1
                
            substitution_analysis['substitution_minutes'].append(minute)
        
        # Other events
        else:
            other_event = {
                'minute': minute,
                'team': team,
                'player': player_name,
                'event_type': event_type
            }
            events_breakdown['other_events'].append(other_event)
    
    # Odds information (if available)
    odds = match.get('odds', {})
    odds_info = {
        'available': bool(odds),
        'match_winner': odds.get('match_winner', {}),
        'over_under': odds.get('over_under', {}),
        'other_markets': {}
    }
    
    # Extract other odds markets
    for market, data in odds.items():
        if market not in ['match_winner', 'over_under']:
            odds_info['other_markets'][market] = data
    
    # Match preview/additional info
    additional_info = {
        'match_preview': match.get('match_preview', ''),
        'venue': match.get('venue', {}),
        'referee': match.get('referee', {}),
        'weather': match.get('weather', {}),
        'attendance': match.get('attendance'),
        'formations': match.get('formations', {})
    }
    
    # Derived insights
    insights = {
        'match_result': determine_match_result(goal_info),
        'halftime_result': determine_halftime_result(goal_info),
        'comeback_win': is_comeback_win(goal_info),
        'clean_sheet': {
            'home': goal_info['fulltime']['away'] == 0,
            'away': goal_info['fulltime']['home'] == 0
        },
        'high_scoring': (goal_info['fulltime']['home'] + goal_info['fulltime']['away']) >= 3,
        'low_scoring': (goal_info['fulltime']['home'] + goal_info['fulltime']['away']) <= 1,
        'both_teams_scored': goal_info['fulltime']['home'] > 0 and goal_info['fulltime']['away'] > 0,
        'disciplinary_heavy': card_discipline['total_cards'] >= 5,
        'early_goal': goal_timing['early_goals'] > 0,
        'late_drama': goal_timing['late_goals'] > 0
    }
    
    return {
        'basic_info': basic_info,
        'teams': team_info,
        'goals': goal_info,
        'events_breakdown': events_breakdown,
        'goal_timing': goal_timing,
        'card_discipline': card_discipline,
        'substitution_analysis': substitution_analysis,
        'odds': odds_info,
        'additional_info': additional_info,
        'insights': insights,
        'raw_events': events  # Keep raw events for any custom analysis
    }

def determine_match_result(goal_info):
    """Determine match result from goal info"""
    home_goals = goal_info['fulltime']['home']
    away_goals = goal_info['fulltime']['away']
    
    if home_goals > away_goals:
        return 'home_win'
    elif away_goals > home_goals:
        return 'away_win'
    else:
        return 'draw'

def determine_halftime_result(goal_info):
    """Determine halftime result"""
    home_ht = goal_info['halftime']['home']
    away_ht = goal_info['halftime']['away']
    
    if home_ht > away_ht:
        return 'home_leading'
    elif away_ht > home_ht:
        return 'away_leading'
    else:
        return 'tied'

def is_comeback_win(goal_info):
    """Check if this was a comeback win"""
    ht_result = determine_halftime_result(goal_info)
    ft_result = determine_match_result(goal_info)
    
    # Comeback scenarios
    if ht_result == 'home_leading' and ft_result == 'away_win':
        return 'away_comeback'
    elif ht_result == 'away_leading' and ft_result == 'home_win':
        return 'home_comeback'
    elif ht_result == 'tied' and ft_result != 'draw':
        return 'second_half_winner'
    else:
        return None

async def get_comprehensive_team_matches(team_id, league_id, limit=15):
    """Get comprehensive data for all team matches"""
    
    print(f"Getting comprehensive match data for team {team_id}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.soccerdataapi.com/matches/",
                params={
                    "team_id": team_id,
                    "league_id": league_id,
                    "season": "2024-2025",
                    "auth_token": AUTH_KEY
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                all_matches = []
                
                # Extract matches from API response
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
                
                # Process only completed matches involving this team
                team_comprehensive_data = []
                
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
                            
                            # Extract comprehensive data
                            comprehensive_data = extract_comprehensive_match_data(match)
                            
                            # Add team-specific context
                            is_home = (home_id == team_id)
                            opponent = away_team if is_home else home_team
                            
                            comprehensive_data['team_context'] = {
                                'is_home': is_home,
                                'opponent': opponent,
                                'result_from_team_perspective': get_team_result(comprehensive_data, is_home)
                            }
                            
                            team_comprehensive_data.append(comprehensive_data)
                
                # Sort by date (most recent first) and limit
                def parse_date(match_data):
                    try:
                        date_str = match_data['basic_info']['date']
                        return datetime.strptime(date_str, "%d/%m/%Y")
                    except:
                        return datetime.min
                
                team_comprehensive_data.sort(key=parse_date, reverse=True)
                return team_comprehensive_data[:limit]
            else:
                print(f"Error getting matches: {response.status_code}")
                return []
                
    except Exception as e:
        print(f"Error getting comprehensive matches: {e}")
        return []

def get_team_result(match_data, is_home):
    """Get result from team's perspective"""
    result = match_data['insights']['match_result']
    
    if result == 'draw':
        return 'D'
    elif (result == 'home_win' and is_home) or (result == 'away_win' and not is_home):
        return 'W'
    else:
        return 'L'

def print_comprehensive_match_summary(match_data):
    """Print a comprehensive summary of a single match"""
    basic = match_data['basic_info']
    teams = match_data['teams']
    goals = match_data['goals']
    events = match_data['events_breakdown']
    timing = match_data['goal_timing']
    cards = match_data['card_discipline']
    subs = match_data['substitution_analysis']
    insights = match_data['insights']
    
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE MATCH ANALYSIS")
    print(f"{'='*80}")
    
    # Basic match info
    print(f"Match: {teams['home_team']['name']} vs {teams['away_team']['name']}")
    print(f"Date: {basic['date']} | Time: {basic['time']} | Status: {basic['status']}")
    print(f"Result: {goals['fulltime']['home']}-{goals['fulltime']['away']}")
    print(f"Halftime: {goals['halftime']['home']}-{goals['halftime']['away']}")
    
    if basic['winner']:
        print(f"Winner: {basic['winner']} team")
    
    # Goals and timing
    if events['goals']:
        print(f"\n[GOAL DETAILS]")
        for goal in events['goals']:
            assist_text = f" (assist: {goal['assist']})" if goal['assist'] else ""
            print(f"  {goal['minute']}': {goal['player']} ({goal['team']}){assist_text}")
        
        print(f"\n[GOAL TIMING ANALYSIS]")
        print(f"  First half goals: {timing['first_half_goals']}")
        print(f"  Second half goals: {timing['second_half_goals']}")
        print(f"  Early goals (0-15 min): {timing['early_goals']}")
        print(f"  Late goals (75+ min): {timing['late_goals']}")
    
    # Cards
    if cards['total_cards'] > 0:
        print(f"\n[DISCIPLINARY RECORD]")
        print(f"  Home yellow cards: {cards['home_yellow_cards']}")
        print(f"  Away yellow cards: {cards['away_yellow_cards']}")
        print(f"  Home red cards: {cards['home_red_cards']}")
        print(f"  Away red cards: {cards['away_red_cards']}")
        print(f"  Total cards: {cards['total_cards']}")
    
    # Substitutions
    if subs['home_subs'] + subs['away_subs'] > 0:
        print(f"\n[SUBSTITUTION ANALYSIS]")
        print(f"  Home substitutions: {subs['home_subs']}")
        print(f"  Away substitutions: {subs['away_subs']}")
        print(f"  Early subs (<60 min): {subs['early_subs']}")
        print(f"  Late subs (>75 min): {subs['late_subs']}")
    
    # Key insights
    print(f"\n[MATCH INSIGHTS]")
    for insight, value in insights.items():
        if value and value != 'None':
            print(f"  {insight.replace('_', ' ').title()}: {value}")
    
    print(f"\n{'='*80}")

async def test_comprehensive_extraction():
    """Test the comprehensive data extraction"""
    
    print("Testing comprehensive data extraction...")
    
    # Test with Real Madrid
    real_madrid_data = await get_comprehensive_team_matches(4883, 297, 3)  # Real Madrid, La Liga
    
    if real_madrid_data:
        print(f"\nExtracted {len(real_madrid_data)} matches for Real Madrid")
        
        # Show detailed analysis of first match
        if real_madrid_data:
            print_comprehensive_match_summary(real_madrid_data[0])
            
            # Save sample data
            with open('comprehensive_sample_data.json', 'w') as f:
                json.dump(real_madrid_data, f, indent=2)
            print(f"\nSaved comprehensive data to: comprehensive_sample_data.json")
    else:
        print("No data extracted")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_extraction())