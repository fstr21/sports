#!/usr/bin/env python3
"""
ESPN WNBA Boxscore Web Scraper - Clean Version
Scrapes comprehensive player stats from ESPN boxscore pages
"""

import sys
import httpx
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional
import re
import json

def scrape_boxscore(game_id: str) -> Dict[str, Any]:
    """Scrape comprehensive player stats from ESPN boxscore webpage"""
    
    url = f"https://www.espn.com/wnba/boxscore/_/gameId/{game_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
        try:
            response = client.get(url)
            response.raise_for_status()
            return parse_boxscore_html(response.text, game_id, url)
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP Error {e.response.status_code}: Failed to load boxscore")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

def parse_boxscore_html(html_content: str, game_id: str, url: str) -> Dict[str, Any]:
    """Parse HTML content to extract comprehensive game and player data"""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract all data components
    game_info = extract_game_info(soup)
    quarter_scores = extract_quarter_scores(soup)
    teams_data = extract_comprehensive_player_stats(soup)
    
    return {
        "game_id": game_id,
        "url": url,
        "game_info": game_info,
        "quarter_scores": quarter_scores,
        "teams": teams_data
    }

def extract_game_info(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract basic game information from page title and elements"""
    
    game_info = {}
    
    # Extract from page title
    title_elem = soup.find('title')
    if title_elem:
        title = title_elem.get_text().strip()
        game_info['page_title'] = title
        
        # Parse title for game details: "Liberty 87-78 Sun (Aug 3, 2025) Box Score - ESPN"
        if ' Box Score' in title:
            game_part = title.split(' Box Score')[0]
            
            # Extract date if present
            date_match = re.search(r'\(([^)]+)\)', game_part)
            if date_match:
                game_info['game_date'] = date_match.group(1)
                game_part = re.sub(r'\s*\([^)]+\)', '', game_part)
            
            # Extract teams and score
            score_match = re.match(r'(.+?)\s+(\d+)-(\d+)\s+(.+)', game_part.strip())
            if score_match:
                game_info['away_team'] = score_match.group(1).strip()
                game_info['away_score'] = int(score_match.group(2))
                game_info['home_score'] = int(score_match.group(3))
                game_info['home_team'] = score_match.group(4).strip()
                game_info['final_score'] = f"{game_info['away_score']}-{game_info['home_score']}"
    
    return game_info

def extract_quarter_scores(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract quarter-by-quarter scoring"""
    
    quarter_data = {}
    
    # Find the scoring table (usually table 0)
    tables = soup.find_all('table')
    if tables:
        score_table = tables[0]  # First table is typically quarter scores
        rows = score_table.find_all('tr')
        
        if len(rows) >= 3:  # Header + 2 team rows
            # Extract headers (quarters)
            header_row = rows[0]
            headers = [cell.get_text().strip() for cell in header_row.find_all(['th', 'td'])]
            
            # Extract team scores
            for i, row in enumerate(rows[1:3]):  # Next 2 rows are team scores
                cells = row.find_all(['td', 'th'])
                if cells:
                    team_abbrev = cells[0].get_text().strip()
                    scores = [cell.get_text().strip() for cell in cells[1:]]
                    
                    team_key = 'away_team' if i == 0 else 'home_team'
                    quarter_data[team_key] = {
                        'abbreviation': team_abbrev,
                        'quarters': {}
                    }
                    
                    # Map quarter scores
                    for j, score in enumerate(scores):
                        if j < len(headers) - 1:  # Skip team abbreviation column
                            quarter_label = headers[j + 1]  # +1 to skip first column
                            if quarter_label and score.isdigit():
                                quarter_data[team_key]['quarters'][quarter_label] = int(score)
    
    return quarter_data

def extract_comprehensive_player_stats(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract comprehensive player statistics from boxscore tables"""
    
    teams_data = []
    tables = soup.find_all('table')
    
    if len(tables) < 4:
        return teams_data
    
    # Extract player and team IDs from links
    player_ids = extract_player_ids(soup)
    team_ids = extract_team_ids(soup)
    
    # Based on our analysis: Tables 1&2 = Team 1, Tables 3&4 = Team 2
    team_pairs = [
        (tables[1], tables[2]),  # Team 1: names table, stats table
        (tables[3], tables[4])   # Team 2: names table, stats table
    ]
    
    # Extract team names from title
    team_names = extract_team_names_from_title(soup)
    
    for i, (names_table, stats_table) in enumerate(team_pairs):
        team_name = team_names[i] if i < len(team_names) else f"Team {i+1}"
        
        # Extract player names and stats
        players = extract_team_players(names_table, stats_table, player_ids)
        
        if players:
            # Calculate team totals
            team_totals = calculate_team_totals(stats_table)
            
            # Get team ID
            team_id = team_ids.get(team_name.lower(), None)
            
            teams_data.append({
                "team_name": team_name,
                "team_id": team_id,
                "players": players,
                "team_totals": team_totals
            })
    
    return teams_data

def extract_player_ids(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract player IDs from profile links"""
    
    player_ids = {}
    
    # Find all player profile links
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        
        # Look for player profile links: /wnba/player/_/id/4066533/sabrina-ionescu
        if '/wnba/player/_/id/' in href:
            # Extract player ID from URL
            parts = href.split('/id/')
            if len(parts) > 1:
                id_part = parts[1].split('/')[0]
                
                # Extract player name from URL slug (more reliable)
                url_parts = href.split('/')
                if len(url_parts) > 1:
                    slug = url_parts[-1]  # e.g., "sabrina-ionescu"
                    clean_name = slug.replace('-', ' ').title()  # "Sabrina Ionescu"
                    player_ids[clean_name.lower()] = id_part
    
    return player_ids

def extract_team_ids(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract team IDs from profile links"""
    
    team_ids = {}
    
    # Find all team profile links
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        text = link.get_text().strip()
        
        # Look for team profile links: /wnba/team/_/name/ny/new-york-liberty
        if '/wnba/team/_/name/' in href:
            # Extract team abbreviation from URL
            parts = href.split('/name/')
            if len(parts) > 1:
                team_abbrev = parts[1].split('/')[0]
                
                # Map team names to abbreviations
                if text:
                    team_ids[text.lower()] = team_abbrev
                    # Also map common variations
                    if 'liberty' in text.lower():
                        team_ids['liberty'] = team_abbrev
                    elif 'sun' in text.lower():
                        team_ids['sun'] = team_abbrev
    
    return team_ids



def extract_team_names_from_title(soup: BeautifulSoup) -> List[str]:
    """Extract team names from page title"""
    
    title_elem = soup.find('title')
    if not title_elem:
        return []
    
    title = title_elem.get_text()
    
    # Parse title: "Liberty 87-78 Sun (Aug 3, 2025) Box Score - ESPN"
    if ' Box Score' in title:
        game_part = title.split(' Box Score')[0]
        # Remove date part
        game_part = re.sub(r'\s*\([^)]+\)', '', game_part)
        
        # Extract teams around score
        match = re.match(r'(.+?)\s+\d+\s*-\s*\d+\s+(.+)', game_part.strip())
        if match:
            return [match.group(1).strip(), match.group(2).strip()]
    
    return []

def extract_team_players(names_table, stats_table, player_ids: Dict[str, str]) -> List[Dict[str, Any]]:
    """Extract players by combining names and stats tables"""
    
    # Extract player names
    player_names = []
    name_rows = names_table.find_all('tr')
    
    for row in name_rows:
        cells = row.find_all(['td', 'th'])
        for cell in cells:
            text = cell.get_text().strip()
            if '#' in text and len(text) > 5:
                clean_name = clean_player_name(text)
                if clean_name:
                    player_names.append(clean_name)
    
    # Extract player stats
    player_stats = []
    stats_rows = stats_table.find_all('tr')
    
    # Find header row for stat mapping
    stat_headers = []
    for row in stats_rows:
        cells = row.find_all(['td', 'th'])
        if cells:
            cell_texts = [cell.get_text().strip().upper() for cell in cells]
            if 'MIN' in cell_texts and 'PTS' in cell_texts:
                stat_headers = cell_texts
                break
    
    # Extract data rows (skip headers and team totals)
    for row in stats_rows:
        cells = row.find_all(['td', 'th'])
        if not cells:
            continue
            
        cell_values = [cell.get_text().strip() for cell in cells]
        
        # Skip header rows and team totals
        if (cell_values[0].upper() in ['MIN', 'MINUTES'] or 
            'DNP' not in cell_values[0] and 
            len(cell_values) > 5 and 
            not any(val.isdigit() and int(val) > 50 for val in cell_values if val.isdigit())):
            
            player_stat = parse_player_stats(cell_values, stat_headers)
            if player_stat:
                player_stats.append(player_stat)
    
    # Combine names with stats
    combined_players = []
    for i, name in enumerate(player_names):
        if i < len(player_stats):
            # Look up player ID
            player_id = player_ids.get(name.lower(), None)
            
            player_data = {
                'name': name,
                'player_id': player_id,
                **player_stats[i]
            }
            combined_players.append(player_data)
    
    return combined_players

def parse_player_stats(cell_values: List[str], headers: List[str]) -> Dict[str, Any]:
    """Parse individual player statistics from table row"""
    
    if not headers or len(cell_values) < len(headers):
        return {}
    
    stats = {}
    
    for i, value in enumerate(cell_values):
        if i >= len(headers):
            break
            
        header = headers[i].upper()
        
        # Handle DNP cases
        if 'DNP' in value:
            stats['status'] = value
            stats['minutes'] = '0'
            stats['points'] = 0
            continue
        
        # Map common stats
        if header == 'MIN':
            stats['minutes'] = value
        elif header == 'PTS':
            stats['points'] = safe_int(value)
        elif header == 'REB':
            stats['rebounds'] = safe_int(value)
        elif header == 'AST':
            stats['assists'] = safe_int(value)
        elif header == 'STL':
            stats['steals'] = safe_int(value)
        elif header == 'BLK':
            stats['blocks'] = safe_int(value)
        elif header == 'TO':
            stats['turnovers'] = safe_int(value)
        elif header == 'PF':
            stats['fouls'] = safe_int(value)
        elif header == 'FG':
            stats['field_goals'] = value
        elif header == '3PT':
            stats['three_pointers'] = value
        elif header == 'FT':
            stats['free_throws'] = value
        elif header == 'OREB':
            stats['offensive_rebounds'] = safe_int(value)
        elif header == 'DREB':
            stats['defensive_rebounds'] = safe_int(value)
        elif header == '+/-':
            stats['plus_minus'] = value
    
    return stats

def calculate_team_totals(stats_table) -> Dict[str, Any]:
    """Extract team totals from the last row of stats table"""
    
    rows = stats_table.find_all('tr')
    if len(rows) < 2:
        return {}
    
    # Team totals are typically in the second-to-last row
    team_row = rows[-2]
    cells = team_row.find_all(['td', 'th'])
    
    if len(cells) < 10:
        return {}
    
    cell_values = [cell.get_text().strip() for cell in cells]
    
    return {
        'field_goals': cell_values[1] if len(cell_values) > 1 else '',
        'three_pointers': cell_values[2] if len(cell_values) > 2 else '',
        'free_throws': cell_values[3] if len(cell_values) > 3 else '',
        'offensive_rebounds': safe_int(cell_values[4]) if len(cell_values) > 4 else 0,
        'defensive_rebounds': safe_int(cell_values[5]) if len(cell_values) > 5 else 0,
        'total_rebounds': safe_int(cell_values[6]) if len(cell_values) > 6 else 0,
        'assists': safe_int(cell_values[7]) if len(cell_values) > 7 else 0,
        'steals': safe_int(cell_values[8]) if len(cell_values) > 8 else 0,
        'blocks': safe_int(cell_values[9]) if len(cell_values) > 9 else 0,
        'turnovers': safe_int(cell_values[10]) if len(cell_values) > 10 else 0,
        'fouls': safe_int(cell_values[11]) if len(cell_values) > 11 else 0,
        'points': safe_int(cell_values[13]) if len(cell_values) > 13 else 0
    }

def safe_int(value: str) -> int:
    """Safely convert string to integer"""
    try:
        # Handle cases like "5-10" by taking first number
        if '-' in value and not value.startswith('-'):
            value = value.split('-')[0]
        return int(value)
    except (ValueError, TypeError):
        return 0



def clean_player_name(raw_text: str) -> str:
    """Clean up player name from ESPN format"""
    # ESPN format: "LEONIE FIEBICHL. FIEBICH#13" -> "Leonie Fiebich"
    
    if '#' not in raw_text:
        return ""
    
    # Split by # to separate name from number
    name_part = raw_text.split('#')[0].strip()
    
    # Handle ESPN pattern: "FIRST LASTABBREV. LAST"
    if '.' in name_part:
        before_dot, after_dot = name_part.split('.', 1)
        after_dot = after_dot.strip()
        
        words_before = before_dot.strip().split()
        
        if len(words_before) >= 2 and after_dot:
            first_name = words_before[0]
            last_name = after_dot
            return f"{first_name} {last_name}".title()
        elif after_dot:
            return after_dot.title()
    
    # Fallback: clean up the name part
    return name_part.replace('.', '').strip().title()

def format_comprehensive_output(data: Dict[str, Any]) -> str:
    """Format comprehensive boxscore data for clean display"""
    
    lines = []
    
    # Header
    lines.append("🏀 ESPN WNBA BOXSCORE")
    lines.append("=" * 60)
    
    # Game Info
    game_info = data.get('game_info', {})
    if game_info:
        lines.append(f"📰 Game: {game_info.get('page_title', 'N/A')}")
        if game_info.get('final_score'):
            lines.append(f"📊 Final Score: {game_info['final_score']}")
        if game_info.get('game_date'):
            lines.append(f"📅 Date: {game_info['game_date']}")
        lines.append("")
    
    # Quarter Scores
    quarter_scores = data.get('quarter_scores', {})
    if quarter_scores:
        lines.append("📈 QUARTER SCORES")
        lines.append("-" * 30)
        
        away_team = quarter_scores.get('away_team', {})
        home_team = quarter_scores.get('home_team', {})
        
        if away_team and home_team:
            # Header
            quarters = list(away_team.get('quarters', {}).keys())
            header = f"{'Team':<12} " + " ".join(f"{q:>3}" for q in quarters)
            lines.append(header)
            lines.append("-" * len(header))
            
            # Away team
            away_scores = [str(away_team['quarters'].get(q, 0)) for q in quarters]
            away_line = f"{away_team.get('abbreviation', 'AWAY'):<12} " + " ".join(f"{s:>3}" for s in away_scores)
            lines.append(away_line)
            
            # Home team  
            home_scores = [str(home_team['quarters'].get(q, 0)) for q in quarters]
            home_line = f"{home_team.get('abbreviation', 'HOME'):<12} " + " ".join(f"{s:>3}" for s in home_scores)
            lines.append(home_line)
        
        lines.append("")
    
    # Team Stats
    teams = data.get('teams', [])
    if not teams:
        lines.append("❌ No player stats available")
        return "\n".join(lines)
    
    for team in teams:
        team_name = team.get('team_name', 'Unknown Team')
        players = team.get('players', [])
        team_totals = team.get('team_totals', {})
        
        lines.append(f"🏆 {team_name.upper()}")
        lines.append("=" * 60)
        
        if not players:
            lines.append("No player data found")
            continue
        
        # Player stats header with ID column
        header = f"{'Player':<20} {'ID':<10} {'MIN':<5} {'PTS':<4} {'REB':<4} {'AST':<4} {'FG':<8} {'3PT':<8} {'FT':<8}"
        lines.append(header)
        lines.append("-" * len(header))
        
        # Player stats
        for player in players:
            name = player.get('name', 'Unknown')[:19]  # Truncate long names
            player_id = player.get('player_id', 'N/A')
            minutes = player.get('minutes', '0')
            points = player.get('points', 0)
            rebounds = player.get('rebounds', 0)
            assists = player.get('assists', 0)
            fg = player.get('field_goals', '0-0')
            three_pt = player.get('three_pointers', '0-0')
            ft = player.get('free_throws', '0-0')
            
            # Skip header rows and percentage rows that got mixed in
            if (minutes in ['MIN', 'MINUTES'] or 
                fg in ['FG', 'FIELD_GOALS'] or 
                three_pt in ['3PT', 'THREE_POINTERS'] or
                '%' in str(fg) or '%' in str(three_pt) or '%' in str(ft)):
                continue
            
            # Handle DNP status
            if player.get('status') and 'DNP' in player.get('status', ''):
                status_line = f"{name:<20} {str(player_id):<10} {'DNP':<5} {player.get('status', '')}"
                lines.append(status_line)
            else:
                # Ensure proper formatting for all values
                minutes_str = str(minutes) if minutes != 'MIN' else '0'
                points_str = str(points) if isinstance(points, int) else '0'
                rebounds_str = str(rebounds) if isinstance(rebounds, int) else '0'
                assists_str = str(assists) if isinstance(assists, int) else '0'
                fg_str = str(fg) if fg not in ['FG', ''] else '0-0'
                three_pt_str = str(three_pt) if three_pt not in ['3PT', ''] else '0-0'
                ft_str = str(ft) if ft not in ['FT', ''] else '0-0'
                
                player_line = f"{name:<20} {str(player_id):<10} {minutes_str:<5} {points_str:<4} {rebounds_str:<4} {assists_str:<4} {fg_str:<8} {three_pt_str:<8} {ft_str:<8}"
                lines.append(player_line)
        
        # Team totals
        if team_totals:
            lines.append("-" * len(header))
            team_id = team.get('team_id', 'N/A')
            totals_line = f"{'TEAM TOTALS':<20} {str(team_id):<10} {'':<5} {team_totals.get('points', 0):<4} {team_totals.get('total_rebounds', 0):<4} {team_totals.get('assists', 0):<4} {team_totals.get('field_goals', ''):<8} {team_totals.get('three_pointers', ''):<8} {team_totals.get('free_throws', ''):<8}"
            lines.append(totals_line)
        
        lines.append("")
    
    return "\n".join(lines)

def save_json_output(data: Dict[str, Any], game_id: str) -> str:
    """Save comprehensive data to JSON file"""
    
    filename = f"boxscore_data_{game_id}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

def main(game_id: str = "401736292") -> None:
    """Main function to scrape and display comprehensive boxscore data"""
    
    try:
        print(f"🚀 Scraping ESPN WNBA boxscore for game {game_id}...")
        
        # Scrape comprehensive data
        data = scrape_boxscore(game_id)
        
        # Display formatted output
        output = format_comprehensive_output(data)
        print("\n" + output)
        
        # Save JSON data
        json_file = save_json_output(data, game_id)
        print(f"💾 Complete data saved to: {json_file}")
        
        # Summary
        teams = data.get('teams', [])
        total_players = sum(len(team.get('players', [])) for team in teams)
        print(f"\n✅ Successfully extracted data for {len(teams)} teams, {total_players} players")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Possible issues:")
        print("• Invalid game ID")
        print("• Game not yet played")
        print("• Network connectivity")
        print("• ESPN page structure changed")

if __name__ == "__main__":
    # Allow passing a different game id: python espn_boxscore_scraper.py 401736292
    game_id = sys.argv[1] if len(sys.argv) > 1 else "401736292"
    main(game_id)