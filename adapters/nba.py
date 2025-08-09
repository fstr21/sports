"""
NBA data adapter for normalizing MCP response data.
Extracts player statistics including points, rebounds, assists, field goals, 3-pointers, free throws.
Handles the real ESPN API structure returned by MCP server.
"""

def normalize(mcp_summary_data):
    """
    Normalize NBA MCP response data into consistent format.
    
    Args:
        mcp_summary_data: MCP response data containing boxscore, leaders, teams_meta
        
    Returns:
        dict: Normalized NBA data with player statistics
    """
    if not mcp_summary_data or not mcp_summary_data.get('ok'):
        return {'error': 'Invalid MCP response data'}
    
    data = mcp_summary_data.get('data', {})
    summary = data.get('summary', {})
    boxscore = summary.get('boxscore', {})
    
    if not boxscore:
        return {'error': 'No boxscore data available'}
    
    result = {
        'players': extract_player_stats(boxscore),
        'team_stats': extract_team_stats(boxscore)
    }
    
    return result


def extract_player_stats(boxscore):
    """Extract player statistics from boxscore data."""
    player_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        # Handle team info (always an object in real MCP response)
        team_info = team_data.get('team', {})
        team_name = team_info.get('displayName', 'Unknown') if isinstance(team_info, dict) else str(team_info)
        
        statistics = team_data.get('statistics', [])
        
        # NBA typically has one main statistics category for players
        for stat_category in statistics:
            athletes = stat_category.get('athletes', [])
            labels = stat_category.get('labels', [])
            
            for athlete_data in athletes:
                athlete_info = athlete_data.get('athlete', {})
                stats = athlete_data.get('stats', [])
                
                if not stats:  # Skip players with no stats
                    continue
                
                # Skip players who did not play
                if athlete_data.get('didNotPlay'):
                    continue
                
                # Map stats using labels if available
                stat_dict = {}
                for i, value in enumerate(stats):
                    if i < len(labels):
                        stat_dict[labels[i]] = value
                
                # Extract key basketball stats (typical order: MIN, FG, 3PT, FT, OREB, DREB, REB, AST, STL, BLK, TO, PF, PTS)
                player_stats.append({
                    'team': team_name,
                    'name': athlete_info.get('displayName', 'Unknown'),
                    'min': stat_dict.get('MIN', stats[0] if len(stats) > 0 else 'N/A'),
                    'pts': safe_int(stat_dict.get('PTS', stats[-1] if len(stats) > 0 else '0')),  # PTS usually last
                    'reb': safe_int(stat_dict.get('REB', stats[6] if len(stats) > 6 else '0')),   # REB typically index 6
                    'ast': safe_int(stat_dict.get('AST', stats[7] if len(stats) > 7 else '0')),   # AST typically index 7
                    'fg': stat_dict.get('FG', stats[1] if len(stats) > 1 else 'N/A'),             # FG typically index 1
                    '3p': stat_dict.get('3PT', stats[2] if len(stats) > 2 else 'N/A'),           # 3PT typically index 2
                    'ft': stat_dict.get('FT', stats[3] if len(stats) > 3 else 'N/A'),             # FT typically index 3
                    'stl': safe_int(stat_dict.get('STL', stats[8] if len(stats) > 8 else '0')),   # STL typically index 8
                    'blk': safe_int(stat_dict.get('BLK', stats[9] if len(stats) > 9 else '0')),   # BLK typically index 9
                    'to': safe_int(stat_dict.get('TO', stats[10] if len(stats) > 10 else '0')),   # TO typically index 10
                    'pf': safe_int(stat_dict.get('PF', stats[11] if len(stats) > 11 else '0'))    # PF typically index 11
                })
    
    return player_stats


def safe_int(value):
    """Safely convert a value to int, return 0 if conversion fails."""
    try:
        if isinstance(value, str) and '/' in value:  # Handle "5/10" format
            return int(value.split('/')[0])
        return int(float(value))  # Handle decimals
    except (ValueError, TypeError):
        return 0


def extract_team_stats(boxscore):
    """Extract team statistics from boxscore data."""
    team_stats = []
    
    # Look for team totals in the statistics
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_info = team_data.get('team', {})
        team_name = team_info.get('displayName', 'Unknown') if isinstance(team_info, dict) else str(team_info)
        
        statistics = team_data.get('statistics', [])
        
        for stat_category in statistics:
            totals = stat_category.get('totals', [])
            labels = stat_category.get('labels', [])
            
            if totals:
                # Map team totals using labels
                stat_dict = {}
                for i, value in enumerate(totals):
                    if i < len(labels):
                        stat_dict[labels[i]] = value
                
                team_stats.append({
                    'team': team_name,
                    'pts': safe_int(stat_dict.get('PTS', totals[-1] if totals else '0')),
                    'fg': stat_dict.get('FG', totals[1] if len(totals) > 1 else 'N/A'),
                    '3p': stat_dict.get('3PT', totals[2] if len(totals) > 2 else 'N/A'),
                    'ft': stat_dict.get('FT', totals[3] if len(totals) > 3 else 'N/A'),
                    'reb': safe_int(stat_dict.get('REB', totals[6] if len(totals) > 6 else '0')),
                    'ast': safe_int(stat_dict.get('AST', totals[7] if len(totals) > 7 else '0')),
                    'stl': safe_int(stat_dict.get('STL', totals[8] if len(totals) > 8 else '0')),
                    'blk': safe_int(stat_dict.get('BLK', totals[9] if len(totals) > 9 else '0')),
                    'to': safe_int(stat_dict.get('TO', totals[10] if len(totals) > 10 else '0'))
                })
                break  # Only process first totals found
    
    return team_stats