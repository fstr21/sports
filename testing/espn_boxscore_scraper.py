#!/usr/bin/env python3
"""
ESPN WNBA Boxscore Web Scraper
Scrapes player stats from ESPN boxscore pages
"""

import sys
import httpx
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional
import re

def scrape_boxscore(game_id: str) -> Dict[str, Any]:
    """Scrape player stats from ESPN boxscore webpage"""
    
    url = f"https://www.espn.com/wnba/boxscore/_/gameId/{game_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    print(f"🔍 Scraping: {url}")
    
    with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
        try:
            response = client.get(url)
            response.raise_for_status()
            
            print(f"✅ Page loaded successfully (Status: {response.status_code})")
            print(f"📄 Content length: {len(response.text)} characters")
            
            # Save HTML for debugging (optional)
            debug_file = f"debug_boxscore_{game_id}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"🔧 Saved HTML to {debug_file} for debugging")
            
            return parse_boxscore_html(response.text, game_id)
            
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"Response: {e.response.text[:200]}...")
            raise
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            raise

def parse_boxscore_html(html_content: str, game_id: str) -> Dict[str, Any]:
    """Parse the HTML content to extract player stats"""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find game info
    game_info = extract_game_info(soup)
    
    # Find player stats tables
    teams_data = extract_player_stats(soup)
    
    return {
        "game_id": game_id,
        "game_info": game_info,
        "teams": teams_data
    }

def extract_game_info(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract basic game information"""
    
    game_info = {}
    
    # Try to find game header/title
    title_elem = soup.find('title')
    if title_elem:
        game_info['title'] = title_elem.get_text().strip()
    
    # Look for team names and scores
    # ESPN often uses specific classes for team info
    team_elements = soup.find_all(['div', 'span'], class_=re.compile(r'team|competitor', re.I))
    
    # Look for score elements
    score_elements = soup.find_all(['div', 'span'], class_=re.compile(r'score', re.I))
    
    # Look for game status
    status_elements = soup.find_all(['div', 'span'], class_=re.compile(r'status|game-status', re.I))
    
    print(f"🏀 Found {len(team_elements)} team elements")
    print(f"📊 Found {len(score_elements)} score elements") 
    print(f"⏰ Found {len(status_elements)} status elements")
    
    return game_info

def extract_player_stats(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract player statistics from boxscore tables"""
    
    teams_data = []
    player_name_tables = []
    stats_tables = []
    
    # Look for boxscore tables - ESPN typically uses tables for stats
    tables = soup.find_all('table')
    print(f"📋 Found {len(tables)} tables on page")
    
    # Look for specific boxscore containers
    boxscore_containers = soup.find_all(['div', 'section'], class_=re.compile(r'boxscore|stats|player', re.I))
    print(f"📦 Found {len(boxscore_containers)} potential boxscore containers")
    
    # Categorize tables into player names vs stats
    for i, table in enumerate(tables):
        print(f"\n🔍 Analyzing table {i+1}:")
        
        # Check if this looks like a stats table
        all_cells = table.find_all(['th', 'td'])
        cell_text = [h.get_text().strip().upper() for h in all_cells[:30]]  # First 30 cells
        
        # Look for common basketball stat abbreviations
        stat_indicators = ['MIN', 'FG', 'FGA', '3PT', 'FT', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']
        player_indicators = ['STARTERS', 'BENCH', '#']
        
        found_stats = [stat for stat in stat_indicators if any(stat in cell for cell in cell_text)]
        found_players = [indicator for indicator in player_indicators if any(indicator in cell for cell in cell_text)]
        
        print(f"  📋 Sample cell content: {cell_text[:10]}")
        
        if found_stats and len(found_stats) >= 5:
            print(f"  📊 Stats table! Found: {found_stats}")
            stats_tables.append((i, table))
            
        elif found_players:
            print(f"  👤 Player names table! Found: {found_players}")
            player_name_tables.append((i, table))
            
        else:
            print(f"  ❌ Not a relevant table. Sample: {cell_text[:5]}...")
    
    # Extract team names from page title if possible
    title_elem = soup.find('title')
    team_names_from_title = []
    if title_elem:
        title = title_elem.get_text()
        # Title is usually like "Liberty 87-78 Sun (Aug 3, 2025) Box Score - ESPN"
        if ' vs ' in title or '-' in title:
            # Try to extract team names
            parts = title.split(' Box Score')[0]  # Remove " Box Score - ESPN"
            if '-' in parts:
                # Format like "Liberty 87-78 Sun"
                score_part = parts.split('(')[0].strip()  # Remove date part
                # Extract team names around the score
                match = re.match(r'(.+?)\s+\d+\s*-\s*\d+\s+(.+)', score_part)
                if match:
                    team_names_from_title = [match.group(1).strip(), match.group(2).strip()]
    
    print(f"🏷️ Extracted team names from title: {team_names_from_title}")
    
    # Now try to match player name tables with stats tables
    print(f"\n🔗 Matching {len(player_name_tables)} name tables with {len(stats_tables)} stats tables")
    
    for i, (name_idx, name_table) in enumerate(player_name_tables):
        # Match each name table to its corresponding stats table
        # ESPN typically has: Table 2 (names) -> Table 3 (stats), Table 4 (names) -> Table 5 (stats)
        
        if i < len(stats_tables):
            # Use the i-th stats table for the i-th name table
            stats_idx, closest_stats_table = stats_tables[i]
            print(f"  🎯 Matching name table {name_idx} with stats table {stats_idx}")
        else:
            # Fallback to closest distance matching
            closest_stats_table = None
            min_distance = float('inf')
            stats_idx = None
            
            for s_idx, stats_table in stats_tables:
                distance = abs(s_idx - name_idx)
                if distance < min_distance:
                    min_distance = distance
                    closest_stats_table = stats_table
                    stats_idx = s_idx
            
            print(f"  🎯 Fallback matching name table {name_idx} with stats table {stats_idx}")
        
        if closest_stats_table is not None:
            print(f"  🎯 Matching name table {name_idx} with stats table")
            
            # Use team name from title if available, otherwise extract from table
            if i < len(team_names_from_title):
                team_name = team_names_from_title[i]
            else:
                team_name = extract_team_name_from_table(name_table)
            
            # Extract player names
            player_names = extract_players_from_table(name_table)
            
            # Extract stats
            player_stats = extract_players_from_table(closest_stats_table)
            
            # Combine names and stats
            combined_players = combine_names_and_stats(player_names, player_stats)
            
            if combined_players:
                teams_data.append({
                    "team_name": team_name,
                    "players": combined_players,
                    "name_table_index": name_idx,
                    "stats_table_index": stats_idx
                })
                
                print(f"  👥 Created team {team_name} with {len(combined_players)} players")
    
    return teams_data

def combine_names_and_stats(player_names: List[Dict], player_stats: List[Dict]) -> List[Dict]:
    """Combine player names with their stats"""
    combined = []
    
    # Filter out non-player entries from names (like "STARTERS", "BENCH")
    actual_names = [p for p in player_names if p.get('name') and len(p.get('name', '')) > 3]
    
    # Filter out team totals from stats (usually the last row with very high numbers)
    filtered_stats = []
    for stat_row in player_stats:
        points = stat_row.get('points', 0)
        # Skip rows that look like team totals (usually > 50 points for a single "player")
        if points > 50:
            print(f"    🚫 Skipping team total row: {points} PTS")
            continue
        filtered_stats.append(stat_row)
    
    print(f"    🔗 Combining {len(actual_names)} names with {len(filtered_stats)} stat rows")
    
    # Debug: Show the alignment
    print(f"    🔍 DEBUG - Player name to stats alignment:")
    for i in range(max(len(actual_names), len(filtered_stats))):
        name = actual_names[i].get('name', 'NO NAME') if i < len(actual_names) else 'NO NAME'
        if i < len(filtered_stats):
            stats = filtered_stats[i]
            pts = stats.get('points', 0)
            reb = stats.get('rebounds', 0)
            ast = stats.get('assists', 0)
            mins = stats.get('minutes', '')
            print(f"      {i}: {name} -> {pts} PTS, {reb} REB, {ast} AST, {mins} MIN")
        else:
            print(f"      {i}: {name} -> NO STATS")
    
    # Match by position (assuming same order)
    for i, name_entry in enumerate(actual_names):
        if i < len(filtered_stats):
            stats = filtered_stats[i]
            combined_player = {
                'name': name_entry.get('name'),
                **stats  # Merge stats
            }
            
            # Clean up minutes display
            minutes = combined_player.get('minutes', '')
            if minutes == 'MIN':
                combined_player['minutes'] = '0'
            
            combined.append(combined_player)
        else:
            # Name without stats
            combined.append(name_entry)
    
    return combined

def extract_team_name_from_table(table) -> str:
    """Try to find team name associated with a stats table"""
    
    # Look for team name in preceding elements (headers, divs, etc.)
    current = table
    for _ in range(10):  # Look up to 10 elements back
        current = current.find_previous_sibling()
        if current is None:
            break
            
        text = current.get_text().strip()
        if text and 5 < len(text) < 50:  # Reasonable team name length
            # Check if it looks like a team name
            team_keywords = ['LIBERTY', 'ACES', 'STORM', 'WINGS', 'FEVER', 'SKY', 'SUN', 'DREAM', 'MERCURY', 'LYNX', 'SPARKS', 'MYSTICS', 'NEW YORK', 'LAS VEGAS', 'SEATTLE', 'CONNECTICUT', 'CHICAGO', 'INDIANA', 'DALLAS', 'ATLANTA', 'PHOENIX', 'MINNESOTA', 'LOS ANGELES', 'WASHINGTON']
            if any(keyword in text.upper() for keyword in team_keywords):
                return text.strip()
    
    # Look in parent containers
    parent = table.find_parent()
    if parent:
        # Look for headers or team identifiers in parent
        headers = parent.find_all(['h1', 'h2', 'h3', 'h4', 'div'], class_=re.compile(r'team|header', re.I))
        for header in headers:
            text = header.get_text().strip()
            if text and 5 < len(text) < 50:
                team_keywords = ['LIBERTY', 'ACES', 'STORM', 'WINGS', 'FEVER', 'SKY', 'SUN', 'DREAM', 'MERCURY', 'LYNX', 'SPARKS', 'MYSTICS']
                if any(keyword in text.upper() for keyword in team_keywords):
                    return text.strip()
    
    # Look for team name in table caption or nearby headers
    caption = table.find('caption')
    if caption:
        return caption.get_text().strip()
    
    # Try to extract from the page title or other context
    # This is a fallback - we'll improve this
    return "Unknown Team"

def extract_players_from_table(table) -> List[Dict[str, Any]]:
    """Extract individual player stats from a table"""
    
    players = []
    
    # Find header row - try multiple approaches
    headers = []
    
    # Method 1: Look for thead
    thead = table.find('thead')
    if thead:
        header_cells = thead.find_all(['th', 'td'])
        headers = [cell.get_text().strip().upper() for cell in header_cells]
    
    # Method 2: Look for first tr with th elements
    if not headers:
        first_row = table.find('tr')
        if first_row:
            th_cells = first_row.find_all('th')
            if th_cells:
                headers = [th.get_text().strip().upper() for th in th_cells]
    
    # Method 3: Look for any row with stat-like text
    if not headers:
        all_rows = table.find_all('tr')
        for row in all_rows[:3]:  # Check first 3 rows
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.get_text().strip().upper() for cell in cells]
            
            # Check if this looks like a header row
            stat_indicators = ['MIN', 'FG', 'FGA', '3PT', 'FT', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'PLAYER', 'NAME']
            found_stats = [stat for stat in stat_indicators if any(stat in text for text in cell_texts)]
            
            if len(found_stats) >= 3:  # If we find 3+ stat indicators, likely a header
                headers = cell_texts
                break
    
    print(f"    📊 Table headers: {headers}")
    
    # Find data rows - ESPN might structure this differently
    all_rows = table.find_all('tr')
    
    # Check if this table has player names (like table 2 & 4)
    has_player_names = False
    for row in all_rows:
        cells = row.find_all(['td', 'th'])
        for cell in cells:
            text = cell.get_text().strip()
            # Look for player name patterns (name with #number)
            if '#' in text and len(text) > 5:
                has_player_names = True
                break
        if has_player_names:
            break
    
    if has_player_names:
        print(f"    👤 This table contains player names")
        # Extract player names from this table
        for row in all_rows:
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text().strip()
                if '#' in text and len(text) > 5:
                    # Clean up player name
                    name = clean_player_name(text)
                    if name:
                        players.append({'name': name, 'raw_text': text})
    
    elif headers and len(headers) > 5:  # This is likely a stats table
        print(f"    📊 This table contains stats data")
        # Find tbody or use all rows except potential header
        tbody = table.find('tbody')
        if tbody:
            data_rows = tbody.find_all('tr')
        else:
            # Skip first row if it looks like headers
            data_rows = all_rows[1:] if all_rows else []
        
        # Additional check: skip any row that looks like headers
        filtered_data_rows = []
        for row in data_rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                first_cell = cells[0].get_text().strip().upper()
                # Skip header rows
                if first_cell in ['MIN', 'MINUTES'] or 'MIN' == first_cell:
                    print(f"      Skipping header row: {first_cell}")
                    continue
                filtered_data_rows.append(row)
        
        data_rows = filtered_data_rows
        
        print(f"    📋 Found {len(data_rows)} data rows in stats table")
        
        for row_idx, row in enumerate(data_rows):
            cells = row.find_all(['td', 'th'])
            if len(cells) < len(headers) * 0.5:  # Skip rows with too few cells
                continue
                
            player_data = {'row_index': row_idx}
            
            # Debug: show raw cell values
            cell_values = [cell.get_text().strip() for cell in cells]
            print(f"      Row {row_idx}: {cell_values[:8]}...")  # Show first 8 values
            
            # Map cell values to headers
            for i, cell in enumerate(cells):
                if i < len(headers):
                    header = headers[i]
                    value = cell.get_text().strip()
                    
                    # Clean up common stat values
                    if header in ['MIN', 'MINUTES']:
                        player_data['minutes'] = value
                    elif header in ['PTS', 'POINTS']:
                        player_data['points'] = parse_number(value)
                    elif header in ['REB', 'REBOUNDS']:
                        player_data['rebounds'] = parse_number(value)
                    elif header in ['AST', 'ASSISTS']:
                        player_data['assists'] = parse_number(value)
                    elif header in ['FG']:
                        player_data['field_goals'] = value
                    elif header in ['3PT']:
                        player_data['three_pointers'] = value
                    elif header in ['FT']:
                        player_data['free_throws'] = value
                    else:
                        player_data[header.lower().replace('+/-', 'plus_minus')] = value
            
            if len(player_data) > 2:  # More than just row_index
                players.append(player_data)
    
    return players

def clean_player_name(raw_text: str) -> str:
    """Clean up player name from ESPN format"""
    # ESPN format examples:
    # "LEONIE FIEBICHL. FIEBICH#13" -> "Leonie Fiebich"
    # "JONQUEL JONESJ. JONES#35" -> "Jonquel Jones"
    # "SABRINA IONESCUS. IONESCU#20" -> "Sabrina Ionescu"
    
    if '#' not in raw_text:
        return ""
    
    # Split by # to separate name from number
    name_part = raw_text.split('#')[0].strip()
    
    # Handle the common ESPN pattern: "FIRST LASTABBREV. LAST"
    if '.' in name_part:
        # Split by dot
        before_dot, after_dot = name_part.split('.', 1)
        after_dot = after_dot.strip()
        
        # Split the before_dot part to get first name and abbreviated last name
        words_before = before_dot.strip().split()
        
        if len(words_before) >= 2 and after_dot:
            # Take first name and the full last name after dot
            first_name = words_before[0]
            last_name = after_dot
            return f"{first_name} {last_name}".title()
        elif after_dot:
            # Just use what's after the dot if before_dot is unclear
            return after_dot.title()
    
    # Handle cases without dots - just clean up
    # Remove any trailing letters that look like abbreviations
    words = name_part.split()
    if len(words) >= 2:
        # Check if last word ends with a single letter (abbreviation)
        last_word = words[-1]
        if len(last_word) > 1 and last_word[-1].isalpha() and last_word[:-1].upper() in ' '.join(words[:-1]).upper():
            # Remove the abbreviated part
            return ' '.join(words[:-1]).title()
    
    # Fallback: just clean up the name part
    return name_part.replace('.', '').strip().title()

def parse_number(value: str) -> int:
    """Parse a string to number, return 0 if invalid"""
    try:
        # Handle fractions like "5-10" -> just take first number
        if '-' in value:
            value = value.split('-')[0]
        return int(value)
    except (ValueError, TypeError):
        return 0

def format_boxscore_output(data: Dict[str, Any]) -> str:
    """Format the scraped data for display"""
    
    lines = []
    lines.append(f"🏀 ESPN WNBA Boxscore - Game ID: {data['game_id']}")
    lines.append("=" * 60)
    
    game_info = data.get('game_info', {})
    if game_info.get('title'):
        lines.append(f"📰 {game_info['title']}")
        lines.append("")
    
    teams = data.get('teams', [])
    if not teams:
        lines.append("❌ No player stats found")
        lines.append("\n💡 This could mean:")
        lines.append("• The game hasn't been played yet")
        lines.append("• The boxscore isn't available")
        lines.append("• The page structure has changed")
        return "\n".join(lines)
    
    for team in teams:
        team_name = team.get('team_name', 'Unknown Team')
        players = team.get('players', [])
        
        lines.append(f"\n🏆 {team_name}")
        lines.append("-" * 40)
        
        if not players:
            lines.append("No player data found")
            continue
        
        # Show players
        for player in players:
            name = player.get('name', 'Unknown Player')
            points = player.get('points', 0)
            rebounds = player.get('rebounds', 0)
            assists = player.get('assists', 0)
            minutes = player.get('minutes', '0')
            
            lines.append(f"👤 {name}")
            lines.append(f"   📊 {points} PTS, {rebounds} REB, {assists} AST, {minutes} MIN")
    
    return "\n".join(lines)

def main(game_id: str = "401736292") -> None:
    """Main function to scrape and display boxscore"""
    
    try:
        print(f"🚀 Starting ESPN boxscore scraper for game {game_id}")
        
        # Scrape the boxscore
        data = scrape_boxscore(game_id)
        
        # Format and display results
        output = format_boxscore_output(data)
        print("\n" + output)
        
        # Also save raw data for debugging
        print(f"\n🔧 Debug info:")
        print(f"Teams found: {len(data.get('teams', []))}")
        for i, team in enumerate(data.get('teams', [])):
            print(f"  Team {i+1}: {team.get('team_name')} ({len(team.get('players', []))} players)")
        
    except Exception as e:
        print(f"❌ Scraping failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Check if the game ID is correct")
        print("2. Verify the game has been played")
        print("3. Check if ESPN's page structure changed")

if __name__ == "__main__":
    # Allow passing a different game id: python espn_boxscore_scraper.py 401736292
    game_id = sys.argv[1] if len(sys.argv) > 1 else "401736292"
    main(game_id)