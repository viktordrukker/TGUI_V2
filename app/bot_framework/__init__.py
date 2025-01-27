"""
Bot Framework for TGUI V2
This package provides the base framework for implementing Telegram bots
in a standardized way within the TGUI V2 management system.
"""

from .base import BaseTelegramBot
from .decorators import bot_command, bot_handler
from .exceptions import BotFrameworkError

__all__ = ['BaseTelegramBot', 'bot_command', 'bot_handler', 'BotFrameworkError']