#!/usr/bin/env python3
"""
Unified H2H Intelligence System
Complete integration of:
1. Future match discovery
2. Recent form analysis 
3. Historical H2H statistics
4. Betting insights generation
5. Confidence scoring
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class UnifiedH2HIntelligence:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.base_url = "https://api.soccerdataapi.com"
        self.headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'
        }
        
        # Major leagues for analysis
        self.leagues = {
            'EPL': {'id': 228, 'name': 'Premier League', 'country': 'England'},
            'La Liga': {'id': 297, 'name': 'La Liga', 'country': 'Spain'}, 
            'Serie A': {'id': 244, 'name': 'Serie A', 'country': 'Italy'},
            'Bundesliga': {'id': 175, 'name': 'Bundesliga', 'country': 'Germany'},
            'MLS': {'id': 168, 'name': 'Major League Soccer', 'country': 'USA'}
        }
    
    def smart_match_finder(self, days_ahead: int = 7) -> Dict[str, List[Dict]]:
        """Smart match finder that looks for upcoming fixtures across leagues"""
        print(f"🔍 SMART MATCH DISCOVERY - Next {days_ahead} days")
        print("=" * 60)
        
        upcoming_matches = {}
        target_date = datetime.now() + timedelta(days=1)  # Start from tomorrow
        
        for i in range(days_ahead):
            search_date = target_date + timedelta(days=i)
            date_str = search_date.strftime("%d-%m-%Y")
            
            print(f"📅 Searching {date_str}...")
            day_matches = []
            
            # Search all major leagues for this date
            for league_code, league_info in self.leagues.items():
                matches_data = self.api_call('matches/', {
                    'league_id': league_info['id'],
                    'date': date_str
                })
                
                if matches_data:
                    matches = self.extract_matches_from_response(matches_data)
                    for match in matches:
                        match['league_code'] = league_code
                        match['league_info'] = league_info
                        match['search_date'] = date_str
                        day_matches.append(match)
            
            if day_matches:
                upcoming_matches[date_str] = day_matches
                print(f"  ✅ Found {len(day_matches)} matches")
            else:
                print(f"  📭 No matches found")
        
        total_found = sum(len(matches) for matches in upcoming_matches.values())
        print(f"\n🎯 DISCOVERY COMPLETE: {total_found} upcoming matches found")
        return upcoming_matches
    
    def enhanced_form_analyzer(self, team_id: int, team_name: str, league_id: int) -> Dict:
        """Enhanced form analysis with deeper insights"""
        print(f"📊 Deep form analysis for {team_name}...")
        
        # Get last 3 months of data
        form_data = {
            'team_id': team_id,
            'team_name': team_name,
            'league_id': league_id,
            'matches': [],
            'home_form': {'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0},
            'away_form': {'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0},
            'recent_form': {'wins': 0, 'draws': 0, 'losses': 0},
            'scoring_form': {'goals_per_game': 0, 'clean_sheets': 0, 'failed_to_score': 0},
            'momentum_indicators': {}
        }
        
        # Search recent matches
        search_dates = [(datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(1, 91)]
        matches_found = []
        
        for date in search_dates:
            if len(matches_found) >= 15:  # Limit to last 15 matches
                break
                
            matches_data = self.api_call('matches/', {'league_id': league_id, 'date': date})
            
            if matches_data:
                matches = self.extract_matches_from_response(matches_data)
                for match in matches:
                    if self.team_played_in_match(team_id, match) and match.get('status') == 'finished':
                        matches_found.append({
                            'match': match,
                            'date': date,
                            'is_home': self.is_team_home(team_id, match)
                        })
        
        # Analyze matches
        form_data['matches'] = matches_found[:15]  # Last 15 matches
        form_data = self.calculate_enhanced_form_stats(form_data)
        
        return form_data
    
    def calculate_enhanced_form_stats(self, form_data: Dict) -> Dict:
        """Calculate comprehensive form statistics"""
        matches = form_data['matches']
        team_id = form_data['team_id']
        
        if not matches:
            return form_data
        
        total_wins = total_draws = total_losses = 0
        total_goals_for = total_goals_against = 0
        clean_sheets = failed_to_score = 0
        home_stats = {'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0}
        away_stats = {'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0}
        
        recent_results = []  # For momentum calculation
        
        for match_info in matches:
            match = match_info['match']
            is_home = match_info['is_home']
            
            # Get goals
            goals = match.get('goals', {})
            home_goals = goals.get('home_ft_goals', 0)
            away_goals = goals.get('away_ft_goals', 0)
            
            if is_home:
                team_goals = home_goals
                opponent_goals = away_goals
                venue_stats = home_stats
            else:
                team_goals = away_goals
                opponent_goals = home_goals
                venue_stats = away_stats
            
            # Calculate result
            if team_goals > opponent_goals:
                result = 'W'
                total_wins += 1
                venue_stats['wins'] += 1
            elif team_goals < opponent_goals:
                result = 'L'
                total_losses += 1
                venue_stats['losses'] += 1
            else:
                result = 'D'
                total_draws += 1
                venue_stats['draws'] += 1
            
            recent_results.append(result)
            total_goals_for += team_goals
            total_goals_against += opponent_goals
            venue_stats['goals_for'] += team_goals
            venue_stats['goals_against'] += opponent_goals
            
            # Track clean sheets and failures to score
            if opponent_goals == 0:
                clean_sheets += 1
            if team_goals == 0:
                failed_to_score += 1
        
        total_games = len(matches)
        
        # Update form data
        form_data['recent_form'] = {
            'wins': total_wins,
            'draws': total_draws, 
            'losses': total_losses,
            'win_percentage': (total_wins / total_games * 100) if total_games > 0 else 0,
            'form_string': ''.join(recent_results[:10]),  # Last 10 games
            'last_5_form': ''.join(recent_results[:5])
        }
        
        form_data['home_form'] = home_stats
        form_data['away_form'] = away_stats
        
        form_data['scoring_form'] = {
            'goals_per_game': total_goals_for / total_games if total_games > 0 else 0,
            'goals_against_per_game': total_goals_against / total_games if total_games > 0 else 0,
            'clean_sheets': clean_sheets,
            'clean_sheet_percentage': (clean_sheets / total_games * 100) if total_games > 0 else 0,
            'failed_to_score': failed_to_score,
            'scoring_reliability': ((total_games - failed_to_score) / total_games * 100) if total_games > 0 else 0
        }
        
        # Momentum indicators
        last_5_results = recent_results[:5]
        last_3_results = recent_results[:3]
        
        form_data['momentum_indicators'] = {
            'last_5_wins': last_5_results.count('W'),
            'last_3_wins': last_3_results.count('W'),
            'momentum': self.calculate_momentum(recent_results),
            'trend': self.calculate_trend(recent_results),
            'form_rating': self.calculate_form_rating(recent_results)
        }
        
        return form_data
    
    def calculate_momentum(self, results: List[str]) -> str:
        """Calculate team momentum based on recent results"""
        if len(results) < 3:
            return 'INSUFFICIENT_DATA'
        
        last_3 = results[:3]
        last_5 = results[:5] if len(results) >= 5 else results
        
        wins_last_3 = last_3.count('W')
        wins_last_5 = last_5.count('W')
        
        if wins_last_3 >= 2:
            return 'STRONG_UP'
        elif wins_last_5 >= 3:
            return 'UP'
        elif last_3.count('L') >= 2:
            return 'DOWN'
        elif last_5.count('L') >= 3:
            return 'STRONG_DOWN'
        else:
            return 'STABLE'
    
    def calculate_trend(self, results: List[str]) -> str:
        """Calculate overall trend"""
        if len(results) < 5:
            return 'INSUFFICIENT_DATA'
        
        first_half = results[:len(results)//2]
        second_half = results[len(results)//2:]
        
        first_half_wins = first_half.count('W') / len(first_half) if first_half else 0
        second_half_wins = second_half.count('W') / len(second_half) if second_half else 0
        
        if second_half_wins > first_half_wins + 0.2:
            return 'IMPROVING'
        elif first_half_wins > second_half_wins + 0.2:
            return 'DECLINING'
        else:
            return 'CONSISTENT'
    
    def calculate_form_rating(self, results: List[str]) -> float:
        """Calculate numerical form rating (0-10)"""
        if not results:
            return 5.0
        
        # Weight recent games more heavily
        score = 0
        weights = [3, 2.5, 2, 1.5, 1.2, 1, 1, 1, 1, 1]  # First game weighted 3x, then decreasing
        
        for i, result in enumerate(results[:10]):
            weight = weights[i] if i < len(weights) else 1
            if result == 'W':
                score += 3 * weight
            elif result == 'D':
                score += 1 * weight
            # Loss = 0 points
        
        max_possible = sum(weights[:len(results[:10])]) * 3
        rating = (score / max_possible) * 10 if max_possible > 0 else 5.0
        
        return round(rating, 1)
    
    def ultimate_h2h_analysis(self, team_1_id: int, team_2_id: int, team_1_name: str, team_2_name: str, league_id: int) -> Dict:
        """Ultimate head-to-head analysis combining all data sources"""
        print(f"\n⚔️  ULTIMATE H2H ANALYSIS: {team_1_name} vs {team_2_name}")
        print("=" * 80)
        
        # Get enhanced form for both teams
        print("📊 Analyzing recent form...")
        team_1_form = self.enhanced_form_analyzer(team_1_id, team_1_name, league_id)
        team_2_form = self.enhanced_form_analyzer(team_2_id, team_2_name, league_id)
        
        # Get historical H2H
        print("🔍 Getting historical head-to-head...")
        h2h_stats = self.api_call('head-to-head/', {
            'team_1_id': team_1_id,
            'team_2_id': team_2_id
        })
        
        # Generate ultimate analysis
        analysis = {
            'teams': {
                'team_1': {'id': team_1_id, 'name': team_1_name, 'form': team_1_form},
                'team_2': {'id': team_2_id, 'name': team_2_name, 'form': team_2_form}
            },
            'historical_h2h': h2h_stats,
            'form_comparison': self.compare_team_forms(team_1_form, team_2_form, team_1_name, team_2_name),
            'betting_intelligence': self.generate_betting_intelligence(team_1_form, team_2_form, h2h_stats, team_1_name, team_2_name),
            'prediction': self.generate_ultimate_prediction(team_1_form, team_2_form, h2h_stats, team_1_name, team_2_name),
            'confidence_score': 0  # Will be calculated
        }
        
        # Calculate overall confidence
        analysis['confidence_score'] = self.calculate_confidence_score(analysis)
        
        return analysis
    
    def compare_team_forms(self, team_1_form: Dict, team_2_form: Dict, team_1_name: str, team_2_name: str) -> Dict:
        """Detailed form comparison"""
        t1_recent = team_1_form['recent_form']
        t2_recent = team_2_form['recent_form']
        t1_momentum = team_1_form['momentum_indicators']
        t2_momentum = team_2_form['momentum_indicators']
        
        comparison = {
            'win_percentage_gap': abs(t1_recent['win_percentage'] - t2_recent['win_percentage']),
            'form_advantage': team_1_name if t1_recent['win_percentage'] > t2_recent['win_percentage'] else team_2_name,
            'momentum_advantage': team_1_name if t1_momentum['form_rating'] > t2_momentum['form_rating'] else team_2_name,
            'attacking_advantage': team_1_name if team_1_form['scoring_form']['goals_per_game'] > team_2_form['scoring_form']['goals_per_game'] else team_2_name,
            'defensive_advantage': team_1_name if team_1_form['scoring_form']['clean_sheet_percentage'] > team_2_form['scoring_form']['clean_sheet_percentage'] else team_2_name,
            'overall_form_edge': 'Even'
        }
        
        # Calculate overall edge
        advantages = [
            comparison['form_advantage'],
            comparison['momentum_advantage'], 
            comparison['attacking_advantage'],
            comparison['defensive_advantage']
        ]
        
        team_1_advantages = advantages.count(team_1_name)
        team_2_advantages = advantages.count(team_2_name)
        
        if team_1_advantages >= 3:
            comparison['overall_form_edge'] = f"{team_1_name} (Strong)"
        elif team_1_advantages > team_2_advantages:
            comparison['overall_form_edge'] = f"{team_1_name} (Moderate)"
        elif team_2_advantages >= 3:
            comparison['overall_form_edge'] = f"{team_2_name} (Strong)"
        elif team_2_advantages > team_1_advantages:
            comparison['overall_form_edge'] = f"{team_2_name} (Moderate)"
        
        return comparison
    
    def generate_betting_intelligence(self, team_1_form: Dict, team_2_form: Dict, h2h_stats: Optional[Dict], team_1_name: str, team_2_name: str) -> Dict:
        """Generate comprehensive betting intelligence"""
        intelligence = {
            'match_winner': {'recommendation': 'No clear favorite', 'confidence': 'Low'},
            'over_under': {'recommendation': 'Under 2.5', 'confidence': 'Low', 'expected_goals': 2.0},
            'both_teams_score': {'recommendation': 'No', 'confidence': 'Low'},
            'value_bets': [],
            'avoid_bets': []
        }
        
        # Match winner analysis
        t1_rating = team_1_form['momentum_indicators']['form_rating']
        t2_rating = team_2_form['momentum_indicators']['form_rating']
        
        rating_gap = abs(t1_rating - t2_rating)
        
        if rating_gap >= 2.0:
            favorite = team_1_name if t1_rating > t2_rating else team_2_name
            intelligence['match_winner'] = {
                'recommendation': favorite,
                'confidence': 'High' if rating_gap >= 3.0 else 'Medium'
            }
        elif rating_gap >= 1.0:
            favorite = team_1_name if t1_rating > t2_rating else team_2_name
            intelligence['match_winner'] = {
                'recommendation': favorite,
                'confidence': 'Low'
            }
        
        # Goals analysis
        t1_goals_avg = team_1_form['scoring_form']['goals_per_game']
        t2_goals_avg = team_2_form['scoring_form']['goals_per_game']
        t1_concede_avg = team_1_form['scoring_form']['goals_against_per_game']
        t2_concede_avg = team_2_form['scoring_form']['goals_against_per_game']
        
        expected_goals = (t1_goals_avg + t2_goals_avg + t1_concede_avg + t2_concede_avg) / 2
        intelligence['over_under']['expected_goals'] = round(expected_goals, 1)
        
        if expected_goals > 2.8:
            intelligence['over_under'] = {'recommendation': 'Over 2.5', 'confidence': 'Medium'}
        elif expected_goals < 2.2:
            intelligence['over_under'] = {'recommendation': 'Under 2.5', 'confidence': 'Medium'}
        
        # Both teams to score
        t1_scoring_reliability = team_1_form['scoring_form']['scoring_reliability']
        t2_scoring_reliability = team_2_form['scoring_form']['scoring_reliability']
        
        if t1_scoring_reliability > 70 and t2_scoring_reliability > 70:
            intelligence['both_teams_score'] = {'recommendation': 'Yes', 'confidence': 'Medium'}
        elif t1_scoring_reliability < 50 or t2_scoring_reliability < 50:
            intelligence['both_teams_score'] = {'recommendation': 'No', 'confidence': 'Medium'}
        
        return intelligence
    
    def generate_ultimate_prediction(self, team_1_form: Dict, team_2_form: Dict, h2h_stats: Optional[Dict], team_1_name: str, team_2_name: str) -> Dict:
        """Generate ultimate prediction with detailed reasoning"""
        # Combine all factors with weights
        factors = {
            'recent_form': 0.4,      # 40% weight
            'momentum': 0.3,         # 30% weight  
            'historical_h2h': 0.2,   # 20% weight
            'home_advantage': 0.1    # 10% weight (assumed team_1 is home)
        }
        
        # Calculate scores
        team_1_score = 50  # Base score
        team_2_score = 50
        
        # Recent form factor
        t1_win_pct = team_1_form['recent_form']['win_percentage']
        t2_win_pct = team_2_form['recent_form']['win_percentage']
        form_diff = t1_win_pct - t2_win_pct
        team_1_score += form_diff * factors['recent_form']
        team_2_score -= form_diff * factors['recent_form']
        
        # Momentum factor
        t1_rating = team_1_form['momentum_indicators']['form_rating']
        t2_rating = team_2_form['momentum_indicators']['form_rating']
        momentum_diff = (t1_rating - t2_rating) * 10  # Scale to percentage
        team_1_score += momentum_diff * factors['momentum']
        team_2_score -= momentum_diff * factors['momentum']
        
        # Historical H2H factor
        if h2h_stats:
            overall = h2h_stats.get('stats', {}).get('overall', {})
            if overall:
                total_games = overall.get('overall_games_played', 0)
                if total_games > 5:  # Minimum sample size
                    t1_wins = overall.get('overall_team1_wins', 0)
                    t2_wins = overall.get('overall_team2_wins', 0)
                    h2h_diff = ((t1_wins - t2_wins) / total_games) * 100
                    team_1_score += h2h_diff * factors['historical_h2h']
                    team_2_score -= h2h_diff * factors['historical_h2h']
        
        # Home advantage (assuming team_1 is home)
        team_1_score += 5 * factors['home_advantage']  # 5% home advantage
        
        # Generate prediction
        score_diff = abs(team_1_score - team_2_score)
        
        if team_1_score > team_2_score:
            if score_diff > 15:
                prediction = f"{team_1_name} Win (Strong)"
                confidence = "High"
            elif score_diff > 8:
                prediction = f"{team_1_name} Win (Moderate)"
                confidence = "Medium"
            else:
                prediction = f"{team_1_name} Win (Slight)"
                confidence = "Low"
        elif team_2_score > team_1_score:
            if score_diff > 15:
                prediction = f"{team_2_name} Win (Strong)"
                confidence = "High"
            elif score_diff > 8:
                prediction = f"{team_2_name} Win (Moderate)"
                confidence = "Medium"
            else:
                prediction = f"{team_2_name} Win (Slight)"
                confidence = "Low"
        else:
            prediction = "Draw/Either Team"
            confidence = "Very Low"
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'team_1_score': round(team_1_score, 1),
            'team_2_score': round(team_2_score, 1),
            'score_difference': round(score_diff, 1),
            'factors_used': list(factors.keys())
        }
    
    def calculate_confidence_score(self, analysis: Dict) -> float:
        """Calculate overall confidence score (0-100)"""
        confidence_factors = []
        
        # Data availability
        team_1_matches = len(analysis['teams']['team_1']['form']['matches'])
        team_2_matches = len(analysis['teams']['team_2']['form']['matches'])
        data_availability = min(team_1_matches, team_2_matches) / 15 * 30  # Max 30 points
        confidence_factors.append(data_availability)
        
        # Form clarity (how clear the form difference is)
        form_gap = analysis['form_comparison']['win_percentage_gap']
        form_clarity = min(form_gap / 50, 1) * 25  # Max 25 points
        confidence_factors.append(form_clarity)
        
        # Historical data
        h2h_stats = analysis['historical_h2h']
        if h2h_stats:
            overall = h2h_stats.get('stats', {}).get('overall', {})
            if overall and overall.get('overall_games_played', 0) > 5:
                confidence_factors.append(20)  # 20 points for good H2H data
            else:
                confidence_factors.append(10)  # 10 points for some H2H data
        else:
            confidence_factors.append(0)  # No H2H data
        
        # Prediction strength
        pred_confidence = analysis['prediction']['confidence']
        if pred_confidence == 'High':
            confidence_factors.append(25)
        elif pred_confidence == 'Medium':
            confidence_factors.append(15)
        elif pred_confidence == 'Low':
            confidence_factors.append(8)
        else:
            confidence_factors.append(3)
        
        return round(sum(confidence_factors), 1)
    
    def display_ultimate_analysis(self, analysis: Dict):
        """Display the ultimate analysis in a beautiful format"""
        teams = analysis['teams']
        team_1 = teams['team_1']
        team_2 = teams['team_2']
        form_comp = analysis['form_comparison'] 
        betting = analysis['betting_intelligence']
        prediction = analysis['prediction']
        confidence = analysis['confidence_score']
        
        print(f"\n🏆 ULTIMATE H2H INTELLIGENCE REPORT")
        print("=" * 80)
        print(f"⚔️  {team_1['name']} vs {team_2['name']}")
        print(f"🎯 Overall Confidence Score: {confidence}/100")
        
        print(f"\n📊 ENHANCED FORM COMPARISON")
        print("-" * 50)
        print(f"{'Metric':<25} | {team_1['name'][:15]:<15} | {team_2['name'][:15]:<15}")
        print("-" * 50)
        
        t1_form = team_1['form']['recent_form']
        t2_form = team_2['form']['recent_form']
        t1_momentum = team_1['form']['momentum_indicators']
        t2_momentum = team_2['form']['momentum_indicators']
        t1_scoring = team_1['form']['scoring_form']
        t2_scoring = team_2['form']['scoring_form']
        
        print(f"{'Win Percentage':<25} | {t1_form['win_percentage']:<14.1f}% | {t2_form['win_percentage']:<14.1f}%")
        print(f"{'Form Rating (0-10)':<25} | {t1_momentum['form_rating']:<15} | {t2_momentum['form_rating']:<15}")
        print(f"{'Recent Form':<25} | {t1_form['form_string'][:15]:<15} | {t2_form['form_string'][:15]:<15}")
        print(f"{'Momentum':<25} | {t1_momentum['momentum']:<15} | {t2_momentum['momentum']:<15}")
        print(f"{'Goals Per Game':<25} | {t1_scoring['goals_per_game']:<14.2f} | {t2_scoring['goals_per_game']:<14.2f}")
        print(f"{'Clean Sheet %':<25} | {t1_scoring['clean_sheet_percentage']:<14.1f}% | {t2_scoring['clean_sheet_percentage']:<14.1f}%")
        
        print(f"\n🎲 BETTING INTELLIGENCE")
        print("-" * 40)
        print(f"Match Winner: {betting['match_winner']['recommendation']} ({betting['match_winner']['confidence']} confidence)")
        print(f"Over/Under 2.5: {betting['over_under']['recommendation']} (Expected: {betting['over_under']['expected_goals']} goals)")
        print(f"Both Teams Score: {betting['both_teams_score']['recommendation']} ({betting['both_teams_score']['confidence']} confidence)")
        
        print(f"\n🔮 ULTIMATE PREDICTION")
        print("-" * 30)
        print(f"Prediction: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Analysis Scores: {team_1['name']} {prediction['team_1_score']} - {prediction['team_2_score']} {team_2['name']}")
        print(f"Score Difference: {prediction['score_difference']}")
        
        print(f"\n📈 ADVANTAGES SUMMARY")
        print("-" * 30)
        print(f"Form Advantage: {form_comp['form_advantage']}")
        print(f"Momentum Edge: {form_comp['momentum_advantage']}")
        print(f"Attacking Edge: {form_comp['attacking_advantage']}")
        print(f"Defensive Edge: {form_comp['defensive_advantage']}")
        print(f"Overall Edge: {form_comp['overall_form_edge']}")
    
    # Utility methods
    def api_call(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API call with error handling"""
        params['auth_token'] = self.auth_token
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            time.sleep(0.3)  # Rate limiting
            return response.json()
        except:
            return None
    
    def extract_matches_from_response(self, response_data) -> List[Dict]:
        """Extract matches from API response"""
        matches = []
        if not response_data or not isinstance(response_data, list):
            return matches
        
        for league_data in response_data:
            if isinstance(league_data, dict):
                if 'matches' in league_data:
                    matches.extend(league_data['matches'])
                elif 'stage' in league_data:
                    for stage in league_data['stage']:
                        if 'matches' in stage:
                            matches.extend(stage['matches'])
        return matches
    
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

def main():
    """Main execution function"""
    print("🚀 UNIFIED H2H INTELLIGENCE SYSTEM")
    print("=" * 80)
    print("The most comprehensive head-to-head analysis system")
    print("Combines: Future match discovery + Enhanced form analysis + Historical H2H + Betting intelligence")
    
    # Initialize
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    analyzer = UnifiedH2HIntelligence(auth_token)
    
    # Find upcoming matches
    upcoming_matches = analyzer.smart_match_finder(days_ahead=5)
    
    if not upcoming_matches:
        print("❌ No upcoming matches found")
        return
    
    # Select first match for demonstration
    first_date = list(upcoming_matches.keys())[0]
    first_match = upcoming_matches[first_date][0]
    
    # Get team info
    teams = first_match.get('teams', {})
    home_team = teams.get('home', {})
    away_team = teams.get('away', {})
    league_info = first_match.get('league_info', {})
    
    if home_team.get('id') and away_team.get('id'):
        # Run ultimate analysis
        analysis = analyzer.ultimate_h2h_analysis(
            home_team['id'], away_team['id'],
            home_team['name'], away_team['name'],
            league_info['id']
        )
        
        # Display results
        analyzer.display_ultimate_analysis(analysis)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ultimate_h2h_analysis_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n💾 Analysis saved to: {filename}")
    
    print("\n✅ Ultimate H2H Intelligence analysis complete!")

if __name__ == "__main__":
    main()