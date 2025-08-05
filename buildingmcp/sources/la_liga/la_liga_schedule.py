import requests
from bs4 import BeautifulSoup
import re

def scrape_la_liga_schedule():
    """
    Scrapes the main ESPN La Liga schedule page to find upcoming games,
    including game and team IDs.
    """
    
    # The La Liga schedule page URL
    url = "https://www.espn.com/soccer/schedule/_/league/esp.1"
    
    # Headers are required to mimic a browser request.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Scraping La Liga schedule from: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find schedule data
        schedule_tables = soup.find_all('div', class_='ResponsiveTable')
        all_tables = soup.find_all('table')
        team_links = soup.find_all('a', href=re.compile(r'/soccer/team/_/id/\d+'))
        
        # Also look for date headers in the page (including Spanish terms)
        date_headers = soup.find_all(['div', 'h2', 'h3', 'h4'], string=re.compile(r'(today|tomorrow|hoy|mañana|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|ene|abr|ago|dic|\d{1,2})', re.IGNORECASE))

        if not schedule_tables and not all_tables and not team_links:
            print("\n❌ Could not find expected schedule data. Page structure may have changed.")
            return

        print("\n--- La Liga Upcoming Fixtures ---\n")
        
        # Print any date information found
        if date_headers:
            print("📅 Date information found on page:")
            for header in date_headers[:5]:  # Show first 5 date headers
                print(f"   - {header.get_text().strip()}")
            print()
        
        # Try the original approach first
        if schedule_tables:
            extract_from_responsive_tables(schedule_tables)
        elif all_tables:
            extract_from_generic_tables(all_tables)
        elif team_links:
            extract_from_team_links(soup, team_links)
        else:
            print("No suitable data structure found.")

    except requests.exceptions.RequestException as e:
        print(f"\nError fetching page: {e}")
    except Exception as e:
        print(f"An error occurred while parsing the page: {e}")
        import traceback
        traceback.print_exc()

def extract_from_responsive_tables(schedule_tables):
    """Extract games from ResponsiveTable elements"""
    
    for i, table in enumerate(schedule_tables):
        # Try multiple approaches to find the date for this group of games
        date_header = None
        
        # Approach 1: Look for Table__Title class
        date_header = table.find_previous_sibling('div', class_='Table__Title')
        
        # Approach 2: Look for any div with date-like text before this table
        if not date_header:
            prev_divs = table.find_all_previous('div', limit=10)
            for div in prev_divs:
                text = div.get_text().strip()
                # Look for date patterns like "Today", "Tomorrow", "Feb 8", etc.
                if any(word in text.lower() for word in ['today', 'tomorrow', 'hoy', 'mañana', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'ene', 'abr', 'ago', 'dic', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']):
                    date_header = div
                    break
        
        # Approach 3: Look for h2, h3 tags with date info
        if not date_header:
            prev_headers = table.find_all_previous(['h2', 'h3', 'h4'], limit=5)
            for header in prev_headers:
                text = header.get_text().strip()
                if any(word in text.lower() for word in ['today', 'tomorrow', 'hoy', 'mañana', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'ene', 'abr', 'ago', 'dic']):
                    date_header = header
                    break
        
        if date_header:
            print(f"📅 {date_header.get_text().strip()}")
            print("-" * 50)
        else:
            print(f"📅 Schedule Group {i+1}")
            print("-" * 50)
        
        # Find table body
        tbody = table.find('tbody')
        if not tbody:
            continue
            
        game_rows = tbody.find_all('tr')
        
        for j, row in enumerate(game_rows):
            try:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue

                # Extract team info
                away_team_cell = cells[0]
                home_team_cell = cells[1]
                
                away_team_name = extract_team_name(away_team_cell)
                home_team_name = extract_team_name(home_team_cell)
                
                away_team_id = extract_team_id(away_team_cell)
                home_team_id = extract_team_id(home_team_cell)

                # Extract game info
                time_cell = cells[2]
                game_time = extract_game_time(time_cell)
                game_id = extract_game_id(time_cell)
                
                # Print the extracted data
                print(f"⚽ {away_team_name} (ID: {away_team_id}) at {home_team_name} (ID: {home_team_id})")
                print(f"   🕐 {game_time} | Game ID: {game_id}")
                print()
                
            except Exception as e:
                continue

def extract_team_name(cell):
    """Extract team name from cell with multiple fallback approaches"""
    
    # Approach 1: Original method
    team_link = cell.find('a', class_='team-name')
    if team_link and team_link.span:
        return team_link.span.text
    
    # Approach 2: Extract from team URL slug
    team_link = cell.find('a', href=re.compile(r'/soccer/team/_/id/\d+'))
    if team_link:
        return extract_team_name_from_link(team_link)
    
    # Approach 3: Look for any span with team name
    span = cell.find('span')
    if span:
        text = span.get_text().strip()
        if text and text not in ['v', 'vs', '@']:
            return text
    
    # Approach 4: Just get cell text and clean it
    cell_text = cell.get_text().strip()
    # Remove common separators
    cell_text = cell_text.replace('v ', '').replace('@ ', '').strip()
    
    return cell_text or "Unknown Team"

def extract_team_name_from_link(team_link):
    """Extract team name from team link URL"""
    
    href = team_link['href']
    # Extract team name from URL: /soccer/team/_/id/83/barcelona -> barcelona
    url_parts = href.split('/')
    if len(url_parts) > 1:
        team_slug = url_parts[-1]  # Get last part of URL
        # Convert slug to readable name with La Liga specific handling
        team_name = convert_la_liga_slug_to_name(team_slug)
        return team_name
    
    return team_link.get_text().strip() or "Unknown Team"

def convert_la_liga_slug_to_name(slug):
    """Convert La Liga team URL slugs to proper team names"""
    
    # La Liga specific team name mappings
    la_liga_teams = {
        'barcelona': 'Barcelona',
        'real-madrid': 'Real Madrid',
        'atletico-madrid': 'Atlético Madrid',
        'athletic-club': 'Athletic Club',
        'real-sociedad': 'Real Sociedad',
        'real-betis': 'Real Betis',
        'villarreal': 'Villarreal',
        'valencia': 'Valencia',
        'sevilla': 'Sevilla',
        'celta-vigo': 'Celta Vigo',
        'rayo-vallecano': 'Rayo Vallecano',
        'real-valladolid': 'Real Valladolid',
        'getafe': 'Getafe',
        'osasuna': 'Osasuna',
        'mallorca': 'Mallorca',
        'las-palmas': 'Las Palmas',
        'girona': 'Girona',
        'alaves': 'Alavés',
        'espanyol': 'Espanyol',
        'leganes': 'Leganés'
    }
    
    # Check if we have a specific mapping
    if slug in la_liga_teams:
        return la_liga_teams[slug]
    
    # Fallback: convert slug to title case
    return slug.replace('-', ' ').title()

def extract_team_id(cell):
    """Extract team ID from cell"""
    
    team_link = cell.find('a', href=re.compile(r'/soccer/team/_/id/\d+'))
    if team_link:
        match = re.search(r'/id/(\d+)/', team_link['href'])
        return match.group(1) if match else "N/A"
    
    return "N/A"

def extract_game_time(cell):
    """Extract game time from cell"""
    
    time_link = cell.find('a')
    if time_link:
        return time_link.get_text().strip()
    
    return cell.get_text().strip() or "TBD"

def extract_game_id(cell):
    """Extract game ID from cell"""
    
    game_link = cell.find('a', href=re.compile(r'gameId/\d+'))
    if game_link:
        match = re.search(r'gameId/(\d+)', game_link['href'])
        return match.group(1) if match else "N/A"
    
    return "N/A"

def find_date_for_table(table):
    """Find date information associated with a table"""
    
    # Look for date in various places around the table
    date_selectors = [
        # Look for previous siblings with date info
        table.find_all_previous(['div', 'h2', 'h3', 'h4', 'span'], limit=10),
        # Look for parent elements with date info
        [table.parent] if table.parent else [],
        # Look for next siblings (sometimes dates come after)
        table.find_all_next(['div', 'h2', 'h3', 'h4', 'span'], limit=5)
    ]
    
    # Include Spanish date keywords
    date_keywords = ['today', 'tomorrow', 'hoy', 'mañana', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                     'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'ene', 'abr', 'ago', 'dic',
                     'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                     'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    
    for selector_group in date_selectors:
        for element in selector_group:
            if element:
                text = element.get_text().strip().lower()
                if any(keyword in text for keyword in date_keywords):
                    return element.get_text().strip()
    
    return None

def extract_from_generic_tables(all_tables):
    """Extract games from generic table elements"""
    
    for i, table in enumerate(all_tables):
        # Try to find date information for this table
        date_info = find_date_for_table(table)
        if date_info:
            print(f"📅 {date_info}")
            print("-" * 50)
        else:
            print(f"📋 Schedule Group {i+1}")
            print("-" * 50)
        
        # Look for team links in this table
        team_links = table.find_all('a', href=re.compile(r'/soccer/team/_/id/\d+'))
        game_links = table.find_all('a', href=re.compile(r'gameId/\d+'))
        
        if team_links or game_links:
            # Process this table similar to responsive tables
            tbody = table.find('tbody') or table
            rows = tbody.find_all('tr')
            
            for j, row in enumerate(rows):
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 2:
                        continue
                    
                    # Look for team links in this row
                    row_team_links = row.find_all('a', href=re.compile(r'/soccer/team/_/id/\d+'))
                    row_game_links = row.find_all('a', href=re.compile(r'gameId/\d+'))
                    
                    if len(row_team_links) >= 2:
                        away_team = row_team_links[0]
                        home_team = row_team_links[1]
                        
                        away_name = extract_team_name_from_link(away_team)
                        home_name = extract_team_name_from_link(home_team)
                        
                        away_id = re.search(r'/id/(\d+)/', away_team['href'])
                        home_id = re.search(r'/id/(\d+)/', home_team['href'])
                        
                        away_id = away_id.group(1) if away_id else "N/A"
                        home_id = home_id.group(1) if home_id else "N/A"
                        
                        game_id = "N/A"
                        game_time = "TBD"
                        
                        if row_game_links:
                            game_link = row_game_links[0]
                            game_time = game_link.get_text().strip()
                            game_id_match = re.search(r'gameId/(\d+)', game_link['href'])
                            game_id = game_id_match.group(1) if game_id_match else "N/A"
                        
                        print(f"⚽ {away_name} (ID: {away_id}) at {home_name} (ID: {home_id})")
                        print(f"   🕐 {game_time} | Game ID: {game_id}")
                        print()
                        
                except Exception as e:
                    continue

def extract_from_team_links(soup, team_links):
    """Extract games by analyzing team link patterns"""
    
    print(f"📅 Schedule Information")
    print("-" * 50)
    print(f"Analyzing {len(team_links)} team links for game patterns...")
    
    # Group team links that might be in the same game
    for i in range(0, len(team_links) - 1, 2):
        try:
            away_link = team_links[i]
            home_link = team_links[i + 1] if i + 1 < len(team_links) else None
            
            if not home_link:
                break
                
            away_name = extract_team_name_from_link(away_link)
            home_name = extract_team_name_from_link(home_link)
            
            away_id = re.search(r'/id/(\d+)/', away_link['href'])
            home_id = re.search(r'/id/(\d+)/', home_link['href'])
            
            away_id = away_id.group(1) if away_id else "N/A"
            home_id = home_id.group(1) if home_id else "N/A"
            
            print(f"⚽ {away_name} (ID: {away_id}) vs {home_name} (ID: {home_id})")
            print(f"   🕐 TBD | Game ID: N/A")
            print()
            
        except Exception as e:
            continue

if __name__ == "__main__":
    scrape_la_liga_schedule()