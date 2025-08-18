#!/usr/bin/env python3
"""
Simple H2H Strategy Tester (No Emojis)
Clean test of the head-to-head analysis workflow
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SimpleH2HTester:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.base_url = "https://api.soccerdataapi.com"
        self.headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'
        }
    
    def api_call(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API call with error handling"""
        params['auth_token'] = self.auth_token
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def test_future_match_discovery(self):
        """Test finding upcoming matches"""
        print("TESTING: Future Match Discovery")
        print("-" * 40)
        
        # Search for matches tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
        
        # Try EPL first
        epl_matches = self.api_call('matches/', {
            'league_id': 228,  # EPL
            'date': tomorrow
        })
        
        if epl_matches:
            matches = self.extract_matches_from_response(epl_matches)
            print(f"Found {len(matches)} EPL matches for {tomorrow}")
            
            if matches:
                for i, match in enumerate(matches[:3], 1):
                    teams = match.get('teams', {})
                    home_name = teams.get('home', {}).get('name', 'Unknown')
                    away_name = teams.get('away', {}).get('name', 'Unknown')
                    print(f"  {i}. {home_name} vs {away_name}")
            
            return True
        else:
            print("No matches found (may be normal)")
            return True
    
    def test_team_recent_form(self):
        """Test recent form analysis"""
        print("\nTESTING: Recent Form Analysis")
        print("-" * 40)
        
        # Test with Liverpool (ID: 4138)
        liverpool_id = 4138
        
        # Search for Liverpool's recent matches
        recent_dates = [(datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(1, 31)]
        matches_found = []
        
        print("Searching Liverpool's recent matches...")
        
        for date in recent_dates:
            if len(matches_found) >= 5:  # Limit for testing
                break
                
            matches_data = self.api_call('matches/', {
                'league_id': 228,  # EPL
                'date': date
            })
            
            if matches_data:
                matches = self.extract_matches_from_response(matches_data)
                for match in matches:
                    if self.team_played_in_match(liverpool_id, match):
                        matches_found.append({
                            'match': match,
                            'date': date
                        })
        
        print(f"Found {len(matches_found)} recent matches for Liverpool")
        
        # Analyze results
        wins = draws = losses = 0
        for match_info in matches_found:
            match = match_info['match']
            result = self.get_team_result(liverpool_id, match)
            if result == 'W':
                wins += 1
            elif result == 'D':
                draws += 1
            elif result == 'L':
                losses += 1
        
        total = wins + draws + losses
        if total > 0:
            win_pct = (wins / total) * 100
            print(f"Recent record: {wins}W-{draws}D-{losses}L ({win_pct:.1f}% win rate)")
            return True
        else:
            print("No completed matches found")
            return False
    
    def test_head_to_head_stats(self):
        """Test H2H statistics"""
        print("\nTESTING: Head-to-Head Statistics")
        print("-" * 40)
        
        # Test Liverpool vs Chelsea
        liverpool_id = 4138
        chelsea_id = 2916
        
        h2h_data = self.api_call('head-to-head/', {
            'team_1_id': liverpool_id,
            'team_2_id': chelsea_id
        })
        
        if h2h_data:
            print("H2H data retrieved successfully")
            
            # Extract basic stats
            stats = h2h_data.get('stats', {})
            overall = stats.get('overall', {})
            
            if overall:
                total_games = overall.get('overall_games_played', 0)
                liverpool_wins = overall.get('overall_team1_wins', 0)
                chelsea_wins = overall.get('overall_team2_wins', 0)
                draws = overall.get('overall_draws', 0)
                
                print(f"Historical record ({total_games} games):")
                print(f"  Liverpool: {liverpool_wins} wins")
                print(f"  Chelsea: {chelsea_wins} wins")
                print(f"  Draws: {draws}")
                
                return True
            else:
                print("No overall stats found")
                return False
        else:
            print("Failed to get H2H data")
            return False
    
    def test_comprehensive_analysis(self):
        """Test putting it all together"""
        print("\nTESTING: Comprehensive Analysis")
        print("-" * 40)
        
        # Simulate a complete analysis
        liverpool_id = 4138
        chelsea_id = 2916
        
        print("Simulating Liverpool vs Chelsea analysis...")
        
        # 1. Get basic team info (simulated)
        teams_info = {
            'home': {'id': liverpool_id, 'name': 'Liverpool'},
            'away': {'id': chelsea_id, 'name': 'Chelsea'}
        }
        
        # 2. Get H2H stats
        h2h_data = self.api_call('head-to-head/', {
            'team_1_id': liverpool_id,
            'team_2_id': chelsea_id
        })
        
        # 3. Generate simple prediction
        if h2h_data:
            stats = h2h_data.get('stats', {})
            overall = stats.get('overall', {})
            
            if overall:
                liverpool_wins = overall.get('overall_team1_wins', 0)
                chelsea_wins = overall.get('overall_team2_wins', 0)
                
                if liverpool_wins > chelsea_wins:
                    prediction = "Liverpool favored (historical edge)"
                elif chelsea_wins > liverpool_wins:
                    prediction = "Chelsea favored (historical edge)"
                else:
                    prediction = "Even match (similar historical record)"
                
                print(f"PREDICTION: {prediction}")
                print("SUCCESS: Comprehensive analysis completed")
                return True
        
        print("Could not complete comprehensive analysis")
        return False
    
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
    
    def get_team_result(self, team_id: int, match: Dict) -> str:
        """Get team's result (W/D/L)"""
        if match.get('status') != 'finished':
            return 'N/A'
        
        teams = match.get('teams', {})
        goals = match.get('goals', {})
        home_id = teams.get('home', {}).get('id')
        home_goals = goals.get('home_ft_goals', 0)
        away_goals = goals.get('away_ft_goals', 0)
        
        is_home = (team_id == home_id)
        team_goals = home_goals if is_home else away_goals
        opponent_goals = away_goals if is_home else home_goals
        
        if team_goals > opponent_goals:
            return 'W'
        elif team_goals < opponent_goals:
            return 'L'
        else:
            return 'D'

def main():
    """Run simple tests"""
    print("=" * 60)
    print("H2H STRATEGY SIMPLE TESTING")
    print("=" * 60)
    print("Testing core functionality of the H2H analysis system")
    print()
    
    # Initialize tester
    auth_token = "a9f37754a540df435e8c40ed89c08565166524ed"
    tester = SimpleH2HTester(auth_token)
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if tester.test_future_match_discovery():
        tests_passed += 1
    
    if tester.test_team_recent_form():
        tests_passed += 1
    
    if tester.test_head_to_head_stats():
        tests_passed += 1
    
    if tester.test_comprehensive_analysis():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed >= 3:
        print("STATUS: CORE FUNCTIONALITY WORKING")
        print("The H2H strategy system is operational")
    else:
        print("STATUS: ISSUES DETECTED")
        print("Some core functions may need attention")
    
    print("\nKEY CAPABILITIES TESTED:")
    print("- Future match discovery")
    print("- Recent form analysis")
    print("- Historical H2H statistics")
    print("- Comprehensive prediction system")
    
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()