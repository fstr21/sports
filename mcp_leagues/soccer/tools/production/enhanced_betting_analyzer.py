#!/usr/bin/env python3
"""
Enhanced Betting Analyzer
Improved version with:
1. Better API error handling using season-based searches
2. Advanced betting-focused head-to-head analysis
3. Momentum indicators and value bet identification
4. Confidence scoring for predictions
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class EnhancedBettingAnalyzer:
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
        """Make API call with error handling and rate limiting"""
        params['auth_token'] = self.auth_token
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            time.sleep(0.1)  # Rate limiting
            return response.json()
        except Exception as e:
            if not silent:
                print(f"API Error: {e}")
            return None
    
    def prompt_for_date(self) -> str:
        """Prompt user for date and convert to proper format"""
        print("=" * 60)
        print("ENHANCED BETTING ANALYZER")
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
            
            api_date = self.validate_and_convert_date(date_input)
            
            if api_date:
                print(f"Date converted to API format: {api_date}")
                return api_date
            else:
                print("ERROR: Invalid date format. Please try again.")
                continue
    
    def validate_and_convert_date(self, date_string: str) -> Optional[str]:
        """Validate and convert date to DD-MM-YYYY format"""
        formats_to_try = [
            "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%y", "%d/%m/%y"
        ]
        
        for date_format in formats_to_try:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
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
        
        if not home_name or not away_name:
            return False
        if home_name.lower() in ['none', 'null', 'undefined', 'tbd']:
            return False
        if away_name.lower() in ['none', 'null', 'undefined', 'tbd']:
            return False
        
        return True
    
    def display_all_matches(self, all_matches: Dict[str, List[Dict]]) -> List[Dict]:
        """Display all matches with filtering options"""
        print(f"\n" + "=" * 80)
        print("ENHANCED BETTING ANALYSIS - MATCH SELECTION")
        print("=" * 80)
        
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
            
            filtered_matches = []
            for match in matches:
                status = match.get('status', 'scheduled').lower()
                if filter_choice == '1':
                    filtered_matches.append(match)
                elif filter_choice == '2':
                    if status in ['scheduled', 'tbd', 'pre-match']:
                        filtered_matches.append(match)
                elif filter_choice == '3':
                    if status in ['live', 'halftime', 'break']:
                        filtered_matches.append(match)
            
            if not filtered_matches:
                continue
            
            league_info = self.leagues[league_code]
            print(f"\n{league_info['name']} ({league_info['country']})")
            print("-" * 60)
            
            for match in filtered_matches:
                numbered_matches.append({
                    'number': match_number,
                    'match': match,
                    'league_code': league_code
                })
                
                teams = match.get('teams', {})
                home_team = teams.get('home', {})
                away_team = teams.get('away', {})
                home_name = home_team.get('name', 'TBD')
                away_name = away_team.get('name', 'TBD')
                match_time = match.get('time', 'TBD')
                status = match.get('status', 'scheduled')
                
                print(f"\n{match_number}. {home_name} vs {away_name}")
                print(f"   Time: {match_time} | Status: {status}")
                
                # Display odds with betting insights
                odds = match.get('odds', {})
                if status.lower() in ['live', 'halftime', 'break']:
                    print(f"   WARNING: Match is {status.upper()} - odds may be stale")
                    self.display_american_odds(odds)
                elif status.lower() == 'finished':
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
            draw_odds = match_winner.get('draw')
            away_odds = match_winner.get('away')
            
            if home_odds and draw_odds and away_odds:
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
        print("SELECT A MATCH FOR ENHANCED BETTING ANALYSIS")
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
    
    def get_team_recent_matches_improved(self, team_id: int, team_name: str, league_id: int, target_matches: int = 10) -> List[Dict]:
        """Improved method using season-based search to avoid API errors"""
        print(f"Analyzing recent form for {team_name}...")
        
        # First try to get current season matches
        current_season = "2024-2025"  # Adjust based on current season
        season_matches = self.api_call('matches/', {
            'league_id': league_id,
            'season': current_season
        }, silent=True)
        
        team_matches = []
        
        if season_matches:
            matches = self.extract_matches_from_response(season_matches)
            
            for match in matches:
                if (self.team_played_in_match(team_id, match) and 
                    match.get('status') == 'finished'):
                    
                    match_date = match.get('date', '')
                    if match_date:
                        try:
                            # Parse date to sort by recency
                            parsed_date = datetime.strptime(match_date, "%d/%m/%Y")
                            team_matches.append({
                                'match': match,
                                'date': match_date,
                                'parsed_date': parsed_date,
                                'is_home': self.is_team_home(team_id, match)
                            })
                        except ValueError:
                            # If date parsing fails, still include the match
                            team_matches.append({
                                'match': match,
                                'date': match_date,
                                'parsed_date': datetime.now(),
                                'is_home': self.is_team_home(team_id, match)
                            })
        
        # Sort by date (most recent first) and limit
        team_matches.sort(key=lambda x: x['parsed_date'], reverse=True)
        result = team_matches[:target_matches]
        
        print(f"   Found {len(result)} recent matches for {team_name}")
        return result
    
    def analyze_team_form_advanced(self, team_matches: List[Dict], team_name: str) -> Dict:
        """Advanced form analysis with betting insights"""
        if not team_matches:
            return {
                'team_name': team_name,
                'matches_found': 0,
                'form_rating': 0,
                'momentum': 'Unknown',
                'betting_trends': {}
            }
        
        wins = draws = losses = 0
        goals_for = goals_against = 0
        form_chars = []
        home_record = {'wins': 0, 'draws': 0, 'losses': 0}
        away_record = {'wins': 0, 'draws': 0, 'losses': 0}
        recent_scores = []
        
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
                record = home_record
            else:
                team_goals = away_goals
                opponent_goals = home_goals
                record = away_record
            
            goals_for += team_goals
            goals_against += opponent_goals
            recent_scores.append((team_goals, opponent_goals))
            
            # Determine result
            if team_goals > opponent_goals:
                wins += 1
                record['wins'] += 1
                form_chars.append('W')
            elif team_goals < opponent_goals:
                losses += 1
                record['losses'] += 1
                form_chars.append('L')
            else:
                draws += 1
                record['draws'] += 1
                form_chars.append('D')
        
        total_games = len(team_matches)
        win_percentage = (wins / total_games * 100) if total_games > 0 else 0
        
        # Advanced metrics
        form_rating = self.calculate_form_rating(form_chars)
        momentum = self.calculate_momentum(form_chars)
        attacking_strength = goals_for / total_games if total_games > 0 else 0
        defensive_strength = goals_against / total_games if total_games > 0 else 0
        
        # Betting trends analysis
        betting_trends = self.analyze_betting_trends(recent_scores, form_chars)
        
        return {
            'team_name': team_name,
            'matches_found': total_games,
            'record': f"{wins}W-{draws}D-{losses}L",
            'win_percentage': win_percentage,
            'form_string': ''.join(form_chars),
            'form_rating': form_rating,
            'momentum': momentum,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'attacking_strength': attacking_strength,
            'defensive_strength': defensive_strength,
            'home_record': home_record,
            'away_record': away_record,
            'betting_trends': betting_trends,
            'matches': team_matches
        }
    
    def calculate_form_rating(self, form_chars: List[str]) -> float:
        """Calculate weighted form rating (0-10)"""
        if not form_chars:
            return 5.0
        
        # Weight recent games more heavily
        weights = [3, 2.5, 2, 1.5, 1.2, 1, 1, 1, 1, 1]
        score = 0
        
        for i, result in enumerate(form_chars[:10]):
            weight = weights[i] if i < len(weights) else 1
            if result == 'W':
                score += 3 * weight
            elif result == 'D':
                score += 1 * weight
        
        max_possible = sum(weights[:len(form_chars[:10])]) * 3
        rating = (score / max_possible) * 10 if max_possible > 0 else 5.0
        
        return round(rating, 1)
    
    def calculate_momentum(self, form_chars: List[str]) -> str:
        """Calculate team momentum"""
        if len(form_chars) < 3:
            return 'Insufficient Data'
        
        last_3 = form_chars[:3]
        last_5 = form_chars[:5] if len(form_chars) >= 5 else form_chars
        
        wins_last_3 = last_3.count('W')
        wins_last_5 = last_5.count('W')
        
        if wins_last_3 >= 2:
            return 'Strong Upward'
        elif wins_last_5 >= 3:
            return 'Upward'
        elif last_3.count('L') >= 2:
            return 'Downward'
        elif last_5.count('L') >= 3:
            return 'Strong Downward'
        else:
            return 'Stable'
    
    def analyze_betting_trends(self, recent_scores: List[Tuple], form_chars: List[str]) -> Dict:
        """Analyze betting trends for over/under and other markets"""
        if not recent_scores:
            return {}
        
        total_goals = [sum(score) for score in recent_scores]
        over_2_5 = sum(1 for goals in total_goals if goals > 2.5)
        over_3_5 = sum(1 for goals in total_goals if goals > 3.5)
        
        both_scored = sum(1 for score in recent_scores if score[0] > 0 and score[1] > 0)
        clean_sheets = sum(1 for score in recent_scores if score[1] == 0)
        
        total_matches = len(recent_scores)
        
        return {
            'avg_total_goals': sum(total_goals) / total_matches if total_matches > 0 else 0,
            'over_2_5_percentage': (over_2_5 / total_matches * 100) if total_matches > 0 else 0,
            'over_3_5_percentage': (over_3_5 / total_matches * 100) if total_matches > 0 else 0,
            'both_teams_score_percentage': (both_scored / total_matches * 100) if total_matches > 0 else 0,
            'clean_sheet_percentage': (clean_sheets / total_matches * 100) if total_matches > 0 else 0
        }
    
    def display_enhanced_h2h_analysis(self, match_info: Dict):
        """Display enhanced betting-focused H2H analysis"""
        home_team_id = match_info['home_team_id']
        away_team_id = match_info['away_team_id']
        home_team_name = match_info['home_team_name']
        away_team_name = match_info['away_team_name']
        league_id = match_info['league_id']
        
        print(f"\n" + "=" * 80)
        print("ENHANCED BETTING ANALYSIS")
        print("=" * 80)
        
        # Get recent matches using improved method
        home_matches = self.get_team_recent_matches_improved(home_team_id, home_team_name, league_id, 10)
        away_matches = self.get_team_recent_matches_improved(away_team_id, away_team_name, league_id, 10)
        
        # Advanced form analysis
        home_analysis = self.analyze_team_form_advanced(home_matches, home_team_name)
        away_analysis = self.analyze_team_form_advanced(away_matches, away_team_name)
        
        # Display enhanced comparison
        self.display_betting_focused_comparison(home_analysis, away_analysis, match_info)
        
        # Get historical H2H
        self.display_historical_h2h_enhanced(home_team_id, away_team_id, home_team_name, away_team_name)
        
        # Generate betting predictions
        self.generate_betting_predictions(home_analysis, away_analysis, match_info)
    
    def display_betting_focused_comparison(self, home_analysis: Dict, away_analysis: Dict, match_info: Dict):
        """Display betting-focused team comparison"""
        print(f"\nBETTING-FOCUSED TEAM COMPARISON")
        print("-" * 60)
        print(f"{'Metric':<25} | {home_analysis['team_name'][:18]:<18} | {away_analysis['team_name'][:18]:<18} | {'Edge':<12}")
        print("-" * 60)
        
        # Basic metrics
        print(f"{'Recent Matches':<25} | {home_analysis['matches_found']:<18} | {away_analysis['matches_found']:<18} | {'N/A':<12}")
        print(f"{'Win Rate':<25} | {home_analysis['win_percentage']:<17.1f}% | {away_analysis['win_percentage']:<17.1f}% | {self.get_edge(home_analysis['win_percentage'], away_analysis['win_percentage'], home_analysis['team_name'], away_analysis['team_name']):<12}")
        print(f"{'Form Rating (0-10)':<25} | {home_analysis['form_rating']:<18} | {away_analysis['form_rating']:<18} | {self.get_edge(home_analysis['form_rating'], away_analysis['form_rating'], home_analysis['team_name'], away_analysis['team_name']):<12}")
        print(f"{'Momentum':<25} | {home_analysis['momentum'][:18]:<18} | {away_analysis['momentum'][:18]:<18} | {'N/A':<12}")
        
        # Attacking/Defensive metrics
        print(f"{'Goals Per Game':<25} | {home_analysis['attacking_strength']:<17.2f} | {away_analysis['attacking_strength']:<17.2f} | {self.get_edge(home_analysis['attacking_strength'], away_analysis['attacking_strength'], home_analysis['team_name'], away_analysis['team_name']):<12}")
        print(f"{'Goals Against/Game':<25} | {home_analysis['defensive_strength']:<17.2f} | {away_analysis['defensive_strength']:<17.2f} | {self.get_edge(away_analysis['defensive_strength'], home_analysis['defensive_strength'], away_analysis['team_name'], home_analysis['team_name']):<12}")
        
        # Betting trends
        home_trends = home_analysis.get('betting_trends', {})
        away_trends = away_analysis.get('betting_trends', {})
        
        if home_trends and away_trends:
            print(f"{'Avg Total Goals':<25} | {home_trends.get('avg_total_goals', 0):<17.2f} | {away_trends.get('avg_total_goals', 0):<17.2f} | {'N/A':<12}")
            print(f"{'Over 2.5 Goals %':<25} | {home_trends.get('over_2_5_percentage', 0):<17.1f}% | {away_trends.get('over_2_5_percentage', 0):<17.1f}% | {'N/A':<12}")
            print(f"{'Both Teams Score %':<25} | {home_trends.get('both_teams_score_percentage', 0):<17.1f}% | {away_trends.get('both_teams_score_percentage', 0):<17.1f}% | {'N/A':<12}")
    
    def get_edge(self, val1: float, val2: float, team1: str, team2: str) -> str:
        """Determine which team has the edge in a metric"""
        if abs(val1 - val2) < 0.1:
            return "Even"
        elif val1 > val2:
            return team1[:8]
        else:
            return team2[:8]
    
    def display_historical_h2h_enhanced(self, team_1_id: int, team_2_id: int, team_1_name: str, team_2_name: str):
        """Display enhanced historical H2H with betting insights"""
        print(f"\nHISTORICAL HEAD-TO-HEAD ANALYSIS")
        print("-" * 50)
        
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
            print("No historical matches found")
            return
        
        # Enhanced H2H metrics
        team_1_win_rate = (team_1_wins / total_games) * 100
        team_2_win_rate = (team_2_wins / total_games) * 100
        draw_rate = (draws / total_games) * 100
        avg_goals_per_game = (team_1_goals + team_2_goals) / total_games
        
        print(f"Total Meetings: {total_games}")
        print(f"{team_1_name}: {team_1_wins} wins ({team_1_win_rate:.1f}%)")
        print(f"{team_2_name}: {team_2_wins} wins ({team_2_win_rate:.1f}%)")
        print(f"Draws: {draws} ({draw_rate:.1f}%)")
        print(f"Average Goals Per Game: {avg_goals_per_game:.2f}")
        
        # Betting insights from H2H
        if avg_goals_per_game > 2.8:
            goals_trend = "HIGH-SCORING fixture (Over 2.5 historically likely)"
        elif avg_goals_per_game < 2.2:
            goals_trend = "LOW-SCORING fixture (Under 2.5 historically likely)"
        else:
            goals_trend = "MODERATE-SCORING fixture"
        
        print(f"Historical Trend: {goals_trend}")
    
    def get_h2h_goals_average(self, team_1_id: int, team_2_id: int) -> Optional[float]:
        """Get historical H2H goals average for prediction weighting"""
        h2h_data = self.api_call('head-to-head/', {
            'team_1_id': team_1_id,
            'team_2_id': team_2_id
        }, silent=True)
        
        if not h2h_data:
            return None
        
        stats = h2h_data.get('stats', {})
        overall = stats.get('overall', {})
        
        if not overall:
            return None
        
        total_games = overall.get('overall_games_played', 0)
        team_1_goals = overall.get('overall_team1_scored', 0)
        team_2_goals = overall.get('overall_team2_scored', 0)
        
        if total_games == 0:
            return None
        
        return (team_1_goals + team_2_goals) / total_games
    
    def generate_betting_predictions(self, home_analysis: Dict, away_analysis: Dict, match_info: Dict):
        """Generate comprehensive betting predictions"""
        print(f"\nBETTING PREDICTIONS & VALUE ANALYSIS")
        print("=" * 50)
        
        # Match winner prediction
        home_score = self.calculate_team_strength_score(home_analysis, True)  # Home advantage
        away_score = self.calculate_team_strength_score(away_analysis, False)
        
        confidence = self.calculate_prediction_confidence(home_analysis, away_analysis)
        
        if home_score > away_score + 10:
            prediction = f"{home_analysis['team_name']} Win (Strong)"
            confidence_level = "High" if confidence > 70 else "Medium"
        elif away_score > home_score + 10:
            prediction = f"{away_analysis['team_name']} Win (Strong)"
            confidence_level = "High" if confidence > 70 else "Medium"
        elif home_score > away_score + 5:
            prediction = f"{home_analysis['team_name']} Win (Moderate)"
            confidence_level = "Medium"
        elif away_score > home_score + 5:
            prediction = f"{away_analysis['team_name']} Win (Moderate)"
            confidence_level = "Medium"
        else:
            prediction = "Close Match (Draw or Either Team)"
            confidence_level = "Low"
        
        print(f"Match Winner: {prediction}")
        print(f"Confidence: {confidence_level} ({confidence:.1f}%)")
        
        # Enhanced goals prediction with H2H integration
        home_trends = home_analysis.get('betting_trends', {})
        away_trends = away_analysis.get('betting_trends', {})
        
        if home_trends and away_trends:
            # Calculate team-based expected goals
            team_expected_goals = (home_trends.get('avg_total_goals', 2.5) + 
                                 away_trends.get('avg_total_goals', 2.5)) / 2
            
            team_over_percentage = (home_trends.get('over_2_5_percentage', 50) + 
                                  away_trends.get('over_2_5_percentage', 50)) / 2
            
            # Get H2H data to factor in historical trends
            h2h_goals = self.get_h2h_goals_average(match_info['home_team_id'], match_info['away_team_id'])
            
            # Weight team trends (70%) vs H2H trends (30%)
            if h2h_goals:
                expected_goals = (team_expected_goals * 0.7) + (h2h_goals * 0.3)
                print(f"H2H Average Goals: {h2h_goals:.2f} (factored into prediction)")
            else:
                expected_goals = team_expected_goals
            
            # More nuanced thresholds
            if expected_goals > 2.7 or team_over_percentage > 60:
                goals_prediction = "Over 2.5 Goals"
                if expected_goals > 3.0 and team_over_percentage > 70:
                    goals_confidence = "High"
                elif expected_goals > 2.8 or team_over_percentage > 65:
                    goals_confidence = "Medium"
                else:
                    goals_confidence = "Low-Medium"
            elif expected_goals < 2.3 or team_over_percentage < 40:
                goals_prediction = "Under 2.5 Goals"
                if expected_goals < 2.0 and team_over_percentage < 30:
                    goals_confidence = "High"
                elif expected_goals < 2.1 or team_over_percentage < 35:
                    goals_confidence = "Medium"
                else:
                    goals_confidence = "Low-Medium"
            else:
                goals_prediction = "Around 2.5 Goals (Lean slightly based on team trends)"
                # Provide slight lean based on which side is stronger
                if team_over_percentage > 50:
                    goals_prediction = "Slight lean to Over 2.5 Goals"
                elif team_over_percentage < 50:
                    goals_prediction = "Slight lean to Under 2.5 Goals"
                goals_confidence = "Low"
            
            print(f"Goals Prediction: {goals_prediction}")
            print(f"Expected Goals: {expected_goals:.2f}")
            print(f"Team Over 2.5%: {team_over_percentage:.1f}%")
            print(f"Goals Confidence: {goals_confidence}")
        
        # Key betting insights
        print(f"\nKEY BETTING INSIGHTS:")
        print(f"- Home Team Form: {home_analysis['form_rating']}/10 ({home_analysis['momentum']})")
        print(f"- Away Team Form: {away_analysis['form_rating']}/10 ({away_analysis['momentum']})")
        
        if home_analysis['form_rating'] > 7.5 and home_analysis['momentum'] in ['Strong Upward', 'Upward']:
            print(f"- {home_analysis['team_name']} in excellent form - consider backing")
        elif away_analysis['form_rating'] > 7.5 and away_analysis['momentum'] in ['Strong Upward', 'Upward']:
            print(f"- {away_analysis['team_name']} in excellent form - consider backing")
        
        if home_analysis['momentum'] == 'Strong Downward':
            print(f"- {home_analysis['team_name']} in poor form - avoid backing")
        elif away_analysis['momentum'] == 'Strong Downward':
            print(f"- {away_analysis['team_name']} in poor form - avoid backing")
    
    def calculate_team_strength_score(self, analysis: Dict, is_home: bool) -> float:
        """Calculate overall team strength score"""
        score = 0
        
        # Form rating (40% weight)
        score += analysis.get('form_rating', 5) * 8
        
        # Win percentage (30% weight)
        score += analysis.get('win_percentage', 50) * 0.6
        
        # Momentum bonus (20% weight)
        momentum = analysis.get('momentum', 'Stable')
        if momentum == 'Strong Upward':
            score += 20
        elif momentum == 'Upward':
            score += 10
        elif momentum == 'Downward':
            score -= 10
        elif momentum == 'Strong Downward':
            score -= 20
        
        # Home advantage (10% weight)
        if is_home:
            score += 10
        
        return score
    
    def calculate_prediction_confidence(self, home_analysis: Dict, away_analysis: Dict) -> float:
        """Calculate confidence in prediction based on data quality"""
        confidence = 50  # Base confidence
        
        # Data availability
        home_matches = home_analysis.get('matches_found', 0)
        away_matches = away_analysis.get('matches_found', 0)
        
        if home_matches >= 8 and away_matches >= 8:
            confidence += 20
        elif home_matches >= 5 and away_matches >= 5:
            confidence += 10
        
        # Form difference
        form_diff = abs(home_analysis.get('form_rating', 5) - away_analysis.get('form_rating', 5))
        if form_diff > 2:
            confidence += 15
        elif form_diff > 1:
            confidence += 10
        
        # Momentum alignment
        home_momentum = home_analysis.get('momentum', 'Stable')
        away_momentum = away_analysis.get('momentum', 'Stable')
        
        if (home_momentum in ['Strong Upward', 'Upward'] and 
            away_momentum in ['Strong Downward', 'Downward']):
            confidence += 15
        elif (away_momentum in ['Strong Upward', 'Upward'] and 
              home_momentum in ['Strong Downward', 'Downward']):
            confidence += 15
        
        return min(confidence, 95)  # Cap at 95%
    
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
        
        venue = match.get('venue', {})
        if venue:
            print(f"Venue: {venue.get('name', 'TBD')}")
        
        print(f"Match ID: {match.get('id', 'N/A')}")
        
        return {
            'home_team_id': home_team.get('id'),
            'away_team_id': away_team.get('id'),
            'home_team_name': home_team.get('name'),
            'away_team_name': away_team.get('name'),
            'league_id': league_info['id']
        }
    
    def run_enhanced_analysis(self):
        """Run the complete enhanced betting analysis"""
        try:
            # Step 1: Get date from user
            target_date = self.prompt_for_date()
            
            # Step 2: Get all matches for that date
            all_matches = self.get_matches_for_date(target_date)
            
            # Step 3: Display matches with filtering options
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
            
            # Step 6: Enhanced betting analysis
            if match_info['home_team_id'] and match_info['away_team_id']:
                self.display_enhanced_h2h_analysis(match_info)
            else:
                print("Cannot perform analysis - team IDs not available")
            
            print(f"\n" + "=" * 60)
            print("ENHANCED BETTING ANALYSIS COMPLETE")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\nAnalysis interrupted by user.")
        except Exception as e:
            print(f"\nError during analysis: {e}")

def main():
    """Main execution function"""
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    analyzer = EnhancedBettingAnalyzer(auth_token)
    analyzer.run_enhanced_analysis()

if __name__ == "__main__":
    main()