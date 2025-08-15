#!/usr/bin/env python3
"""
CFB Rankings Tool - Test college football rankings endpoint
"""

import asyncio
import json
import httpx

# Test the rankings endpoint
async def test_cfb_rankings():
    """Test CFB rankings endpoint"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    test_cases = [
        {
            "name": "2024 Final Rankings",
            "params": {"year": 2024, "week": 15}
        },
        {
            "name": "2024 Week 1 Rankings",
            "params": {"year": 2024, "week": 1}
        },
        {
            "name": "2024 Postseason Rankings",
            "params": {"year": 2024, "seasonType": "postseason"}
        }
    ]
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        for test in test_cases:
            print(f"\n🏆 Testing: {test['name']}")
            print("-" * 40)
            
            try:
                response = await client.get(
                    f"{base_url}/rankings",
                    headers=headers,
                    params=test['params']
                )
                
                if response.status_code == 200:
                    rankings = response.json()
                    print(f"✅ Success: Found {len(rankings)} ranking periods")
                    
                    for ranking_period in rankings:
                        season = ranking_period.get('season')
                        week = ranking_period.get('week')
                        season_type = ranking_period.get('seasonType')
                        polls = ranking_period.get('polls', [])
                        
                        print(f"\n📅 {season} {season_type} Week {week}")
                        print(f"   Found {len(polls)} polls")
                        
                        for poll in polls:
                            poll_name = poll.get('poll', 'Unknown')
                            ranks = poll.get('ranks', [])
                            
                            print(f"\n   🗳️  {poll_name} (Top 10):")
                            for rank in ranks[:10]:
                                rank_num = rank.get('rank')
                                school = rank.get('school')
                                conference = rank.get('conference', 'Independent')
                                points = rank.get('points', 0)
                                first_place = rank.get('firstPlaceVotes', 0)
                                
                                first_place_str = f" ({first_place} 1st)" if first_place > 0 else ""
                                print(f"      {rank_num:2}. {school} ({conference}) - {points} pts{first_place_str}")
                        
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_cfb_rankings())