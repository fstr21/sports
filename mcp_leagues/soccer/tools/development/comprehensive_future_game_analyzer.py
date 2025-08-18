#!/usr/bin/env python3
"""
Comprehensive Future Game H2H Analyzer
Advanced testing framework that:
1. Searches for upcoming matches across multiple leagues
2. Analyzes recent form for each team in upcoming fixtures
3. Provides complete head-to-head intelligence with betting insights
4. Tests the reliability of our H2H strategy with real data
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class FutureGameAnalyzer:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.base_url = "https://api.soccerdataapi.com"
        self.headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'
        }
        
        # Supported leagues for analysis
        self.leagues = {
            'EPL': {'id': 228, 'name': 'Premier League', 'country': 'England'},
            'La Liga': {'id': 297, 'name': 'La Liga', 'country': 'Spain'},
            'MLS': {'id': 168, 'name': 'Major League Soccer', 'country': 'USA'},
            'Serie A': {'id': 244, 'name': 'Serie A', 'country': 'Italy'},
            'Bundesliga': {'id': 175, 'name': 'Bundesliga', 'country': 'Germany'},
            'Ligue 1': {'id': 168, 'name': 'Ligue 1', 'country': 'France'}
        }
    
    def api_call(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API call with error handling and rate limiting"""
        params['auth_token'] = self.auth_token
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Rate limiting - be respectful to the API
            time.sleep(0.5)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error for {endpoint}: {e}")
            return None
        except ValueError as e:
            print(f"JSON Parse Error for {endpoint}: {e}")
            return None
    
    def get_future_dates(self, days_ahead: int = 14) -> List[str]:
        """Generate list of future dates for match searching"""
        dates = []
        today = datetime.now()
        
        for i in range(1, days_ahead + 1):
            future_date = today + timedelta(days=i)
            dates.append(future_date.strftime("%d-%m-%Y"))
        
        return dates
    
    def get_recent_dates(self, days_back: int = 90) -> List[str]:
        """Generate list of recent dates for form analysis"""
        dates = []
        today = datetime.now()
        
        for i in range(1, days_back + 1):
            past_date = today - timedelta(days=i)
            dates.append(past_date.strftime("%d-%m-%Y"))
        
        return dates
    
    def find_future_matches(self, target_leagues: List[str] = None) -> Dict:
        """Find all upcoming matches in specified leagues"""
        if target_leagues is None:
            target_leagues = ['EPL', 'La Liga', 'MLS']
        
        future_dates = self.get_future_dates(14)  # Next 2 weeks
        all_future_matches = {}
        
        print("🔍 SEARCHING FOR UPCOMING MATCHES")
        print("=" * 60)
        
        for league_code in target_leagues:
            if league_code not in self.leagues:
                continue
                
            league_info = self.leagues[league_code]
            league_id = league_info['id']
            league_name = league_info['name']
            
            print(f"\n📅 Searching {league_name}...")
            league_matches = []
            
            for date in future_dates:
                matches_data = self.api_call('matches/', {
                    'league_id': league_id,
                    'date': date
                })
                
                if matches_data:
                    matches = self.extract_matches_from_response(matches_data)
                    for match in matches:
                        match['search_date'] = date
                        match['league_info'] = league_info
                        league_matches.append(match)
                
                # Progress indicator
                print(f"  Checked {date}: {len(matches) if matches_data else 0} matches")
            
            all_future_matches[league_code] = {
                'league_info': league_info,
                'matches': league_matches,
                'total_found': len(league_matches)
            }
            
            print(f"✅ {league_name}: Found {len(league_matches)} upcoming matches")
        
        return all_future_matches
    
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
    
    def analyze_team_recent_form(self, team_id: int, team_name: str, league_id: int, matches_target: int = 10) -> Dict:
        """Analyze recent form for a specific team"""
        print(f"📊 Analyzing recent form for {team_name}...")
        
        recent_dates = self.get_recent_dates(90)  # Last 3 months
        team_matches = []
        
        for date in recent_dates:
            if len(team_matches) >= matches_target:
                break
            
            matches_data = self.api_call('matches/', {
                'league_id': league_id,
                'date': date
            })
            
            if matches_data:
                matches = self.extract_matches_from_response(matches_data)
                
                for match in matches:
                    teams = match.get('teams', {})
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    
                    # Check if this team played in this match
                    if (home_team.get('id') == team_id or away_team.get('id') == team_id):
                        if match.get('status') == 'finished':
                            match['date_played'] = date
                            match['team_is_home'] = (home_team.get('id') == team_id)
                            team_matches.append(match)
        
        # Sort by date (most recent first)
        team_matches.sort(key=lambda x: datetime.strptime(x['date_played'], "%d-%m-%Y"), reverse=True)
        team_matches = team_matches[:matches_target]  # Take only the target number
        
        # Analyze the matches
        analysis = self.calculate_form_stats(team_matches, team_id, team_name)
        analysis['matches_analyzed'] = team_matches
        
        return analysis
    
    def calculate_form_stats(self, matches: List[Dict], team_id: int, team_name: str) -> Dict:
        """Calculate comprehensive form statistics"""
        if not matches:
            return {
                'team_id': team_id,
                'team_name': team_name,
                'matches_found': 0,
                'record': {'wins': 0, 'draws': 0, 'losses': 0},
                'win_percentage': 0.0,
                'goals_for': 0,
                'goals_against': 0,
                'recent_form': '',
                'momentum': 'Unknown'
            }
        
        wins = draws = losses = 0
        goals_for = goals_against = 0
        recent_form_chars = []
        
        for match in matches:
            teams = match.get('teams', {})
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            goals = match.get('goals', {})
            
            is_home = (home_team.get('id') == team_id)
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
                recent_form_chars.append('W')
            elif team_goals < opponent_goals:
                losses += 1
                recent_form_chars.append('L')
            else:
                draws += 1
                recent_form_chars.append('D')
        
        total_games = len(matches)
        win_percentage = (wins / total_games * 100) if total_games > 0 else 0
        
        # Determine momentum from last 5 games
        last_5_form = recent_form_chars[:5]
        recent_wins = last_5_form.count('W')
        momentum = 'UP' if recent_wins >= 3 else 'DOWN' if recent_wins <= 1 else 'STABLE'
        
        return {
            'team_id': team_id,
            'team_name': team_name,
            'matches_found': total_games,
            'record': {'wins': wins, 'draws': draws, 'losses': losses},
            'win_percentage': win_percentage,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goals_per_game': goals_for / total_games if total_games > 0 else 0,
            'goals_conceded_per_game': goals_against / total_games if total_games > 0 else 0,
            'recent_form': ''.join(recent_form_chars[:10]),  # Last 10 games
            'last_5_form': ''.join(last_5_form),
            'momentum': momentum
        }
    
    def get_head_to_head_stats(self, team_1_id: int, team_2_id: int) -> Optional[Dict]:
        """Get historical head-to-head statistics"""
        return self.api_call('head-to-head/', {
            'team_1_id': team_1_id,
            'team_2_id': team_2_id
        })
    
    def comprehensive_match_analysis(self, match: Dict) -> Dict:
        """Perform comprehensive analysis for a specific match"""
        teams = match.get('teams', {})
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        
        home_id = home_team.get('id')
        away_id = away_team.get('id')
        home_name = home_team.get('name', 'Unknown')
        away_name = away_team.get('name', 'Unknown')
        
        league_info = match.get('league_info', {})
        league_id = league_info.get('id')
        
        print(f"\n🥊 COMPREHENSIVE ANALYSIS: {home_name} vs {away_name}")
        print("=" * 80)
        
        # Get recent form for both teams
        home_form = self.analyze_team_recent_form(home_id, home_name, league_id)
        away_form = self.analyze_team_recent_form(away_id, away_name, league_id)
        
        # Get historical head-to-head
        h2h_stats = self.get_head_to_head_stats(home_id, away_id)
        
        # Generate comprehensive analysis
        analysis = {
            'match_info': {
                'home_team': {'id': home_id, 'name': home_name},
                'away_team': {'id': away_id, 'name': away_name},
                'match_date': match.get('date'),
                'match_time': match.get('time'),
                'league': league_info.get('name'),
                'venue': match.get('venue', {}).get('name', 'Unknown')
            },
            'recent_form': {
                'home_team': home_form,
                'away_team': away_form
            },
            'head_to_head': h2h_stats,
            'betting_insights': self.generate_betting_insights(home_form, away_form, h2h_stats, home_name, away_name),
            'prediction': self.generate_prediction(home_form, away_form, h2h_stats, home_name, away_name)
        }
        
        return analysis
    
    def generate_betting_insights(self, home_form: Dict, away_form: Dict, h2h_stats: Optional[Dict], home_name: str, away_name: str) -> Dict:
        """Generate betting insights based on form and H2H data"""
        insights = {
            'form_advantage': 'Even',
            'momentum_factor': 'Neutral',
            'historical_edge': 'Even',
            'goal_expectation': 'Moderate',
            'confidence_level': 'Low'
        }
        
        # Form comparison
        home_win_pct = home_form.get('win_percentage', 0)
        away_win_pct = away_form.get('win_percentage', 0)
        
        if home_win_pct > away_win_pct + 20:
            insights['form_advantage'] = f'{home_name} (Strong)'
        elif home_win_pct > away_win_pct + 10:
            insights['form_advantage'] = f'{home_name} (Moderate)'
        elif away_win_pct > home_win_pct + 20:
            insights['form_advantage'] = f'{away_name} (Strong)'
        elif away_win_pct > home_win_pct + 10:
            insights['form_advantage'] = f'{away_name} (Moderate)'
        
        # Momentum factor
        home_momentum = home_form.get('momentum', 'STABLE')
        away_momentum = away_form.get('momentum', 'STABLE')
        
        if home_momentum == 'UP' and away_momentum == 'DOWN':
            insights['momentum_factor'] = f'{home_name} (Rising vs Falling)'
        elif away_momentum == 'UP' and home_momentum == 'DOWN':
            insights['momentum_factor'] = f'{away_name} (Rising vs Falling)'
        elif home_momentum == 'UP' and away_momentum != 'UP':
            insights['momentum_factor'] = f'{home_name} (Rising)'
        elif away_momentum == 'UP' and home_momentum != 'UP':
            insights['momentum_factor'] = f'{away_name} (Rising)'
        
        # Historical analysis
        if h2h_stats:
            overall_stats = h2h_stats.get('stats', {}).get('overall', {})
            if overall_stats:
                total_games = overall_stats.get('overall_games_played', 0)
                home_wins = overall_stats.get('overall_team1_wins', 0)
                away_wins = overall_stats.get('overall_team2_wins', 0)
                
                if total_games > 5:  # Only if significant sample size
                    if home_wins > away_wins + 3:
                        insights['historical_edge'] = f'{home_name} (Dominates H2H)'
                    elif away_wins > home_wins + 3:
                        insights['historical_edge'] = f'{away_name} (Dominates H2H)'
                    elif home_wins > away_wins:
                        insights['historical_edge'] = f'{home_name} (Slight H2H edge)'
                    elif away_wins > home_wins:
                        insights['historical_edge'] = f'{away_name} (Slight H2H edge)'
        
        # Goal expectation
        home_goals_avg = home_form.get('goals_per_game', 0)
        away_goals_avg = away_form.get('goals_per_game', 0)
        combined_avg = (home_goals_avg + away_goals_avg) / 2
        
        if combined_avg > 2.5:
            insights['goal_expectation'] = 'High (Over 2.5 likely)'
        elif combined_avg < 1.5:
            insights['goal_expectation'] = 'Low (Under 2.5 likely)'
        else:
            insights['goal_expectation'] = 'Moderate (Around 2-3 goals)'
        
        # Confidence level based on data alignment
        confidence_factors = 0
        if insights['form_advantage'] != 'Even':
            confidence_factors += 1
        if insights['momentum_factor'] != 'Neutral':
            confidence_factors += 1
        if insights['historical_edge'] != 'Even':
            confidence_factors += 1
        
        if confidence_factors >= 3:
            insights['confidence_level'] = 'High'
        elif confidence_factors >= 2:
            insights['confidence_level'] = 'Medium'
        else:
            insights['confidence_level'] = 'Low'
        
        return insights
    
    def generate_prediction(self, home_form: Dict, away_form: Dict, h2h_stats: Optional[Dict], home_name: str, away_name: str) -> Dict:
        """Generate match prediction based on all available data"""
        home_win_pct = home_form.get('win_percentage', 0)
        away_win_pct = away_form.get('win_percentage', 0)
        
        # Base prediction on recent form (60% weight) + home advantage (20%) + H2H (20%)
        home_score = home_win_pct * 0.6 + 10  # 10% home advantage
        away_score = away_win_pct * 0.6
        
        # Adjust for H2H if available
        if h2h_stats:
            overall_stats = h2h_stats.get('stats', {}).get('overall', {})
            if overall_stats:
                total_games = overall_stats.get('overall_games_played', 0)
                if total_games > 5:
                    home_h2h_wins = overall_stats.get('overall_team1_wins', 0)
                    away_h2h_wins = overall_stats.get('overall_team2_wins', 0)
                    home_h2h_pct = (home_h2h_wins / total_games) * 100
                    away_h2h_pct = (away_h2h_wins / total_games) * 100
                    
                    home_score += home_h2h_pct * 0.2
                    away_score += away_h2h_pct * 0.2
        
        # Determine prediction
        if home_score > away_score + 15:
            prediction = f"{home_name} Win (Strong)"
            confidence = "High"
        elif home_score > away_score + 8:
            prediction = f"{home_name} Win (Moderate)"
            confidence = "Medium"
        elif away_score > home_score + 8:
            prediction = f"{away_name} Win (Moderate)"
            confidence = "Medium"
        elif away_score > home_score + 15:
            prediction = f"{away_name} Win (Strong)"
            confidence = "High"
        else:
            prediction = "Close Match (Draw/Either team)"
            confidence = "Low"
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'home_score': round(home_score, 1),
            'away_score': round(away_score, 1),
            'reasoning': self.generate_reasoning(home_form, away_form, h2h_stats, home_name, away_name)
        }
    
    def generate_reasoning(self, home_form: Dict, away_form: Dict, h2h_stats: Optional[Dict], home_name: str, away_name: str) -> List[str]:
        """Generate reasoning for the prediction"""
        reasons = []
        
        # Form comparison
        home_win_pct = home_form.get('win_percentage', 0)
        away_win_pct = away_form.get('win_percentage', 0)
        
        if home_win_pct > away_win_pct + 15:
            reasons.append(f"{home_name} has significantly better recent form ({home_win_pct:.1f}% vs {away_win_pct:.1f}%)")
        elif away_win_pct > home_win_pct + 15:
            reasons.append(f"{away_name} has significantly better recent form ({away_win_pct:.1f}% vs {home_win_pct:.1f}%)")
        
        # Momentum
        home_momentum = home_form.get('momentum', 'STABLE')
        away_momentum = away_form.get('momentum', 'STABLE')
        
        if home_momentum == 'UP' and away_momentum == 'DOWN':
            reasons.append(f"{home_name} has rising momentum while {away_name} is declining")
        elif away_momentum == 'UP' and home_momentum == 'DOWN':
            reasons.append(f"{away_name} has rising momentum while {home_name} is declining")
        
        # Historical
        if h2h_stats:
            overall_stats = h2h_stats.get('stats', {}).get('overall', {})
            if overall_stats:
                total_games = overall_stats.get('overall_games_played', 0)
                if total_games > 5:
                    home_wins = overall_stats.get('overall_team1_wins', 0)
                    away_wins = overall_stats.get('overall_team2_wins', 0)
                    if home_wins > away_wins + 2:
                        reasons.append(f"{home_name} dominates historical meetings ({home_wins}-{away_wins})")
                    elif away_wins > home_wins + 2:
                        reasons.append(f"{away_name} dominates historical meetings ({away_wins}-{home_wins})")
        
        # Home advantage
        reasons.append(f"{home_name} has home field advantage")
        
        return reasons
    
    def display_comprehensive_analysis(self, analysis: Dict):
        """Display comprehensive analysis in a beautiful format"""
        match_info = analysis['match_info']
        home_team = match_info['home_team']
        away_team = match_info['away_team']
        home_form = analysis['recent_form']['home_team']
        away_form = analysis['recent_form']['away_team']
        betting_insights = analysis['betting_insights']
        prediction = analysis['prediction']
        
        print(f"\n🏟️  MATCH: {home_team['name']} vs {away_team['name']}")
        print(f"📅 Date: {match_info['match_date']} at {match_info['match_time']}")
        print(f"🏆 League: {match_info['league']}")
        print(f"📍 Venue: {match_info['venue']}")
        
        print(f"\n📊 RECENT FORM COMPARISON")
        print("=" * 60)
        print(f"| {'Metric':<20} | {home_team['name'][:12]:<12} | {away_team['name'][:12]:<12} |")
        print("|" + "-" * 20 + "|" + "-" * 14 + "|" + "-" * 14 + "|")
        print(f"| {'Matches Analyzed':<20} | {home_form['matches_found']:<12} | {away_form['matches_found']:<12} |")
        print(f"| {'Win Percentage':<20} | {home_form['win_percentage']:<11.1f}% | {away_form['win_percentage']:<11.1f}% |")
        print(f"| {'Recent Form (L10)':<20} | {home_form['recent_form'][:10]:<12} | {away_form['recent_form'][:10]:<12} |")
        print(f"| {'Last 5 Games':<20} | {home_form['last_5_form']:<12} | {away_form['last_5_form']:<12} |")
        print(f"| {'Momentum':<20} | {home_form['momentum']:<12} | {away_form['momentum']:<12} |")
        print(f"| {'Goals Per Game':<20} | {home_form['goals_per_game']:<11.2f} | {away_form['goals_per_game']:<11.2f} |")
        
        print(f"\n💡 BETTING INSIGHTS")
        print("=" * 40)
        print(f"Form Advantage: {betting_insights['form_advantage']}")
        print(f"Momentum Factor: {betting_insights['momentum_factor']}")
        print(f"Historical Edge: {betting_insights['historical_edge']}")
        print(f"Goal Expectation: {betting_insights['goal_expectation']}")
        print(f"Confidence Level: {betting_insights['confidence_level']}")
        
        print(f"\n🎯 PREDICTION")
        print("=" * 30)
        print(f"Predicted Outcome: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Analysis Scores: {home_team['name']} {prediction['home_score']} - {prediction['away_score']} {away_team['name']}")
        
        print(f"\n📝 REASONING")
        print("=" * 30)
        for i, reason in enumerate(prediction['reasoning'], 1):
            print(f"{i}. {reason}")
    
    def run_comprehensive_test(self, target_leagues: List[str] = None, max_matches_to_analyze: int = 5):
        """Run comprehensive testing of H2H strategy"""
        print("🚀 COMPREHENSIVE FUTURE GAME H2H ANALYZER")
        print("=" * 80)
        print("Testing our head-to-head strategy with real upcoming fixtures")
        print("This will search for future games, analyze recent form, and provide betting insights")
        print()
        
        # Find future matches
        future_matches = self.find_future_matches(target_leagues)
        
        # Collect all matches for analysis
        all_matches = []
        for league_code, league_data in future_matches.items():
            for match in league_data['matches']:
                if match.get('status') in ['scheduled', 'tbd']:  # Only upcoming matches
                    all_matches.append(match)
        
        if not all_matches:
            print("❌ No upcoming matches found in the specified leagues and timeframe")
            return
        
        print(f"\n✅ Found {len(all_matches)} upcoming matches across all leagues")
        print(f"📊 Analyzing first {min(max_matches_to_analyze, len(all_matches))} matches for comprehensive H2H testing")
        
        # Analyze selected matches
        analyses = []
        for i, match in enumerate(all_matches[:max_matches_to_analyze], 1):
            print(f"\n{'🔍 ANALYSIS ' + str(i):<20}")
            print("-" * 60)
            
            try:
                analysis = self.comprehensive_match_analysis(match)
                analyses.append(analysis)
                self.display_comprehensive_analysis(analysis)
            except Exception as e:
                print(f"❌ Error analyzing match: {e}")
                continue
        
        # Save results
        self.save_test_results(analyses)
        
        print(f"\n🎯 TESTING SUMMARY")
        print("=" * 50)
        print(f"Total Matches Analyzed: {len(analyses)}")
        print(f"Strategy Reliability: Testing complete - review results above")
        print(f"Data Sources Used: Recent form, Historical H2H, Home advantage")
        print("✅ Head-to-head strategy testing complete!")
    
    def save_test_results(self, analyses: List[Dict]):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"h2h_strategy_test_results_{timestamp}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_timestamp': timestamp,
                    'total_analyses': len(analyses),
                    'analyses': analyses
                }, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    # Initialize analyzer
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    analyzer = FutureGameAnalyzer(auth_token)
    
    # Run comprehensive testing
    target_leagues = ['EPL', 'La Liga', 'MLS']  # Customize as needed
    analyzer.run_comprehensive_test(target_leagues, max_matches_to_analyze=3)

if __name__ == "__main__":
    main()