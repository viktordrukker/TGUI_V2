"""
Base class for all Telegram bots in the system.
Provides common functionality and structure for bot implementation.
"""

import logging
import inspect
from typing import Dict, List, Optional, Any, Callable
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from .exceptions import BotInitializationError, BotConfigError

logger = logging.getLogger(__name__)

class BaseTelegramBot:
    """
    Base class for all Telegram bots in the system.
    
    Attributes:
        token (str): Bot API token
        name (str): Bot name
        description (str): Bot description
        application (Application): Telegram application instance
        config (dict): Bot configuration
        commands (dict): Registered bot commands
        handlers (dict): Registered event handlers
    """
    
    def __init__(self, token: str, name: str, description: str = "", config: Optional[Dict] = None):
        """
        Initialize the bot.
        
        Args:
            token (str): Bot API token
            name (str): Bot name
            description (str): Bot description
            config (dict, optional): Additional bot configuration
        """
        self.token = token
        self.name = name
        self.description = description
        self.config = config or {}
        self.commands = {}
        self.handlers = {}
        self.application = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the bot application and register handlers."""
        try:
            self.application = Application.builder().token(self.token).build()
            self._register_methods()
            logger.info(f"Bot {self.name} initialized successfully")
        except Exception as e:
            raise BotInitializationError(f"Failed to initialize bot {self.name}: {str(e)}") from e
    
    def _register_methods(self) -> None:
        """Register all decorated methods as commands or handlers."""
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '_bot_command'):
                self._register_command(method)
            elif hasattr(method, '_bot_handler'):
                self._register_handler(method)
    
    def _register_command(self, method: Callable) -> None:
        """Register a command handler."""
        command = method._command
        self.commands[command] = {
            'handler': method,
            'description': method._description,
            'admin_only': method._admin_only
        }
        self.application.add_handler(
            CommandHandler(command, method)
        )
        logger.debug(f"Registered command /{command} for bot {self.name}")
    
    def _register_handler(self, method: Callable) -> None:
        """Register an event handler."""
        event_type = method._event_type
        pattern = method._pattern
        priority = method._priority
        
        if event_type == "message":
            handler = MessageHandler(
                filters.TEXT & (filters.Regex(pattern) if pattern else filters.ALL),
                method
            )
        elif event_type == "callback_query":
            handler = CallbackQueryHandler(
                method,
                pattern=pattern
            )
        else:
            raise BotConfigError(f"Unsupported event type: {event_type}")
        
        self.application.add_handler(handler, group=priority)
        logger.debug(f"Registered {event_type} handler for bot {self.name}")
    
    async def is_admin(self, user_id: int) -> bool:
        """
        Check if a user is an admin.
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if user is admin, False otherwise
        """
        admin_ids = self.config.get('admin_ids', [])
        return user_id in admin_ids
    
    async def start(self) -> None:
        """Start the bot."""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.update_bot_commands([
                (cmd, info['description'])
                for cmd, info in self.commands.items()
                if not info['admin_only']
            ])
            logger.info(f"Bot {self.name} started successfully")
        except Exception as e:
            raise BotInitializationError(f"Failed to start bot {self.name}: {str(e)}") from e
    
    async def stop(self) -> None:
        """Stop the bot."""
        try:
            await self.application.stop()
            logger.info(f"Bot {self.name} stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping bot {self.name}: {str(e)}")
    
    def get_command_list(self) -> List[Dict[str, str]]:
        """
        Get list of available commands.
        
        Returns:
            List[Dict[str, str]]: List of command information
        """
        return [
            {
                'command': cmd,
                'description': info['description'],
                'admin_only': info['admin_only']
            }
            for cmd, info in self.commands.items()
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get bot statistics.
        
        Returns:
            Dict[str, Any]: Bot statistics
        """
        return {
            'name': self.name,
            'description': self.description,
            'commands': len(self.commands),
            'handlers': len(self.handlers),
            'config': self.config
        }