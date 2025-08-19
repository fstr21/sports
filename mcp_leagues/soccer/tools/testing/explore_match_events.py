#!/usr/bin/env python3
"""
Explore match events and additional data we're not using
"""
import asyncio
import json
import httpx
import os

AUTH_KEY = os.environ.get("AUTH_KEY", "a9f37754a540df435e8c40ed89c08565166524ed")

async def explore_detailed_match_data():
    """Explore what additional data we can extract from matches"""
    
    print("=" * 70)
    print("EXPLORING ADDITIONAL MATCH DATA WE'RE NOT USING")
    print("=" * 70)
    
    # Get a recent completed match
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://api.soccerdataapi.com/matches/",
            params={
                "league_id": 297,  # La Liga
                "date": "24-05-2025",
                "auth_token": AUTH_KEY
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Find a completed match
            sample_match = None
            if isinstance(data, list) and data:
                for league_data in data:
                    if isinstance(league_data, dict) and 'matches' in league_data:
                        for match in league_data['matches']:
                            if match.get('status') == 'finished':
                                sample_match = match
                                break
                    if sample_match:
                        break
            
            if sample_match:
                teams = sample_match.get('teams', {})
                home_team = teams.get('home', {}).get('name', 'Unknown')
                away_team = teams.get('away', {}).get('name', 'Unknown')
                
                print(f"ANALYZING: {home_team} vs {away_team}")
                print(f"Date: {sample_match.get('date')}")
                print("-" * 70)
                
                # 1. HALFTIME SCORES (we're not using)
                goals = sample_match.get('goals', {})
                ht_home = goals.get('home_ht_goals', 0)
                ht_away = goals.get('away_ht_goals', 0)
                ft_home = goals.get('home_ft_goals', 0)
                ft_away = goals.get('away_ft_goals', 0)
                
                print(f"\n1. HALFTIME/FULLTIME SCORES (currently unused):")
                print(f"   Halftime: {home_team} {ht_home}-{ht_away} {away_team}")
                print(f"   Fulltime: {home_team} {ft_home}-{ft_away} {away_team}")
                
                # 2. DETAILED EVENTS BREAKDOWN
                events = sample_match.get('events', [])
                print(f"\n2. DETAILED MATCH EVENTS ({len(events)} total):")
                
                event_types = {}
                goal_events = []
                card_events = []
                sub_events = []
                
                for event in events:
                    if isinstance(event, dict):
                        event_type = event.get('type', 'unknown')
                        event_types[event_type] = event_types.get(event_type, 0) + 1
                        
                        if 'goal' in event_type.lower():
                            goal_events.append(event)
                        elif 'card' in event_type.lower():
                            card_events.append(event)
                        elif 'substitution' in event_type.lower():
                            sub_events.append(event)
                
                print(f"   Event types found: {event_types}")
                
                # Show goal details
                if goal_events:
                    print(f"\n   GOAL DETAILS:")
                    for goal in goal_events:
                        minute = goal.get('minute', '?')
                        player_data = goal.get('player', {})
                        player_name = player_data.get('name', 'Unknown') if isinstance(player_data, dict) else str(player_data)
                        team_data = goal.get('team', {})
                        team_name = team_data.get('name', 'Unknown') if isinstance(team_data, dict) else str(team_data)
                        goal_type = goal.get('type', 'goal')
                        print(f"     {minute}': {player_name} ({team_name}) - {goal_type}")
                
                # Show card details
                if card_events:
                    print(f"\n   CARD DETAILS:")
                    for card in card_events:
                        minute = card.get('minute', '?')
                        player_data = card.get('player', {})
                        player_name = player_data.get('name', 'Unknown') if isinstance(player_data, dict) else str(player_data)
                        team_data = card.get('team', {})
                        team_name = team_data.get('name', 'Unknown') if isinstance(team_data, dict) else str(team_data)
                        card_type = card.get('type', 'card')
                        print(f"     {minute}': {player_name} ({team_name}) - {card_type}")
                
                # 3. ODDS DETAILS
                odds = sample_match.get('odds', {})
                print(f"\n3. AVAILABLE ODDS DATA:")
                if odds:
                    print(f"   Odds sections: {list(odds.keys())}")
                    
                    # Show match winner odds
                    match_winner = odds.get('match_winner', {})
                    if match_winner:
                        print(f"   Match Winner: Home {match_winner.get('home', 'N/A')}, " + 
                              f"Draw {match_winner.get('draw', 'N/A')}, Away {match_winner.get('away', 'N/A')}")
                    
                    # Show over/under
                    over_under = odds.get('over_under', {})
                    if over_under:
                        total = over_under.get('total', 'N/A')
                        over = over_under.get('over', 'N/A')
                        under = over_under.get('under', 'N/A')
                        print(f"   Over/Under {total}: Over {over}, Under {under}")
                    
                    # Show any other odds
                    for odds_type, odds_data in odds.items():
                        if odds_type not in ['match_winner', 'over_under']:
                            print(f"   {odds_type}: {odds_data}")
                else:
                    print("   No odds data available")
                
                # 4. ADDITIONAL FIELDS
                print(f"\n4. ADDITIONAL MATCH INFO:")
                print(f"   Match ID: {sample_match.get('id', 'N/A')}")
                print(f"   Time: {sample_match.get('time', 'N/A')}")
                print(f"   Winner: {sample_match.get('winner', 'N/A')}")
                print(f"   Has Extra Time: {sample_match.get('has_extra_time', 'N/A')}")
                print(f"   Has Penalties: {sample_match.get('has_penalties', 'N/A')}")
                
                match_preview = sample_match.get('match_preview', '')
                if match_preview:
                    preview_text = match_preview[:200] + "..." if len(match_preview) > 200 else match_preview
                    print(f"   Match Preview: {preview_text}")
                
                # 5. WHAT WE'RE CURRENTLY MISSING
                print(f"\n5. POTENTIALLY VALUABLE DATA WE'RE NOT USING:")
                print(f"   ✓ Halftime scores (could predict 2nd half performance)")
                print(f"   ✓ Goal timing patterns (early/late goals)")
                print(f"   ✓ Card discipline (yellow/red cards affect future matches)")
                print(f"   ✓ Substitution patterns (tactical changes)")
                print(f"   ✓ Match winner determination (home/away/draw)")
                print(f"   ✓ Goal types (penalty, own goal, regular)")
                print(f"   ✓ Extra time/penalty history")
                
                # Save full match for inspection
                with open('detailed_match_sample.json', 'w') as f:
                    json.dump(sample_match, f, indent=2)
                print(f"\n   Saved full match data to: detailed_match_sample.json")
                
            else:
                print("No completed matches found")
        else:
            print(f"API Error: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(explore_detailed_match_data())