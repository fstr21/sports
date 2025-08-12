#!/usr/bin/env python3
"""
Systematic ESPN Player Stats API Debugging Script
Debug why Cal Raleigh (41292) has missing games vs Coby Mayo (4683371)
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List

# Test players
WORKING_PLAYER = {
    "name": "Coby Mayo", 
    "id": "4683371",
    "expected_recent_games": ["2025-08-10", "2025-08-09", "2025-08-08", "2025-08-06", "2025-08-05"]
}

PROBLEMATIC_PLAYER = {
    "name": "Cal Raleigh",
    "id": "41292", 
    "expected_recent_games": ["2025-08-10", "2025-08-09", "2025-08-08", "2025-08-07", "2025-08-06"],
    "missing_games": ["2025-08-08"]  # Known missing game
}

class ESPNAPIDebugger:
    def __init__(self):
        self.session = None
        self.debug_log = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log(self, message: str, data: Any = None):
        """Log debug message with optional data"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.debug_log.append({
            "timestamp": timestamp,
            "message": message,
            "data": data
        })
        
        if data and isinstance(data, dict):
            print(f"  Data: {json.dumps(data, indent=2)[:300]}...")
    
    async def fetch_url(self, url: str, description: str) -> Dict[str, Any]:
        """Fetch URL with detailed logging"""
        self.log(f"[FETCH] Fetching: {description}", {"url": url})
        
        try:
            async with self.session.get(url) as response:
                status = response.status
                text = await response.text()
                
                if status == 200:
                    try:
                        data = json.loads(text)
                        self.log(f"✅ Success: {description} ({status})", {
                            "status": status,
                            "data_keys": list(data.keys()) if isinstance(data, dict) else "non-dict",
                            "data_size": len(text)
                        })
                        return {"ok": True, "data": data, "status": status}
                    except json.JSONDecodeError as e:
                        self.log(f"❌ JSON Error: {description}", {"status": status, "json_error": str(e), "text_preview": text[:200]})
                        return {"ok": False, "error": f"JSON decode error: {e}", "status": status}
                else:
                    self.log(f"❌ HTTP Error: {description}", {"status": status, "text": text[:200]})
                    return {"ok": False, "error": f"HTTP {status}: {text[:200]}", "status": status}
                    
        except Exception as e:
            self.log(f"❌ Request Error: {description}", {"error": str(e)})
            return {"ok": False, "error": f"Request error: {e}"}
    
    async def analyze_eventlog_structure(self, player_id: str, player_name: str):
        """Analyze ESPN eventlog API structure for a player"""
        self.log(f"\n🔍 ANALYZING EVENTLOG STRUCTURE FOR {player_name} (ID: {player_id})")
        
        base_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}"
        eventlog_url = f"{base_url}/eventlog"
        
        # Step 1: Get main eventlog
        resp = await self.fetch_url(eventlog_url, f"{player_name} eventlog")
        if not resp["ok"]:
            return None
            
        eventlog_data = resp["data"]
        events = eventlog_data.get("events", {})
        total_pages = events.get("pageCount", 1)
        total_count = events.get("count", 0)
        
        self.log(f"📊 Eventlog Summary", {
            "total_pages": total_pages,
            "total_count": total_count,
            "events_structure": {k: type(v).__name__ for k, v in events.items()}
        })
        
        # Step 2: Get ALL pages, not just the last one
        all_games = []
        
        for page in range(1, min(total_pages + 1, 4)):  # Limit to first 3 pages for debugging
            page_url = f"{eventlog_url}?page={page}"
            page_resp = await self.fetch_url(page_url, f"{player_name} eventlog page {page}")
            
            if not page_resp["ok"]:
                continue
                
            page_data = page_resp["data"]
            page_events = page_data.get("events", {}).get("items", [])
            
            self.log(f"📄 Page {page} Analysis", {
                "events_count": len(page_events),
                "page_structure": {k: type(v).__name__ for k, v in page_data.get("events", {}).items()}
            })
            
            # Step 3: Analyze each event on this page
            for i, event_item in enumerate(page_events):
                event_ref = event_item.get("event", {}).get("$ref")
                stats_ref = event_item.get("statistics", {}).get("$ref")
                
                self.log(f"  🎮 Event {i+1}", {
                    "has_event_ref": bool(event_ref),
                    "has_stats_ref": bool(stats_ref),
                    "event_ref": event_ref[-50:] if event_ref else None  # Last 50 chars
                })
                
                if event_ref:
                    # Get event details
                    event_resp = await self.fetch_url(event_ref, f"{player_name} event {i+1}")
                    if event_resp["ok"]:
                        event_data = event_resp["data"]
                        game_date = event_data.get("date", "")
                        
                        if game_date:
                            try:
                                utc_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                                date_str = utc_dt.strftime("%Y-%m-%d")
                                
                                game_info = {
                                    "date": date_str,
                                    "raw_date": game_date,
                                    "has_stats": bool(stats_ref)
                                }
                                
                                # Get stats if available
                                if stats_ref:
                                    stats_resp = await self.fetch_url(stats_ref, f"{player_name} stats {date_str}")
                                    if stats_resp["ok"]:
                                        stats_data = stats_resp["data"]
                                        
                                        # Analyze stats structure
                                        splits = stats_data.get("splits", {})
                                        categories = splits.get("categories", [])
                                        
                                        batting_stats = {}
                                        all_categories = []
                                        
                                        for category in categories:
                                            cat_name = category.get("name", "").lower()
                                            all_categories.append(cat_name)
                                            
                                            if cat_name == "batting":
                                                for stat in category.get("stats", []):
                                                    stat_name = stat.get("name", "").lower()
                                                    stat_value = stat.get("value", 0)
                                                    
                                                    if stat_name in ["hits", "homeruns", "runs", "rbis"]:
                                                        batting_stats[stat_name] = stat_value
                                        
                                        game_info["categories"] = all_categories
                                        game_info["batting_stats"] = batting_stats
                                
                                all_games.append(game_info)
                                self.log(f"    📅 Game: {date_str}", game_info)
                                
                            except Exception as e:
                                self.log(f"    ❌ Date parsing error: {e}")
        
        # Step 4: Sort games by date and analyze coverage
        all_games.sort(key=lambda x: x["date"], reverse=True)
        
        self.log(f"\n📈 FINAL ANALYSIS FOR {player_name}", {
            "total_games_found": len(all_games),
            "date_range": f"{all_games[-1]['date']} to {all_games[0]['date']}" if all_games else "No games",
            "games_with_stats": len([g for g in all_games if g.get("has_stats", False)]),
            "games_by_date": [g["date"] for g in all_games[:10]]  # Last 10 games
        })
        
        return all_games
    
    async def compare_players(self):
        """Compare working vs problematic player"""
        self.log("\n🆚 COMPARING PLAYERS")
        
        # Analyze both players
        working_games = await self.analyze_eventlog_structure(
            WORKING_PLAYER["id"], 
            WORKING_PLAYER["name"]
        )
        
        print("\n" + "="*80 + "\n")
        
        problematic_games = await self.analyze_eventlog_structure(
            PROBLEMATIC_PLAYER["id"],
            PROBLEMATIC_PLAYER["name"]
        )
        
        # Compare results
        self.log("\n🔬 COMPARISON RESULTS")
        
        if working_games and problematic_games:
            working_dates = set([g["date"] for g in working_games[:10]])
            problematic_dates = set([g["date"] for g in problematic_games[:10]])
            
            missing_in_problematic = working_dates - problematic_dates
            extra_in_problematic = problematic_dates - working_dates
            
            self.log("Date Coverage Comparison", {
                "working_player_dates": sorted(list(working_dates), reverse=True),
                "problematic_player_dates": sorted(list(problematic_dates), reverse=True),
                "missing_in_problematic": sorted(list(missing_in_problematic)),
                "extra_in_problematic": sorted(list(extra_in_problematic))
            })
        
        return {
            "working": working_games,
            "problematic": problematic_games
        }
    
    async def test_alternative_approaches(self, player_id: str, player_name: str):
        """Test alternative ESPN API approaches"""
        self.log(f"\n🔧 TESTING ALTERNATIVE APPROACHES FOR {player_name}")
        
        base_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}"
        
        # Alternative 1: Try different eventlog parameters
        alt_urls = [
            f"{base_url}/eventlog?limit=20",
            f"{base_url}/eventlog?limit=50", 
            f"{base_url}/statistics",
            f"{base_url}/gamelog",
            f"{base_url}/seasons/2025/types/2/eventlog"  # 2025 regular season
        ]
        
        for i, url in enumerate(alt_urls):
            resp = await self.fetch_url(url, f"{player_name} alternative {i+1}")
            if resp["ok"]:
                data = resp["data"]
                self.log(f"✅ Alternative {i+1} worked", {
                    "url_suffix": url.split(player_id)[-1],
                    "top_keys": list(data.keys()) if isinstance(data, dict) else "non-dict"
                })
            
        return True

async def main():
    """Run systematic debugging"""
    
    async with ESPNAPIDebugger() as debugger:
        print("[START] Starting ESPN Player Stats Debugging")
        print(f"Working Player: {WORKING_PLAYER['name']} ({WORKING_PLAYER['id']})")
        print(f"Problematic Player: {PROBLEMATIC_PLAYER['name']} ({PROBLEMATIC_PLAYER['id']})")
        print("="*80)
        
        # Main comparison
        results = await debugger.compare_players()
        
        print("\n" + "="*80)
        
        # Test alternatives for problematic player
        await debugger.test_alternative_approaches(
            PROBLEMATIC_PLAYER["id"],
            PROBLEMATIC_PLAYER["name"]
        )
        
        print(f"\n[DONE] Debug session complete. {len(debugger.debug_log)} log entries generated.")
        
        # Save debug log
        with open("debug_player_stats_log.json", "w") as f:
            json.dump({
                "session_time": datetime.now().isoformat(),
                "players_tested": [WORKING_PLAYER, PROBLEMATIC_PLAYER],
                "debug_log": debugger.debug_log
            }, f, indent=2)
        
        print("[SAVE] Debug log saved to debug_player_stats_log.json")

if __name__ == "__main__":
    asyncio.run(main())