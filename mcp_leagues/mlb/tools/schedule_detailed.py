#!/usr/bin/env python3
"""
MLB Schedule Tool - Detailed Game Data

Gets the MLB schedule for a specific date and retrieves detailed information
for each game including teams, times, status, and venue details.

Usage:
    python schedule_detailed.py

Default date: 2025-08-20
Modify the TARGET_DATE variable to change the date.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

# Configuration
TARGET_DATE = "2025-08-20"
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class MLBScheduleDetailer:
    """Detailed MLB schedule retriever"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.schedule_data = {
            "date_requested": TARGET_DATE,
            "timestamp": datetime.now().isoformat(),
            "games": [],
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
    
    def format_time(self, time_str: str) -> str:
        """Format time string for display"""
        if not time_str or time_str == "Unknown":
            return "TBD"
        
        try:
            # Parse ISO format and convert to readable time
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return dt.strftime("%I:%M %p ET")
        except:
            return time_str
    
    def format_status(self, status: str) -> str:
        """Format game status for display"""
        status_map = {
            "Scheduled": "⏰ Scheduled",
            "Pre-Game": "🔄 Pre-Game", 
            "In Progress": "🔴 LIVE",
            "Live": "🔴 LIVE",
            "Final": "✅ Final",
            "Postponed": "⏸️ Postponed",
            "Cancelled": "❌ Cancelled",
            "Suspended": "⏸️ Suspended"
        }
        return status_map.get(status, f"🔹 {status}")
    
    async def get_schedule(self):
        """Get MLB schedule for the target date"""
        print("🏟️  MLB SCHEDULE RETRIEVER")
        print("=" * 60)
        print(f"📅 Date: {TARGET_DATE}")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print("=" * 60)
        
        # Get schedule
        print(f"\n🔍 Fetching schedule for {TARGET_DATE}...")
        result = await self.call_mcp_tool("getMLBScheduleET", {"date": TARGET_DATE})
        
        if not result or not result.get("ok"):
            print("❌ Failed to get schedule data")
            return
        
        data = result.get("data", {})
        games = data.get("games", [])
        count = data.get("count", 0)
        date_et = data.get("date_et", TARGET_DATE)
        
        print(f"✅ Found {count} games for {date_et}")
        
        if not games:
            print("\n📋 No games scheduled for this date")
            self.schedule_data["summary"] = {
                "total_games": 0,
                "status_breakdown": {},
                "time_slots": {}
            }
            await self.save_results()
            return
        
        # Process each game
        print(f"\n📋 GAME DETAILS:")
        print("=" * 80)
        
        status_counts = {}
        time_slots = {}
        
        for i, game in enumerate(games, 1):
            # Extract game data
            game_pk = game.get("gamePk", "Unknown")
            start_time = game.get("start_et", "Unknown")
            status = game.get("status", "Unknown")
            venue = game.get("venue", "Unknown")
            
            # Team data
            away_team = game.get("away", {})
            home_team = game.get("home", {})
            
            away_name = away_team.get("name", "Unknown")
            away_id = away_team.get("teamId", "Unknown")
            away_abbrev = away_team.get("abbrev", "N/A")
            
            home_name = home_team.get("name", "Unknown")
            home_id = home_team.get("teamId", "Unknown") 
            home_abbrev = home_team.get("abbrev", "N/A")
            
            # Format for display
            formatted_time = self.format_time(start_time)
            formatted_status = self.format_status(status)
            
            # Count statuses and time slots
            status_counts[status] = status_counts.get(status, 0) + 1
            time_slot = formatted_time
            time_slots[time_slot] = time_slots.get(time_slot, 0) + 1
            
            # Create detailed game object
            game_detail = {
                "game_number": i,
                "game_pk": game_pk,
                "matchup": f"{away_name} @ {home_name}",
                "away_team": {
                    "name": away_name,
                    "id": away_id,
                    "abbreviation": away_abbrev
                },
                "home_team": {
                    "name": home_name,
                    "id": home_id,
                    "abbreviation": home_abbrev
                },
                "start_time": {
                    "raw": start_time,
                    "formatted": formatted_time
                },
                "status": {
                    "raw": status,
                    "formatted": formatted_status
                },
                "venue": venue
            }
            
            self.schedule_data["games"].append(game_detail)
            
            # Terminal output
            print(f"\n🎲 GAME {i:2d}")
            print(f"   Matchup: {away_name} @ {home_name}")
            print(f"   Teams: {away_abbrev or 'N/A'} (ID: {away_id}) @ {home_abbrev or 'N/A'} (ID: {home_id})")
            print(f"   Time: {formatted_time}")
            print(f"   Status: {formatted_status}")
            print(f"   Venue: {venue}")
            print(f"   Game ID: {game_pk}")
            print("-" * 80)
        
        # Summary statistics
        self.schedule_data["summary"] = {
            "total_games": count,
            "status_breakdown": status_counts,
            "time_slots": time_slots,
            "venues": list(set(game.get("venue", "Unknown") for game in games)),
            "teams_playing": {
                "away": [game.get("away", {}).get("name", "Unknown") for game in games],
                "home": [game.get("home", {}).get("name", "Unknown") for game in games]
            }
        }
        
        # Print summary
        print(f"\n📊 SUMMARY")
        print("=" * 40)
        print(f"📅 Date: {date_et}")
        print(f"🎲 Total Games: {count}")
        
        print(f"\n📈 Status Breakdown:")
        for status, count_status in sorted(status_counts.items()):
            formatted = self.format_status(status)
            print(f"   {formatted}: {count_status} games")
        
        print(f"\n⏰ Time Slots:")
        for time_slot, count_time in sorted(time_slots.items()):
            print(f"   {time_slot}: {count_time} games")
        
        unique_venues = len(set(game.get("venue", "Unknown") for game in games))
        print(f"\n🏟️ Venues: {unique_venues} different ballparks")
        
        # Show some venue examples
        venues = list(set(game.get("venue", "Unknown") for game in games))[:5]
        for venue in venues:
            print(f"   • {venue}")
        if len(venues) == 5 and unique_venues > 5:
            print(f"   ... and {unique_venues - 5} more")
        
        await self.save_results()
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\schedule_detailed_{TARGET_DATE.replace('-', '')}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"🎲 Games: {len(self.schedule_data['games'])}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    scheduler = MLBScheduleDetailer()
    
    try:
        await scheduler.get_schedule()
    finally:
        await scheduler.close()

if __name__ == "__main__":
    asyncio.run(main())