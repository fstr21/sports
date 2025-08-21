#!/usr/bin/env python3
"""
MLB Team Roster Tool - Detailed Roster Data

Gets the complete roster for Team ID 135 (San Diego Padres) with detailed
player information including positions, jersey numbers, and status.

Usage:
    python roster_detailed.py
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

# Configuration
TARGET_TEAM_ID = 135  # San Diego Padres
TARGET_SEASON = 2025
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

class MLBRosterDetailer:
    """Detailed MLB roster retriever"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.roster_data = {
            "team_id": TARGET_TEAM_ID,
            "season": TARGET_SEASON,
            "timestamp": datetime.now().isoformat(),
            "players": [],
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
    
    def get_position_category(self, position: str) -> str:
        """Categorize player position"""
        if not position or position == "N/A":
            return "Unknown"
        
        pitchers = ["P", "SP", "RP", "CP", "LHP", "RHP"]
        catchers = ["C"]
        infielders = ["1B", "2B", "3B", "SS", "IF"]
        outfielders = ["LF", "CF", "RF", "OF"]
        
        pos = position.upper()
        
        if pos in pitchers:
            return "Pitcher"
        elif pos in catchers:
            return "Catcher"
        elif pos in infielders:
            return "Infielder"
        elif pos in outfielders:
            return "Outfielder"
        else:
            return "Other"
    
    def format_jersey_number(self, number: Any) -> str:
        """Format jersey number for display"""
        if number is None or number == "":
            return "N/A"
        return str(number)
    
    async def get_roster(self):
        """Get team roster for the target team"""
        print("👥 MLB TEAM ROSTER RETRIEVER")
        print("=" * 60)
        print(f"🏟️  Team ID: {TARGET_TEAM_ID}")
        print(f"📅 Season: {TARGET_SEASON}")
        print(f"🔗 Server: {MLB_MCP_URL}")
        print("=" * 60)
        
        # Get roster
        print(f"\n🔍 Fetching roster for Team {TARGET_TEAM_ID} ({TARGET_SEASON} season)...")
        result = await self.call_mcp_tool("getMLBTeamRoster", {
            "teamId": TARGET_TEAM_ID,
            "season": TARGET_SEASON
        })
        
        if not result or not result.get("ok"):
            print("❌ Failed to get roster data")
            return
        
        data = result.get("data", {})
        players = data.get("players", [])
        count = data.get("count", 0)
        season = data.get("season", TARGET_SEASON)
        team_id = data.get("teamId", TARGET_TEAM_ID)
        
        print(f"✅ Found {count} players for Team {team_id} ({season} season)")
        
        if not players:
            print("\n📋 No players found")
            await self.save_results()
            return
        
        # Organize players by position category
        position_groups = {}
        jersey_numbers = {}
        status_counts = {}
        
        for player in players:
            position = player.get("position", "N/A")
            category = self.get_position_category(position)
            
            if category not in position_groups:
                position_groups[category] = []
            position_groups[category].append(player)
            
            # Track jersey numbers
            jersey = self.format_jersey_number(player.get("primaryNumber"))
            if jersey != "N/A":
                jersey_numbers[jersey] = player.get("fullName", "Unknown")
            
            # Track status
            status = player.get("status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Display roster by position groups
        print(f"\n📋 ROSTER DETAILS:")
        print("=" * 80)
        
        # Position categories in logical order
        categories = ["Pitcher", "Catcher", "Infielder", "Outfielder", "Other", "Unknown"]
        
        for category in categories:
            if category in position_groups:
                category_players = position_groups[category]
                print(f"\n⚾ {category.upper()}S ({len(category_players)} players)")
                print("-" * 50)
                
                # Sort players by jersey number, then name
                sorted_players = sorted(category_players, key=lambda x: (
                    int(self.format_jersey_number(x.get("primaryNumber"))) if self.format_jersey_number(x.get("primaryNumber")).isdigit() else 999,
                    x.get("fullName", "")
                ))
                
                for player in sorted_players:
                    self.display_player(player)
        
        # Store all players in data
        for player in players:
            player_detail = {
                "player_id": player.get("playerId"),
                "full_name": player.get("fullName"),
                "jersey_number": self.format_jersey_number(player.get("primaryNumber")),
                "position": player.get("position"),
                "position_category": self.get_position_category(player.get("position")),
                "status": player.get("status")
            }
            self.roster_data["players"].append(player_detail)
        
        # Generate summary
        self.roster_data["summary"] = {
            "total_players": count,
            "position_breakdown": {cat: len(players) for cat, players in position_groups.items()},
            "status_breakdown": status_counts,
            "jersey_numbers_assigned": len([j for j in jersey_numbers.keys() if j != "N/A"]),
            "players_without_numbers": len([p for p in players if self.format_jersey_number(p.get("primaryNumber")) == "N/A"])
        }
        
        # Print summary
        print(f"\n📊 ROSTER SUMMARY")
        print("=" * 40)
        print(f"🏟️  Team: {team_id}")
        print(f"📅 Season: {season}")
        print(f"👥 Total Players: {count}")
        
        print(f"\n⚾ Position Breakdown:")
        for category, players_list in position_groups.items():
            print(f"   {category}: {len(players_list)} players")
        
        print(f"\n📝 Status Breakdown:")
        for status, status_count in sorted(status_counts.items()):
            print(f"   {status}: {status_count} players")
        
        print(f"\n🔢 Jersey Numbers:")
        print(f"   Assigned: {len([j for j in jersey_numbers.keys() if j != 'N/A'])}")
        print(f"   Unassigned: {len([p for p in players if self.format_jersey_number(p.get('primaryNumber')) == 'N/A'])}")
        
        # Show some notable jersey numbers
        notable_numbers = ["1", "99", "27", "42"]
        notable_found = []
        for num in notable_numbers:
            if num in jersey_numbers:
                notable_found.append(f"#{num}: {jersey_numbers[num]}")
        
        if notable_found:
            print(f"\n🌟 Notable Numbers:")
            for notable in notable_found:
                print(f"   {notable}")
        
        await self.save_results()
    
    def display_player(self, player: Dict[str, Any]):
        """Display a single player's information"""
        player_id = player.get("playerId", "N/A")
        name = player.get("fullName", "Unknown")
        jersey = self.format_jersey_number(player.get("primaryNumber"))
        position = player.get("position", "N/A")
        status = player.get("status", "Unknown")
        
        # Format jersey display
        jersey_display = f"#{jersey}" if jersey != "N/A" else "No #"
        
        # Status emoji
        status_emoji = "✅" if status == "Active" else "⚠️" if "Injured" in status else "📋"
        
        print(f"    👤 {name}")
        print(f"        ID: {player_id} | {jersey_display} | {position} | {status_emoji} {status}")
        print()
    
    async def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\Users\\fstr2\\Desktop\\sports\\mcp_leagues\\mlb\\tools\\roster_detailed_team{TARGET_TEAM_ID}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.roster_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
            
            print(f"\n💾 RESULTS SAVED")
            print("=" * 40)
            print(f"📁 File: {os.path.basename(filename)}")
            print(f"📊 Size: {size_str}")
            print(f"👥 Players: {len(self.roster_data['players'])}")
            print(f"📍 Full path: {filename}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main function"""
    roster_detailer = MLBRosterDetailer()
    
    try:
        await roster_detailer.get_roster()
    finally:
        await roster_detailer.close()

if __name__ == "__main__":
    asyncio.run(main())