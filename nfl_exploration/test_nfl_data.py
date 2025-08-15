#!/usr/bin/env python3
"""
NFL Data Exploration - Local Testing
Test nfl_data_py endpoints to evaluate data quality and usefulness
"""

import nfl_data_py as nfl
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

class NFLDataExplorer:
    """Test NFL data endpoints locally"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "data_samples": {},
            "evaluation": {}
        }
    
    def test_schedule_data(self):
        """Test NFL schedule data"""
        print("=" * 60)
        print("TEST 1: NFL Schedule Data")
        print("=" * 60)
        
        try:
            # Get current season schedule
            current_year = datetime.now().year
            if datetime.now().month < 9:  # Before NFL season starts
                season_year = current_year
            else:
                season_year = current_year
            
            print(f"Getting {season_year} NFL schedule...")
            schedule = nfl.import_schedules([season_year])
            
            print(f"Schedule shape: {schedule.shape}")
            print(f"Columns: {list(schedule.columns)}")
            
            # Show recent/upcoming games
            print("\nRecent/Upcoming Games (First 5):")
            recent_games = schedule.head()
            for idx, game in recent_games.iterrows():
                home_team = game.get('home_team', 'Unknown')
                away_team = game.get('away_team', 'Unknown')
                game_date = game.get('gameday', 'Unknown')
                week = game.get('week', 'Unknown')
                print(f"  Week {week}: {away_team} @ {home_team} ({game_date})")
            
            self.results["tests"]["schedule"] = {
                "success": True,
                "rows": len(schedule),
                "columns": len(schedule.columns),
                "sample_data": recent_games.to_dict('records')[:3]
            }
            
            return schedule
            
        except Exception as e:
            print(f"[!] Schedule test failed: {e}")
            self.results["tests"]["schedule"] = {"success": False, "error": str(e)}
            return None
    
    def test_team_data(self):
        """Test NFL team data"""
        print("\n" + "=" * 60)
        print("TEST 2: NFL Team Data")
        print("=" * 60)
        
        try:
            # Get team info
            teams = nfl.import_team_desc()
            
            print(f"Teams data shape: {teams.shape}")
            print(f"Columns: {list(teams.columns)}")
            
            # Show some teams
            print("\nNFL Teams (First 10):")
            for idx, team in teams.head(10).iterrows():
                team_name = team.get('team_name', 'Unknown')
                team_abbr = team.get('team_abbr', 'Unknown')
                division = team.get('team_division', 'Unknown')
                print(f"  {team_abbr}: {team_name} ({division})")
            
            self.results["tests"]["teams"] = {
                "success": True,
                "total_teams": len(teams),
                "columns": len(teams.columns),
                "sample_data": teams.head(5).to_dict('records')
            }
            
            return teams
            
        except Exception as e:
            print(f"[!] Team test failed: {e}")
            self.results["tests"]["teams"] = {"success": False, "error": str(e)}
            return None
    
    def test_player_stats(self):
        """Test NFL player statistics"""
        print("\n" + "=" * 60)
        print("TEST 3: NFL Player Statistics")
        print("=" * 60)
        
        try:
            # Get recent season player stats
            current_year = datetime.now().year
            stats_year = current_year - 1 if datetime.now().month < 9 else current_year
            
            print(f"Getting {stats_year} player stats...")
            
            # Weekly stats (passing)
            weekly_passing = nfl.import_weekly_data([stats_year], columns=['player_name', 'recent_team', 'week', 'passing_yards', 'passing_tds', 'interceptions'])
            
            print(f"Weekly passing stats shape: {weekly_passing.shape}")
            
            # Show top passers
            if not weekly_passing.empty:
                top_passers = weekly_passing.groupby('player_name')['passing_yards'].sum().sort_values(ascending=False).head(10)
                print("\nTop 10 Passers by Total Yards:")
                for player, yards in top_passers.items():
                    print(f"  {player}: {yards:,} yards")
            
            self.results["tests"]["player_stats"] = {
                "success": True,
                "rows": len(weekly_passing),
                "columns": len(weekly_passing.columns),
                "sample_data": weekly_passing.head(3).to_dict('records') if not weekly_passing.empty else []
            }
            
            return weekly_passing
            
        except Exception as e:
            print(f"[!] Player stats test failed: {e}")
            self.results["tests"]["player_stats"] = {"success": False, "error": str(e)}
            return None
    
    def test_pbp_data(self):
        """Test play-by-play data (limited sample)"""
        print("\n" + "=" * 60)
        print("TEST 4: Play-by-Play Data (Sample)")
        print("=" * 60)
        
        try:
            # Get small sample of play-by-play data
            current_year = datetime.now().year
            pbp_year = current_year - 1 if datetime.now().month < 9 else current_year
            
            print(f"Getting sample {pbp_year} play-by-play data...")
            print("NOTE: This may take a moment - PBP data is large")
            
            # Import small sample 
            pbp = nfl.import_pbp_data([pbp_year], columns=['game_id', 'week', 'home_team', 'away_team', 'play_type', 'yards_gained'])
            
            print(f"Play-by-play shape: {pbp.shape}")
            
            if not pbp.empty:
                # Show play types
                play_types = pbp['play_type'].value_counts().head(10)
                print("\nTop Play Types:")
                for play_type, count in play_types.items():
                    print(f"  {play_type}: {count:,} plays")
            
            self.results["tests"]["pbp"] = {
                "success": True,
                "rows": len(pbp),
                "columns": len(pbp.columns),
                "play_types": play_types.to_dict() if not pbp.empty else {}
            }
            
            return pbp
            
        except Exception as e:
            print(f"[!] PBP test failed: {e}")
            self.results["tests"]["pbp"] = {"success": False, "error": str(e)}
            return None
    
    def test_injury_data(self):
        """Test injury report data"""
        print("\n" + "=" * 60)
        print("TEST 5: Injury Report Data")
        print("=" * 60)
        
        try:
            # Get current injury reports
            injuries = nfl.import_injuries([2024])  # Use 2024 as example
            
            print(f"Injury data shape: {injuries.shape}")
            print(f"Columns: {list(injuries.columns)}")
            
            if not injuries.empty:
                # Show recent injuries
                print("\nRecent Injury Reports (First 10):")
                for idx, injury in injuries.head(10).iterrows():
                    player = injury.get('full_name', 'Unknown')
                    team = injury.get('team', 'Unknown')
                    status = injury.get('report_status', 'Unknown')
                    body_part = injury.get('report_primary_injury', 'Unknown')
                    print(f"  {player} ({team}): {status} - {body_part}")
            
            self.results["tests"]["injuries"] = {
                "success": True,
                "rows": len(injuries),
                "columns": len(injuries.columns),
                "sample_data": injuries.head(3).to_dict('records') if not injuries.empty else []
            }
            
            return injuries
            
        except Exception as e:
            print(f"[!] Injury test failed: {e}")
            self.results["tests"]["injuries"] = {"success": False, "error": str(e)}
            return None
    
    def evaluate_data_quality(self):
        """Evaluate overall data quality and usefulness"""
        print("\n" + "=" * 60)
        print("DATA QUALITY EVALUATION")
        print("=" * 60)
        
        evaluation = {
            "overall_score": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendation": ""
        }
        
        successful_tests = [test for test in self.results["tests"].values() if test.get("success", False)]
        total_tests = len(self.results["tests"])
        success_rate = len(successful_tests) / total_tests if total_tests > 0 else 0
        
        print(f"Success Rate: {len(successful_tests)}/{total_tests} tests passed ({success_rate:.1%})")
        
        # Evaluate each test
        for test_name, test_result in self.results["tests"].items():
            if test_result.get("success", False):
                print(f"[+] {test_name}: PASSED")
                
                # Check data richness
                rows = test_result.get("rows", 0)
                columns = test_result.get("columns", 0)
                
                if rows > 100:
                    evaluation["strengths"].append(f"{test_name}: Rich data ({rows:,} rows)")
                elif rows > 0:
                    evaluation["strengths"].append(f"{test_name}: Some data ({rows} rows)")
                
                if columns > 10:
                    evaluation["strengths"].append(f"{test_name}: Many data points ({columns} columns)")
                    
            else:
                print(f"[-] {test_name}: FAILED - {test_result.get('error', 'Unknown error')}")
                evaluation["weaknesses"].append(f"{test_name}: Failed to load")
        
        # Overall assessment
        if success_rate >= 0.8:
            evaluation["overall_score"] = 9
            evaluation["recommendation"] = "EXCELLENT: Highly recommend building NFL MCP"
        elif success_rate >= 0.6:
            evaluation["overall_score"] = 7
            evaluation["recommendation"] = "GOOD: Recommend building NFL MCP with focus on working endpoints"
        elif success_rate >= 0.4:
            evaluation["overall_score"] = 5
            evaluation["recommendation"] = "MODERATE: Consider building limited NFL MCP"
        else:
            evaluation["overall_score"] = 3
            evaluation["recommendation"] = "POOR: Do not recommend NFL MCP at this time"
        
        print(f"\n[*] Overall Score: {evaluation['overall_score']}/10")
        print(f"[*] Recommendation: {evaluation['recommendation']}")
        
        if evaluation["strengths"]:
            print(f"\n[+] Strengths:")
            for strength in evaluation["strengths"]:
                print(f"  - {strength}")
        
        if evaluation["weaknesses"]:
            print(f"\n[-] Weaknesses:")
            for weakness in evaluation["weaknesses"]:
                print(f"  - {weakness}")
        
        self.results["evaluation"] = evaluation
        
        return evaluation
    
    def export_results(self):
        """Export test results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nfl_data_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n[+] Results exported to: {filename}")
            return filename
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
            return None

def main():
    """Run NFL data exploration"""
    print("NFL Data Exploration - Local Testing")
    print("Testing nfl_data_py package capabilities")
    print("=" * 60)
    
    explorer = NFLDataExplorer()
    
    # Run all tests
    explorer.test_schedule_data()
    explorer.test_team_data()
    explorer.test_player_stats()
    explorer.test_pbp_data()
    explorer.test_injury_data()
    
    # Evaluate results
    evaluation = explorer.evaluate_data_quality()
    
    # Export results
    explorer.export_results()
    
    print("\n" + "=" * 60)
    print("NFL DATA EXPLORATION COMPLETE")
    print("=" * 60)
    print(f"Final Assessment: {evaluation['recommendation']}")

if __name__ == "__main__":
    main()