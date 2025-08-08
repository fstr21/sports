"""
NFL data adapter for normalizing MCP response data.
Extracts passing, rushing, and receiving statistics from ESPN boxscore data.
"""

def normalize(mcp_summary_data):
    """
    Normalize NFL MCP response data into consistent format.
    
    Args:
        mcp_summary_data: MCP response data containing boxscore, leaders, teams_meta
        
    Returns:
        dict: Normalized NFL data with passing, rushing, receiving stats
    """
    if not mcp_summary_data or not mcp_summary_data.get('ok'):
        return {'error': 'Invalid MCP response data'}
    
    data = mcp_summary_data.get('data', {})
    summary = data.get('summary', {})
    boxscore = summary.get('boxscore', {})
    
    if not boxscore:
        return {'error': 'No boxscore data available'}
    
    result = {
        'passing': extract_passing_stats(boxscore),
        'rushing': extract_rushing_stats(boxscore),
        'receiving': extract_receiving_stats(boxscore)
    }
    
    return result


def extract_passing_stats(boxscore):
    """Extract passing statistics from boxscore data."""
    passing_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find passing statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() == 'passing':
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    if len(stats) >= 5:  # Ensure we have enough passing stats
                        passing_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'completions_attempts': f"{stats[0]}/{stats[1]}" if len(stats) > 1 else 'N/A',
                            'yards': stats[2] if len(stats) > 2 else 'N/A',
                            'avg': stats[3] if len(stats) > 3 else 'N/A',
                            'touchdowns': stats[4] if len(stats) > 4 else 'N/A',
                            'interceptions': stats[5] if len(stats) > 5 else 'N/A',
                            'rating': stats[6] if len(stats) > 6 else 'N/A'
                        })
    
    return passing_stats


def extract_rushing_stats(boxscore):
    """Extract rushing statistics from boxscore data."""
    rushing_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find rushing statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() == 'rushing':
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    if len(stats) >= 3:  # Ensure we have basic rushing stats
                        rushing_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'carries': stats[0] if len(stats) > 0 else 'N/A',
                            'yards': stats[1] if len(stats) > 1 else 'N/A',
                            'average': stats[2] if len(stats) > 2 else 'N/A',
                            'touchdowns': stats[3] if len(stats) > 3 else 'N/A',
                            'long': stats[4] if len(stats) > 4 else 'N/A'
                        })
    
    return rushing_stats


def extract_receiving_stats(boxscore):
    """Extract receiving statistics from boxscore data."""
    receiving_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find receiving statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() == 'receiving':
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    if len(stats) >= 3:  # Ensure we have basic receiving stats
                        receiving_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'receptions': stats[0] if len(stats) > 0 else 'N/A',
                            'yards': stats[1] if len(stats) > 1 else 'N/A',
                            'average': stats[2] if len(stats) > 2 else 'N/A',
                            'touchdowns': stats[3] if len(stats) > 3 else 'N/A',
                            'long': stats[4] if len(stats) > 4 else 'N/A',
                            'targets': stats[5] if len(stats) > 5 else 'N/A'
                        })
    
    return receiving_stats