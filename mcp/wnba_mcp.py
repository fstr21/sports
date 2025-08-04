import asyncio
import json
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("wnba-stats")

@mcp.tool()
async def get_wnba_standings() -> str:
    """Get current WNBA team standings and records"""
    try:
        # ESPN WNBA scoreboard API - contains team records
        url = "http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # Extract team records from events
        teams_data = {}
        
        if 'events' in data:
            for event in data['events']:
                if 'competitions' in event:
                    for comp in event['competitions']:
                        if 'competitors' in comp:
                            for team in comp['competitors']:
                                if 'team' in team and 'records' in team:
                                    team_name = team['team']['displayName']
                                    
                                    # Find overall record
                                    for record in team['records']:
                                        if record.get('type') == 'total' and record.get('name') == 'overall':
                                            record_str = record.get('summary', '0-0')
                                            
                                            # Calculate win percentage
                                            try:
                                                wins, losses = record_str.split('-')
                                                wins, losses = int(wins), int(losses)
                                                total_games = wins + losses
                                                win_pct = wins / total_games if total_games > 0 else 0
                                                
                                                teams_data[team_name] = {
                                                    'wins': wins,
                                                    'losses': losses,
                                                    'pct': win_pct,
                                                    'record': record_str
                                                }
                                            except:
                                                teams_data[team_name] = {
                                                    'wins': 0,
                                                    'losses': 0,
                                                    'pct': 0,
                                                    'record': record_str
                                                }
        
        if not teams_data:
            return "No team records found in API data"
        
        # Sort teams by win percentage (descending)
        sorted_teams = sorted(teams_data.items(), key=lambda x: x[1]['pct'], reverse=True)
        
        # Format output
        standings_text = "WNBA STANDINGS\n" + "="*50 + "\n\n"
        
        for i, (team_name, stats) in enumerate(sorted_teams, 1):
            win_pct_display = f"({stats['pct']:.3f})"
            standings_text += f"{i:2d}. {team_name:<22} {stats['record']} {win_pct_display}\n"
        
        standings_text += f"\n✓ Found {len(sorted_teams)} teams"
        return standings_text
        
    except Exception as e:
        return f"Error fetching WNBA standings: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')