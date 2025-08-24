#!/usr/bin/env python3
"""
Pitcher Stats Research - Comprehensive Panel Testing
Test the MLB MCP server for detailed pitcher statistics and create
a comprehensive pitcher panel format for Custom Chronulus analysis.
"""

import asyncio
import json
import httpx
from datetime import datetime

async def test_pitcher_stats_panel():
    """Test comprehensive pitcher stats panel creation"""
    
    print("🥎 PITCHER STATS RESEARCH & PANEL TESTING")
    print("=" * 60)
    
    # Test with today's games
    client = httpx.AsyncClient(timeout=90.0)
    
    try:
        # First, get today's games
        schedule_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call", 
            "id": 1,
            "params": {
                "name": "getMLBScheduleET",
                "arguments": {
                    "date": "2025-08-23"
                }
            }
        }
        
        print("📅 Getting today's MLB schedule...")
        response = await client.post("https://mlbmcp-production.up.railway.app/mcp", json=schedule_payload)
        schedule_result = response.json()
        
        print(f"🔍 Schedule API Response: {json.dumps(schedule_result, indent=2)[:500]}...")
        
        if "result" in schedule_result and schedule_result["result"]:
            result_data = schedule_result["result"]
            if "data" in result_data and "games" in result_data["data"]:
                raw_games = result_data["data"]["games"]
                games = []
                for g in raw_games:
                    games.append({
                        "home_team_id": g["home"]["teamId"],
                        "away_team_id": g["away"]["teamId"],
                        "home_team_name": g["home"]["name"],
                        "away_team_name": g["away"]["name"],
                        "venue": "Stadium",
                        "status": g.get("status", "Unknown")
                    })
                print(f"✅ Found {len(games)} games today")
            elif "content" in result_data and result_data["content"]:
                games = json.loads(result_data["content"][0]["text"])
                print(f"✅ Found {len(games)} games today")
            else:
                print("❌ No content in result, using demo data")
                games = [{
                    "home_team_id": 119,
                    "away_team_id": 135,
                    "home_team_name": "Los Angeles Dodgers", 
                    "away_team_name": "San Diego Padres",
                    "venue": "Dodger Stadium"
                }]
            
            # Test with first game
            if games:
                game = games[0]
                home_team_id = game["home_team_id"]
                away_team_id = game["away_team_id"]
                home_team = game["home_team_name"]
                away_team = game["away_team_name"]
                
                print(f"\n🎯 Testing with: {away_team} @ {home_team}")
                print(f"   Team IDs: Away={away_team_id}, Home={home_team_id}")
                
                # Get comprehensive pitcher data for both teams
                pitcher_panel = await create_pitcher_panel(client, home_team_id, away_team_id, home_team, away_team)
                
                if pitcher_panel:
                    print("\n" + "="*80)
                    print("🏆 COMPREHENSIVE PITCHER PANEL CREATED")
                    print("="*80)
                    print(pitcher_panel)
                    
                    # Test this panel with Custom Chronulus
                    await test_panel_with_chronulus(client, game, pitcher_panel)
                
        else:
            print(f"❌ Error getting schedule: {schedule_result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()

async def create_pitcher_panel(client, home_team_id, away_team_id, home_team, away_team):
    """Create comprehensive pitcher stats panel"""
    
    print(f"\n📊 Creating pitcher panel...")
    
    try:
        # Get rosters for both teams
        home_roster = await get_team_roster(client, home_team_id)
        away_roster = await get_team_roster(client, away_team_id)
        
        if not home_roster or not away_roster:
            print("❌ Could not get team rosters")
            return None
            
        # Find starting pitchers (first pitcher in roster for demo)
        home_pitchers = [p for p in home_roster if p.get("position") == "P"]
        away_pitchers = [p for p in away_roster if p.get("position") == "P"]
        
        if not home_pitchers or not away_pitchers:
            print("❌ No pitchers found in rosters")
            return None
            
        # Get detailed stats for starting pitchers
        home_pitcher = home_pitchers[0]  # First pitcher as demo
        away_pitcher = away_pitchers[0]  # First pitcher as demo
        
        print(f"🏠 Home Pitcher: {home_pitcher.get('fullName', 'Unknown')}")
        print(f"✈️ Away Pitcher: {away_pitcher.get('fullName', 'Unknown')}")
        
        # Get comprehensive stats for both pitchers
        home_stats = await get_pitcher_comprehensive_stats(client, home_pitcher.get("playerId"))
        away_stats = await get_pitcher_comprehensive_stats(client, away_pitcher.get("playerId"))
        
        # Create formatted panel
        panel = create_formatted_pitcher_panel(
            home_pitcher, home_stats, home_team,
            away_pitcher, away_stats, away_team
        )
        
        return panel
        
    except Exception as e:
        print(f"❌ Error creating pitcher panel: {e}")
        return None

async def get_team_roster(client, team_id):
    """Get team roster"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getMLBTeamRoster",
            "arguments": {"teamId": team_id}
        }
    }
    
    response = await client.post("https://mlbmcp-production.up.railway.app/mcp", json=payload)
    result = response.json()
    
    print(f"   🔍 Roster API Response for team {team_id}: {str(result)[:200]}...")
    
    if "result" in result and result["result"]:
        result_data = result["result"]
        if "data" in result_data and "players" in result_data["data"]:
            return result_data["data"]["players"]
        elif "content" in result_data and result_data["content"]:
            return json.loads(result_data["content"][0]["text"])
        elif "text" in result_data:
            return json.loads(result_data["text"])
    return None

async def get_pitcher_comprehensive_stats(client, player_id):
    """Get comprehensive pitcher statistics"""
    
    if not player_id:
        return None
        
    try:
        # Get pitcher matchup data (includes recent starts and aggregates)
        matchup_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": "getMLBPitcherMatchup",
                "arguments": {"pitcher_id": player_id}
            }
        }
        
        response = await client.post("https://mlbmcp-production.up.railway.app/mcp", json=matchup_payload)
        result = response.json()
        
        print(f"   🔍 Pitcher stats API response for {player_id}: {str(result)[:200]}...")
        
        if "result" in result and result["result"]:
            result_data = result["result"]
            if "data" in result_data:
                stats = result_data["data"]
                print(f"   ✅ Got stats for pitcher ID {player_id} (data format)")
                return stats
            elif "content" in result_data and result_data["content"]:
                stats = json.loads(result_data["content"][0]["text"])
                print(f"   ✅ Got stats for pitcher ID {player_id}")
                return stats
            elif "text" in result_data:
                stats = json.loads(result_data["text"])
                print(f"   ✅ Got stats for pitcher ID {player_id} (text format)")
                return stats
        
        print(f"   ❌ No stats for pitcher ID {player_id}")
        return None
            
    except Exception as e:
        print(f"   ❌ Error getting pitcher stats: {e}")
        return None

def create_formatted_pitcher_panel(home_pitcher, home_stats, home_team, away_pitcher, away_stats, away_team):
    """Create user-friendly formatted pitcher panel"""
    
    panel = f"""
🥎 STARTING PITCHER MATCHUP ANALYSIS 🥎

🏠 HOME: {home_pitcher.get('fullName', 'Unknown')} ({home_team})
{format_pitcher_stats(home_stats)}

✈️ AWAY: {away_pitcher.get('fullName', 'Unknown')} ({away_team})  
{format_pitcher_stats(away_stats)}

📊 MATCHUP SUMMARY:
{create_matchup_summary(home_pitcher, home_stats, away_pitcher, away_stats)}

💡 BETTING IMPLICATIONS:
{create_betting_implications(home_stats, away_stats)}
"""
    
    return panel.strip()

def format_pitcher_stats(stats):
    """Format individual pitcher statistics"""
    
    if not stats:
        return "   ❌ No recent performance data available"
        
    try:
        aggregates = stats.get("aggregates", {})
        recent_starts = stats.get("recent_starts", [])
        
        if not aggregates:
            return "   ❌ No aggregate statistics available"
            
        # Core stats
        era = aggregates.get("era", 0)
        whip = aggregates.get("whip", 0)
        k_per_9 = aggregates.get("k_per_9", 0)
        innings_pitched = aggregates.get("innings_pitched", 0)
        
        # Recent form
        recent_form = ""
        if recent_starts:
            last_start = recent_starts[0]
            last_era = last_start.get("game_era", 0)
            last_opponent = last_start.get("opponent_name", "Unknown")
            recent_form = f"\n   📅 Last Start: {last_era:.2f} ERA vs {last_opponent}"
        
        return f"""   📈 Season Stats: {era:.2f} ERA, {whip:.3f} WHIP, {k_per_9:.1f} K/9
   🎯 Innings Pitched: {innings_pitched} IP{recent_form}
   💪 Recent Form: {analyze_recent_form(recent_starts)}"""
   
    except Exception as e:
        return f"   ❌ Error formatting stats: {e}"

def analyze_recent_form(recent_starts):
    """Analyze pitcher's recent form"""
    
    if not recent_starts or len(recent_starts) < 2:
        return "Limited recent data"
        
    # Analyze last 3 starts
    last_3 = recent_starts[:3]
    eras = [start.get("game_era", 999) for start in last_3 if start.get("game_era", 999) < 50]
    
    if not eras:
        return "Inconsistent recent starts"
        
    avg_era = sum(eras) / len(eras)
    
    if avg_era <= 2.50:
        return "🔥 EXCELLENT (Sub-2.50 ERA)"
    elif avg_era <= 4.00:
        return "✅ SOLID (Good control)"
    elif avg_era <= 6.00:
        return "⚠️ SHAKY (Some struggles)"
    else:
        return "❌ CONCERNING (High ERA)"

def create_matchup_summary(home_pitcher, home_stats, away_pitcher, away_stats):
    """Create head-to-head matchup summary"""
    
    home_name = home_pitcher.get('fullName', 'Home Pitcher')
    away_name = away_pitcher.get('fullName', 'Away Pitcher')
    
    # Compare ERAs
    home_era = home_stats.get("aggregates", {}).get("era", 999) if home_stats else 999
    away_era = away_stats.get("aggregates", {}).get("era", 999) if away_stats else 999
    
    if home_era < away_era:
        edge = f"🏠 {home_name} has ERA advantage ({home_era:.2f} vs {away_era:.2f})"
    elif away_era < home_era:
        edge = f"✈️ {away_name} has ERA advantage ({away_era:.2f} vs {home_era:.2f})"
    else:
        edge = "Even matchup based on ERA"
        
    # Compare strikeout rates
    home_k9 = home_stats.get("aggregates", {}).get("k_per_9", 0) if home_stats else 0
    away_k9 = away_stats.get("aggregates", {}).get("k_per_9", 0) if away_stats else 0
    
    if home_k9 > away_k9:
        strikeout_edge = f"🏠 {home_name} strikes out more ({home_k9:.1f} vs {away_k9:.1f} K/9)"
    elif away_k9 > home_k9:
        strikeout_edge = f"✈️ {away_name} strikes out more ({away_k9:.1f} vs {home_k9:.1f} K/9)"
    else:
        strikeout_edge = "Similar strikeout rates"
    
    return f"""   🎯 Pitching Edge: {edge}
   ⚡ Strikeout Edge: {strikeout_edge}
   🏟️ This appears to be a {"pitcher's duel" if max(home_era, away_era) < 4.0 else "hitter-friendly"} matchup"""

def create_betting_implications(home_stats, away_stats):
    """Create betting implications analysis"""
    
    implications = []
    
    # Total implications
    home_era = home_stats.get("aggregates", {}).get("era", 999) if home_stats else 999
    away_era = away_stats.get("aggregates", {}).get("era", 999) if away_stats else 999
    
    avg_era = (home_era + away_era) / 2
    
    if avg_era < 3.00:
        implications.append("🔻 UNDER looks attractive (Strong pitching matchup)")
    elif avg_era > 5.00:
        implications.append("🔺 OVER has potential (Weaker pitching)")
    else:
        implications.append("⚖️ Total depends on offensive matchups")
        
    # Moneyline implications  
    era_diff = abs(home_era - away_era)
    if era_diff > 1.50:
        better_pitcher = "Home" if home_era < away_era else "Away"
        implications.append(f"💰 {better_pitcher} pitcher creates value (Significant ERA edge)")
    else:
        implications.append("🎲 Even pitching matchup - focus on other factors")
        
    return "\n   ".join(implications)

async def test_panel_with_chronulus(client, game, pitcher_panel):
    """Test the pitcher panel with Custom Chronulus"""
    
    print(f"\n🧪 Testing pitcher panel with Custom Chronulus...")
    
    # Prepare game data with comprehensive pitcher panel
    game_data = {
        "home_team": f"{game['home_team_name']} ({game.get('home_record', 'N/A')})",
        "away_team": f"{game['away_team_name']} ({game.get('away_record', 'N/A')})",
        "venue": game.get("venue", "Unknown Venue"),
        "game_date": "2025-08-23",
        "additional_context": f"MLB Game Analysis with Comprehensive Pitcher Intelligence:\n\n{pitcher_panel}"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": "getCustomChronulusAnalysis",
            "arguments": {
                "game_data": game_data,
                "expert_count": 5,
                "analysis_depth": "comprehensive"
            }
        }
    }
    
    try:
        response = await client.post(
            "https://customchronpredictormcp-production.up.railway.app/mcp", 
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                content = result["result"]["content"][0]["text"]
                analysis_data = json.loads(content)
                
                print("✅ Custom Chronulus analysis successful!")
                print(f"📊 Win Probability: {analysis_data.get('analysis', {}).get('away_team_win_probability', 0):.1%}")
                
                # Check if experts mention pitcher details
                expert_text = analysis_data.get('analysis', {}).get('expert_analysis', '')
                
                pitcher_mentions = {
                    "ERA mentions": "ERA" in expert_text.upper(),
                    "WHIP mentions": "WHIP" in expert_text.upper(),
                    "Strikeout mentions": any(term in expert_text.upper() for term in ["K/9", "STRIKEOUT", "STRIKEOUTS"]),
                    "Recent form": any(term in expert_text.lower() for term in ["recent", "last start", "form"]),
                    "Pitcher names": any(term in expert_text.lower() for term in ["pitcher", "pitching"])
                }
                
                print("\n📋 PITCHER INTELLIGENCE IN ANALYSIS:")
                for check, found in pitcher_mentions.items():
                    status = "✅" if found else "❌"
                    print(f"  {status} {check}: {'DETECTED' if found else 'MISSING'}")
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pitcher_panel_analysis_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "game": game,
                        "pitcher_panel": pitcher_panel,
                        "analysis": analysis_data,
                        "pitcher_mentions": pitcher_mentions
                    }, f, indent=2)
                
                print(f"💾 Analysis saved to: {filename}")
                
            else:
                print(f"❌ Custom Chronulus error: {result}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing with Custom Chronulus: {e}")

if __name__ == "__main__":
    asyncio.run(test_pitcher_stats_panel())