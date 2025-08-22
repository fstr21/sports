#!/usr/bin/env python3
"""
Recent Form Data Investigation

This script thoroughly investigates all possible sources for MLB recent form data:
1. Direct MLB Stats API calls
2. MLB Schedule API to calculate recent records
3. Team game logs for last 10 games
4. Alternative MLB data endpoints

Goal: Find a reliable way to get last 10 games, home/away splits, recent form
"""

import asyncio
import json
from datetime import datetime, timedelta
import httpx
from typing import Dict, List, Any

class RecentFormInvestigator:
    """Investigate all sources for MLB recent form data"""
    
    def __init__(self):
        # MLB Stats API (official)
        self.mlb_api_base = "https://statsapi.mlb.com/api/v1"
        
        # Our MCP server
        self.mcp_url = "https://mlbmcp-production.up.railway.app/mcp"
        
        # Test teams
        self.test_teams = {
            "Yankees": 147,
            "Dodgers": 119,
            "Rockies": 115,
            "Pirates": 134
        }
        
        self.client = None
    
    async def init_client(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def test_mlb_direct_api(self, team_id: int, team_name: str):
        """Test direct MLB Stats API for recent form data"""
        print(f"\n🔍 TESTING DIRECT MLB STATS API: {team_name}")
        print("-" * 60)
        
        endpoints_to_test = [
            f"/teams/{team_id}/stats?stats=season&season=2025",
            f"/teams/{team_id}?hydrate=record",
            f"/teams/{team_id}?hydrate=standings", 
            f"/teams/{team_id}?hydrate=record(splitType=lastTen)",
            f"/teams/{team_id}?hydrate=record(splitType=home),record(splitType=away)",
            f"/schedule?teamId={team_id}&startDate=2025-08-01&endDate=2025-08-22",
            f"/schedule?teamId={team_id}&sportId=1&hydrate=team,linescore&startDate=2025-08-10&endDate=2025-08-22",
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            url = f"{self.mlb_api_base}{endpoint}"
            print(f"\n🧪 Testing: {endpoint}")
            
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                
                print(f"✅ SUCCESS - Status: {response.status_code}")
                
                # Analyze response for useful data
                if "teams" in data and data["teams"]:
                    team_data = data["teams"][0]
                    
                    # Check for record data
                    if "record" in team_data:
                        record = team_data["record"]
                        print(f"📊 Record found: {record.get('wins', 'N/A')}-{record.get('losses', 'N/A')}")
                        
                        # Check for splits
                        if "records" in record:
                            records = record["records"]
                            print(f"📈 Record splits found: {len(records)} types")
                            for rec in records:
                                split_type = rec.get("type", "Unknown")
                                wins = rec.get("wins", 0)
                                losses = rec.get("losses", 0)
                                print(f"   {split_type}: {wins}-{losses}")
                
                elif "dates" in data:
                    # Schedule data
                    games = []
                    for date_entry in data["dates"]:
                        games.extend(date_entry.get("games", []))
                    
                    print(f"🎮 Games found: {len(games)} games")
                    
                    # Analyze recent games for wins/losses
                    if games:
                        recent_record = self.calculate_record_from_games(games, team_id)
                        print(f"📊 Calculated recent record: {recent_record}")
                
                # Store successful results
                results[endpoint] = {
                    "status": "success",
                    "data": data
                }
                
                # Show sample of data structure
                print(f"📄 Sample data keys: {list(data.keys())}")
                
            except Exception as e:
                print(f"❌ FAILED: {e}")
                results[endpoint] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results
    
    def calculate_record_from_games(self, games: List[Dict], team_id: int) -> Dict[str, Any]:
        """Calculate wins/losses from a list of games"""
        wins = 0
        losses = 0
        home_wins = 0
        home_losses = 0
        away_wins = 0
        away_losses = 0
        
        completed_games = [g for g in games if g.get("status", {}).get("detailedState") == "Final"]
        
        for game in completed_games[-10:]:  # Last 10 completed games
            teams = game.get("teams", {})
            home_team = teams.get("home", {}).get("team", {}).get("id")
            away_team = teams.get("away", {}).get("team", {}).get("id")
            
            home_score = teams.get("home", {}).get("score", 0)
            away_score = teams.get("away", {}).get("score", 0)
            
            if team_id == home_team:
                # Team played at home
                if home_score > away_score:
                    wins += 1
                    home_wins += 1
                else:
                    losses += 1
                    home_losses += 1
            elif team_id == away_team:
                # Team played away
                if away_score > home_score:
                    wins += 1
                    away_wins += 1
                else:
                    losses += 1
                    away_losses += 1
        
        return {
            "last_10": f"{wins}-{losses}",
            "home_recent": f"{home_wins}-{home_losses}",
            "away_recent": f"{away_wins}-{away_losses}",
            "total_games": len(completed_games)
        }
    
    async def test_mcp_schedule_method(self, team_id: int, team_name: str):
        """Test if we can get recent form by calling MCP schedule tools"""
        print(f"\n🔧 TESTING MCP SCHEDULE METHOD: {team_name}")
        print("-" * 60)
        
        # Try to get recent games through MCP schedule
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getMLBScheduleET",
                "arguments": {
                    "date": end_date,
                    "team_id": team_id
                }
            }
        }
        
        try:
            print(f"🧪 Calling getMLBScheduleET for team {team_id}")
            response = await self.client.post(self.mcp_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" not in result:
                print("✅ Schedule data retrieved successfully")
                schedule_data = result.get("result", {}).get("data", {})
                games = schedule_data.get("games", [])
                
                print(f"📅 Games on {end_date}: {len(games)}")
                
                # This might only give us today's games, but let's see
                for game in games:
                    home = game.get("home", {}).get("name", "Unknown")
                    away = game.get("away", {}).get("name", "Unknown")
                    status = game.get("status", "Unknown")
                    print(f"   {away} @ {home} - {status}")
                
                return schedule_data
            else:
                print(f"❌ MCP Schedule error: {result['error']}")
        
        except Exception as e:
            print(f"❌ MCP Schedule failed: {e}")
        
        return None
    
    async def test_alternative_apis(self, team_id: int, team_name: str):
        """Test alternative baseball data APIs"""
        print(f"\n🌐 TESTING ALTERNATIVE APIs: {team_name}")
        print("-" * 60)
        
        # Try ESPN API (sometimes has good recent data)
        espn_url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/{team_id}/schedule"
        
        try:
            print("🧪 Testing ESPN API...")
            response = await self.client.get(espn_url)
            response.raise_for_status()
            data = response.json()
            
            print("✅ ESPN API success")
            
            if "events" in data:
                events = data["events"]
                print(f"📅 ESPN events found: {len(events)}")
                
                # Look for recent completed games
                recent_games = [e for e in events if e.get("status", {}).get("type", {}).get("completed")]
                print(f"🎮 Recent completed games: {len(recent_games)}")
                
                return data
                
        except Exception as e:
            print(f"❌ ESPN API failed: {e}")
        
        return None
    
    async def comprehensive_investigation(self):
        """Run comprehensive investigation of all sources"""
        print("🏟️  MLB RECENT FORM COMPREHENSIVE INVESTIGATION")
        print("=" * 80)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        await self.init_client()
        
        all_results = {}
        
        # Test one team thoroughly  
        test_team = "Rockies"
        test_team_id = self.test_teams[test_team]
        
        print(f"\n🎯 COMPREHENSIVE TEST: {test_team} (ID: {test_team_id})")
        
        # 1. Direct MLB API
        mlb_results = await self.test_mlb_direct_api(test_team_id, test_team)
        all_results["mlb_direct"] = mlb_results
        
        # 2. MCP Schedule method
        mcp_schedule = await self.test_mcp_schedule_method(test_team_id, test_team)
        all_results["mcp_schedule"] = mcp_schedule
        
        # 3. Alternative APIs
        alt_results = await self.test_alternative_apis(test_team_id, test_team)
        all_results["alternative"] = alt_results
        
        # Analysis and recommendations
        await self.analyze_results(all_results)
        
        return all_results
    
    async def analyze_results(self, results: Dict[str, Any]):
        """Analyze all results and provide recommendations"""
        print(f"\n🎯 ANALYSIS & RECOMMENDATIONS")
        print("=" * 60)
        
        viable_sources = []
        
        # Check MLB direct API results
        if "mlb_direct" in results:
            mlb_results = results["mlb_direct"]
            successful_endpoints = [ep for ep, res in mlb_results.items() if res.get("status") == "success"]
            
            print(f"📊 MLB Direct API: {len(successful_endpoints)} successful endpoints")
            
            # Look for endpoints that might have recent form data
            promising_endpoints = []
            for endpoint in successful_endpoints:
                if "schedule" in endpoint:
                    promising_endpoints.append(endpoint)
                elif "lastTen" in endpoint:
                    promising_endpoints.append(endpoint)
                elif "home" in endpoint or "away" in endpoint:
                    promising_endpoints.append(endpoint)
            
            if promising_endpoints:
                print(f"✅ Promising MLB endpoints: {len(promising_endpoints)}")
                for ep in promising_endpoints:
                    print(f"   - {ep}")
                viable_sources.append("MLB Direct API")
        
        # Check other sources
        if results.get("mcp_schedule"):
            print(f"✅ MCP Schedule method: Available")
            viable_sources.append("MCP Schedule")
        
        if results.get("alternative"):
            print(f"✅ Alternative APIs: Available")
            viable_sources.append("Alternative APIs")
        
        # Final recommendation
        print(f"\n💡 FINAL RECOMMENDATION:")
        print("-" * 40)
        
        if viable_sources:
            print(f"✅ {len(viable_sources)} viable sources found for recent form data!")
            print(f"📋 Best approach: {viable_sources[0]}")
            
            if "MLB Direct API" in viable_sources:
                print("\n🔧 Implementation Plan:")
                print("1. Use MLB Schedule API to get last 20 games")
                print("2. Filter for completed games")
                print("3. Calculate last 10 record from game results")
                print("4. Calculate home/away splits from venue data")
                print("5. Add this as enhanced team form to MCP server")
        else:
            print("❌ No viable sources found for recent form data")
            print("💡 Recommendation: Stick with current basic team data")
        
        print(f"\n🏁 Investigation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()

async def main():
    """Main investigation function"""
    investigator = RecentFormInvestigator()
    
    try:
        results = await investigator.comprehensive_investigation()
        
        # Save results to file for analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\testing\\recent_form_investigation_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        
    finally:
        await investigator.close()

if __name__ == "__main__":
    print("🚀 Starting Recent Form Investigation...")
    asyncio.run(main())