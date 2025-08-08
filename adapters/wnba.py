"""
WNBA data adapter for normalizing MCP response data.
Extracts player statistics including points, rebounds, assists, field goals, 3-pointers, free throws.
Uses same structure as NBA adapter since WNBA follows similar statistical categories.
"""

def normalize(mcp_summary_data):
    """
    Normalize WNBA MCP response data into consistent format.
    
    Args:
        mcp_summary_data: MCP response data containing boxscore, leaders, teams_meta
        
    Returns:
        dict: Normalized WNBA data with player statistics
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
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find player statistics (usually the main category)
        for stat_category in statistics:
            athletes = stat_category.get('athletes', [])
            
            for athlete in athletes:
                athlete_data = athlete.get('athlete', {})
                stats = athlete.get('stats', [])
                
                # WNBA stats typically: MIN, FG, 3PT, FT, OREB, DREB, REB, AST, STL, BLK, TO, PF, PTS
                if len(stats) >= 13:
                    player_stats.append({
                        'team': team_name,
                        'name': athlete_data.get('displayName', 'Unknown'),
                        'minutes': stats[0] if len(stats) > 0 else 'N/A',
                        'fg': stats[1] if len(stats) > 1 else 'N/A',  # Field goals made-attempted
                        '3p': stats[2] if len(stats) > 2 else 'N/A',  # 3-pointers made-attempted
                        'ft': stats[3] if len(stats) > 3 else 'N/A',  # Free throws made-attempted
                        'oreb': stats[4] if len(stats) > 4 else 'N/A',  # Offensive rebounds
                        'dreb': stats[5] if len(stats) > 5 else 'N/A',  # Defensive rebounds
                        'reb': stats[6] if len(stats) > 6 else 'N/A',   # Total rebounds
                        'ast': stats[7] if len(stats) > 7 else 'N/A',   # Assists
                        'stl': stats[8] if len(stats) > 8 else 'N/A',   # Steals
                        'blk': stats[9] if len(stats) > 9 else 'N/A',   # Blocks
                        'to': stats[10] if len(stats) > 10 else 'N/A',  # Turnovers
                        'pf': stats[11] if len(stats) > 11 else 'N/A',  # Personal fouls
                        'pts': stats[12] if len(stats) > 12 else 'N/A'  # Points
                    })
    
    return player_stats


def extract_team_stats(boxscore):
    """Extract team statistics from boxscore data."""
    team_stats = []
    
    teams = boxscore.get('teams', [])
    
    for team in teams:
        team_name = team.get('team', {}).get('displayName', 'Unknown')
        statistics = team.get('statistics', [])
        
        # Extract team totals
        for stat_category in statistics:
            stats = stat_category.get('stats', [])
            
            if len(stats) >= 13:
                team_stats.append({
                    'team': team_name,
                    'fg': stats[1] if len(stats) > 1 else 'N/A',
                    '3p': stats[2] if len(stats) > 2 else 'N/A',
                    'ft': stats[3] if len(stats) > 3 else 'N/A',
                    'reb': stats[6] if len(stats) > 6 else 'N/A',
                    'ast': stats[7] if len(stats) > 7 else 'N/A',
                    'stl': stats[8] if len(stats) > 8 else 'N/A',
                    'blk': stats[9] if len(stats) > 9 else 'N/A',
                    'to': stats[10] if len(stats) > 10 else 'N/A',
                    'pts': stats[12] if len(stats) > 12 else 'N/A'
                })
    
    return team_stats