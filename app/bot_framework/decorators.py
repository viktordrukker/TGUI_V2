"""
Decorators for the bot framework.
These decorators help in registering commands and handlers for bot functionality.
"""

import functools
from typing import Callable, Optional, Any
from .exceptions import BotHandlerError

def bot_command(command: str, description: str = "", admin_only: bool = False):
    """
    Decorator to register a bot command.
    
    Args:
        command (str): The command name without the leading slash
        description (str): Command description for the bot's command list
        admin_only (bool): Whether the command is restricted to admin users
    
    Example:
        @bot_command("start", "Start the bot")
        async def start_command(update, context):
            await update.message.reply_text("Bot started!")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, update, context, *args, **kwargs):
            if admin_only and not await self.is_admin(update.effective_user.id):
                await update.message.reply_text("This command is only available to administrators.")
                return
            return await func(self, update, context, *args, **kwargs)
        
        wrapper._bot_command = True
        wrapper._command = command
        wrapper._description = description
        wrapper._admin_only = admin_only
        return wrapper
    return decorator

def bot_handler(event_type: str, pattern: Optional[str] = None, priority: int = 1):
    """
    Decorator to register a bot event handler.
    
    Args:
        event_type (str): Type of event to handle (message, callback_query, etc.)
        pattern (str, optional): Regex pattern for filtering messages
        priority (int): Handler priority (lower numbers = higher priority)
    
    Example:
        @bot_handler("message", pattern=r"^[0-9]+$")
        async def handle_numbers(update, context):
            await update.message.reply_text("That's a number!")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, update, context, *args, **kwargs):
            try:
                return await func(self, update, context, *args, **kwargs)
            except Exception as e:
                raise BotHandlerError(f"Error in handler {func.__name__}: {str(e)}") from e
        
        wrapper._bot_handler = True
        wrapper._event_type = event_type
        wrapper._pattern = pattern
        wrapper._priority = priority
        return wrapper
    return decorator