"""
Custom exceptions for the bot framework.
"""

class BotFrameworkError(Exception):
    """Base exception for all bot framework errors."""
    pass

class BotConfigError(BotFrameworkError):
    """Raised when there's an error in bot configuration."""
    pass

class BotHandlerError(BotFrameworkError):
    """Raised when there's an error in bot handler execution."""
    pass

class BotInitializationError(BotFrameworkError):
    """Raised when there's an error during bot initialization."""
    pass