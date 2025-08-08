"""
Soccer data adapter for normalizing MCP response data.
Extracts player statistics including minutes, goals, assists, cards, saves for soccer matches.
Works for MLS, EPL, La Liga, and other soccer leagues.
"""

def normalize(mcp_summary_data):
    """
    Normalize Soccer MCP response data into consistent format.
    
    Args:
        mcp_summary_data: MCP response data containing boxscore, leaders, teams_meta
        
    Returns:
        dict: Normalized soccer data with player statistics
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
        'goalkeepers': extract_goalkeeper_stats(boxscore)
    }
    
    return result


def extract_player_stats(boxscore):
    """Extract player statistics from boxscore data."""
    player_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find player statistics category (outfield players)
        for stat_category in statistics:
            if stat_category.get('name', '').lower() in ['players', 'outfield', 'field players']:
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    # Soccer stats typically: MIN, G, A, SOG, YC, RC, etc.
                    if len(stats) >= 3:
                        player_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'minutes': stats[0] if len(stats) > 0 else 'N/A',
                            'goals': stats[1] if len(stats) > 1 else 'N/A',
                            'assists': stats[2] if len(stats) > 2 else 'N/A',
                            'shots_on_goal': stats[3] if len(stats) > 3 else 'N/A',
                            'shots': stats[4] if len(stats) > 4 else 'N/A',
                            'yellow_cards': stats[5] if len(stats) > 5 else 'N/A',
                            'red_cards': stats[6] if len(stats) > 6 else 'N/A',
                            'fouls_committed': stats[7] if len(stats) > 7 else 'N/A',
                            'fouls_suffered': stats[8] if len(stats) > 8 else 'N/A',
                            'offsides': stats[9] if len(stats) > 9 else 'N/A'
                        })
    
    return player_stats


def extract_goalkeeper_stats(boxscore):
    """Extract goalkeeper statistics from boxscore data."""
    goalkeeper_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        team_name = team_data.get('team', {}).get('displayName', 'Unknown')
        statistics = team_data.get('statistics', [])
        
        # Find goalkeeper statistics category
        for stat_category in statistics:
            if stat_category.get('name', '').lower() in ['goalkeepers', 'keepers', 'goalies']:
                athletes = stat_category.get('athletes', [])
                
                for athlete in athletes:
                    athlete_data = athlete.get('athlete', {})
                    stats = athlete.get('stats', [])
                    
                    # Goalkeeper stats typically: MIN, SV, GA, YC, RC, etc.
                    if len(stats) >= 3:
                        goalkeeper_stats.append({
                            'team': team_name,
                            'name': athlete_data.get('displayName', 'Unknown'),
                            'minutes': stats[0] if len(stats) > 0 else 'N/A',
                            'saves': stats[1] if len(stats) > 1 else 'N/A',
                            'goals_against': stats[2] if len(stats) > 2 else 'N/A',
                            'yellow_cards': stats[3] if len(stats) > 3 else 'N/A',
                            'red_cards': stats[4] if len(stats) > 4 else 'N/A',
                            'clean_sheet': stats[5] if len(stats) > 5 else 'N/A'
                        })
    
    return goalkeeper_stats