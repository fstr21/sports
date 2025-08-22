#!/usr/bin/env python3
"""
Enhanced Team Form - Live MLB API Integration

This tool fetches REAL recent form data using the working MLB API endpoints
discovered in our investigation. It calculates:
- Last 10 games record
- Home/Away recent splits  
- Current streak with game details

Ready for integration into MCP server and Discord bot.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import httpx

class EnhancedTeamFormLive:
    """Get real recent form data from MLB APIs"""
    
    def __init__(self):
        self.mlb_api_base = "https://statsapi.mlb.com/api/v1"
        self.client = None
        
        # Team ID mapping for testing
        self.team_mapping = {
            115: "Colorado Rockies",
            134: "Pittsburgh Pirates", 
            147: "New York Yankees",
            119: "Los Angeles Dodgers"
        }
    
    async def init_client(self):
        """Initialize HTTP client"""
        if not self.client:
            self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_team_recent_games(self, team_id: int, days_back: int = 20) -> Dict[str, Any]:
        """Get recent games for a team using MLB Schedule API"""
        await self.init_client()
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        url = f"{self.mlb_api_base}/schedule"
        params = {
            "teamId": team_id,
            "sportId": 1,
            "hydrate": "team,linescore",
            "startDate": start_date,
            "endDate": end_date
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting recent games: {e}")
            return {}
    
    async def get_team_last_ten_record(self, team_id: int) -> Dict[str, Any]:
        """Get last 10 games record using MLB record splits API"""
        await self.init_client()
        
        url = f"{self.mlb_api_base}/teams/{team_id}"
        params = {
            "hydrate": "record(splitType=lastTen)"
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting last ten record: {e}")
            return {}
    
    def calculate_recent_form_from_games(self, games_data: Dict[str, Any], team_id: int) -> Dict[str, Any]:
        """Calculate recent form statistics from games data"""
        if not games_data.get("dates"):
            return {
                "last_10": "0-0",
                "home_recent": "0-0", 
                "away_recent": "0-0",
                "recent_games": 0
            }
        
        # Collect all completed games
        all_games = []
        for date_entry in games_data["dates"]:
            for game in date_entry.get("games", []):
                if game.get("status", {}).get("detailedState") == "Final":
                    all_games.append(game)
        
        # Sort by date (most recent last)
        all_games.sort(key=lambda g: g.get("gameDate", ""))
        
        # Take last 10 completed games
        recent_games = all_games[-10:] if len(all_games) >= 10 else all_games
        
        # Calculate records
        wins = losses = 0
        home_wins = home_losses = 0
        away_wins = away_losses = 0
        
        game_details = []
        
        for game in recent_games:
            teams = game.get("teams", {})
            home_team_id = teams.get("home", {}).get("team", {}).get("id")
            away_team_id = teams.get("away", {}).get("team", {}).get("id")
            
            home_score = teams.get("home", {}).get("score", 0)
            away_score = teams.get("away", {}).get("score", 0)
            
            game_date = game.get("gameDate", "")[:10]  # YYYY-MM-DD
            
            if team_id == home_team_id:
                # Team played at home
                opponent = teams.get("away", {}).get("team", {}).get("name", "Unknown")
                is_home = True
                
                if home_score > away_score:
                    wins += 1
                    home_wins += 1
                    result = "W"
                else:
                    losses += 1
                    home_losses += 1
                    result = "L"
                    
            elif team_id == away_team_id:
                # Team played away
                opponent = teams.get("home", {}).get("team", {}).get("name", "Unknown")
                is_home = False
                
                if away_score > home_score:
                    wins += 1
                    away_wins += 1
                    result = "W"
                else:
                    losses += 1
                    away_losses += 1
                    result = "L"
            else:
                continue  # Skip games this team wasn't in
            
            game_details.append({
                "date": game_date,
                "opponent": opponent,
                "home": is_home,
                "result": result,
                "score": f"{home_score}-{away_score}" if is_home else f"{away_score}-{home_score}"
            })
        
        return {
            "last_10": f"{wins}-{losses}",
            "home_recent": f"{home_wins}-{home_losses}",
            "away_recent": f"{away_wins}-{away_losses}",
            "recent_games": len(recent_games),
            "game_details": game_details
        }
    
    def determine_current_streak(self, game_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine current winning/losing streak from game details"""
        if not game_details:
            return {
                "type": "none",
                "count": 0,
                "display": "No recent games",
                "emoji": "⚪"
            }
        
        # Start from most recent game
        recent_games = list(reversed(game_details))
        current_result = recent_games[0]["result"]
        streak_count = 1
        
        # Count consecutive games with same result
        for game in recent_games[1:]:
            if game["result"] == current_result:
                streak_count += 1
            else:
                break
        
        if current_result == "W":
            streak_type = "winning"
            emoji = "🔥" if streak_count >= 3 else "⚡"
            display = f"{emoji} {streak_count}-game winning streak"
        else:
            streak_type = "losing"
            emoji = "❄️" if streak_count >= 3 else "📉"
            display = f"{emoji} {streak_count}-game losing streak"
        
        return {
            "type": streak_type,
            "count": streak_count,
            "display": display,
            "emoji": emoji
        }
    
    async def get_enhanced_team_form(self, team_id: int) -> Dict[str, Any]:
        """Get comprehensive enhanced team form data"""
        team_name = self.team_mapping.get(team_id, f"Team {team_id}")
        
        print(f"\n🔍 Getting enhanced form for {team_name} (ID: {team_id})")
        
        # Get recent games data
        games_data = await self.get_team_recent_games(team_id)
        
        if not games_data:
            return {
                "error": "Could not fetch recent games data",
                "team_id": team_id,
                "team_name": team_name
            }
        
        # Calculate recent form
        recent_form = self.calculate_recent_form_from_games(games_data, team_id)
        
        # Determine current streak
        streak_info = self.determine_current_streak(recent_form.get("game_details", []))
        
        # Also try to get the official last 10 record for comparison
        last_ten_data = await self.get_team_last_ten_record(team_id)
        official_last_ten = None
        
        if last_ten_data.get("teams"):
            team_data = last_ten_data["teams"][0]
            if "record" in team_data and "records" in team_data["record"]:
                for record in team_data["record"]["records"]:
                    if record.get("type") == "lastTen":
                        wins = record.get("wins", 0)
                        losses = record.get("losses", 0)
                        official_last_ten = f"{wins}-{losses}"
        
        return {
            "team_id": team_id,
            "team_name": team_name,
            "timestamp": datetime.now().isoformat(),
            "recent_form": {
                "last_10_calculated": recent_form["last_10"],
                "last_10_official": official_last_ten,
                "home_recent": recent_form["home_recent"],
                "away_recent": recent_form["away_recent"],
                "recent_games_analyzed": recent_form["recent_games"]
            },
            "streak_info": streak_info,
            "game_details": recent_form["game_details"][-5:],  # Last 5 games for display
            "data_source": "MLB Stats API - Live",
            "success": True
        }
    
    async def test_multiple_teams(self):
        """Test enhanced form for multiple teams"""
        print("🏟️  ENHANCED TEAM FORM - LIVE DATA TEST")
        print("=" * 60)
        
        results = {}
        
        for team_id, team_name in self.team_mapping.items():
            try:
                form_data = await self.get_enhanced_team_form(team_id)
                results[team_id] = form_data
                
                if form_data.get("success"):
                    recent = form_data["recent_form"]
                    streak = form_data["streak_info"]
                    
                    print(f"\n✅ {team_name}:")
                    print(f"   Last 10 (calc): {recent['last_10_calculated']}")
                    print(f"   Last 10 (official): {recent['last_10_official']}")
                    print(f"   Home recent: {recent['home_recent']}")
                    print(f"   Away recent: {recent['away_recent']}")
                    print(f"   Current streak: {streak['display']}")
                    
                    # Show recent games
                    print(f"   Recent games:")
                    for game in form_data["game_details"][-3:]:
                        venue = "vs" if game["home"] else "@"
                        print(f"     {game['date']}: {game['result']} {venue} {game['opponent']} ({game['score']})")
                else:
                    print(f"\n❌ {team_name}: {form_data.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"\n❌ {team_name}: Error - {e}")
                results[team_id] = {"error": str(e), "team_id": team_id}
        
        return results
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()

async def main():
    """Main test function"""
    enhancer = EnhancedTeamFormLive()
    
    try:
        results = await enhancer.test_multiple_teams()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_team_form_live_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        print(f"\n🎯 CONCLUSION: Enhanced team form data is now available!")
        print("Next step: Integrate this into MCP server and Discord bot")
        
    finally:
        await enhancer.close()

if __name__ == "__main__":
    print("🚀 Testing Enhanced Team Form with Live MLB Data...")
    asyncio.run(main())