#!/usr/bin/env python3
"""
Interactive Match Analyzer
1. Prompts for date
2. Shows all games for MLS, EPL, La Liga with American odds
3. Allows numerical selection of game
4. Shows detailed match info and head-to-head analysis for last 10 matches per team
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class InteractiveMatchAnalyzer:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.base_url = "https://api.soccerdataapi.com"
        self.headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'
        }
        
        # Target leagues
        self.leagues = {
            'MLS': {'id': 168, 'name': 'Major League Soccer', 'country': 'USA'},
            'EPL': {'id': 228, 'name': 'Premier League', 'country': 'England'},
            'La Liga': {'id': 297, 'name': 'La Liga', 'country': 'Spain'}
        }
    
    def api_call(self, endpoint: str, params: Dict, silent: bool = False) -> Optional[Dict]:
        """Make API call with error handling"""
        params['auth_token'] = self.auth_token
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if not silent:
                print(f"API Error: {e}")
            return None
    
    def prompt_for_date(self) -> str:
        """Prompt user for date and convert to proper format"""
        print("=" * 60)
        print("INTERACTIVE MATCH ANALYZER")
        print("=" * 60)
        print("Supported date formats:")
        print("  - DD-MM-YYYY (e.g., 17-08-2025)")
        print("  - DD/MM/YYYY (e.g., 17/08/2025)")
        print("  - YYYY-MM-DD (e.g., 2025-08-17)")
        print("  - MM/DD/YYYY (e.g., 08/17/2025)")
        print()
        
        while True:
            date_input = input("Enter the date to search for matches: ").strip()
            
            if not date_input:
                print("ERROR: Please enter a date")
                continue
            
            # Try to parse various date formats
            api_date = self.validate_and_convert_date(date_input)
            
            if api_date:
                print(f"Date converted to API format: {api_date}")
                return api_date
            else:
                print("ERROR: Invalid date format. Please try again.")
                print("Examples: 17-08-2025, 17/08/2025, 2025-08-17")
                continue
    
    def validate_and_convert_date(self, date_string: str) -> Optional[str]:
        """Validate and convert date to DD-MM-YYYY format"""
        formats_to_try = [
            "%d-%m-%Y",    # DD-MM-YYYY (API format)
            "%d/%m/%Y",    # DD/MM/YYYY
            "%Y-%m-%d",    # YYYY-MM-DD
            "%m/%d/%Y",    # MM/DD/YYYY
            "%d-%m-%y",    # DD-MM-YY
            "%d/%m/%y",    # DD/MM/YY
        ]
        
        for date_format in formats_to_try:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                # Convert to API format (DD-MM-YYYY)
                return parsed_date.strftime("%d-%m-%Y")
            except ValueError:
                continue
        
        return None
    
    def get_matches_for_date(self, date: str) -> Dict[str, List[Dict]]:
        """Get matches for all target leagues on specified date"""
        print(f"\nSearching for matches on {date}...")
        print("-" * 50)
        
        all_matches = {}
        
        for league_code, league_info in self.leagues.items():
            print(f"Searching {league_info['name']}...")
            
            matches_data = self.api_call('matches/', {
                'league_id': league_info['id'],
                'date': date
            })
            
            if matches_data:
                matches = self.extract_matches_from_response(matches_data)
                for match in matches:
                    match['league_code'] = league_code
                    match['league_info'] = league_info
                
                all_matches[league_code] = matches
                print(f"  Found {len(matches)} matches")
            else:
                all_matches[league_code] = []
                print(f"  No matches found")
        
        return all_matches
    
    def extract_matches_from_response(self, response_data) -> List[Dict]:
        """Extract matches from API response, filtering out invalid matches"""
        matches = []
        if not response_data or not isinstance(response_data, list):
            return matches
        
        for league_data in response_data:
            if isinstance(league_data, dict):
                raw_matches = []
                if 'matches' in league_data:
                    raw_matches.extend(league_data['matches'])
                elif 'stage' in league_data:
                    for stage in league_data['stage']:
                        if 'matches' in stage:
                            raw_matches.extend(stage['matches'])
                
                # Filter out invalid matches (None vs None, missing team data)
                for match in raw_matches:
                    if self.is_valid_match(match):
                        matches.append(match)
        
        return matches
    
    def is_valid_match(self, match: Dict) -> bool:
        """Check if match has valid team data"""
        teams = match.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        home_name = home_team.get('name', '').strip()
        away_name = away_team.get('name', '').strip()
        
        # Filter out matches with missing or "None" team names
        if not home_name or not away_name:
            return False
        if home_name.lower() in ['none', 'null', 'undefined', 'tbd']:
            return False
        if away_name.lower() in ['none', 'null', 'undefined', 'tbd']:
            return False
        
        return True
    
    def display_all_matches(self, all_matches: Dict[str, List[Dict]]) -> List[Dict]:
        """Display all matches with numerical selection and return numbered list"""
        print(f"\n" + "=" * 80)
        print("ALL MATCHES WITH AMERICAN ODDS")
        print("=" * 80)
        
        # Ask user if they want to see all matches or only upcoming
        print("\nFilter options:")
        print("1. Show all matches (scheduled, live, finished)")
        print("2. Show only upcoming matches (scheduled)")
        print("3. Show only live matches")
        
        while True:
            filter_choice = input("Select filter (1-3): ").strip()
            if filter_choice in ['1', '2', '3']:
                break
            print("Please enter 1, 2, or 3")
        
        numbered_matches = []
        match_number = 1
        
        for league_code, matches in all_matches.items():
            if not matches:
                continue
            
            # Filter matches based on user choice
            filtered_matches = []
            for match in matches:
                status = match.get('status', 'scheduled').lower()
                if filter_choice == '1':  # All matches
                    filtered_matches.append(match)
                elif filter_choice == '2':  # Only upcoming
                    if status in ['scheduled', 'tbd', 'pre-match']:
                        filtered_matches.append(match)
                elif filter_choice == '3':  # Only live
                    if status in ['live', 'halftime', 'break']:
                        filtered_matches.append(match)
            
            if not filtered_matches:
                continue
            
            league_info = self.leagues[league_code]
            print(f"\n{league_info['name']} ({league_info['country']})")
            print("-" * 60)
            
            for match in filtered_matches:
                # Add to numbered list
                numbered_matches.append({
                    'number': match_number,
                    'match': match,
                    'league_code': league_code
                })
                
                # Display match info
                teams = match.get('teams', {})
                home_team = teams.get('home', {})
                away_team = teams.get('away', {})
                home_name = home_team.get('name', 'TBD')
                away_name = away_team.get('name', 'TBD')
                match_time = match.get('time', 'TBD')
                status = match.get('status', 'scheduled')
                
                print(f"\n{match_number}. {home_name} vs {away_name}")
                print(f"   Time: {match_time} | Status: {status}")
                
                # Display odds if available, with warnings for live games
                odds = match.get('odds', {})
                if status.lower() in ['live', 'halftime', 'break']:
                    print(f"   ⚠️  WARNING: Match is {status.upper()} - odds may be stale/pre-match only")
                    self.display_american_odds(odds)
                elif status.lower() == 'finished':
                    # Show final score if available
                    goals = match.get('goals', {})
                    if goals:
                        home_goals = goals.get('home_ft_goals', 'N/A')
                        away_goals = goals.get('away_ft_goals', 'N/A')
                        print(f"   Final Score: {home_goals}-{away_goals}")
                    print(f"   (Pre-match odds shown below)")
                    self.display_american_odds(odds)
                else:
                    self.display_american_odds(odds)
                
                match_number += 1
        
        if not numbered_matches:
            print("No matches found for this date.")
        
        return numbered_matches
    
    def display_american_odds(self, odds: Dict):
        """Display American odds in clean format"""
        if not odds:
            print("   Odds: Not available")
            return
        
        # Match Winner (Moneyline)
        match_winner = odds.get('match_winner', {})
        if match_winner:
            home_odds = match_winner.get('home')
            away_odds = match_winner.get('away')
            draw_odds = match_winner.get('draw')
            
            if home_odds and away_odds and draw_odds:
                # Convert to American odds if they're not already
                home_american = self.convert_to_american_odds(home_odds)
                away_american = self.convert_to_american_odds(away_odds)
                draw_american = self.convert_to_american_odds(draw_odds)
                
                print(f"   Moneyline: Home {home_american} | Draw {draw_american} | Away {away_american}")
        
        # Spread (Handicap)
        handicap = odds.get('handicap', {})
        if handicap:
            home_handicap = handicap.get('home')
            away_handicap = handicap.get('away')
            market = handicap.get('market', 'N/A')
            
            if home_handicap and away_handicap:
                home_american = self.convert_to_american_odds(home_handicap)
                away_american = self.convert_to_american_odds(away_handicap)
                print(f"   Spread ({market}): Home {home_american} | Away {away_american}")
        
        # Total (Over/Under)
        over_under = odds.get('over_under', {})
        if over_under:
            over_odds = over_under.get('over')
            under_odds = over_under.get('under')
            total = over_under.get('total', 'N/A')
            
            if over_odds and under_odds:
                over_american = self.convert_to_american_odds(over_odds)
                under_american = self.convert_to_american_odds(under_odds)
                print(f"   Total ({total} goals): Over {over_american} | Under {under_american}")
        
        if not any([match_winner, handicap, over_under]):
            print("   Odds: Not available")
    
    def convert_to_american_odds(self, decimal_odds) -> str:
        """Convert decimal odds to American format"""
        try:
            decimal = float(decimal_odds)
            if decimal >= 2.0:
                american = int((decimal - 1) * 100)
                return f"+{american}"
            else:
                american = int(-100 / (decimal - 1))
                return str(american)
        except (ValueError, ZeroDivisionError):
            return str(decimal_odds)
    
    def prompt_for_match_selection(self, numbered_matches: List[Dict]) -> Optional[Dict]:
        """Prompt user to select a match"""
        if not numbered_matches:
            return None
        
        print(f"\n" + "=" * 60)
        print("SELECT A MATCH FOR DETAILED ANALYSIS")
        print("=" * 60)
        print(f"Enter a number (1-{len(numbered_matches)}) or 'exit' to quit:")
        
        while True:
            selection = input("Selection: ").strip().lower()
            
            if selection == 'exit':
                return None
            
            try:
                match_number = int(selection)
                if 1 <= match_number <= len(numbered_matches):
                    selected = numbered_matches[match_number - 1]
                    return selected
                else:
                    print(f"Please enter a number between 1 and {len(numbered_matches)}, or 'exit':")
            except ValueError:
                print("Please enter a valid number or 'exit':")
    
    def display_match_details(self, selected_match: Dict):
        """Display detailed match information"""
        match = selected_match['match']
        league_code = selected_match['league_code']
        league_info = self.leagues[league_code]
        
        teams = match.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        print(f"\n" + "=" * 80)
        print("DETAILED MATCH INFORMATION")
        print("=" * 80)
        
        print(f"League: {league_info['name']} ({league_info['country']})")
        print(f"Match: {home_team.get('name', 'TBD')} vs {away_team.get('name', 'TBD')}")
        print(f"Date: {match.get('date', 'TBD')}")
        print(f"Time: {match.get('time', 'TBD')}")
        print(f"Status: {match.get('status', 'scheduled')}")
        
        # Venue information
        venue = match.get('venue', {})
        if venue:
            print(f"Venue: {venue.get('name', 'TBD')}")
            print(f"City: {venue.get('city', 'TBD')}")
        
        # Match ID for reference
        print(f"Match ID: {match.get('id', 'N/A')}")
        
        # Detailed odds
        print(f"\nDETAILED ODDS:")
        print("-" * 30)
        odds = match.get('odds', {})
        self.display_detailed_odds(odds)
        
        return {
            'home_team_id': home_team.get('id'),
            'away_team_id': away_team.get('id'),
            'home_team_name': home_team.get('name'),
            'away_team_name': away_team.get('name'),
            'league_id': league_info['id']
        }
    
    def display_detailed_odds(self, odds: Dict):
        """Display detailed odds information"""
        if not odds:
            print("No odds available for this match")
            return
        
        # Match Winner
        match_winner = odds.get('match_winner', {})
        if match_winner:
            print("Match Winner (Moneyline):")
            home_odds = match_winner.get('home')
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
            
            if home_odds:
                print(f"  Home Win: {self.convert_to_american_odds(home_odds)} (Decimal: {home_odds})")
            if draw_odds:
                print(f"  Draw:     {self.convert_to_american_odds(draw_odds)} (Decimal: {draw_odds})")
            if away_odds:
                print(f"  Away Win: {self.convert_to_american_odds(away_odds)} (Decimal: {away_odds})")
        
        # Handicap
        handicap = odds.get('handicap', {})
        if handicap:
            print("\nHandicap (Spread):")
            market = handicap.get('market', 'N/A')
            home_handicap = handicap.get('home')
            away_handicap = handicap.get('away')
            
            print(f"  Market: {market}")
            if home_handicap:
                print(f"  Home: {self.convert_to_american_odds(home_handicap)} (Decimal: {home_handicap})")
            if away_handicap:
                print(f"  Away: {self.convert_to_american_odds(away_handicap)} (Decimal: {away_handicap})")
        
        # Over/Under
        over_under = odds.get('over_under', {})
        if over_under:
            print("\nTotal Goals (Over/Under):")
            total = over_under.get('total', 'N/A')
            over_odds = over_under.get('over')
            under_odds = over_under.get('under')
            
            print(f"  Total: {total} goals")
            if over_odds:
                print(f"  Over:  {self.convert_to_american_odds(over_odds)} (Decimal: {over_odds})")
            if under_odds:
                print(f"  Under: {self.convert_to_american_odds(under_odds)} (Decimal: {under_odds})")
    
    def get_team_recent_matches(self, team_id: int, team_name: str, league_id: int, target_matches: int = 10) -> List[Dict]:
        """Get last N matches for a team with improved error handling"""
        print(f"Searching recent matches for {team_name}...")
        
        # Search back 180 days but with better error handling
        search_dates = [(datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y") 
                       for i in range(1, 181)]
        
        team_matches = []
        consecutive_errors = 0
        max_consecutive_errors = 10  # Stop if too many consecutive errors
        
        for date in search_dates:
            if len(team_matches) >= target_matches:
                break
            
            # Stop if too many consecutive API errors
            if consecutive_errors >= max_consecutive_errors:
                print(f"   Stopping search after {max_consecutive_errors} consecutive API errors")
                break
            
            matches_data = self.api_call('matches/', {
                'league_id': league_id,
                'date': date
            }, silent=True)  # Silent to avoid spam during recent match search
            
            if matches_data:
                consecutive_errors = 0  # Reset error counter
                matches = self.extract_matches_from_response(matches_data)
                
                for match in matches:
                    if self.team_played_in_match(team_id, match) and match.get('status') == 'finished':
                        team_matches.append({
                            'match': match,
                            'date': date,
                            'is_home': self.is_team_home(team_id, match)
                        })
            else:
                consecutive_errors += 1
        
        # Sort by date (most recent first) and limit
        team_matches.sort(key=lambda x: datetime.strptime(x['date'], "%d-%m-%Y"), reverse=True)
        
        print(f"   Found {len(team_matches)} recent matches for {team_name}")
        return team_matches[:target_matches]
    
    def team_played_in_match(self, team_id: int, match: Dict) -> bool:
        """Check if team played in match"""
        teams = match.get('teams', {})
        home_id = teams.get('home', {}).get('id')
        away_id = teams.get('away', {}).get('id')
        return team_id in [home_id, away_id]
    
    def is_team_home(self, team_id: int, match: Dict) -> bool:
        """Check if team was playing at home"""
        teams = match.get('teams', {})
        home_id = teams.get('home', {}).get('id')
        return team_id == home_id
    
    def analyze_team_recent_form(self, team_matches: List[Dict], team_name: str) -> Dict:
        """Analyze team's recent form"""
        if not team_matches:
            return {
                'team_name': team_name,
                'matches_found': 0,
                'record': 'No recent matches found',
                'form_string': 'N/A',
                'goals_for': 0,
                'goals_against': 0
            }
        
        wins = draws = losses = 0
        goals_for = goals_against = 0
        form_chars = []
        
        for match_info in team_matches:
            match = match_info['match']
            is_home = match_info['is_home']
            
            teams = match.get('teams', {})
            goals = match.get('goals', {})
            
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            
            if is_home:
                team_goals = home_goals
                opponent_goals = away_goals
            else:
                team_goals = away_goals
                opponent_goals = home_goals
            
            goals_for += team_goals
            goals_against += opponent_goals
            
            # Determine result
            if team_goals > opponent_goals:
                wins += 1
                form_chars.append('W')
            elif team_goals < opponent_goals:
                losses += 1
                form_chars.append('L')
            else:
                draws += 1
                form_chars.append('D')
        
        total_games = len(team_matches)
        win_percentage = (wins / total_games * 100) if total_games > 0 else 0
        
        return {
            'team_name': team_name,
            'matches_found': total_games,
            'record': f"{wins}W-{draws}D-{losses}L",
            'win_percentage': win_percentage,
            'form_string': ''.join(form_chars),
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goals_per_game': goals_for / total_games if total_games > 0 else 0,
            'matches': team_matches
        }
    
    def display_head_to_head_analysis(self, match_info: Dict):
        """Display comprehensive head-to-head analysis"""
        home_team_id = match_info['home_team_id']
        away_team_id = match_info['away_team_id']
        home_team_name = match_info['home_team_name']
        away_team_name = match_info['away_team_name']
        league_id = match_info['league_id']
        
        print(f"\n" + "=" * 80)
        print("HEAD-TO-HEAD ANALYSIS (LAST 10 MATCHES PER TEAM)")
        print("=" * 80)
        
        # Get recent matches for both teams
        home_matches = self.get_team_recent_matches(home_team_id, home_team_name, league_id, 10)
        away_matches = self.get_team_recent_matches(away_team_id, away_team_name, league_id, 10)
        
        # Analyze recent form
        home_analysis = self.analyze_team_recent_form(home_matches, home_team_name)
        away_analysis = self.analyze_team_recent_form(away_matches, away_team_name)
        
        # Display form comparison table
        print(f"\nRECENT FORM COMPARISON")
        print("-" * 60)
        print(f"{'Metric':<20} | {home_team_name[:18]:<18} | {away_team_name[:18]:<18}")
        print("-" * 60)
        print(f"{'Matches Found':<20} | {home_analysis['matches_found']:<18} | {away_analysis['matches_found']:<18}")
        print(f"{'Record':<20} | {home_analysis['record']:<18} | {away_analysis['record']:<18}")
        
        if home_analysis['matches_found'] > 0 and away_analysis['matches_found'] > 0:
            print(f"{'Win Percentage':<20} | {home_analysis['win_percentage']:<17.1f}% | {away_analysis['win_percentage']:<17.1f}%")
            print(f"{'Form (Recent)':<20} | {home_analysis['form_string'][:18]:<18} | {away_analysis['form_string'][:18]:<18}")
            print(f"{'Goals Per Game':<20} | {home_analysis['goals_per_game']:<17.2f} | {away_analysis['goals_per_game']:<17.2f}")
            print(f"{'Goals For':<20} | {home_analysis['goals_for']:<18} | {away_analysis['goals_for']:<18}")
            print(f"{'Goals Against':<20} | {home_analysis['goals_against']:<18} | {away_analysis['goals_against']:<18}")
        
        # Display detailed match results
        self.display_detailed_recent_matches(home_analysis, "HOME TEAM")
        self.display_detailed_recent_matches(away_analysis, "AWAY TEAM")
        
        # Get historical H2H if available
        self.display_historical_h2h(home_team_id, away_team_id, home_team_name, away_team_name)
    
    def display_detailed_recent_matches(self, team_analysis: Dict, team_label: str):
        """Display detailed recent matches for a team"""
        if team_analysis['matches_found'] == 0:
            print(f"\n{team_label} - {team_analysis['team_name']}: No recent matches found")
            return
        
        print(f"\n{team_label} - {team_analysis['team_name']} (Last {team_analysis['matches_found']} matches):")
        print("-" * 70)
        print(f"{'#':<3} | {'Date':<12} | {'Opponent':<20} | {'H/A':<3} | {'Result':<8} | {'Form':<4}")
        print("-" * 70)
        
        for i, match_info in enumerate(team_analysis['matches'][:10], 1):
            match = match_info['match']
            date = match_info['date']
            is_home = match_info['is_home']
            
            teams = match.get('teams', {})
            goals = match.get('goals', {})
            
            # Get opponent name
            if is_home:
                opponent_name = teams.get('away', {}).get('name', 'Unknown')[:20]
                venue = 'H'
                team_goals = goals.get('home_ft_goals', 0)
                opponent_goals = goals.get('away_ft_goals', 0)
            else:
                opponent_name = teams.get('home', {}).get('name', 'Unknown')[:20]
                venue = 'A'
                team_goals = goals.get('away_ft_goals', 0)
                opponent_goals = goals.get('home_ft_goals', 0)
            
            # Determine result
            if team_goals > opponent_goals:
                result = f"W {team_goals}-{opponent_goals}"
                form_char = 'W'
            elif team_goals < opponent_goals:
                result = f"L {team_goals}-{opponent_goals}"
                form_char = 'L'
            else:
                result = f"D {team_goals}-{opponent_goals}"
                form_char = 'D'
            
            print(f"{i:<3} | {date:<12} | {opponent_name:<20} | {venue:<3} | {result:<8} | {form_char:<4}")
    
    def display_historical_h2h(self, team_1_id: int, team_2_id: int, team_1_name: str, team_2_name: str):
        """Display historical head-to-head statistics"""
        print(f"\n" + "=" * 60)
        print("HISTORICAL HEAD-TO-HEAD")
        print("=" * 60)
        
        h2h_data = self.api_call('head-to-head/', {
            'team_1_id': team_1_id,
            'team_2_id': team_2_id
        })
        
        if not h2h_data:
            print("Historical H2H data not available")
            return
        
        stats = h2h_data.get('stats', {})
        overall = stats.get('overall', {})
        
        if not overall:
            print("No historical statistics available")
            return
        
        total_games = overall.get('overall_games_played', 0)
        team_1_wins = overall.get('overall_team1_wins', 0)
        team_2_wins = overall.get('overall_team2_wins', 0)
        draws = overall.get('overall_draws', 0)
        team_1_goals = overall.get('overall_team1_scored', 0)
        team_2_goals = overall.get('overall_team2_scored', 0)
        
        if total_games == 0:
            print("No historical matches found between these teams")
            return
        
        team_1_pct = (team_1_wins / total_games) * 100
        team_2_pct = (team_2_wins / total_games) * 100
        draws_pct = (draws / total_games) * 100
        
        print(f"Total Historical Meetings: {total_games}")
        print("-" * 50)
        print(f"{team_1_name}: {team_1_wins} wins ({team_1_pct:.1f}%) | {team_1_goals} goals scored")
        print(f"{team_2_name}: {team_2_wins} wins ({team_2_pct:.1f}%) | {team_2_goals} goals scored")
        print(f"Draws: {draws} ({draws_pct:.1f}%)")
        
        # Historical advantage
        if team_1_wins > team_2_wins:
            advantage = f"{team_1_name} has historical advantage"
        elif team_2_wins > team_1_wins:
            advantage = f"{team_2_name} has historical advantage"
        else:
            advantage = "Historical record is even"
        
        print(f"\nHistorical Advantage: {advantage}")
        print(f"Average Goals Per Game: {(team_1_goals + team_2_goals) / total_games:.2f}")
    
    def run_interactive_analysis(self):
        """Run the complete interactive analysis"""
        try:
            # Step 1: Get date from user
            target_date = self.prompt_for_date()
            
            # Step 2: Get all matches for that date
            all_matches = self.get_matches_for_date(target_date)
            
            # Step 3: Display matches with odds and get user selection
            numbered_matches = self.display_all_matches(all_matches)
            
            if not numbered_matches:
                print("No matches available for analysis.")
                return
            
            # Step 4: Prompt for match selection
            selected_match = self.prompt_for_match_selection(numbered_matches)
            
            if not selected_match:
                print("Analysis cancelled.")
                return
            
            # Step 5: Display detailed match info
            match_info = self.display_match_details(selected_match)
            
            # Step 6: Display head-to-head analysis
            if match_info['home_team_id'] and match_info['away_team_id']:
                self.display_head_to_head_analysis(match_info)
            else:
                print("Cannot perform H2H analysis - team IDs not available")
            
            print(f"\n" + "=" * 60)
            print("ANALYSIS COMPLETE")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\nAnalysis interrupted by user.")
        except Exception as e:
            print(f"\nError during analysis: {e}")

def main():
    """Main execution function"""
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    analyzer = InteractiveMatchAnalyzer(auth_token)
    analyzer.run_interactive_analysis()

if __name__ == "__main__":
    main()