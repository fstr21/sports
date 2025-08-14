#!/usr/bin/env python3
"""
Test the 4 new MLB MCP tools
"""

import requests
import json

MLB_MCP_URL = "https://mlbmcp-production.up.railway.app/mcp"

def call_tool(name, args=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call", 
        "id": 1,
        "params": {"name": name, "arguments": args or {}}
    }
    try:
        r = requests.post(MLB_MCP_URL, json=payload, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def test_tool(name, args, description):
    print(f"Testing {name}: {description}")
    result = call_tool(name, args)
    
    if "error" in result:
        print(f"ERROR: {result['error']}")
        return False
    
    if not result.get("result", {}).get("ok"):
        error = result.get("result", {}).get("error", "Unknown error")
        print(f"FAILED: {error}")
        return False
    
    data = result["result"]["data"]
    if "count" in data:
        print(f"SUCCESS: Found {data['count']} items")
    else:
        print(f"SUCCESS: Data retrieved")
    
    # Show sample data for new tools
    if name == "getMLBTeamForm" and "form" in data:
        form = data["form"]
        print(f"   Record: {form.get('wins', 0)}-{form.get('losses', 0)} ({form.get('win_percentage', '0.000')})")
        print(f"   Streak: {form.get('streak', 'Unknown')}")
        print(f"   Home: {form.get('home_record', 'Unknown')}")
        print(f"   Away: {form.get('away_record', 'Unknown')}")
    
    elif name == "getMLBPlayerStreaks" and "results" in data:
        for player_id, result in data["results"].items():
            streaks = result.get("streaks", {})
            print(f"   Hit streak: {streaks.get('current_hit_streak', 0)} games")
            print(f"   Multi-hit streak: {streaks.get('current_multi_hit_streak', 0)} games") 
            print(f"   HR streak: {streaks.get('current_hr_streak', 0)} games")
            print(f"   Multi-hit frequency: {streaks.get('multi_hit_frequency', '0/0')}")
    
    elif name == "getMLBPitcherMatchup" and "aggregates" in data:
        aggs = data["aggregates"]
        print(f"   ERA: {aggs.get('era', 0):.2f}")
        print(f"   WHIP: {aggs.get('whip', 0):.2f}")
        print(f"   K/9: {aggs.get('k_per_9', 0):.1f}")
        print(f"   IP: {aggs.get('innings_pitched', 0):.1f}")
    
    elif name == "getMLBTeamScoringTrends" and "trends" in data:
        trends = data["trends"]
        print(f"   Runs/game: {trends.get('runs_per_game', 0)}")
        print(f"   Runs allowed/game: {trends.get('runs_allowed_per_game', 0)}")
        print(f"   Run differential: {trends.get('run_differential', 0)}")
        print(f"   Note: {data.get('note', 'Data retrieved')}")
    
    return True

def main():
    print("=" * 60)
    print("Testing New MLB MCP Tools")
    print("=" * 60)
    
    tests = [
        ("getMLBTeamForm", {"team_id": 147}, "Yankees team form"),
        ("getMLBPlayerStreaks", {"player_ids": [592450], "lookback": 15}, "Aaron Judge streaks"),
        ("getMLBPitcherMatchup", {"pitcher_id": 670280}, "Pitcher analysis"),
        ("getMLBTeamScoringTrends", {"team_id": 147}, "Yankees scoring trends")
    ]
    
    passed = 0
    for name, args, desc in tests:
        if test_tool(name, args, desc):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} new tools working")
    print("=" * 60)

if __name__ == "__main__":
    main()