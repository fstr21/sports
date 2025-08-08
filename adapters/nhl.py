"""
NHL data adapter for normalizing MCP response data.
Extracts skater and goalie statistics from ESPN boxscore data.
"""

def normalize(mcp_summary_data):
    """
    Normalize NHL MCP response data into consistent format.
    
    Args:
        mcp_summary_data: MCP response data containing boxscore, leaders, teams_meta
        
    Returns:
        dict: Normalized NHL data with skater and goalie stats
    """
    if not mcp_summary_data or not mcp_summary_data.get('ok'):
        return {'error': 'Invalid MCP response data'}
    
    data = mcp_summary_data.get('data', {})
    summary = data.get('summary', {})
    boxscore = summary.get('boxscore', {})
    
    if not boxscore:
        return {'error': 'No boxscore data available'}
    
    result = {
        'skaters': extract_skater_stats(boxscore),
        'goalies': extract_goalie_stats(boxscore)
    }
    
    return result


def extract_skater_stats(boxscore):
    """Extract skater statistics from boxscore data."""
    skater_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find skater statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() in ['skaters', 'skating']:
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    # NHL skater stats typically: G, A, PTS, +/-, PIM, SOG, TOI, etc.
                    if len(stats) >= 6:
                        skater_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'goals': stats[0] if len(stats) > 0 else 'N/A',
                            'assists': stats[1] if len(stats) > 1 else 'N/A',
                            'points': stats[2] if len(stats) > 2 else 'N/A',
                            'plus_minus': stats[3] if len(stats) > 3 else 'N/A',
                            'penalty_minutes': stats[4] if len(stats) > 4 else 'N/A',
                            'shots_on_goal': stats[5] if len(stats) > 5 else 'N/A',
                            'time_on_ice': stats[6] if len(stats) > 6 else 'N/A',
                            'hits': stats[7] if len(stats) > 7 else 'N/A',
                            'blocked_shots': stats[8] if len(stats) > 8 else 'N/A'
                        })
    
    return skater_stats


def extract_goalie_stats(boxscore):
    """Extract goalie statistics from boxscore data."""
    goalie_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find goalie statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() in ['goalies', 'goaltending']:
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    # NHL goalie stats typically: SA, GA, SV, SV%, TOI, etc.
                    if len(stats) >= 4:
                        goalie_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'shots_against': stats[0] if len(stats) > 0 else 'N/A',
                            'goals_against': stats[1] if len(stats) > 1 else 'N/A',
                            'saves': stats[2] if len(stats) > 2 else 'N/A',
                            'save_percentage': stats[3] if len(stats) > 3 else 'N/A',
                            'time_on_ice': stats[4] if len(stats) > 4 else 'N/A',
                            'decision': stats[5] if len(stats) > 5 else 'N/A'
                        })
    
    return goalie_stats