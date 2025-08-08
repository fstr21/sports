"""
MLB data adapter for normalizing MCP response data.
Extracts batting and pitching statistics from ESPN boxscore data.
"""

def normalize(mcp_summary_data):
    """
    Normalize MLB MCP response data into consistent format.
    
    Args:
        mcp_summary_data: MCP response data containing boxscore, leaders, teams_meta
        
    Returns:
        dict: Normalized MLB data with batting and pitching stats
    """
    if not mcp_summary_data or not mcp_summary_data.get('ok'):
        return {'error': 'Invalid MCP response data'}
    
    data = mcp_summary_data.get('data', {})
    summary = data.get('summary', {})
    boxscore = summary.get('boxscore', {})
    
    if not boxscore:
        return {'error': 'No boxscore data available'}
    
    result = {
        'batting': extract_batting_stats(boxscore),
        'pitching': extract_pitching_stats(boxscore)
    }
    
    return result


def extract_batting_stats(boxscore):
    """Extract batting statistics from boxscore data."""
    batting_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find batting statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() == 'batting':
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    # MLB batting stats typically: AB, R, H, RBI, BB, SO, AVG, etc.
                    if len(stats) >= 6:
                        batting_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'at_bats': stats[0] if len(stats) > 0 else 'N/A',
                            'runs': stats[1] if len(stats) > 1 else 'N/A',
                            'hits': stats[2] if len(stats) > 2 else 'N/A',
                            'rbi': stats[3] if len(stats) > 3 else 'N/A',
                            'walks': stats[4] if len(stats) > 4 else 'N/A',
                            'strikeouts': stats[5] if len(stats) > 5 else 'N/A',
                            'avg': stats[6] if len(stats) > 6 else 'N/A',
                            'obp': stats[7] if len(stats) > 7 else 'N/A',
                            'slg': stats[8] if len(stats) > 8 else 'N/A'
                        })
    
    return batting_stats


def extract_pitching_stats(boxscore):
    """Extract pitching statistics from boxscore data."""
    pitching_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find pitching statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() == 'pitching':
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    # MLB pitching stats typically: IP, H, R, ER, BB, SO, HR, ERA, etc.
                    if len(stats) >= 6:
                        pitching_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'innings_pitched': stats[0] if len(stats) > 0 else 'N/A',
                            'hits_allowed': stats[1] if len(stats) > 1 else 'N/A',
                            'runs_allowed': stats[2] if len(stats) > 2 else 'N/A',
                            'earned_runs': stats[3] if len(stats) > 3 else 'N/A',
                            'walks_allowed': stats[4] if len(stats) > 4 else 'N/A',
                            'strikeouts': stats[5] if len(stats) > 5 else 'N/A',
                            'home_runs_allowed': stats[6] if len(stats) > 6 else 'N/A',
                            'era': stats[7] if len(stats) > 7 else 'N/A',
                            'whip': stats[8] if len(stats) > 8 else 'N/A'
                        })
    
    return pitching_stats