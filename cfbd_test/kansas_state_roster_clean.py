#!/usr/bin/env python3
"""
Get Kansas State roster with clean formatting
"""

import requests

def get_kansas_state_roster():
    """Get Kansas State roster with robust error handling"""
    
    api_key = "Z0NGwLNiztE/3/YtS+Jajy4tID7xbjON1UFh6s8q0XgpM66VEkMGHYCt6ALSud7Y"
    base_url = "https://api.collegefootballdata.com"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    print("🏈 Kansas State Wildcats - 2024 Roster")
    print("=" * 60)
    
    try:
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
                print(f"🏆 Conference: Big 12")
                print("=" * 60)
                
                # Group by position
                positions = {}
                for player in roster:
                    pos = player.get('position', 'Unknown')
                    if pos not in positions:
                        positions[pos] = []
                    positions[pos].append(player)
                
                # Position order
                position_order = ['QB', 'RB', 'FB', 'WR', 'TE', 'OL', 'C', 'OG', 'OT', 
                                'DL', 'DE', 'DT', 'NT', 'LB', 'ILB', 'OLB', 'CB', 'S', 'FS', 'SS', 'K', 'P', 'LS']
                
                for position in position_order:
                    if position in positions:
                        players = positions[position]
                        print(f"\n🏈 {position} ({len(players)} players)")
                        print("-" * 40)
                        
                        # Sort by jersey number safely
                        def safe_sort_key(player):
                            jersey = player.get('jersey')
                            if jersey is None:
                                return 999
                            try:
                                return int(jersey)
                            except:
                                return 999
                        
                        sorted_players = sorted(players, key=safe_sort_key)
                        
                        for player in sorted_players:
                            # Safely get all fields
                            first_name = player.get('firstName') or ''
                            last_name = player.get('lastName') or ''
                            name = f"{first_name} {last_name}".strip() or 'Unknown'
                            
                            jersey = player.get('jersey')
                            jersey_str = str(jersey) if jersey is not None else 'N/A'
                            
                            year = player.get('year')
                            year_map = {1: "FR", 2: "SO", 3: "JR", 4: "SR", 5: "5Y"}
                            year_str = year_map.get(year, str(year) if year else 'N/A')
                            
                            height = player.get('height')
                            if height and height > 0:
                                feet = height // 12
                                inches = height % 12
                                height_str = f"{feet}'{inches}\""
                            else:
                                height_str = "N/A"
                            
                            weight = player.get('weight')
                            weight_str = f"{weight}lbs" if weight and weight > 0 else "N/A"
                            
                            home_city = player.get('homeCity') or ''
                            home_state = player.get('homeState') or ''
                            hometown = f"{home_city}, {home_state}" if home_city and home_state else "N/A"
                            
                            print(f"   #{jersey_str:>2} {name:<25} {year_str:>2} {height_str:>5} {weight_str:>6} {hometown}")
                
                # Show summary
                print(f"\n📈 POSITION BREAKDOWN")
                print("=" * 30)
                total_players = 0
                for pos in sorted(positions.keys()):
                    count = len(positions[pos])
                    total_players += count
                    print(f"{pos:>3}: {count:>2} players")
                
                print(f"\nTotal: {total_players} players")
                
                # Show some key players
                print(f"\n⭐ KEY PLAYERS TO WATCH")
                print("=" * 30)
                
                key_positions = ['QB', 'RB', 'WR']
                for pos in key_positions:
                    if pos in positions:
                        players = positions[pos][:3]  # Top 3 by jersey number
                        for player in players:
                            name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                            jersey = player.get('jersey', 'N/A')
                            year = player.get('year', 0)
                            year_str = {1: "FR", 2: "SO", 3: "JR", 4: "SR", 5: "5Y"}.get(year, str(year))
                            print(f"   {pos}: #{jersey} {name} ({year_str})")
                
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
        print(f"\n✅ SUCCESS: Kansas State roster retrieved!")
        print("🎉 Full player data available through CFBD API!")
        print("\n💡 Available data includes:")
        print("   • Player names, positions, jersey numbers")
        print("   • Height, weight, class year")
        print("   • Hometown information")
        print("   • Player statistics (separate endpoint)")
        print("   • Player usage data")
    else:
        print("\n❌ Failed to retrieve roster")