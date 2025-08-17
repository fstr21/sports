#!/usr/bin/env python3
"""
Analyze the leagues response we got

The API returned: {'count': 128, 'results': [...]}
Let's properly parse this and find our target leagues.
"""

import json
import glob
from datetime import datetime

def find_latest_leagues_file():
    """Find the most recent leagues JSON file"""
    files = glob.glob("soccerdata_leagues_*.json")
    if not files:
        print("❌ No leagues JSON files found")
        return None
    
    # Get the most recent file
    latest_file = max(files, key=lambda x: x.split('_')[-1])
    print(f"📁 Using file: {latest_file}")
    return latest_file

def analyze_leagues_data():
    """Analyze the leagues data we received"""
    
    # Find the JSON file
    json_file = find_latest_leagues_file()
    if not json_file:
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("🏆 ANALYZING SOCCERDATAAPI LEAGUES")
        print("=" * 50)
        
        # Check the structure
        if isinstance(data, dict) and 'results' in data:
            leagues_list = data['results']
            total_count = data.get('count', len(leagues_list))
            
            print(f"✅ Found {len(leagues_list)} leagues (API says {total_count} total)")
            
            # Target leagues we care about
            target_leagues = {
                "premier league": ["premier league", "english premier", "epl"],
                "la liga": ["la liga", "primera division", "laliga", "primera división"],
                "mls": ["mls", "major league soccer"],
                "serie a": ["serie a", "italian serie"],
                "bundesliga": ["bundesliga", "german bundesliga"],
                "ligue 1": ["ligue 1", "french ligue"],
                "champions league": ["champions league", "uefa champions"],
                "europa league": ["europa league", "uefa europa"]
            }
            
            found_leagues = {}
            all_leagues_by_country = {}
            
            print(f"\n🔍 Searching through {len(leagues_list)} leagues:")
            
            for league in leagues_list:
                if isinstance(league, dict):
                    league_name = str(league.get("name", "")).lower()
                    league_id = league.get("id")
                    country_info = league.get("country", {})
                    country_name = country_info.get("name", "Unknown") if isinstance(country_info, dict) else str(country_info)
                    is_cup = league.get("is_cup", False)
                    
                    # Group by country for overview
                    if country_name not in all_leagues_by_country:
                        all_leagues_by_country[country_name] = []
                    all_leagues_by_country[country_name].append({
                        "id": league_id,
                        "name": league.get("name"),
                        "is_cup": is_cup
                    })
                    
                    # Check against our target leagues
                    for target_key, search_terms in target_leagues.items():
                        for term in search_terms:
                            if term in league_name:
                                found_leagues[target_key] = {
                                    "id": league_id,
                                    "name": league.get("name"),
                                    "country": country_name,
                                    "is_cup": is_cup
                                }
                                print(f"   ✅ {target_key.upper()}: ID {league_id} - {league.get('name')} ({country_name})")
                                break
            
            # Show what we found
            print(f"\n🎯 KEY LEAGUES FOR BETTING:")
            print("=" * 40)
            
            priority_leagues = ["premier league", "la liga", "mls"]
            for league_key in priority_leagues:
                if league_key in found_leagues:
                    info = found_leagues[league_key]
                    print(f"✅ {league_key.upper()}")
                    print(f"   ID: {info['id']}")
                    print(f"   Name: {info['name']}")
                    print(f"   Country: {info['country']}")
                    print()
                else:
                    print(f"❌ {league_key.upper()}: Not found")
            
            # Show other interesting leagues
            other_leagues = ["serie a", "bundesliga", "ligue 1", "champions league"]
            found_others = [league for league in other_leagues if league in found_leagues]
            
            if found_others:
                print(f"🌟 OTHER MAJOR LEAGUES AVAILABLE:")
                for league_key in found_others:
                    info = found_leagues[league_key]
                    print(f"   {league_key.upper()}: ID {info['id']} - {info['name']}")
            
            # Show countries with most leagues
            print(f"\n🌍 TOP COUNTRIES BY LEAGUE COUNT:")
            country_counts = [(country, len(leagues)) for country, leagues in all_leagues_by_country.items()]
            country_counts.sort(key=lambda x: x[1], reverse=True)
            
            for country, count in country_counts[:10]:
                print(f"   {country}: {count} leagues")
                # Show a few league examples
                examples = all_leagues_by_country[country][:3]
                for example in examples:
                    cup_marker = " (Cup)" if example["is_cup"] else ""
                    print(f"      - {example['name']} (ID: {example['id']}){cup_marker}")
                if len(all_leagues_by_country[country]) > 3:
                    print(f"      ... and {len(all_leagues_by_country[country]) - 3} more")
            
            # Save our key findings
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"leagues_analysis_{timestamp}.json"
            
            analysis_output = {
                "summary": {
                    "total_leagues": len(leagues_list),
                    "api_reported_count": total_count,
                    "key_leagues_found": len([l for l in priority_leagues if l in found_leagues]),
                    "analysis_timestamp": timestamp
                },
                "key_leagues": found_leagues,
                "all_countries": {country: len(leagues) for country, leagues in all_leagues_by_country.items()},
                "next_steps": {
                    "premier_league_id": found_leagues.get("premier league", {}).get("id"),
                    "la_liga_id": found_leagues.get("la liga", {}).get("id"),
                    "mls_id": found_leagues.get("mls", {}).get("id")
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_output, f, indent=2, ensure_ascii=False)
            
            print(f"\n📁 Analysis saved to: {output_file}")
            
            # Final summary
            print(f"\n📊 FINAL ASSESSMENT:")
            print(f"   Total leagues available: {len(leagues_list)}")
            print(f"   Our priority leagues found: {len([l for l in priority_leagues if l in found_leagues])}/3")
            
            if all(league in found_leagues for league in priority_leagues):
                print(f"   ✅ SUCCESS: All priority leagues available!")
                print(f"   🎯 Ready to get teams and players")
            else:
                missing = [league for league in priority_leagues if league not in found_leagues]
                print(f"   ⚠️  Missing: {', '.join(missing)}")
            
        else:
            print(f"❌ Unexpected data structure: {type(data)}")
            print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
    
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_leagues_data()