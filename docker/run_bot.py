"""
Bot runner script for individual bot containers.
"""

import os
import sys
import json
import logging
import asyncio
import signal
from typing import Optional
import redis
from app.models import TelegramBot
from app.bots.number_converter_bot import NumberConverterBot
from app.bots.dice_mmo_bot import DiceMMOBot

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot type mapping
BOT_TYPES = {
    'number_converter': NumberConverterBot,
    'dice_mmo': DiceMMOBot
}

class BotRunner:
    """Runs a single bot instance in a container."""
    
    def __init__(self):
        """Initialize the bot runner."""
        self.bot_token = os.getenv('BOT_TOKEN')
        self.bot_type = os.getenv('BOT_TYPE')
        self.webhook_host = os.getenv('WEBHOOK_HOST')
        self.webhook_port = int(os.getenv('WEBHOOK_PORT', '8443'))
        self.container_name = os.getenv('CONTAINER_NAME')
        
        if not all([self.bot_token, self.bot_type, self.webhook_host]):
            raise ValueError("Missing required environment variables")
        
        self.redis = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
        self.bot_instance = None
        self.running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {signum}")
        self.running = False
        if self.bot_instance:
            asyncio.run(self.stop_bot())
        sys.exit(0)
    
    def update_status(self, status: str, error: Optional[str] = None):
        """Update bot status in Redis."""
        self.redis.hset(
            f"bot:{self.bot_token}",
            mapping={
                'status': status,
                'error': error or '',
                'container': self.container_name,
                'webhook_url': f"https://{self.webhook_host}:{self.webhook_port}/webhook/{self.bot_token}"
            }
        )
    
    async def setup_webhook(self):
        """Set up webhook for the bot."""
        webhook_url = f"https://{self.webhook_host}:{self.webhook_port}/webhook/{self.bot_token}"
        await self.bot_instance.application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    
    async def start_bot(self):
        """Start the bot."""
        try:
            # Get bot class
            bot_class = BOT_TYPES.get(self.bot_type)
            if not bot_class:
                raise ValueError(f"Invalid bot type: {self.bot_type}")
            
            # Initialize bot
            self.update_status('starting')
            self.bot_instance = bot_class(
                token=self.bot_token,
                config={
                    'webhook_host': self.webhook_host,
                    'webhook_port': self.webhook_port
                }
            )
            
            # Start bot and set up webhook
            await self.bot_instance.start()
            await self.setup_webhook()
            
            self.update_status('running')
            self.running = True
            
            # Keep the bot running
            while self.running:
                await asyncio.sleep(1)
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error running bot: {error_msg}")
            self.update_status('error', error_msg)
            raise
    
    async def stop_bot(self):
        """Stop the bot."""
        try:
            if self.bot_instance:
                self.update_status('stopping')
                await self.bot_instance.stop()
                self.update_status('stopped')
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            self.update_status('error', str(e))

def main():
    """Main entry point."""
    try:
        runner = BotRunner()
        asyncio.run(runner.start_bot())
    except Exception as e:
        logger.error(f"Bot runner failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()