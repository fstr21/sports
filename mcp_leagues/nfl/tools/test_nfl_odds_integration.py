#!/usr/bin/env python3
"""
Test #5: NFL + Odds MCP Integration
Test integration between NFL MCP and existing Odds MCP
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional

class NFLOddsIntegrationTester:
    """Test NFL + Odds MCP integration"""
    
    def __init__(self):
        # MCP server URLs
        self.nfl_mcp_url = "https://nflmcp-production.up.railway.app/mcp"
        self.odds_mcp_url = "https://odds-mcp-v2-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "nfl_server": self.nfl_mcp_url,
            "odds_server": self.odds_mcp_url,
            "tests": {},
            "integration_data": {},
            "summary": {}
        }
    
    async def call_mcp_tool(self, server_url: str, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call an MCP tool on specified server"""
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
        
        server_name = "NFL" if "nfl" in server_url else "Odds"
        print(f"[*] Calling {server_name} MCP: {tool_name}")
        if arguments:
            print(f"    Arguments: {arguments}")
        
        try:
            response = await self.client.post(server_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"[!] {server_name} MCP Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"[!] {server_name} MCP request failed: {e}")
            return None
    
    async def test_nfl_odds_integration(self):
        """Test NFL + Odds integration"""
        print("=" * 60)
        print("TEST #5: NFL + ODDS MCP INTEGRATION")
        print("=" * 60)
        print("Target: Week 1 NFL games with enhanced odds")
        
        # Test 5A: NFL Week 1 games
        print("\n--- Test 5A: Get NFL Week 1 Games ---")
        await self.test_nfl_week1()
        
        # Test 5B: NFL odds from Odds MCP
        print("\n--- Test 5B: Get NFL Odds from Odds MCP ---")
        await self.test_nfl_odds()
        
        # Test 5C: Specific game integration
        print("\n--- Test 5C: Specific Game Integration ---")
        await self.test_specific_game_integration()
        
        # Test 5D: Player props integration
        print("\n--- Test 5D: Player Props Integration ---")
        await self.test_player_props_integration()
        
        # Summary and export
        await self.generate_summary()
        await self.export_results()
    
    async def test_nfl_week1(self):
        """Test getting NFL Week 1 games"""
        print("Getting NFL Week 1 games:")
        
        result = await self.call_mcp_tool(
            self.nfl_mcp_url,
            "getNFLSchedule",
            {
                "season": 2025,
                "week": 1
            }
        )
        
        test_key = "nfl_week1"
        if result and result.get("ok"):
            games = result.get("data", {}).get("games", [])
            print(f"    [+] Found {len(games)} Week 1 games")
            
            # Show sample games
            if games:
                print(f"    Sample games:")
                for i, game in enumerate(games[:3]):
                    away = game.get("away_team", "?")
                    home = game.get("home_team", "?")
                    date = game.get("date", "Unknown")
                    print(f"      {i+1}. {away} @ {home} ({date})")
                    
                    # Show built-in odds if available
                    odds = game.get("betting_odds", {})
                    if odds.get("away_moneyline"):
                        away_ml = odds.get("away_moneyline")
                        home_ml = odds.get("home_moneyline")
                        spread = odds.get("spread_line", "N/A")
                        print(f"         Built-in odds: {away} {away_ml:+.0f}, {home} {home_ml:+.0f}, Spread: {spread}")
            
            self.results["tests"][test_key] = {
                "success": True,
                "games_found": len(games),
                "raw_data": result
            }
            
            # Store for integration
            self.results["integration_data"]["nfl_games"] = games
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No games returned"
            }
    
    async def test_nfl_odds(self):
        """Test getting NFL odds from Odds MCP"""
        print("Getting NFL odds from Odds MCP:")
        
        result = await self.call_mcp_tool(
            self.odds_mcp_url,
            "getOdds",
            {
                "sport": "americanfootball_nfl",
                "regions": "us",
                "markets": "h2h,spreads,totals"
            }
        )
        
        test_key = "nfl_odds"
        if result and result.get("ok"):
            data = result.get("data", {})
            odds_games = data.get("odds", [])
            print(f"    [+] Found {len(odds_games)} NFL games with odds")
            
            # Show sample odds
            if odds_games:
                print(f"    Sample odds:")
                for i, odds_game in enumerate(odds_games[:3]):
                    home_team = odds_game.get("home_team", "Unknown")
                    away_team = odds_game.get("away_team", "Unknown")
                    commence_time = odds_game.get("commence_time", "Unknown")
                    print(f"      {i+1}. {away_team} @ {home_team} ({commence_time})")
                    
                    # Show bookmaker odds
                    bookmakers = odds_game.get("bookmakers", [])
                    if bookmakers:
                        sample_book = bookmakers[0]
                        book_name = sample_book.get("title", "Unknown")
                        print(f"         {book_name} odds available")
            
            self.results["tests"][test_key] = {
                "success": True,
                "odds_games_found": len(odds_games),
                "raw_data": result
            }
            
            # Store for integration
            self.results["integration_data"]["odds_games"] = odds_games
        else:
            self.results["tests"][test_key] = {
                "success": False,
                "error": "No odds returned"
            }
    
    async def test_specific_game_integration(self):
        """Test integrating data for a specific game"""
        print("Testing specific game integration:")
        
        # Get stored data
        nfl_games = self.results["integration_data"].get("nfl_games", [])
        odds_games = self.results["integration_data"].get("odds_games", [])
        
        if not nfl_games or not odds_games:
            print("    [!] Missing NFL or odds data for integration")
            self.results["tests"]["game_integration"] = {
                "success": False,
                "error": "Missing data for integration"
            }
            return
        
        # Try to match a game
        matched_games = []
        for nfl_game in nfl_games[:5]:  # Check first 5 NFL games
            nfl_away = nfl_game.get("away_team", "").upper()
            nfl_home = nfl_game.get("home_team", "").upper()
            
            for odds_game in odds_games:
                odds_away = odds_game.get("away_team", "").upper()
                odds_home = odds_game.get("home_team", "").upper()
                
                # Simple team name matching (could be improved)
                if (nfl_away in odds_away or odds_away in nfl_away) and \
                   (nfl_home in odds_home or odds_home in nfl_home):
                    
                    matched_games.append({
                        "nfl_game": nfl_game,
                        "odds_game": odds_game
                    })
                    break
        
        print(f"    [+] Matched {len(matched_games)} games between NFL and Odds MCPs")
        
        if matched_games:
            # Show sample integration
            sample_match = matched_games[0]
            nfl_data = sample_match["nfl_game"]
            odds_data = sample_match["odds_game"]
            
            print(f"    Sample integration:")
            print(f"      NFL: {nfl_data.get('away_team')} @ {nfl_data.get('home_team')}")
            print(f"      Date: {nfl_data.get('date')} at {nfl_data.get('time', 'TBD')}")
            print(f"      Stadium: {nfl_data.get('stadium', 'TBD')}")
            
            # Built-in odds from NFL MCP
            nfl_odds = nfl_data.get("betting_odds", {})
            if nfl_odds.get("away_moneyline"):
                print(f"      Built-in odds: {nfl_odds.get('away_moneyline')}/{nfl_odds.get('home_moneyline')}")
            
            # Enhanced odds from Odds MCP
            bookmakers = odds_data.get("bookmakers", [])
            if bookmakers:
                sample_book = bookmakers[0]
                book_name = sample_book.get("title", "Unknown")
                print(f"      {book_name}: Enhanced odds available")
            
            self.results["tests"]["game_integration"] = {
                "success": True,
                "matched_games": len(matched_games),
                "sample_integration": sample_match
            }
        else:
            print(f"    [!] No games could be matched between NFL and Odds data")
            self.results["tests"]["game_integration"] = {
                "success": False,
                "error": "No games matched"
            }
    
    async def test_player_props_integration(self):
        """Test player props integration"""
        print("Testing player props integration:")
        
        # Get Chiefs players for props
        chiefs_players = await self.call_mcp_tool(
            self.nfl_mcp_url,
            "getNFLPlayerStats",
            {
                "season": 2024,
                "team": "KC",
                "stat_type": "passing",
                "limit": 5
            }
        )
        
        if chiefs_players and chiefs_players.get("ok"):
            players = chiefs_players.get("data", {}).get("players", [])
            print(f"    [+] Found {len(players)} Chiefs players")
            
            # Show how this could integrate with player props
            if players:
                mahomes = next((p for p in players if "Mahomes" in p.get("player_name", "")), None)
                if mahomes:
                    name = mahomes.get("player_name")
                    yards_2024 = mahomes.get("passing_yards", 0)
                    tds_2024 = mahomes.get("passing_tds", 0)
                    
                    print(f"    Sample props integration:")
                    print(f"      Player: {name}")
                    print(f"      2024 Stats: {yards_2024:,} yards, {tds_2024} TDs")
                    print(f"      Props potential: Passing yards O/U, TD passes O/U")
                    print(f"      Note: Would get live props from Odds MCP when available")
            
            self.results["tests"]["player_props"] = {
                "success": True,
                "players_found": len(players),
                "integration_ready": True
            }
        else:
            print(f"    [!] Could not get Chiefs players for props integration")
            self.results["tests"]["player_props"] = {
                "success": False,
                "error": "Could not get player data"
            }
    
    async def generate_summary(self):
        """Generate integration test summary"""
        print(f"\n{'=' * 60}")
        print("TEST #5 SUMMARY - NFL + Odds Integration")
        print(f"{'=' * 60}")
        
        summary = {
            "status": "UNKNOWN",
            "total_tests": len(self.results["tests"]),
            "successful_tests": 0,
            "integration_info": {}
        }
        
        # Count successful tests
        for test_name, test_data in self.results["tests"].items():
            if test_data.get("success", False):
                summary["successful_tests"] += 1
        
        # Integration analysis
        nfl_games = self.results["integration_data"].get("nfl_games", [])
        odds_games = self.results["integration_data"].get("odds_games", [])
        
        summary["integration_info"]["nfl_games_available"] = len(nfl_games)
        summary["integration_info"]["odds_games_available"] = len(odds_games)
        
        if "game_integration" in self.results["tests"]:
            integration_test = self.results["tests"]["game_integration"]
            if integration_test.get("success"):
                summary["integration_info"]["games_matched"] = integration_test.get("matched_games", 0)
        
        # Overall status
        if summary["successful_tests"] >= 3:
            summary["status"] = "SUCCESS"
            print(f"[+] SUCCESS: NFL + Odds integration working")
        elif summary["successful_tests"] >= 2:
            summary["status"] = "PARTIAL"
            print(f"[!] PARTIAL: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        else:
            summary["status"] = "FAILED"
            print(f"[-] FAILED: NFL + Odds integration not working")
        
        print(f"[+] Overall: {summary['successful_tests']}/{summary['total_tests']} tests passed")
        
        # Show integration capabilities
        integration_info = summary["integration_info"]
        print(f"[+] NFL Games Available: {integration_info.get('nfl_games_available', 0)}")
        print(f"[+] Odds Games Available: {integration_info.get('odds_games_available', 0)}")
        
        if "games_matched" in integration_info:
            matched = integration_info["games_matched"]
            print(f"[+] Games Successfully Matched: {matched}")
            print(f"[+] Integration: NFL schedule + Odds MCP betting data")
        
        self.results["summary"] = summary
    
    async def export_results(self):
        """Export test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\nfl\\tools"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nfl_odds_integration_results_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[+] Results exported to: {filename}")
            
            summary = self.results.get("summary", {})
            status = summary.get("status", "UNKNOWN")
            print(f"[+] Integration test status: {status}")
            
        except Exception as e:
            print(f"[!] Failed to export results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the NFL + Odds integration test"""
    tester = NFLOddsIntegrationTester()
    
    print("NFL + Odds MCP Integration Test")
    print("Testing integration between NFL and Odds MCPs")
    print(f"NFL Server: nflmcp-production.up.railway.app")
    print(f"Odds Server: odds-mcp-v2-production.up.railway.app")
    
    try:
        await tester.test_nfl_odds_integration()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())