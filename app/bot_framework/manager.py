"""
Bot Manager class for handling multiple bot instances.
"""

import logging
from typing import Dict, List, Type, Optional
from .base import BaseTelegramBot
from .exceptions import BotFrameworkError

logger = logging.getLogger(__name__)

class BotManager:
    """
    Manages multiple bot instances.
    
    Attributes:
        bots (Dict[str, BaseTelegramBot]): Dictionary of active bot instances
    """
    
    def __init__(self):
        """Initialize the bot manager."""
        self.bots: Dict[str, BaseTelegramBot] = {}
    
    async def add_bot(self, bot_class: Type[BaseTelegramBot], token: str, config: Optional[Dict] = None) -> BaseTelegramBot:
        """
        Add a new bot instance.
        
        Args:
            bot_class: The bot class to instantiate
            token: Bot API token
            config: Optional bot configuration
            
        Returns:
            BaseTelegramBot: The created bot instance
            
        Raises:
            BotFrameworkError: If bot creation fails
        """
        try:
            bot = bot_class(token=token, config=config)
            self.bots[token] = bot
            await bot.start()
            logger.info(f"Added bot {bot.name} successfully")
            return bot
        except Exception as e:
            raise BotFrameworkError(f"Failed to add bot: {str(e)}") from e
    
    async def remove_bot(self, token: str) -> None:
        """
        Remove a bot instance.
        
        Args:
            token: Bot API token
            
        Raises:
            BotFrameworkError: If bot removal fails
        """
        try:
            if token in self.bots:
                bot = self.bots[token]
                await bot.stop()
                del self.bots[token]
                logger.info(f"Removed bot {bot.name} successfully")
            else:
                logger.warning(f"Bot with token {token} not found")
        except Exception as e:
            raise BotFrameworkError(f"Failed to remove bot: {str(e)}") from e
    
    def get_bot(self, token: str) -> Optional[BaseTelegramBot]:
        """
        Get a bot instance by token.
        
        Args:
            token: Bot API token
            
        Returns:
            Optional[BaseTelegramBot]: The bot instance or None if not found
        """
        return self.bots.get(token)
    
    def get_all_bots(self) -> List[BaseTelegramBot]:
        """
        Get all active bot instances.
        
        Returns:
            List[BaseTelegramBot]: List of active bot instances
        """
        return list(self.bots.values())
    
    async def start_all(self) -> None:
        """Start all registered bots."""
        for bot in self.bots.values():
            try:
                await bot.start()
            except Exception as e:
                logger.error(f"Failed to start bot {bot.name}: {str(e)}")
    
    async def stop_all(self) -> None:
        """Stop all registered bots."""
        for bot in self.bots.values():
            try:
                await bot.stop()
            except Exception as e:
                logger.error(f"Failed to stop bot {bot.name}: {str(e)}")
    
    def get_stats(self) -> Dict:
        """
        Get statistics for all bots.
        
        Returns:
            Dict: Statistics for all managed bots
        """
        return {
            'total_bots': len(self.bots),
            'bots': [bot.get_stats() for bot in self.bots.values()]
        }