"""
Example script demonstrating DataOrchestrator usage.

This script shows how to use the DataOrchestrator to fetch game data
for multiple leagues on a specific date.
"""

import asyncio
import logging
from datetime import date

from daily_betting_intelligence.data_orchestrator import DataOrchestrator
from daily_betting_intelligence.config_manager import ConfigManager
from clients.logging_config import setup_logging


async def main():
    """Main example function."""
    # Setup logging
    setup_logging(level='INFO')
    logger = logging.getLogger(__name__)
    
    # Create configuration manager
    config_manager = ConfigManager()
    
    # Limit to a few leagues for the example
    config_manager.config.leagues = ['wnba', 'nba']
    config_manager.config.max_concurrent_requests = 2
    
    # Create data orchestrator
    orchestrator = DataOrchestrator(config_manager)
    
    # Use current date (from system context: 2025-08-09)
    target_date = "2025-08-09"
    
    logger.info(f"Fetching game data for {target_date}")
    logger.info(f"Supported leagues: {orchestrator.get_supported_leagues()}")
    
    try:
        # Fetch data for all configured leagues
        results = await orchestrator.fetch_all_leagues_data(target_date)
        
        # Display results
        print(f"\n=== Daily Game Data for {target_date} ===\n")
        
        total_games = 0
        successful_leagues = 0
        
        for league, result in results.items():
            league_display = config_manager.get_league_config(league)['display_name']
            
            if result.success:
                successful_leagues += 1
                total_games += len(result.games)
                
                print(f"{league_display} ({len(result.games)} games):")
                
                if result.games:
                    for game in result.games:
                        status_display = game.status.replace('-', ' ').title()
                        time_str = game.game_time.strftime('%I:%M %p ET')
                        
                        print(f"  • {game.away_team} @ {game.home_team}")
                        print(f"    {time_str} - {status_display}")
                        
                        if game.home_score is not None and game.away_score is not None:
                            print(f"    Score: {game.away_team} {game.away_score}, {game.home_team} {game.home_score}")
                        
                        print(f"    Venue: {game.venue}")
                        print()
                else:
                    print("  No games scheduled\n")
            else:
                print(f"{league_display}: ERROR - {result.error}\n")
        
        # Summary
        print(f"=== Summary ===")
        print(f"Leagues processed: {len(results)}")
        print(f"Successful: {successful_leagues}")
        print(f"Total games: {total_games}")
        
        # Show any errors
        errors = orchestrator.aggregate_errors(results)
        if errors:
            print(f"Errors encountered: {len(errors)}")
            for error in errors:
                print(f"  - {error.context}: {error.error_message}")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())