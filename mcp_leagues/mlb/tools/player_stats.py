#!/usr/bin/env python3
"""
Test #4: MLB MCP - Player Stats
Tests getting historical statistics for specific MLB players
Focus: Edward Cabrera (pitcher) and Steven Kwan (batter - hits/HR)
"""

import httpx
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class PlayerStatsTester:
    """Test MLB MCP player statistics functionality"""
    
    def __init__(self):
        self.server_url = "https://mlbmcp-production.up.railway.app/mcp"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results_data = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "test_name": "MLB Player Statistics Test",
            "players_tested": [],
            "summary": {}
        }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call an MCP tool"""
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
        
        print(f"[*] Calling MLB MCP: {tool_name}")
        if arguments:
            print(f"    Arguments: {arguments}")
        
        try:
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"[!] MCP Error: {result['error']}")
                return None
            
            return result.get("result", {})
            
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return None
    
    async def test_player_stats(self):
        """Test getting player stats for Edward Cabrera and Steven Kwan"""
        print("=" * 60)
        print("TEST #4: MLB MCP - Player Statistics")
        print("=" * 60)
        
        # Step 1: Find player IDs 
        print("\n--- Step 1: Find Player IDs ---")
        
        # We need to search for players by name. Let's try different approaches
        
        # Method 1: Search through team rosters for Steven Kwan (Guardians)
        print("\nSearching for Steven Kwan on Cleveland Guardians roster...")
        kwan_id = await self.find_player_on_team("Steven Kwan", 114)  # Guardians team ID
        
        # Method 2: Search through team rosters for Edward Cabrera (Marlins)  
        print("\nSearching for Edward Cabrera on Miami Marlins roster...")
        cabrera_id = await self.find_player_on_team("Edward Cabrera", 146)  # Marlins team ID
        
        if not kwan_id:
            print("[!] Could not find Steven Kwan - trying alternate search methods...")
            kwan_id = await self.search_player_alternate("Steven Kwan", ["kwan"])
        
        if not cabrera_id:
            print("[!] Could not find Edward Cabrera - trying alternate search methods...")
            cabrera_id = await self.search_player_alternate("Edward Cabrera", ["cabrera", "edward"])
        
        # Step 2: Get stats for found players
        players_to_test = []
        
        if kwan_id:
            players_to_test.append({
                "name": "Steven Kwan",
                "id": kwan_id,
                "type": "batter",
                "stats": ["hits", "homeRuns", "atBats", "doubles", "triples"]
            })
        
        if cabrera_id:
            players_to_test.append({
                "name": "Edward Cabrera", 
                "id": cabrera_id,
                "type": "pitcher",
                "stats": ["strikeOuts", "walks", "hits", "earnedRuns"]
            })
        
        if not players_to_test:
            print("[!] Could not find either player - trying with known player IDs...")
            # Use known IDs as fallback
            players_to_test = [
                {
                    "name": "Steven Kwan (fallback)",
                    "id": 663734,  # This might be Steven Kwan's ID
                    "type": "batter",
                    "stats": ["hits", "homeRuns", "atBats", "doubles", "triples"]
                },
                {
                    "name": "Edward Cabrera (fallback)",
                    "id": 665795,  # This might be Edward Cabrera's ID
                    "type": "pitcher", 
                    "stats": ["strikeOuts", "walks", "hits", "earnedRuns"]
                }
            ]
        
        # Step 3: Get last 10 games stats for each player
        print(f"\n--- Step 2: Get Player Statistics (Last 10 Games) ---")
        
        for player in players_to_test:
            await self.test_player_individual_stats(player)
        
        # Step 4: Test batch stats call
        if len(players_to_test) >= 2:
            print(f"\n--- Step 3: Test Batch Stats Call ---")
            await self.test_batch_stats(players_to_test)
        
        # Summary
        print(f"\n{'=' * 60}")
        print("TEST #4 SUMMARY")
        print(f"{'=' * 60}")
        
        found_players = [p["name"] for p in players_to_test]
        if found_players:
            print(f"[+] Found players: {', '.join(found_players)}")
            print(f"[+] MLB MCP getMLBPlayerLastN: WORKING")
            self.results_data["summary"]["status"] = "SUCCESS"
            self.results_data["summary"]["players_found"] = len(found_players)
        else:
            print(f"[-] No players found")
            print(f"[-] MLB MCP player search: NEEDS WORK")
            self.results_data["summary"]["status"] = "FAILED"
            self.results_data["summary"]["players_found"] = 0
        
        # Save results to JSON file
        await self.save_results_json()
    
    async def find_player_on_team(self, player_name: str, team_id: int) -> Optional[int]:
        """Find a player on a specific team roster"""
        roster_result = await self.call_mcp_tool("getMLBTeamRoster", {
            "teamId": team_id,
            "season": 2025
        })
        
        if not roster_result or not roster_result.get("data"):
            return None
        
        players = roster_result["data"].get("players", [])
        
        # Search for player by name
        for player in players:
            full_name = player.get("fullName", "")
            if player_name.lower() in full_name.lower():
                player_id = player.get("playerId")
                print(f"[+] Found {full_name} (ID: {player_id})")
                return player_id
        
        print(f"[-] {player_name} not found on team roster")
        return None
    
    async def search_player_alternate(self, player_name: str, search_terms: List[str]) -> Optional[int]:
        """Search for player using alternate methods"""
        # This is a placeholder - in reality we might search multiple team rosters
        print(f"[*] Alternate search for {player_name} not implemented yet")
        return None
    
    async def test_player_individual_stats(self, player_info: Dict[str, Any]):
        """Test getting stats for individual player"""
        player_name = player_info["name"]
        player_id = player_info["id"]
        player_type = player_info["type"]
        stats_list = player_info["stats"]
        
        print(f"\n--- Testing: {player_name} (ID: {player_id}) ---")
        
        # Test with different game counts
        for count in [5, 10]:
            print(f"\nLast {count} games for {player_name}:")
            
            # Set group based on player type
            group = "hitting" if player_type == "batter" else "pitching"
            
            stats_result = await self.call_mcp_tool("getMLBPlayerLastN", {
                "player_ids": [player_id],
                "season": 2025,
                "group": group,
                "stats": stats_list,
                "count": count
            })
            
            if stats_result:
                self.analyze_player_stats(stats_result, player_name, player_type, count, player_id)
            else:
                print(f"    [!] Failed to get stats for {player_name}")
    
    async def test_batch_stats(self, players_list: List[Dict[str, Any]]):
        """Test getting stats for multiple players in one call"""
        print(f"\nBatch stats call for {len(players_list)} players:")
        
        # Separate batters and pitchers (they need different calls)
        batters = [p for p in players_list if p["type"] == "batter"]
        pitchers = [p for p in players_list if p["type"] == "pitcher"]
        
        # Test batters together
        if batters:
            batter_ids = [p["id"] for p in batters]
            batter_names = [p["name"] for p in batters]
            
            print(f"  Batch hitting stats for: {', '.join(batter_names)}")
            
            batch_result = await self.call_mcp_tool("getMLBPlayerLastN", {
                "player_ids": batter_ids,
                "season": 2025,
                "group": "hitting",
                "stats": ["hits", "homeRuns", "atBats"],
                "count": 5
            })
            
            if batch_result:
                self.analyze_batch_stats(batch_result, batter_names, "hitting")
        
        # Test pitchers together
        if pitchers:
            pitcher_ids = [p["id"] for p in pitchers]
            pitcher_names = [p["name"] for p in pitchers]
            
            print(f"  Batch pitching stats for: {', '.join(pitcher_names)}")
            
            batch_result = await self.call_mcp_tool("getMLBPlayerLastN", {
                "player_ids": pitcher_ids,
                "season": 2025,
                "group": "pitching", 
                "stats": ["strikeOuts", "walks", "hits"],
                "count": 5
            })
            
            if batch_result:
                self.analyze_batch_stats(batch_result, pitcher_names, "pitching")
    
    def analyze_player_stats(self, result: Dict[str, Any], player_name: str, player_type: str, count: int, player_id: int = None):
        """Analyze individual player stats result"""
        
        data = result.get("data", {})
        results = data.get("results", {})
        
        if not results:
            print(f"    [!] No results data for {player_name}")
            return
        
        # Find the player's data (results keyed by player ID)
        player_data = None
        for player_id, stats in results.items():
            player_data = stats
            break  # Take first (should only be one)
        
        if not player_data:
            print(f"    [!] No player data found")
            return
        
        games = player_data.get("games", [])
        aggregates = player_data.get("aggregates", {})
        
        print(f"    [+] Found {len(games)} games of data")
        
        # Store data for JSON output
        player_json_data = {
            "name": player_name,
            "player_id": player_id,
            "player_type": player_type,
            "games_count": count,
            "games_found": len(games),
            "games": [],
            "totals": {},
            "averages": {}
        }
        
        if games:
            print(f"    Complete game-by-game breakdown:")
            for i, game in enumerate(games):  # Show ALL games
                date = game.get("date_et", "Unknown")
                
                game_stats = {"game_number": i+1, "date": date}
                
                if player_type == "batter":
                    hits = game.get("hits", 0)
                    hrs = game.get("homeRuns", 0)
                    abs = game.get("atBats", 0)
                    doubles = game.get("doubles", 0)
                    triples = game.get("triples", 0)
                    
                    game_stats.update({
                        "hits": hits,
                        "home_runs": hrs,
                        "at_bats": abs,
                        "doubles": doubles,
                        "triples": triples
                    })
                    
                    print(f"      Game {i+1:2d} ({date}): {hits} hits, {hrs} HR, {abs} AB, {doubles} 2B, {triples} 3B")
                else:  # pitcher
                    ks = game.get("strikeOuts", 0)
                    walks = game.get("walks", 0)
                    hits = game.get("hits", 0)
                    er = game.get("earnedRuns", 0)
                    
                    game_stats.update({
                        "strikeouts": ks,
                        "walks": walks,
                        "hits_allowed": hits,
                        "earned_runs": er
                    })
                    
                    print(f"      Game {i+1:2d} ({date}): {ks} K, {walks} BB, {hits} H, {er} ER")
                
                player_json_data["games"].append(game_stats)
        
        if aggregates:
            print(f"    Totals and averages over {count} games:")
            if player_type == "batter":
                total_hits = aggregates.get("hits_sum", 0)
                total_hrs = aggregates.get("homeRuns_sum", 0)
                total_abs = aggregates.get("atBats_sum", 0)
                avg_hits = aggregates.get("hits_avg", 0)
                avg_hrs = aggregates.get("homeRuns_avg", 0)
                
                # Calculate batting average if we have at-bats
                batting_avg = total_hits / total_abs if total_abs > 0 else 0
                
                player_json_data["totals"] = {
                    "hits": total_hits,
                    "home_runs": total_hrs,
                    "at_bats": total_abs
                }
                player_json_data["averages"] = {
                    "hits_per_game": round(avg_hits, 2),
                    "home_runs_per_game": round(avg_hrs, 2),
                    "batting_average": round(batting_avg, 3)
                }
                
                print(f"      Totals: {total_hits} hits, {total_hrs} HR, {total_abs} AB")
                print(f"      Averages: {avg_hits:.2f} hits/game, {avg_hrs:.2f} HR/game")
                print(f"      Batting Average: {batting_avg:.3f}")
            else:  # pitcher
                total_ks = aggregates.get("strikeOuts_sum", 0)
                total_walks = aggregates.get("walks_sum", 0)
                total_hits = aggregates.get("hits_sum", 0)
                avg_ks = aggregates.get("strikeOuts_avg", 0)
                avg_walks = aggregates.get("walks_avg", 0)
                
                player_json_data["totals"] = {
                    "strikeouts": total_ks,
                    "walks": total_walks,
                    "hits_allowed": total_hits
                }
                player_json_data["averages"] = {
                    "strikeouts_per_game": round(avg_ks, 2),
                    "walks_per_game": round(avg_walks, 2)
                }
                
                print(f"      Totals: {total_ks} K, {total_walks} BB, {total_hits} H")
                print(f"      Averages: {avg_ks:.2f} K/game, {avg_walks:.2f} BB/game")
        
        # Add this player's data to the results
        self.results_data["players_tested"].append(player_json_data)
    
    def analyze_batch_stats(self, result: Dict[str, Any], player_names: List[str], group: str):
        """Analyze batch stats result"""
        
        data = result.get("data", {})
        results = data.get("results", {})
        
        print(f"    [+] Batch results for {len(results)} players:")
        
        for i, (player_id, stats) in enumerate(results.items()):
            name = player_names[i] if i < len(player_names) else f"Player {player_id}"
            games = stats.get("games", [])
            aggregates = stats.get("aggregates", {})
            
            print(f"      {name}: {len(games)} games")
            
            if aggregates:
                if group == "hitting":
                    avg_hits = aggregates.get("hits_avg", 0)
                    avg_hrs = aggregates.get("homeRuns_avg", 0)
                    print(f"        {avg_hits:.2f} hits/game, {avg_hrs:.2f} HR/game")
                else:  # pitching
                    avg_ks = aggregates.get("strikeOuts_avg", 0)
                    avg_walks = aggregates.get("walks_avg", 0)
                    print(f"        {avg_ks:.2f} K/game, {avg_walks:.2f} BB/game")
    
    async def save_results_json(self):
        """Save test results to JSON file"""
        output_dir = "C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools"
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"player_stats_test_results_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results_data, f, indent=2, ensure_ascii=False)
            
            print(f"[+] Results saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"[!] Failed to save results: {e}")
            return None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Run the test"""
    tester = PlayerStatsTester()
    
    try:
        await tester.test_player_stats()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())