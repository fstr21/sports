#!/usr/bin/env python3
"""
ESPN API Data Validator - Specific Game Dates
Tests data from completed game (Aug 3, 2025) and future game (Aug 7, 2025)
Generates verified data availability with real examples from both scenarios
"""

import asyncio
import json
from datetime import datetime
import httpx

ESPN_BASE_URL = "http://site.api.espn.com/apis/site/v2/sports"

class ESPNDataValidator:
    def __init__(self):
        self.results = {
            "game_data": {},
            "team_data": {},
            "news_data": {},
            "standings_data": {},
            "validation_summary": {}
        }
        self.test_count = 0
        self.passed_count = 0
    
    async def fetch_data(self, endpoint: str) -> dict:
        """Fetch data from ESPN API"""
        url = f"{ESPN_BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(url, headers={
                    "user-agent": "espn-data-validator/1.0",
                    "accept": "application/json"
                })
                response.raise_for_status()
                return {"success": True, "data": response.json(), "status": response.status_code}
            except Exception as e:
                return {"success": False, "error": str(e), "data": None}
    
    def validate_field(self, data, field_path, description):
        """Validate if a specific field exists in the data"""
        self.test_count += 1
        try:
            current = data
            for key in field_path.split('.'):
                if '[' in key and ']' in key:
                    # Handle array access like "events[0]"
                    array_key = key.split('[')[0]
                    index = int(key.split('[')[1].split(']')[0])
                    current = current[array_key][index]
                else:
                    current = current[key]
            
            self.passed_count += 1
            return {
                "available": True,
                "value": current,
                "type": type(current).__name__,
                "description": description
            }
        except (KeyError, IndexError, TypeError):
            return {
                "available": False,
                "value": None,
                "type": "missing",
                "description": description
            }
    
    async def test_game_data(self):
        """Test game data from specific dates"""
        print("🏀 Testing Game Data...")
        
        # Test completed game from August 3, 2025
        print("   📅 Testing completed game (August 3, 2025)...")
        completed_result = await self.fetch_data("/basketball/wnba/scoreboard?dates=20250803")
        
        # Test future game from August 7, 2025  
        print("   📅 Testing future game (August 7, 2025)...")
        future_result = await self.fetch_data("/basketball/wnba/scoreboard?dates=20250807")
        
        # Use current scoreboard as fallback
        print("   📅 Testing current scoreboard...")
        current_result = await self.fetch_data("/basketball/wnba/scoreboard")
        
        # Choose the best data source
        result = None
        game_type = ""
        
        if completed_result["success"] and "events" in completed_result["data"] and len(completed_result["data"]["events"]) > 0:
            result = completed_result
            game_type = "completed_game_aug3"
            print("   ✅ Using completed game from August 3, 2025")
        elif future_result["success"] and "events" in future_result["data"] and len(future_result["data"]["events"]) > 0:
            result = future_result  
            game_type = "future_game_aug7"
            print("   ✅ Using future game from August 7, 2025")
        elif current_result["success"] and "events" in current_result["data"] and len(current_result["data"]["events"]) > 0:
            result = current_result
            game_type = "current_game"
            print("   ✅ Using current game data")
        else:
            self.results["game_data"]["error"] = "No game data available for any date"
            return
        
        data = result["data"]
        game_tests = {"game_type": game_type}
        
        # Basic Game Information
        if "events" in data and len(data["events"]) > 0:
            event = data["events"][0]
            
            game_tests["basic_info"] = {
                "game_id": self.validate_field(event, "id", "Unique game identifier"),
                "matchup": self.validate_field(event, "name", "Team matchup description"),
                "date_time": self.validate_field(event, "date", "Game date and time"),
                "short_name": self.validate_field(event, "shortName", "Abbreviated matchup"),
                "season_year": self.validate_field(event, "season.year", "Season year"),
                "season_type": self.validate_field(event, "season.type", "Season type (regular/playoffs)"),
            }
            
            # Competition data
            if "competitions" in event and len(event["competitions"]) > 0:
                comp = event["competitions"][0]
                
                game_tests["venue_info"] = {
                    "venue_name": self.validate_field(comp, "venue.fullName", "Stadium/arena name"),
                    "venue_city": self.validate_field(comp, "venue.address.city", "Venue city"),
                    "venue_state": self.validate_field(comp, "venue.address.state", "Venue state"),
                    "indoor_outdoor": self.validate_field(comp, "venue.indoor", "Indoor/outdoor venue"),
                    "attendance": self.validate_field(comp, "attendance", "Game attendance"),
                    "neutral_site": self.validate_field(comp, "neutralSite", "Neutral site game"),
                }
                
                game_tests["game_status"] = {
                    "status_type": self.validate_field(comp, "status.type.description", "Game status"),
                    "status_detail": self.validate_field(comp, "status.type.detail", "Detailed status"),
                    "clock": self.validate_field(comp, "status.displayClock", "Game clock"),
                    "period": self.validate_field(comp, "status.period", "Current period"),
                    "completed": self.validate_field(comp, "status.type.completed", "Game completed flag"),
                }
                
                # Team Information
                if "competitors" in comp and len(comp["competitors"]) >= 2:
                    team1 = comp["competitors"][0]
                    team2 = comp["competitors"][1]
                    
                    game_tests["team_basic"] = {
                        "team1_id": self.validate_field(team1, "team.id", "Team unique ID"),
                        "team1_name": self.validate_field(team1, "team.displayName", "Team full name"),
                        "team1_abbrev": self.validate_field(team1, "team.abbreviation", "Team abbreviation"),
                        "team1_location": self.validate_field(team1, "team.location", "Team location"),
                        "team1_color": self.validate_field(team1, "team.color", "Team primary color"),
                        "team1_alt_color": self.validate_field(team1, "team.alternateColor", "Team alternate color"),
                        "team1_logo": self.validate_field(team1, "team.logo", "Team logo URL"),
                        "home_away": self.validate_field(team1, "homeAway", "Home or away designation"),
                        "current_score": self.validate_field(team1, "score", "Current/final score"),
                        "winner": self.validate_field(team1, "winner", "Winner designation"),
                    }
                    
                    game_tests["team_records"] = {
                        "overall_record": self.validate_field(team1, "records[0].summary", "Overall win-loss record"),
                        "record_type": self.validate_field(team1, "records[0].type", "Record type (total/home/road)"),
                        "record_name": self.validate_field(team1, "records[0].name", "Record category name"),
                    }
                    
                    game_tests["team_statistics"] = {
                        "stat_name": self.validate_field(team1, "statistics[0].name", "Statistic name"),
                        "stat_value": self.validate_field(team1, "statistics[0].displayValue", "Statistic display value"),
                        "stat_abbreviation": self.validate_field(team1, "statistics[0].abbreviation", "Statistic abbreviation"),
                        "stat_ranking": self.validate_field(team1, "statistics[0].rankDisplayValue", "League ranking"),
                    }
                    
                    game_tests["player_leaders"] = {
                        "leader_category": self.validate_field(team1, "leaders[0].name", "Leadership category"),
                        "leader_display_name": self.validate_field(team1, "leaders[0].displayName", "Category display name"),
                        "player_name": self.validate_field(team1, "leaders[0].leaders[0].athlete.fullName", "Player full name"),
                        "player_display_name": self.validate_field(team1, "leaders[0].leaders[0].athlete.displayName", "Player display name"),
                        "player_value": self.validate_field(team1, "leaders[0].leaders[0].displayValue", "Statistical value"),
                        "player_jersey": self.validate_field(team1, "leaders[0].leaders[0].athlete.jersey", "Jersey number"),
                        "player_position": self.validate_field(team1, "leaders[0].leaders[0].athlete.position.abbreviation", "Player position"),
                        "player_headshot": self.validate_field(team1, "leaders[0].leaders[0].athlete.headshot", "Player photo URL"),
                        "player_profile_link": self.validate_field(team1, "leaders[0].leaders[0].athlete.links[0].href", "Player profile link"),
                    }
                
                # Betting Information
                game_tests["betting_info"] = {
                    "odds_provider": self.validate_field(comp, "odds[0].provider.name", "Betting provider name"),
                    "spread_details": self.validate_field(comp, "odds[0].details", "Point spread details"),
                    "over_under": self.validate_field(comp, "odds[0].overUnder", "Over/under total"),
                    "spread_line": self.validate_field(comp, "odds[0].spread", "Point spread number"),
                    "away_moneyline": self.validate_field(comp, "odds[0].awayTeamOdds.moneyLine", "Away team moneyline"),
                    "home_moneyline": self.validate_field(comp, "odds[0].homeTeamOdds.moneyLine", "Home team moneyline"),
                    "away_spread_odds": self.validate_field(comp, "odds[0].awayTeamOdds.spreadOdds", "Away spread odds"),
                    "home_spread_odds": self.validate_field(comp, "odds[0].homeTeamOdds.spreadOdds", "Home spread odds"),
                    "favorite": self.validate_field(comp, "odds[0].awayTeamOdds.favorite", "Favorite designation"),
                }
                
                # Broadcast Information
                game_tests["broadcast_info"] = {
                    "broadcast_network": self.validate_field(comp, "broadcasts[0].names[0]", "TV network"),
                    "broadcast_market": self.validate_field(comp, "broadcasts[0].market", "Broadcast market"),
                    "geo_broadcast_type": self.validate_field(comp, "geoBroadcasts[0].type.shortName", "Broadcast type"),
                    "geo_broadcast_media": self.validate_field(comp, "geoBroadcasts[0].media.shortName", "Media outlet"),
                }
                
                # Tickets
                game_tests["ticket_info"] = {
                    "ticket_summary": self.validate_field(comp, "tickets[0].summary", "Ticket pricing summary"),
                    "tickets_available": self.validate_field(comp, "tickets[0].numberAvailable", "Number of tickets available"),
                    "ticket_link": self.validate_field(comp, "tickets[0].links[0].href", "Ticket purchase link"),
                }
        
        self.results["game_data"] = game_tests
    
    async def test_team_data(self):
        """Test team data fields"""
        print("🏈 Testing Team Data (WNBA Teams)...")
        
        result = await self.fetch_data("/basketball/wnba/teams")
        if not result["success"]:
            self.results["team_data"]["error"] = result["error"]
            return
        
        data = result["data"]
        team_tests = {}
        
        if "sports" in data and len(data["sports"]) > 0:
            sport = data["sports"][0]
            if "leagues" in sport and len(sport["leagues"]) > 0:
                league = sport["leagues"][0]
                if "teams" in league and len(league["teams"]) > 0:
                    team_data = league["teams"][0]["team"]
                    
                    team_tests["team_profile"] = {
                        "team_id": self.validate_field(team_data, "id", "Team unique identifier"),
                        "team_uid": self.validate_field(team_data, "uid", "Team universal identifier"),
                        "team_slug": self.validate_field(team_data, "slug", "Team URL slug"),
                        "abbreviation": self.validate_field(team_data, "abbreviation", "Team abbreviation"),
                        "display_name": self.validate_field(team_data, "displayName", "Team display name"),
                        "short_display_name": self.validate_field(team_data, "shortDisplayName", "Short display name"),
                        "name": self.validate_field(team_data, "name", "Team name"),
                        "nickname": self.validate_field(team_data, "nickname", "Team nickname"),
                        "location": self.validate_field(team_data, "location", "Team location"),
                        "primary_color": self.validate_field(team_data, "color", "Primary color hex"),
                        "alternate_color": self.validate_field(team_data, "alternateColor", "Alternate color hex"),
                        "is_active": self.validate_field(team_data, "isActive", "Team active status"),
                        "is_all_star": self.validate_field(team_data, "isAllStar", "All-star team flag"),
                    }
                    
                    team_tests["team_branding"] = {
                        "logo_default": self.validate_field(team_data, "logos[0].href", "Default logo URL"),
                        "logo_width": self.validate_field(team_data, "logos[0].width", "Logo width"),
                        "logo_height": self.validate_field(team_data, "logos[0].height", "Logo height"),
                        "logo_dark": self.validate_field(team_data, "logos[1].href", "Dark theme logo URL"),
                    }
                    
                    team_tests["team_links"] = {
                        "clubhouse_link": self.validate_field(team_data, "links[0].href", "Team clubhouse link"),
                        "roster_link": self.validate_field(team_data, "links[1].href", "Team roster link"),
                        "stats_link": self.validate_field(team_data, "links[2].href", "Team statistics link"),
                        "schedule_link": self.validate_field(team_data, "links[3].href", "Team schedule link"),
                        "tickets_link": self.validate_field(team_data, "links[4].href", "Team tickets link"),
                        "link_text": self.validate_field(team_data, "links[0].text", "Link display text"),
                        "link_external": self.validate_field(team_data, "links[0].isExternal", "External link flag"),
                        "link_premium": self.validate_field(team_data, "links[0].isPremium", "Premium content flag"),
                    }
        
        self.results["team_data"] = team_tests
    
    async def test_news_data(self):
        """Test news and injury data fields"""
        print("📰 Testing News Data (WNBA News)...")
        
        result = await self.fetch_data("/basketball/wnba/news")
        if not result["success"]:
            self.results["news_data"]["error"] = result["error"]
            return
        
        data = result["data"]
        news_tests = {}
        
        if "articles" in data and len(data["articles"]) > 0:
            article = data["articles"][0]
            
            news_tests["article_info"] = {
                "article_id": self.validate_field(article, "id", "Article unique ID"),
                "headline": self.validate_field(article, "headline", "Article headline"),
                "description": self.validate_field(article, "description", "Article description"),
                "published": self.validate_field(article, "published", "Publication date"),
                "last_modified": self.validate_field(article, "lastModified", "Last modification date"),
                "article_type": self.validate_field(article, "type", "Article type"),
                "byline": self.validate_field(article, "byline", "Article author"),
                "premium": self.validate_field(article, "premium", "Premium content flag"),
            }
            
            news_tests["article_media"] = {
                "image_id": self.validate_field(article, "images[0].id", "Image ID"),
                "image_url": self.validate_field(article, "images[0].url", "Image URL"),
                "image_caption": self.validate_field(article, "images[0].caption", "Image caption"),
                "image_credit": self.validate_field(article, "images[0].credit", "Image credit"),
                "image_width": self.validate_field(article, "images[0].width", "Image width"),
                "image_height": self.validate_field(article, "images[0].height", "Image height"),
                "image_type": self.validate_field(article, "images[0].type", "Image type"),
            }
            
            news_tests["article_categories"] = {
                "category_id": self.validate_field(article, "categories[0].id", "Category ID"),
                "category_type": self.validate_field(article, "categories[0].type", "Category type"),
                "category_description": self.validate_field(article, "categories[0].description", "Category description"),
                "sport_id": self.validate_field(article, "categories[0].sportId", "Sport ID"),
                "team_id": self.validate_field(article, "categories[0].teamId", "Team ID"),
            }
            
            news_tests["article_links"] = {
                "web_link": self.validate_field(article, "links.web.href", "Web article link"),
                "mobile_link": self.validate_field(article, "links.mobile.href", "Mobile article link"),
                "api_link": self.validate_field(article, "links.api.self.href", "API link"),
            }
        
        self.results["news_data"] = news_tests
    
    async def test_standings_data(self):
        """Test standings data fields"""
        print("🏆 Testing Standings Data (WNBA Standings)...")
        
        result = await self.fetch_data("/basketball/wnba/standings")
        if not result["success"]:
            self.results["standings_data"]["error"] = result["error"]
            return
        
        data = result["data"]
        standings_tests = {}
        
        standings_tests["standings_info"] = {
            "full_view_link": self.validate_field(data, "fullViewLink.text", "Full standings link text"),
            "full_view_href": self.validate_field(data, "fullViewLink.href", "Full standings URL"),
        }
        
        # Note: WNBA standings endpoint returns minimal data, just links to full standings
        self.results["standings_data"] = standings_tests
    
    def generate_summary(self):
        """Generate validation summary"""
        self.results["validation_summary"] = {
            "total_tests": self.test_count,
            "passed_tests": self.passed_count,
            "success_rate": f"{(self.passed_count/self.test_count*100):.1f}%" if self.test_count > 0 else "0%",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting ESPN API Data Validation...")
        print("=" * 50)
        
        await self.test_game_data()
        await self.test_team_data()
        await self.test_news_data()
        await self.test_standings_data()
        
        self.generate_summary()
        
        print(f"\n✅ Validation Complete!")
        print(f"📊 Results: {self.passed_count}/{self.test_count} tests passed ({self.results['validation_summary']['success_rate']})")
        
        return self.results

async def main():
    validator = ESPNDataValidator()
    results = await validator.run_all_tests()
    
    # Save results to JSON file
    with open("espn_validation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📄 Detailed results saved to: espn_validation_results.json")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())