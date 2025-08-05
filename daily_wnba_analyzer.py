#!/usr/bin/env python3
"""
Daily WNBA Game Analyzer
Efficiently processes all games for a given day with minimal API calls and token usage.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class WNBAAnalyzer:
    def __init__(self):
        self.base_url = "http://site.api.espn.com"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "ESPN-Research/1.0"
        }
        
    def get_daily_games(self, date: str = None) -> Dict:
        """Get all games for a specific date. If no date provided, uses today."""
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        url = f"{self.base_url}/apis/site/v2/sports/basketball/wnba/scoreboard"
        if date != datetime.now().strftime("%Y%m%d"):
            url += f"?dates={date}"
            
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {}
    
    def get_team_stats_batch(self, team_ids: List[str]) -> Dict[str, Dict]:
        """Get stats for multiple teams efficiently."""
        team_stats = {}
        
        for team_id in team_ids:
            url = f"{self.base_url}/apis/site/v2/sports/basketball/wnba/teams/{team_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                team_stats[team_id] = self.extract_key_stats(data)
                
        return team_stats
    
    def extract_key_stats(self, team_data: Dict) -> Dict:
        """Extract only the essential stats we need for analysis."""
        team = team_data.get('team', {})
        record_items = team.get('record', {}).get('items', [])
        
        # Find overall record
        overall_record = next((item for item in record_items if item.get('type') == 'total'), {})
        home_record = next((item for item in record_items if item.get('type') == 'home'), {})
        road_record = next((item for item in record_items if item.get('type') == 'road'), {})
        
        overall_stats = overall_record.get('stats', [])
        
        return {
            'name': team.get('displayName', ''),
            'abbreviation': team.get('abbreviation', ''),
            'overall_record': overall_record.get('summary', '0-0'),
            'home_record': home_record.get('summary', '0-0'),
            'road_record': road_record.get('summary', '0-0'),
            'win_pct': next((s['value'] for s in overall_stats if s['name'] == 'winPercent'), 0),
            'ppg': next((s['value'] for s in overall_stats if s['name'] == 'avgPointsFor'), 0),
            'opp_ppg': next((s['value'] for s in overall_stats if s['name'] == 'avgPointsAgainst'), 0),
            'point_diff': next((s['value'] for s in overall_stats if s['name'] == 'differential'), 0),
            'streak': next((s['value'] for s in overall_stats if s['name'] == 'streak'), 0),
        }
    
    def analyze_matchup(self, home_stats: Dict, away_stats: Dict, game_info: Dict) -> Dict:
        """Analyze a single matchup efficiently."""
        
        # Calculate key metrics
        home_advantage = 0.05  # Typical home court advantage
        talent_gap = home_stats['win_pct'] - away_stats['win_pct']
        offensive_edge = home_stats['ppg'] - away_stats['opp_ppg']
        defensive_edge = away_stats['ppg'] - home_stats['opp_ppg']
        
        # Simple scoring system
        home_score = 0
        away_score = 0
        
        # Record advantage
        if home_stats['win_pct'] > away_stats['win_pct']:
            home_score += 2
        else:
            away_score += 2
            
        # Home court
        home_score += 1
        
        # Point differential
        if home_stats['point_diff'] > away_stats['point_diff']:
            home_score += 1
        else:
            away_score += 1
            
        # Recent form (streak)
        if home_stats['streak'] > 0 and away_stats['streak'] <= 0:
            home_score += 1
        elif away_stats['streak'] > 0 and home_stats['streak'] <= 0:
            away_score += 1
            
        # Determine prediction
        predicted_winner = "home" if home_score > away_score else "away"
        confidence = abs(home_score - away_score) / 5.0  # Scale to 0-1
        
        return {
            'game_id': game_info.get('id'),
            'matchup': f"{away_stats['name']} @ {home_stats['name']}",
            'home_team': home_stats['name'],
            'away_team': away_stats['name'],
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'home_score_factors': home_score,
            'away_score_factors': away_score,
            'key_stats': {
                'home': {
                    'record': home_stats['overall_record'],
                    'ppg': round(home_stats['ppg'], 1),
                    'point_diff': round(home_stats['point_diff'], 1)
                },
                'away': {
                    'record': away_stats['overall_record'],
                    'ppg': round(away_stats['ppg'], 1),
                    'point_diff': round(away_stats['point_diff'], 1)
                }
            },
            'betting_recommendation': self.get_betting_rec(predicted_winner, confidence)
        }
    
    def get_betting_rec(self, predicted_winner: str, confidence: float) -> Dict:
        """Generate betting recommendations based on prediction confidence."""
        if confidence >= 0.8:
            strength = "STRONG"
            stars = 5
        elif confidence >= 0.6:
            strength = "MODERATE"
            stars = 4
        elif confidence >= 0.4:
            strength = "LEAN"
            stars = 3
        else:
            strength = "AVOID"
            stars = 2
            
        return {
            'strength': strength,
            'stars': stars,
            'primary_bet': f"{predicted_winner.title()} team moneyline",
            'confidence_pct': round(confidence * 100, 1)
        }
    
    def process_daily_games(self, date: str = None) -> List[Dict]:
        """Main function to process all games for a day."""
        print(f"🏀 Fetching WNBA games for {date or 'today'}...")
        
        # Get daily scoreboard (1 API call)
        scoreboard = self.get_daily_games(date)
        
        if not scoreboard.get('events'):
            print("No games found for this date.")
            return []
            
        games = scoreboard['events']
        print(f"Found {len(games)} games")
        
        # Extract unique team IDs
        team_ids = set()
        for game in games:
            for competitor in game.get('competitions', [{}])[0].get('competitors', []):
                team_ids.add(competitor['team']['id'])
        
        print(f"Fetching stats for {len(team_ids)} teams...")
        
        # Get team stats (N API calls where N = unique teams)
        team_stats = self.get_team_stats_batch(list(team_ids))
        
        # Analyze each game
        analyses = []
        for game in games:
            competition = game.get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) != 2:
                continue
                
            home_team = next((c for c in competitors if c['homeAway'] == 'home'), {})
            away_team = next((c for c in competitors if c['homeAway'] == 'away'), {})
            
            home_id = home_team.get('team', {}).get('id')
            away_id = away_team.get('team', {}).get('id')
            
            if home_id in team_stats and away_id in team_stats:
                analysis = self.analyze_matchup(
                    team_stats[home_id], 
                    team_stats[away_id], 
                    game
                )
                analyses.append(analysis)
        
        return analyses
    
    def generate_daily_report(self, analyses: List[Dict], date: str = None) -> str:
        """Generate a concise daily report."""
        report_date = date or datetime.now().strftime("%Y-%m-%d")
        
        report = f"""# WNBA Daily Analysis - {report_date}
*Generated automatically*

## Games Summary
Total Games: {len(analyses)}

"""
        
        for i, analysis in enumerate(analyses, 1):
            rec = analysis['betting_recommendation']
            stars = "⭐" * rec['stars']
            
            report += f"""### Game {i}: {analysis['matchup']}

**Prediction**: {analysis['predicted_winner'].title()} team wins
**Confidence**: {rec['confidence_pct']}% {stars}
**Recommendation**: {rec['strength']} - {rec['primary_bet']}

**Key Stats**:
- Home: {analysis['key_stats']['home']['record']} ({analysis['key_stats']['home']['ppg']} PPG, {analysis['key_stats']['home']['point_diff']:+.1f} diff)
- Away: {analysis['key_stats']['away']['record']} ({analysis['key_stats']['away']['ppg']} PPG, {analysis['key_stats']['away']['point_diff']:+.1f} diff)

---

"""
        
        return report

def main():
    """Run daily analysis."""
    analyzer = WNBAAnalyzer()
    
    # Process today's games
    analyses = analyzer.process_daily_games()
    
    if analyses:
        # Generate report
        report = analyzer.generate_daily_report(analyses)
        
        # Save to file
        filename = f"wnba_daily_analysis_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Analysis complete! Report saved to {filename}")
        print(f"📊 Processed {len(analyses)} games")
        
        # Print summary
        strong_bets = [a for a in analyses if a['betting_recommendation']['strength'] == 'STRONG']
        if strong_bets:
            print(f"🎯 {len(strong_bets)} STRONG betting opportunities found")
    else:
        print("No games to analyze today.")

if __name__ == "__main__":
    main()