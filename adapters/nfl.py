"""
NFL data adapter for normalizing MCP response data.
Extracts passing, rushing, and receiving statistics from ESPN boxscore data.
Handles the real ESPN API structure returned by MCP server.
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
        # Handle team info (always an object in real MCP response)
        team_info = team_data.get('team', {})
        team_name = team_info.get('displayName', 'Unknown') if isinstance(team_info, dict) else str(team_info)
        
        statistics = team_data.get('statistics', [])
        
        # Look for passing statistics category
        for stat_category in statistics:
            if stat_category.get('name') == 'passing':
                athletes = stat_category.get('athletes', [])
                labels = stat_category.get('labels', [])
                
                for athlete_data in athletes:
                    athlete_info = athlete_data.get('athlete', {})
                    stats = athlete_data.get('stats', [])
                    
                    if not stats or len(stats) < 4:  # Need at least C/ATT, YDS, TD, INT
                        continue
                        
                    # Map stats using labels if available
                    stat_dict = {}
                    for i, value in enumerate(stats):
                        if i < len(labels):
                            stat_dict[labels[i]] = value
                    
                    passing_stats.append({
                        'team': team_name,
                        'name': athlete_info.get('displayName', 'Unknown'),
                        'c_att': stat_dict.get('C/ATT', stats[0] if len(stats) > 0 else 'N/A'),
                        'yards': stat_dict.get('YDS', stats[1] if len(stats) > 1 else 'N/A'),
                        'td': stat_dict.get('TD', stats[3] if len(stats) > 3 else 'N/A'),
                        'int': stat_dict.get('INT', stats[4] if len(stats) > 4 else 'N/A'),
                        'rtg': stat_dict.get('RTG', stats[-1] if len(stats) > 6 else 'N/A')
                    })
    
    return {'players': passing_stats}


def extract_rushing_stats(boxscore):
    """Extract rushing statistics from boxscore data."""
    rushing_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        # Handle team info
        team_info = team_data.get('team', {})
        team_name = team_info.get('displayName', 'Unknown') if isinstance(team_info, dict) else str(team_info)
        
        statistics = team_data.get('statistics', [])
        
        # Look for rushing statistics category
        for stat_category in statistics:
            if stat_category.get('name') == 'rushing':
                athletes = stat_category.get('athletes', [])
                labels = stat_category.get('labels', [])
                
                for athlete_data in athletes:
                    athlete_info = athlete_data.get('athlete', {})
                    stats = athlete_data.get('stats', [])
                    
                    if not stats or len(stats) < 3:  # Need at least CAR, YDS, AVG
                        continue
                    
                    # Map stats using labels if available
                    stat_dict = {}
                    for i, value in enumerate(stats):
                        if i < len(labels):
                            stat_dict[labels[i]] = value
                    
                    rushing_stats.append({
                        'team': team_name,
                        'name': athlete_info.get('displayName', 'Unknown'),
                        'car': stat_dict.get('CAR', stats[0] if len(stats) > 0 else 'N/A'),
                        'yards': stat_dict.get('YDS', stats[1] if len(stats) > 1 else 'N/A'),
                        'avg': stat_dict.get('AVG', stats[2] if len(stats) > 2 else 'N/A'),
                        'td': stat_dict.get('TD', stats[3] if len(stats) > 3 else 'N/A'),
                        'long': stat_dict.get('LONG', stats[4] if len(stats) > 4 else 'N/A')
                    })
    
    return {'players': rushing_stats}


def extract_receiving_stats(boxscore):
    """Extract receiving statistics from boxscore data."""
    receiving_stats = []
    
    players = boxscore.get('players', [])
    
    for team_data in players:
        # Handle team info
        team_info = team_data.get('team', {})
        team_name = team_info.get('displayName', 'Unknown') if isinstance(team_info, dict) else str(team_info)
        
        statistics = team_data.get('statistics', [])
        
        # Look for receiving statistics category
        for stat_category in statistics:
            if stat_category.get('name') == 'receiving':
                athletes = stat_category.get('athletes', [])
                labels = stat_category.get('labels', [])
                
                for athlete_data in athletes:
                    athlete_info = athlete_data.get('athlete', {})
                    stats = athlete_data.get('stats', [])
                    
                    if not stats or len(stats) < 3:  # Need at least REC, YDS, AVG
                        continue
                    
                    # Map stats using labels if available
                    stat_dict = {}
                    for i, value in enumerate(stats):
                        if i < len(labels):
                            stat_dict[labels[i]] = value
                    
                    receiving_stats.append({
                        'team': team_name,
                        'name': athlete_info.get('displayName', 'Unknown'),
                        'rec': stat_dict.get('REC', stats[0] if len(stats) > 0 else 'N/A'),
                        'yards': stat_dict.get('YDS', stats[1] if len(stats) > 1 else 'N/A'),
                        'avg': stat_dict.get('AVG', stats[2] if len(stats) > 2 else 'N/A'),
                        'td': stat_dict.get('TD', stats[3] if len(stats) > 3 else 'N/A'),
                        'long': stat_dict.get('LONG', stats[4] if len(stats) > 4 else 'N/A'),
                        'tgts': stat_dict.get('TGTS', stats[5] if len(stats) > 5 else 'N/A')
                    })
    
    return {'players': receiving_stats}