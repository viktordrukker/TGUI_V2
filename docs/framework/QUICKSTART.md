# Quick Start Guide

This guide will help you create and deploy your first bot using our framework.

## Prerequisites

- Python 3.10+
- Docker
- Redis server
- Bot token from [@BotFather](https://t.me/botfather)

## 5-Minute Bot

1. **Clone Template**:
```bash
git clone https://github.com/your-username/telegram-bot-base.git my-bot
cd my-bot
```

2. **Create Bot Class**:

Create `bots/echo_bot.py`:
```python
from main import BotBase
from telegram.ext import CommandHandler, MessageHandler, filters

class EchoBot(BotBase):
    """Simple echo bot example."""
    
    async def start(self):
        """Initialize bot."""
        # Add handlers
        self.application.add_handler(
            CommandHandler("start", self.cmd_start)
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT, self.echo)
        )
        
        # Start bot
        await self.application.initialize()
        await self.application.start()
        self.update_status('running')
    
    async def cmd_start(self, update, context):
        """Handle /start command."""
        await update.message.reply_text(
            "Hi! I'm Echo Bot. Send me any message!"
        )
    
    async def echo(self, update, context):
        """Echo the user message."""
        await update.message.reply_text(update.message.text)
```

3. **Set Environment**:

Create `.env`:
```bash
BOT_TOKEN=your-bot-token
BOT_TYPE=echo_bot
REDIS_URL=redis://redis:6379/0
```

4. **Build & Run**:
```bash
# Build container
docker build -t echo-bot .

# Run bot
docker run -d \
  --name echo_bot \
  --env-file .env \
  --network tgui_v2_default \
  echo-bot
```

5. **Monitor Bot**:
```bash
# View logs
docker logs -f echo_bot

# Check status
docker-compose exec redis redis-cli
> HGETALL "bot:YOUR_BOT_TOKEN"
```

## Next Steps

1. **Add Features**:
   - Add more commands
   - Handle different message types
   - Add user tracking
   - Implement business logic

2. **Improve Error Handling**:
```python
async def echo(self, update, context):
    try:
        await update.message.reply_text(update.message.text)
    except Exception as e:
        self.update_status('error', str(e))
        await update.message.reply_text("Sorry, an error occurred!")
```

3. **Add State Management**:
```python
def __init__(self):
    super().__init__()
    self.state = {
        'messages': 0,
        'users': set()
    }

async def echo(self, update, context):
    self.state['messages'] += 1
    self.state['users'].add(update.effective_user.id)
    await update.message.reply_text(update.message.text)
```

4. **Add Configuration**:
```python
def __init__(self):
    super().__init__()
    self.config = {
        'max_length': int(os.getenv('MAX_LENGTH', 1000)),
        'allowed_users': os.getenv('ALLOWED_USERS', '').split(',')
    }
```

## Common Tasks

1. **Add Command**:
```python
@bot_command("help", "Show help message")
async def cmd_help(self, update, context):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start bot\n"
        "/help - Show this message"
    )
```

2. **Add Handler**:
```python
@bot_handler("message", pattern=r"^/\w+")
async def handle_command(self, update, context):
    await update.message.reply_text(
        f"Unknown command: {update.message.text}"
    )
```

3. **Add Keyboard**:
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [
    [
        InlineKeyboardButton("Option 1", callback_data='1'),
        InlineKeyboardButton("Option 2", callback_data='2')
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text(
    "Choose an option:",
    reply_markup=reply_markup
)
```

4. **Handle Callbacks**:
```python
@bot_handler("callback_query")
async def handle_callback(self, update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"Selected option: {query.data}"
    )
```

## Testing

1. **Manual Testing**:
```bash
# Run bot locally
python main.py

# Send messages to bot
# Check responses
# Verify state updates
```

2. **Automated Testing**:
```python
# test_echo_bot.py
import pytest
from bots.echo_bot import EchoBot

@pytest.fixture
def bot():
    return EchoBot()

def test_echo(bot):
    # Mock update
    update = Mock()
    update.message.text = "Hello"
    
    # Test echo
    response = await bot.echo(update, None)
    assert response.text == "Hello"
```

## Deployment

1. **Production Settings**:
```bash
# .env.prod
BOT_TOKEN=prod-bot-token
BOT_TYPE=echo_bot
REDIS_URL=redis://prod-redis:6379/0
LOG_LEVEL=INFO
```

2. **Deploy Container**:
```bash
docker build -t echo-bot:prod .
docker run -d \
  --name echo_bot_prod \
  --env-file .env.prod \
  --restart unless-stopped \
  echo-bot:prod
```

3. **Monitor Production**:
```bash
# View logs
docker logs -f echo_bot_prod

# Check metrics
docker stats echo_bot_prod

# Monitor Redis
redis-cli -h prod-redis
```

## Support

Need help?
1. Read [Framework Documentation](README.md)
2. Check [Example Bots](../examples/)
3. Open GitHub Issue
4. Contact Support Team