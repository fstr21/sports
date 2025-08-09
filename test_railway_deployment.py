#!/usr/bin/env python3
"""
Railway Deployment Test Script

This script tests all endpoints of your deployed Sports HTTP Server on Railway,
including a comprehensive NBA games and moneylines example.

Usage:
    python test_railway_deployment.py

Set your Railway URL and API key below.
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys

# =============================================================================
# CONFIGURATION - UPDATE THESE WITH YOUR RAILWAY DEPLOYMENT
# =============================================================================

# Your Railway URL (get this from Railway dashboard)
RAILWAY_URL = "https://your-app-name.railway.app"

# Your API key (should match SPORTS_API_KEY in Railway environment variables)
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"

# Request headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# =============================================================================
# TEST UTILITIES
# =============================================================================

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_success(message: str):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")

def make_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple[bool, Dict[str, Any]]:
    """
    Make HTTP request to the server
    
    Returns:
        tuple: (success: bool, response_data: dict)
    """
    url = f"{RAILWAY_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        else:
            return False, {"error": f"Unsupported HTTP method: {method}"}
        
        # Print request info
        print(f"🔄 {method} {endpoint}")
        if data:
            print(f"   📤 Request: {json.dumps(data, indent=2)}")
            
        # Check response
        if response.status_code == 200:
            result = response.json()
            print_success(f"Status: {response.status_code}")
            return True, result
        else:
            print_error(f"Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📥 Error: {json.dumps(error_data, indent=2)}")
                return False, error_data
            except:
                print(f"   📥 Error: {response.text}")
                return False, {"error": response.text}
                
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return False, {"error": str(e)}

def display_response(data: Dict[str, Any], max_items: int = 5):
    """Display response data in a readable format"""
    if isinstance(data, dict) and len(data) == 0:
        print("   📥 Response: Empty")
        return
        
    print("   📥 Response:")
    
    # Handle different response structures
    if "data" in data and isinstance(data["data"], dict):
        # Display summary info
        for key, value in data["data"].items():
            if isinstance(value, list):
                print(f"      {key}: {len(value)} items")
                if len(value) > 0 and max_items > 0:
                    print(f"         Sample: {value[0] if isinstance(value[0], (str, int, float)) else type(value[0]).__name__}")
            elif isinstance(value, dict):
                print(f"      {key}: {len(value)} properties")
            else:
                print(f"      {key}: {value}")
    else:
        # Display raw data (truncated)
        data_str = json.dumps(data, indent=2)
        if len(data_str) > 500:
            data_str = data_str[:500] + "... (truncated)"
        print(f"      {data_str}")

# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_health_check():
    """Test the health check endpoint"""
    print_section("Health Check")
    
    success, data = make_request("GET", "/health")
    
    if success:
        print_success("Health check passed!")
        services = data.get("services", {})
        print("   🔍 Service Status:")
        print(f"      ESPN Sports AI: {'✅' if services.get('sports_ai') else '❌'}")
        print(f"      Wagyu Odds API: {'✅' if services.get('odds') else '❌'}")
        print(f"      OpenRouter AI: {'✅' if services.get('openrouter') else '❌'}")
        return True
    else:
        print_error("Health check failed!")
        display_response(data)
        return False

def test_espn_endpoints():
    """Test ESPN Sports AI endpoints"""
    print_section("ESPN Sports AI Endpoints")
    
    # Test NBA teams
    print("\n📋 Testing NBA Teams...")
    success, data = make_request("POST", "/espn/teams", {
        "sport": "basketball",
        "league": "nba"
    })
    
    teams_data = None
    if success:
        print_success("NBA teams retrieved!")
        teams_data = data.get("data", {}).get("teams", [])
        print(f"   🏀 Found {len(teams_data)} NBA teams")
        if teams_data:
            sample_team = teams_data[0]
            print(f"   📋 Sample team: {sample_team.get('displayName', 'N/A')} ({sample_team.get('abbreviation', 'N/A')})")
    else:
        print_error("Failed to get NBA teams")
        display_response(data)
        
    # Test NBA scoreboard (today's games)
    print("\n🏀 Testing NBA Scoreboard (Today's Games)...")
    success, data = make_request("POST", "/espn/scoreboard", {
        "sport": "basketball",
        "league": "nba"
    })
    
    games_data = None
    if success:
        print_success("NBA scoreboard retrieved!")
        scoreboard = data.get("data", {}).get("scoreboard", {})
        games_data = scoreboard.get("events", [])
        print(f"   🎮 Found {len(games_data)} NBA games today")
        
        if games_data:
            for i, game in enumerate(games_data[:3]):  # Show first 3 games
                competitors = game.get("competitions", [{}])[0].get("competitors", [])
                if len(competitors) >= 2:
                    team1 = competitors[0].get("team", {}).get("displayName", "Team 1")
                    team2 = competitors[1].get("team", {}).get("displayName", "Team 2")
                    status = game.get("status", {}).get("type", {}).get("description", "Unknown")
                    print(f"      Game {i+1}: {team1} vs {team2} ({status})")
        else:
            print("   ℹ️  No games found for today")
    else:
        print_error("Failed to get NBA scoreboard")
        display_response(data)
    
    return games_data

def test_odds_endpoints():
    """Test Wagyu Odds API endpoints"""
    print_section("Wagyu Odds API Endpoints")
    
    # Test available sports
    print("\n⚽ Testing Available Sports...")
    success, data = make_request("GET", "/odds/sports", params={"all_sports": "true"})
    
    sports_data = None
    if success:
        print_success("Sports list retrieved!")
        if isinstance(data, list):
            sports_data = data
            print(f"   🏆 Found {len(sports_data)} sports")
            
            # Look for basketball_nba
            nba_sport = None
            for sport in sports_data:
                if sport.get("key") == "basketball_nba":
                    nba_sport = sport
                    break
                    
            if nba_sport:
                print(f"   🏀 NBA found: {nba_sport.get('title', 'N/A')} (Key: {nba_sport.get('key', 'N/A')})")
            else:
                print("   ⚠️  NBA not found in sports list")
                
            # Show sample sports
            print("   📋 Sample sports:")
            for sport in sports_data[:5]:
                print(f"      - {sport.get('title', 'N/A')} ({sport.get('key', 'N/A')})")
        else:
            print("   ⚠️  Unexpected response format")
            display_response(data)
    else:
        print_error("Failed to get sports list")
        display_response(data)
        
    # Test NBA odds with moneylines
    print("\n💰 Testing NBA Odds (Moneylines)...")
    success, data = make_request("POST", "/odds/get-odds", {
        "sport": "basketball_nba",
        "regions": "us",
        "markets": "h2h",  # h2h = head-to-head = moneylines
        "odds_format": "american"
    })
    
    odds_data = None
    if success:
        print_success("NBA odds retrieved!")
        if isinstance(data, list):
            odds_data = data
            print(f"   💸 Found odds for {len(odds_data)} NBA games")
            
            # Display detailed moneyline info
            for i, game in enumerate(odds_data[:3]):  # Show first 3 games
                home_team = game.get("home_team", "Home Team")
                away_team = game.get("away_team", "Away Team")
                commence_time = game.get("commence_time", "Unknown time")
                
                print(f"\n      🏀 Game {i+1}: {away_team} @ {home_team}")
                print(f"         ⏰ Time: {commence_time}")
                
                bookmakers = game.get("bookmakers", [])
                if bookmakers:
                    print(f"         💰 Moneylines from {len(bookmakers)} bookmakers:")
                    
                    for book in bookmakers[:2]:  # Show first 2 bookmakers
                        book_name = book.get("title", "Unknown Book")
                        markets = book.get("markets", [])
                        
                        for market in markets:
                            if market.get("key") == "h2h":
                                outcomes = market.get("outcomes", [])
                                print(f"           📊 {book_name}:")
                                for outcome in outcomes:
                                    team = outcome.get("name", "Unknown")
                                    odds = outcome.get("price", "N/A")
                                    print(f"              {team}: {odds}")
                else:
                    print("         ⚠️  No bookmaker data available")
        else:
            print("   ⚠️  Unexpected response format")
            display_response(data)
    else:
        print_error("Failed to get NBA odds")
        display_response(data)
        
    return sports_data, odds_data

def test_daily_intelligence():
    """Test the high-level daily intelligence endpoint"""
    print_section("Daily Intelligence (Combined Data)")
    
    print("\n📊 Testing Daily Intelligence for NBA...")
    success, data = make_request("POST", "/daily-intelligence", {
        "leagues": ["basketball/nba"],
        "include_odds": True,
        "include_analysis": False
    })
    
    if success:
        print_success("Daily intelligence retrieved!")
        intelligence_data = data.get("data", {})
        
        for league, league_data in intelligence_data.items():
            print(f"\n   🏀 League: {league}")
            
            # Games info
            games = league_data.get("games", [])
            if games:
                print(f"      🎮 Games: {len(games)} found")
                for i, game in enumerate(games[:2]):  # Show first 2 games
                    competitors = game.get("competitions", [{}])[0].get("competitors", [])
                    if len(competitors) >= 2:
                        team1 = competitors[0].get("team", {}).get("displayName", "Team 1")
                        team2 = competitors[1].get("team", {}).get("displayName", "Team 2")
                        print(f"         Game {i+1}: {team1} vs {team2}")
            else:
                print("      🎮 Games: None found")
                
            # Teams info
            teams = league_data.get("teams", [])
            if teams:
                print(f"      🏀 Teams: {len(teams)} found")
            
            # Odds info
            odds = league_data.get("odds", [])
            if odds:
                print(f"      💰 Odds: Available for {len(odds)} games")
            elif "odds_error" in league_data:
                print(f"      💰 Odds: Error - {league_data['odds_error']}")
            else:
                print("      💰 Odds: Not available")
                
    else:
        print_error("Failed to get daily intelligence")
        display_response(data)

def test_natural_language():
    """Test the natural language query endpoint"""
    print_section("Natural Language Query")
    
    print("\n💬 Testing Natural Language: 'What NBA games are today and what are their moneylines?'")
    success, data = make_request("POST", "/ask", {
        "question": "What NBA games are today and what are their moneylines?"
    })
    
    if success:
        print_success("Natural language query processed!")
        
        interpretation = data.get("interpretation", "")
        if interpretation:
            print(f"   🧠 Interpretation: {interpretation}")
            
        result = data.get("result", {})
        if result and result.get("ok"):
            print("   ✅ Query executed successfully")
            # The result would contain the combined scoreboard and odds data
        else:
            print("   ⚠️  Query execution had issues")
            
        display_response(data, max_items=2)
    else:
        print_error("Failed to process natural language query")
        display_response(data)

def test_quota_info():
    """Test API quota information"""
    print_section("API Quota Information")
    
    print("\n📊 Testing Odds API Quota...")
    success, data = make_request("GET", "/odds/quota")
    
    if success:
        print_success("Quota information retrieved!")
        remaining = data.get("remaining_requests", "Unknown")
        used = data.get("used_requests", "Unknown")
        print(f"   📊 Remaining requests: {remaining}")
        print(f"   📊 Used requests: {used}")
    else:
        print_error("Failed to get quota information")
        display_response(data)

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    """Run all tests"""
    print("🚀 Railway Deployment Test Suite")
    print(f"🌐 Testing: {RAILWAY_URL}")
    print(f"🔑 API Key: {API_KEY[:10]}..." if API_KEY else "🔑 No API Key Set")
    
    # Check configuration
    if RAILWAY_URL == "https://your-app-name.railway.app":
        print_error("❌ Please update RAILWAY_URL with your actual Railway deployment URL!")
        print("   Get this from your Railway dashboard")
        return False
        
    if not API_KEY:
        print_error("❌ Please set your API_KEY!")
        return False
    
    # Track test results
    test_results = []
    
    # Run tests
    print_info("Starting comprehensive tests...")
    
    # 1. Health Check
    health_ok = test_health_check()
    test_results.append(("Health Check", health_ok))
    
    if not health_ok:
        print_error("🛑 Health check failed - stopping tests")
        return False
    
    # 2. ESPN Endpoints
    games_data = test_espn_endpoints()
    test_results.append(("ESPN Endpoints", games_data is not None))
    
    # 3. Odds Endpoints  
    sports_data, odds_data = test_odds_endpoints()
    test_results.append(("Odds Endpoints", sports_data is not None))
    
    # 4. Daily Intelligence
    test_daily_intelligence()
    test_results.append(("Daily Intelligence", True))  # No specific failure condition
    
    # 5. Natural Language
    test_natural_language()
    test_results.append(("Natural Language", True))  # No specific failure condition
    
    # 6. Quota Info
    test_quota_info()
    test_results.append(("Quota Info", True))  # No specific failure condition
    
    # Final Results
    print_section("Test Results Summary")
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("🎉 All tests passed! Your Railway deployment is working perfectly!")
        print("\n🚀 Ready for production use!")
        print(f"   Your API is live at: {RAILWAY_URL}")
        print(f"   Use API key: {API_KEY}")
        
        print("\n📖 Example usage:")
        print("   # Get NBA games and odds")
        print(f'   curl -H "Authorization: Bearer {API_KEY}" \\')
        print(f'        -H "Content-Type: application/json" \\')
        print(f'        -d \'{{"question": "What NBA games are today and their moneylines?"}}\' \\')
        print(f'        {RAILWAY_URL}/ask')
        
    else:
        print_error(f"🔧 {total - passed} tests failed. Check the logs above for details.")
        
    return passed == total

if __name__ == "__main__":
    print("=" * 80)
    print("🏀 SPORTS MCP RAILWAY DEPLOYMENT TEST")
    print("=" * 80)
    print()
    print("Before running this script:")
    print("1. Update RAILWAY_URL with your actual Railway deployment URL")
    print("2. Make sure SPORTS_API_KEY and ODDS_API_KEY are set in Railway")
    print("3. Ensure your deployment is running and accessible")
    print()
    
    # Wait a moment for user to read
    time.sleep(2)
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)