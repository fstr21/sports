#!/usr/bin/env python3
"""
Get Kansas State complete roster with proper formatting
"""

import requests
import json

def get_kansas_state_roster():
    """Get complete Kansas State roster"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    print("🏈 Kansas State Wildcats - Complete Roster")
    print("=" * 60)
    
    try:
        # Get 2024 roster (most complete data)
        response = requests.get(
            f"{base_url}/roster", 
            headers=headers, 
            params={"team": "Kansas State", "year": 2024}, 
            timeout=15
        )
        
        if response.status_code == 200:
            roster = response.json()
            
            if roster:
                print(f"📊 Total Players: {len(roster)}")
                print(f"🗓️  Season: 2024")
                print(f"🏆 Conference: Big 12")
                print("=" * 60)
                
                # Group by position
                positions = {}
                for player in roster:
                    pos = player.get('position', 'Unknown')
                    if pos not in positions:
                        positions[pos] = []
                    positions[pos].append(player)
                
                # Define position order for better display
                position_order = ['QB', 'RB', 'FB', 'WR', 'TE', 'OL', 'C', 'OG', 'OT', 
                                'DL', 'DE', 'DT', 'NT', 'LB', 'ILB', 'OLB', 'CB', 'S', 'FS', 'SS', 'K', 'P', 'LS']
                
                # Display by position
                for position in position_order:
                    if position in positions:
                        players = positions[position]
                        print(f"\n🏈 {position} - {len(players)} player{'s' if len(players) != 1 else ''}")
                        print("-" * 50)
                        
                        # Sort by jersey number, handling None values
                        def sort_key(player):
                            jersey = player.get('jersey')
                            if jersey is None:
                                return 999
                            try:
                                return int(jersey)
                            except (ValueError, TypeError):
                                return 999
                        
                        sorted_players = sorted(players, key=sort_key)
                        
                        for player in sorted_players:
                            # Get player info
                            first_name = player.get('firstName', '')
                            last_name = player.get('lastName', '')
                            name = f"{first_name} {last_name}".strip()
                            jersey = player.get('jersey', 'N/A')
                            year = player.get('year', 'N/A')
                            height = player.get('height', 0)
                            weight = player.get('weight', 0)
                            home_city = player.get('homeCity', '')
                            home_state = player.get('homeState', '')
                            
                            # Format height (convert inches to feet-inches)
                            if height and height > 0:
                                feet = height // 12
                                inches = height % 12
                                height_str = f"{feet}'{inches}\""
                            else:
                                height_str = "N/A"
                            
                            # Format weight
                            weight_str = f"{weight}" if weight and weight > 0 else "N/A"
                            
                            # Format hometown
                            hometown = f"{home_city}, {home_state}" if home_city and home_state else "N/A"
                            
                            # Format year
                            year_map = {1: "FR", 2: "SO", 3: "JR", 4: "SR", 5: "5Y"}
                            year_str = year_map.get(year, str(year) if year else "N/A")
                            
                            print(f"   #{jersey:>2} {name:<25} {year_str:>2} {height_str:>5} {weight_str:>3}lbs {hometown}")
                
                # Show any remaining positions not in our predefined list
                remaining_positions = set(positions.keys()) - set(position_order)
                for position in sorted(remaining_positions):
                    players = positions[position]
                    print(f"\n🏈 {position} - {len(players)} player{'s' if len(players) != 1 else ''}")
                    print("-" * 50)
                    
                    for player in players:
                        first_name = player.get('firstName', '')
                        last_name = player.get('lastName', '')
                        name = f"{first_name} {last_name}".strip()
                        jersey = player.get('jersey', 'N/A')
                        print(f"   #{jersey:>2} {name}")
                
                # Summary stats
                print(f"\n📈 ROSTER SUMMARY")
                print("=" * 30)
                for pos in sorted(positions.keys()):
                    count = len(positions[pos])
                    print(f"{pos:>3}: {count:>2} players")
                
                return roster
            else:
                print("⚠️  No roster data found")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return []

if __name__ == "__main__":
    roster = get_kansas_state_roster()
    
    if roster:
        print(f"\n✅ SUCCESS: Retrieved complete Kansas State roster!")
        print("🎉 Player data is fully available through the CFBD API!")
    else:
        print("\n❌ Failed to retrieve roster data")