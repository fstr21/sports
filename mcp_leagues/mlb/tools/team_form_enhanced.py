#!/usr/bin/env python3
"""
Enhanced MLB Team Form Tool - Comprehensive Team Form Analysis

Gets enhanced team form data by combining standings data with recent games
to calculate actual home/away records and last 10 games performance.

Usage:
    python team_form_enhanced.py
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

# Configuration
TARGET_TEAMS = [135, 137]  # Padres and Giants
TARGET_SEASON = 2025
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class EnhancedTeamFormAnalyzer:
    """Enhanced MLB team form analyzer with calculated records"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.form_data = {
            "teams": TARGET_TEAMS,
            "season": TARGET_SEASON,
            "timestamp": datetime.now().isoformat(),
            "team_forms": {},
            "recent_games": {},
            "calculated_records": {},
            "summary": {}
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call MLB MCP tool"""
        if arguments is None:
            arguments = {}
            
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.client.post(MLB_MCP_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ MCP Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_team_name(self, team_id: int) -> str:
        """Get team name from ID"""
        team_names = {
            135: "San Diego Padres",
            137: "San Francisco Giants"
        }
        return team_names.get(team_id, f"Team {team_id}")
    
    async def get_recent_games_for_team(self, team_id: int, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent games for a team by checking multiple dates"""
        team_name = self.get_team_name(team_id)
        print(f"\n🔍 Fetching recent games for {team_name} (last {days_back} days)...")
        
        recent_games = []
        current_date = datetime.now()
        
        # Check last 30 days for games
        for i in range(days_back):
            check_date = current_date - timedelta(days=i)
            date_str = check_date.strftime("%Y-%m-%d")
            
            # Get schedule for this date
            result = await self.call_mcp_tool("getMLBScheduleET", {"date": date_str})
            
            if result and result.get("ok"):
                data = result.get("data", {})
                games = data.get("games", [])
                
                # Find games involving our team
                for game in games:
                    home_team = game.get("home", {})
                    away_team = game.get("away", {})
                    
                    if (home_team.get("teamId") == team_id or 
                        away_team.get("teamId") == team_id):
                        
                        # Only include completed games
                        status = game.get("status", "")
                        if status and "Final" in status:
                            recent_games.append({
                                "date": date_str,
                                "game_pk": game.get("gamePk"),
                                "home_team_id": home_team.get("teamId"),
                                "away_team_id": away_team.get("teamId"),
                                "home_team_name": home_team.get("name"),
                                "away_team_name": away_team.get("name"),
                                "status": status,
                                "is_home": home_team.get("teamId") == team_id
                            })
            
            # Add small delay to be respectful to API
            await asyncio.sleep(0.1)
        
        # Sort by date (most recent first)
        recent_games.sort(key=lambda x: x["date"], reverse=True)
        
        print(f"✅ Found {len(recent_games)} completed games for {team_name}")
        return recent_games
    
    def analyze_recent_games(self, games: List[Dict[str, Any]], team_id: int) -> Dict[str, Any]:
        """Analyze recent games to calculate records"""
        if not games:
            return {
                "last_10": "0-0",
                "home_record": "0-0", 
                "away_record": "0-0",
                "total_games": 0,
                "home_games": 0,
                "away_games": 0
            }
        
        # For this analysis, we'll assume Final games without score details
        # In a real implementation, you'd need game details to determine wins/losses
        
        last_10_games = games[:10]
        home_games = [g for g in games if g["is_home"]]
        away_games = [g for g in games if not g["is_home"]]
        
        # Since we don't have win/loss data from the schedule endpoint,
        # we'll show game counts and note the limitation
        
        return {
            "last_10": f"Data available for {len(last_10_games)} games",
            "home_record": f"{len(home_games)} home games played",
            "away_record": f"{len(away_games)} away games played", 
            "total_games": len(games),
            "home_games": len(home_games),
            "away_games": len(away_games),
            "recent_game_details": last_10_games[:5]  # Last 5 games for display
        }
    
    async def get_enhanced_team_form(self, team_id: int) -> Dict[str, Any]:
        """Get enhanced form data combining standings and recent games"""
        team_name = self.get_team_name(team_id)
        print(f"\n📊 Getting enhanced form data for {team_name} (ID: {team_id})...")
        
        # Get basic form from standings
        form_result = await self.call_mcp_tool("getMLBTeamForm", {
            "team_id": team_id,
            "season": TARGET_SEASON
        })
        
        if not form_result or not form_result.get("ok"):
            print(f"❌ Failed to get form data for {team_name}")
            return {}
        
        # Get recent games to enhance the data
        recent_games = await self.get_recent_games_for_team(team_id, days_back=20)
        
        # Analyze recent games
        recent_analysis = self.analyze_recent_games(recent_games, team_id)
        
        # Combine data
        form_data = form_result.get("data", {})
        basic_form = form_data.get("form", {})
        
        enhanced_form = {
            "team_id": team_id,
            "team_name": form_data.get("team_name", team_name),
            "basic_record": {
                "wins": basic_form.get("wins", 0),
                "losses": basic_form.get("losses", 0),
                "win_percentage": basic_form.get("win_percentage", "N/A"),
                "games_back": basic_form.get("games_back", "N/A"),
                "streak": basic_form.get("streak", "")
            },
            "enhanced_records": {
                "last_10_info": recent_analysis["last_10"],
                "home_games_info": recent_analysis["home_record"],
                "away_games_info": recent_analysis["away_record"],
                "total_recent_games": recent_analysis["total_games"],
                "home_games_count": recent_analysis["home_games"],
                "away_games_count": recent_analysis["away_games"]
            },
            "recent_game_sample": recent_analysis.get("recent_game_details", []),
            "api_limitation_note": "Win/Loss details require game-level analysis beyond current scope"
        }
        
        return enhanced_form
    
    async def analyze_enhanced_forms(self):
        """Analyze enhanced form for both teams"""
        print("📊 ENHANCED MLB TEAM FORM ANALYZER")
        print("=" * 60)
        print(f"🏟️  Teams: {[self.get_team_name(tid) for tid in TARGET_TEAMS]}")
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print(f"📝 Note: Enhanced with recent game analysis")
        print("=" * 60)
        
        enhanced_forms = {}
        
        # Get enhanced form for each team
        for team_id in TARGET_TEAMS:
            form_data = await self.get_enhanced_team_form(team_id)
            if form_data:
                enhanced_forms[team_id] = form_data
        
        if not enhanced_forms:
            print("\n❌ No enhanced form data retrieved")
            await self.save_results()
            return
        
        # Display enhanced analysis
        print(f"\n📈 ENHANCED TEAM FORM ANALYSIS")
        print("=" * 80)
        
        for team_id, team_data in enhanced_forms.items():
            self.display_enhanced_form(team_data)
        
        # Compare teams
        if len(enhanced_forms) == 2:
            print(f"\n⚖️  ENHANCED TEAM COMPARISON")
            print("=" * 50)
            self.compare_enhanced_forms(list(enhanced_forms.values()))
        
        # Store data
        self.form_data["team_forms"] = enhanced_forms
        
        # Generate summary
        self.form_data["summary"] = {
            "teams_analyzed": len(enhanced_forms),
            "total_recent_games": sum(data["enhanced_records"]["total_recent_games"] for data in enhanced_forms.values()),
            "api_enhancement": "Combined standings data with recent game schedules for better analysis"
        }
        
        await self.save_results()
    
    def display_enhanced_form(self, team_data: Dict[str, Any]):
        """Display enhanced form for a single team"""
        team_name = team_data["team_name"]
        basic = team_data["basic_record"]
        enhanced = team_data["enhanced_records"]
        recent_games = team_data["recent_game_sample"]
        
        print(f"\n🏟️  {team_name.upper()}")
        print("-" * 40)
        
        # Basic record (from standings)
        print(f"📊 Season Record: {basic['wins']}-{basic['losses']}")
        print(f"📈 Win Percentage: {basic['win_percentage']}")
        print(f"📏 Games Back: {basic['games_back']}")
        print(f"🔥 Current Streak: {self.format_streak(basic['streak'])}")
        
        # Enhanced recent data
        print(f"\n📈 Recent Activity Analysis:")
        print(f"🔟 Last 10 Games: {enhanced['last_10_info']}")
        print(f"🏠 Home Games: {enhanced['home_games_info']}")
        print(f"✈️  Away Games: {enhanced['away_games_info']}")
        print(f"📊 Total Recent Games Found: {enhanced['total_recent_games']}")
        
        # Recent games sample
        if recent_games:
            print(f"\n🎮 Recent Games Sample:")
            for i, game in enumerate(recent_games[:3], 1):
                location = "vs" if game["is_home"] else "@"
                opponent = game["away_team_name"] if game["is_home"] else game["home_team_name"]
                print(f"   {i}. {game['date']}: {location} {opponent} ({game['status']})")
        
        # Win rate calculation
        if basic['wins'] + basic['losses'] > 0:
            win_rate = (basic['wins'] / (basic['wins'] + basic['losses'])) * 100
            print(f"\n💯 Win Rate: {win_rate:.1f}%")
        
        # Data quality note
        print(f"\n📝 Note: {team_data['api_limitation_note']}")
    
    def format_streak(self, streak: str) -> str:
        """Format streak with emoji"""
        if not streak:
            return "Unknown"
        
        if streak.startswith('W'):
            count = streak[1:] if len(streak) > 1 else "1"
            return f"🔥 {count}-game winning streak"
        elif streak.startswith('L'):
            count = streak[1:] if len(streak) > 1 else "1"
            return f"❄️ {count}-game losing streak"
        else:
            return streak
    
    def compare_enhanced_forms(self, teams: List[Dict[str, Any]]):
        """Compare enhanced forms between teams"""
        if len(teams) != 2:
            return
        
        team1, team2 = teams
        
        # Record comparison
        wins1 = team1["basic_record"]["wins"]
        wins2 = team2["basic_record"]["wins"]
        
        print(f"🥇 Season Record Comparison:")
        print(f"   {team1['team_name']}: {wins1}-{team1['basic_record']['losses']}")
        print(f"   {team2['team_name']}: {wins2}-{team2['basic_record']['losses']}")
        
        if wins1 > wins2:
            print(f"   🏆 {team1['team_name']} leads by {wins1 - wins2} wins")
        elif wins2 > wins1:
            print(f"   🏆 {team2['team_name']} leads by {wins2 - wins1} wins")
        
        # Recent activity comparison
        recent1 = team1["enhanced_records"]["total_recent_games"]
        recent2 = team2["enhanced_records"]["total_recent_games"]
        
        print(f"\n📊 Recent Activity Comparison:")
        print(f"   {team1['team_name']}: {recent1} recent games analyzed")
        print(f"   {team2['team_name']}: {recent2} recent games analyzed")
        
        # Home/Away comparison
        home1 = team1["enhanced_records"]["home_games_count"]
        away1 = team1["enhanced_records"]["away_games_count"]
        home2 = team2["enhanced_records"]["home_games_count"]
        away2 = team2["enhanced_records"]["away_games_count"]
        
        print(f"\n🏟️  Home/Away Game Distribution:")
        print(f"   {team1['team_name']}: {home1} home, {away1} away")
        print(f"   {team2['team_name']}: {home2} home, {away2} away")
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\team_form_enhanced_teams{'-'.join(map(str, TARGET_TEAMS))}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.form_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 ENHANCED RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"🏟️  Teams: {self.form_data['summary'].get('teams_analyzed', 0)}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    enhanced_analyzer = EnhancedTeamFormAnalyzer()
    
    try:
        await enhanced_analyzer.analyze_enhanced_forms()
    finally:
        await enhanced_analyzer.close()

if __name__ == "__main__":
    asyncio.run(main())