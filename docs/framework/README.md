# Telegram Bot Framework Documentation

## Overview

This framework provides a standardized way to create Telegram bots that can be managed through the TGUI V2 management interface. Each bot runs in its own container and communicates its status through Redis.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Bot Development](#bot-development)
4. [State Management](#state-management)
5. [Status Reporting](#status-reporting)
6. [Integration Guide](#integration-guide)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Getting Started

1. **Clone the Base Project**:
```bash
git clone https://github.com/your-username/telegram-bot-base.git
cd telegram-bot-base
```

2. **Install Dependencies**:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

3. **Set Up Environment**:
```bash
cp .env.example .env
# Edit .env with your settings:
# BOT_TOKEN=your-bot-token
# BOT_TYPE=your-bot-type
# REDIS_URL=redis://redis:6379/0
```

## Project Structure

```
telegram-bot-base/
├── bots/                  # Bot implementations
│   ├── __init__.py
│   ├── base.py           # Base bot class
│   └── your_bot.py       # Your bot implementation
├── main.py               # Bot runner script
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## Bot Development

1. **Create Your Bot Class**:

```python
from main import BotBase

class MyBot(BotBase):
    """
    My custom bot implementation.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize your bot state
        self.state = {
            'users': set(),
            'messages': 0
        }
    
    async def start(self):
        """Initialize bot and set up handlers."""
        # Set up command handlers
        self.application.add_handler(
            CommandHandler("start", self.cmd_start)
        )
        
        # Set up message handlers
        self.application.add_handler(
            MessageHandler(filters.TEXT, self.handle_message)
        )
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        
        # Update status
        self.update_status('running')
    
    async def stop(self):
        """Clean up and stop bot."""
        # Save state
        self._save_state()
        
        # Stop the bot
        await self.application.stop()
        
        # Update status
        self.update_status('stopped')
    
    async def cmd_start(self, update, context):
        """Handle /start command."""
        user_id = update.effective_user.id
        self.state['users'].add(user_id)
        await update.message.reply_text("Welcome!")
    
    async def handle_message(self, update, context):
        """Handle text messages."""
        self.state['messages'] += 1
        # Your message handling logic here
```

2. **Update Bot Type**:

Add your bot type to the management interface configuration:

```python
BOT_TYPES = {
    'my_bot': MyBot,
    # ... other bot types ...
}
```

## State Management

The framework provides built-in state persistence through Redis:

1. **Save State**:
```python
self._save_state()  # Automatically called on stop
```

2. **Load State**:
```python
self.state = self._load_state()  # Automatically called on start
```

3. **State Structure**:
```python
self.state = {
    'key1': value1,
    'key2': value2,
    # Any JSON-serializable data
}
```

## Status Reporting

Bots should report their status to the management interface:

1. **Update Status**:
```python
self.update_status(
    status='running',      # running, error, stopped
    error=None,           # Error message if any
    webhook_url=None      # Webhook URL if using webhooks
)
```

2. **Status Types**:
- `running`: Bot is operational
- `error`: Bot encountered an error
- `stopped`: Bot is stopped
- `starting`: Bot is initializing
- `stopping`: Bot is shutting down

## Integration Guide

1. **Build Container**:
```bash
docker build -t my-telegram-bot .
```

2. **Run Container**:
```bash
docker run -d \
  --name my_bot \
  --env-file .env \
  --network tgui_v2_default \
  my-telegram-bot
```

3. **Register in Management UI**:
- Open management interface
- Add bot with token
- Select your bot type
- Monitor status

## Best Practices

1. **State Management**:
   - Keep state minimal
   - Use atomic updates
   - Handle load/save errors
   - Regular state backups

2. **Error Handling**:
```python
try:
    # Your code
except Exception as e:
    self.update_status('error', str(e))
    logger.error(f"Error: {e}")
```

3. **Resource Management**:
   - Clean up resources in stop()
   - Use async context managers
   - Handle disconnections
   - Implement graceful shutdown

4. **Logging**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Operation successful")
logger.error("Error occurred", exc_info=True)
```

5. **Configuration**:
   - Use environment variables
   - Don't hardcode values
   - Validate configuration
   - Document requirements

## Troubleshooting

1. **Bot Not Starting**:
   - Check logs: `docker logs my_bot`
   - Verify environment variables
   - Check Redis connection
   - Verify token validity

2. **State Issues**:
   - Check Redis connection
   - Verify state format
   - Check permissions
   - Clear state: `redis-cli DEL "bot_state:YOUR_TOKEN"`

3. **Status Updates**:
   - Check Redis keys
   - Verify status format
   - Check network connectivity
   - Monitor logs

4. **Common Errors**:
   ```
   # Check bot status
   redis-cli HGETALL "bot:YOUR_TOKEN"
   
   # Check bot state
   redis-cli GET "bot_state:YOUR_TOKEN"
   
   # Check logs
   docker logs my_bot
   ```

## Example Implementations

1. **Number Converter Bot**:
   - [Source Code](bots/number_converter.py)
   - Handles number conversions
   - Multiple language support
   - State persistence

2. **Dice MMO Bot**:
   - [Source Code](bots/dice_mmo.py)
   - Game mechanics
   - User tracking
   - Score persistence

## Support

For issues and questions:
1. Check documentation
2. Review logs
3. Open GitHub issue
4. Contact support team