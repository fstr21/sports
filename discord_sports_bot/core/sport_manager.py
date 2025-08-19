"""
Sport manager for dynamic loading and management of sport handlers
"""
import logging
from typing import Dict, Optional, List
from discord.ext import commands
from .base_sport_handler import BaseSportHandler
from .mcp_client import MCPClient
from ..config.models import BotConfig


logger = logging.getLogger(__name__)


class SportManager:
    """
    Manages sport handlers with dynamic loading and registration
    """
    
    def __init__(self, config: BotConfig, mcp_client: MCPClient):
        """
        Initialize sport manager
        
        Args:
            config: Bot configuration
            mcp_client: MCP client instance
        """
        self.config = config
        self.mcp_client = mcp_client
        self.sports: Dict[str, BaseSportHandler] = {}
        self._loaded = False
    
    def load_sports(self):
        """
        Dynamically load and register sport handlers based on configuration
        """
        if self._loaded:
            return
        
        logger.info("Loading sport handlers...")
        
        for sport_name, sport_config in self.config.sports.items():
            try:
                handler = self._create_sport_handler(sport_name, sport_config)
                if handler:
                    self.sports[sport_name] = handler
                    logger.info(f"Loaded sport handler: {sport_name}")
                else:
                    logger.warning(f"Failed to create handler for sport: {sport_name}")
            except Exception as e:
                logger.error(f"Error loading sport handler {sport_name}: {e}")
        
        self._loaded = True
        logger.info(f"Sport manager loaded with {len(self.sports)} sports: {', '.join(self.sports.keys())}")
    
    def _create_sport_handler(self, sport_name: str, sport_config) -> Optional[BaseSportHandler]:
        """
        Create sport handler instance based on sport name
        
        Args:
            sport_name: Name of the sport
            sport_config: Sport configuration object
            
        Returns:
            Sport handler instance or None if creation fails
        """
        try:
            # Import sport handlers dynamically
            if sport_name == "soccer":
                from ..sports.soccer_handler import SoccerHandler
                return SoccerHandler(sport_name, sport_config.__dict__, self.mcp_client)
            
            elif sport_name == "mlb":
                from ..sports.mlb_handler import MLBHandler
                return MLBHandler(sport_name, sport_config.__dict__, self.mcp_client)
            
            elif sport_name == "nfl":
                from ..sports.nfl_handler import NFLHandler
                return NFLHandler(sport_name, sport_config.__dict__, self.mcp_client)
            
            elif sport_name == "nba":
                from ..sports.nba_handler import NBAHandler
                return NBAHandler(sport_name, sport_config.__dict__, self.mcp_client)
            
            else:
                logger.warning(f"Unknown sport type: {sport_name}")
                return None
                
        except ImportError as e:
            logger.warning(f"Sport handler not implemented yet: {sport_name} ({e})")
            return None
        except Exception as e:
            logger.error(f"Error creating sport handler {sport_name}: {e}")
            return None
    
    def get_sport_handler(self, sport_name: str) -> Optional[BaseSportHandler]:
        """
        Get sport handler by name
        
        Args:
            sport_name: Name of the sport
            
        Returns:
            Sport handler instance or None if not found
        """
        return self.sports.get(sport_name.lower())
    
    def get_available_sports(self) -> List[str]:
        """
        Get list of available sport names
        
        Returns:
            List of sport names
        """
        return list(self.sports.keys())
    
    def is_sport_available(self, sport_name: str) -> bool:
        """
        Check if a sport is available
        
        Args:
            sport_name: Name of the sport
            
        Returns:
            True if sport is available
        """
        return sport_name.lower() in self.sports
    
    def register_sport_commands(self, bot: commands.Bot):
        """
        Register sport-specific commands with the bot
        
        Args:
            bot: Discord bot instance
        """
        logger.info("Registering sport commands...")
        
        # Create choices for sport selection
        sport_choices = []
        for sport_name in self.sports.keys():
            display_name = sport_name.upper()
            sport_choices.append({"name": display_name, "value": sport_name})
        
        if not sport_choices:
            logger.warning("No sports available for command registration")
            return
        
        logger.info(f"Registered commands for sports: {', '.join(self.sports.keys())}")
    
    def validate_sports(self) -> List[str]:
        """
        Validate all loaded sport handlers
        
        Returns:
            List of validation errors
        """
        errors = []
        
        for sport_name, handler in self.sports.items():
            try:
                # Basic validation - check if handler has required methods
                required_methods = ['create_channels', 'clear_channels', 'get_matches', 'format_match_analysis']
                for method_name in required_methods:
                    if not hasattr(handler, method_name):
                        errors.append(f"Sport handler {sport_name} missing method: {method_name}")
                    elif not callable(getattr(handler, method_name)):
                        errors.append(f"Sport handler {sport_name} method not callable: {method_name}")
                
                # Validate configuration
                if not handler.config.get('mcp_url'):
                    errors.append(f"Sport {sport_name} missing MCP URL")
                
                if not handler.config.get('category_name'):
                    errors.append(f"Sport {sport_name} missing category name")
                    
            except Exception as e:
                errors.append(f"Error validating sport {sport_name}: {e}")
        
        return errors
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Perform health check on all sport handlers
        
        Returns:
            Dictionary mapping sport names to health status
        """
        health_status = {}
        
        for sport_name, handler in self.sports.items():
            try:
                # Basic health check - verify MCP client connectivity
                mcp_url = handler.config.get('mcp_url')
                if mcp_url and self.mcp_client.is_healthy():
                    health_status[sport_name] = True
                else:
                    health_status[sport_name] = False
            except Exception as e:
                logger.error(f"Health check failed for {sport_name}: {e}")
                health_status[sport_name] = False
        
        return health_status