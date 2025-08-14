#!/usr/bin/env python3
"""
Miami Marlins @ Cleveland Guardians Player Props

Gets player prop odds for the specific Marlins @ Guardians game.
Focuses on: batter_home_runs, batter_hits, pitcher_strikeouts

Usage:
    python get_mlb_props_json.py
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import httpx

# MCP Server URLs
MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"
ODDS_MCP_URL = "https://odds-mcp-v2-production.up.railway.app/mcp"

# Target player prop markets
TARGET_MARKETS = ["batter_home_runs", "batter_hits", "pitcher_strikeouts"]

# Target game
TARGET_AWAY_TEAM = "Miami Marlins"
TARGET_HOME_TEAM = "Cleveland Guardians"

async def call_mcp_tool(http_client: httpx.AsyncClient, server_url: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool on a server"""
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
        response = await http_client.post(server_url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            return {"ok": False, "error": result["error"]}
        
        return result.get("result", {})
    except Exception as e:
        return {"ok": False, "error": f"MCP call failed: {str(e)}"}

async def get_player_props():
    """Get player props for Miami Marlins @ Cleveland Guardians game"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"🎯 Looking for {TARGET_AWAY_TEAM} @ {TARGET_HOME_TEAM} game...")
        
        # Get MLB events from odds API
        result = await call_mcp_tool(
            client,
            ODDS_MCP_URL,
            "getOdds",
            {
                "sport": "baseball_mlb",
                "regions": "us",
                "markets": "h2h"
            }
        )
        
        if not result.get("ok"):
            print(f"❌ Failed to get odds events: {result.get('error')}")
            return
        
        events = result.get("data", {}).get("odds", [])
        print(f"✅ Found {len(events)} MLB events with odds")
        
        if not events:
            print("❌ No MLB games with odds found for today")
            return
        
        # Find the specific game
        target_event = None
        for event in events:
            home_team = event.get("home_team", "")
            away_team = event.get("away_team", "")
            
            if (TARGET_HOME_TEAM in home_team and TARGET_AWAY_TEAM in away_team):
                target_event = event
                break
        
        if not target_event:
            print(f"❌ Could not find {TARGET_AWAY_TEAM} @ {TARGET_HOME_TEAM} game")
            print("Available games:")
            for event in events:
                print(f"   {event.get('away_team', '')} @ {event.get('home_team', '')}")
            return
        
        event_id = target_event.get("id", "")
        home_team = target_event.get("home_team", "")
        away_team = target_event.get("away_team", "")
        commence_time = target_event.get("commence_time", "")
        
        print(f"🎲 Found target game: {away_team} @ {home_team}")
        print(f"⏰ Game time: {commence_time}")
        
        # Get player props for this specific event
        markets_str = ",".join(TARGET_MARKETS)
        props_result = await call_mcp_tool(
            client,
            ODDS_MCP_URL,
            "getEventOdds",
            {
                "sport": "baseball_mlb",
                "event_id": event_id,
                "regions": "us",
                "markets": markets_str,
                "odds_format": "american"
            }
        )
        
        if not props_result.get("ok"):
            print(f"❌ No player props for this event: {props_result.get('error')}")
            return
        
        event_data = props_result.get("data", {}).get("event", {})
        
        # Extract props data
        game_props = {
            "event_id": event_id,
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": commence_time,
            "player_props": {
                "batter_home_runs": [],
                "batter_hits": [],
                "pitcher_strikeouts": []
            }
        }
        
        bookmakers = event_data.get("bookmakers", [])
        props_found = 0
        
        for bookmaker in bookmakers:
            bookmaker_name = bookmaker.get("title", "Unknown")
            markets = bookmaker.get("markets", [])
            
            for market in markets:
                market_key = market.get("key", "")
                if market_key in TARGET_MARKETS:
                    outcomes = market.get("outcomes", [])
                    
                    # Group outcomes by player
                    player_props = {}
                    for outcome in outcomes:
                        description = outcome.get("description", "")
                        name = outcome.get("name", "")  # Over/Under
                        price = outcome.get("price", 0)
                        point = outcome.get("point", 0)
                        
                        if description not in player_props:
                            player_props[description] = {}
                        
                        player_props[description][name.lower()] = {
                            "price": price,
                            "point": point
                        }
                    
                    # Add complete player props
                    for player_name, prop_data in player_props.items():
                        if "over" in prop_data and "under" in prop_data:
                            game_props["player_props"][market_key].append({
                                "player": player_name,
                                "bookmaker": bookmaker_name,
                                "over_price": prop_data["over"]["price"],
                                "over_point": prop_data["over"]["point"],
                                "under_price": prop_data["under"]["price"],
                                "under_point": prop_data["under"]["point"]
                            })
                            props_found += 1
        
        if props_found == 0:
            print("❌ No player props available for this game")
            return
        
        # Save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"testing/marlins_guardians_props_{timestamp}.json"
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "game": f"{TARGET_AWAY_TEAM} @ {TARGET_HOME_TEAM}",
            "target_markets": TARGET_MARKETS,
            "game_data": game_props
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Summary
        total_props = (
            len(game_props["player_props"]["batter_home_runs"]) +
            len(game_props["player_props"]["batter_hits"]) +
            len(game_props["player_props"]["pitcher_strikeouts"])
        )
        
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print(f"   Game: {TARGET_AWAY_TEAM} @ {TARGET_HOME_TEAM}")
        print(f"   Total player props: {total_props}")
        print(f"   Saved to: {filename}")
        print("=" * 60)
        
        # Show breakdown by market
        for market in TARGET_MARKETS:
            market_total = len(game_props["player_props"][market])
            print(f"   {market}: {market_total} props")
        
        # Display the props
        print("\n🏠 BATTER HOME RUNS:")
        for prop in game_props["player_props"]["batter_home_runs"]:
            print(f"   {prop['player']}: Over {prop['over_point']} ({prop['over_price']:+d}) / Under {prop['under_point']} ({prop['under_price']:+d}) - {prop['bookmaker']}")
        
        print("\n🎯 BATTER HITS:")
        for prop in game_props["player_props"]["batter_hits"]:
            print(f"   {prop['player']}: Over {prop['over_point']} ({prop['over_price']:+d}) / Under {prop['under_point']} ({prop['under_price']:+d}) - {prop['bookmaker']}")
        
        print("\n⚾ PITCHER STRIKEOUTS:")
        for prop in game_props["player_props"]["pitcher_strikeouts"]:
            print(f"   {prop['player']}: Over {prop['over_point']} ({prop['over_price']:+d}) / Under {prop['under_point']} ({prop['under_price']:+d}) - {prop['bookmaker']}")

if __name__ == "__main__":
    asyncio.run(get_player_props())