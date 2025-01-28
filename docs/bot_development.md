# Bot Development Guide

This guide explains how to create and integrate new Telegram bots into the TGUI V2 management system.

## Table of Contents
1. [Framework Overview](#framework-overview)
2. [Creating a New Bot](#creating-a-new-bot)
3. [Bot Features](#bot-features)
4. [Best Practices](#best-practices)
5. [Example Bots](#example-bots)

## Framework Overview

The bot framework provides a structured way to create Telegram bots with common functionality and consistent error handling. Key components include:

- `BaseTelegramBot`: Base class for all bots
- `bot_command`: Decorator for command handlers
- `bot_handler`: Decorator for message/event handlers
- `BotManager`: Class for managing multiple bot instances

## Creating a New Bot

1. Create a new Python file in `app/bots/`
2. Import the framework components:
```python
from app.bot_framework import BaseTelegramBot, bot_command, bot_handler
```

3. Create your bot class:
```python
class MyBot(BaseTelegramBot):
    def __init__(self, token: str, config: dict = None):
        super().__init__(
            token=token,
            name="MyBot",
            description="Description of my bot",
            config=config or {}
        )
```

4. Add command handlers:
```python
@bot_command("start", "Start the bot")
async def cmd_start(self, update, context):
    await update.message.reply_text("Hello! Bot started.")
```

5. Add message handlers:
```python
@bot_handler("message", pattern=r"^hello$")
async def handle_hello(self, update, context):
    await update.message.reply_text("Hi there!")
```

## Bot Features

### Commands
- Use `@bot_command` decorator
- Specify command name and description
- Optional `admin_only` parameter
```python
@bot_command("help", "Show help", admin_only=False)
async def cmd_help(self, update, context):
    # Command implementation
```

### Message Handlers
- Use `@bot_handler` decorator
- Specify event type and optional pattern
- Set priority for multiple handlers
```python
@bot_handler("message", pattern=r"^\d+$", priority=1)
async def handle_numbers(self, update, context):
    # Handler implementation
```

### Configuration
- Pass configuration in bot initialization
- Access via `self.config`
```python
config = {
    'admin_ids': [123456789],
    'custom_setting': 'value'
}
bot = MyBot(token="BOT_TOKEN", config=config)
```

## Best Practices

1. **Error Handling**
   - Use try-except blocks for user input
   - Raise appropriate framework exceptions
   - Provide clear error messages to users

2. **Documentation**
   - Document all commands and features
   - Include examples in command help
   - Use docstrings for methods

3. **User Experience**
   - Provide clear instructions
   - Use emoji for visual feedback
   - Include help commands

4. **Performance**
   - Avoid blocking operations
   - Use async/await properly
   - Cache frequent data

5. **Security**
   - Validate all user input
   - Use admin_only for sensitive commands
   - Implement rate limiting

## Example Bots

### Numbers Bot
See `app/bots/numbers_bot.py` for an example of:
- Basic command handling
- Input validation
- Number processing
- User feedback

### Dice Roller Bot
See `app/bots/dice_bot.py` for an example of:
- Complex input parsing
- Multiple command variations
- Admin-only features
- Formatted responses

## Integration Steps

1. Create your bot class
2. Test locally
3. Add to bot manager:
```python
from app.bot_framework.manager import BotManager
from app.bots.my_bot import MyBot

manager = BotManager()
await manager.add_bot(MyBot, "BOT_TOKEN", config={})
```

4. Register in the management interface

## Testing

1. Create unit tests in `tests/bots/`
2. Test all commands and handlers
3. Test error cases
4. Test admin features
5. Test concurrent usage

## Deployment

1. Add bot token to environment variables
2. Update configuration as needed
3. Restart the application
4. Monitor bot status in admin interface

## Support

For questions or issues:
1. Check existing documentation
2. Review example bots
3. Contact the development team
4. Submit issues on GitHub