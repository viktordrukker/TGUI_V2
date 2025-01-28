from app import celery, db
from app.models import TelegramBot
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery.task
def update_bot_status(bot_id):
    """Update bot status from Redis."""
    try:
        bot = TelegramBot.query.get(bot_id)
        if not bot:
            logger.warning(f"Bot {bot_id} not found")
            return False

        # Get status from Redis
        from app.bot_framework.bot_monitor import BotMonitor
        monitor = BotMonitor()
        status = monitor.get_bot_status(bot.bot_token)
        
        # Update bot record
        bot.status = status['status']
        bot.error_message = status['error']
        bot.webhook_url = status['webhook_url']
        if status['last_update']:
            bot.last_activity = datetime.fromisoformat(status['last_update'])
        db.session.commit()
        
        logger.info(f"Updated status for bot {bot_id}: {status['status']}")
        return True

    except Exception as e:
        logger.error(f"Error updating bot status {bot_id}: {str(e)}")
        return False

@celery.task
def monitor_bots():
    """Monitor all registered bots."""
    try:
        bots = TelegramBot.query.all()
        for bot in bots:
            update_bot_status.delay(bot.id)
        return True
    except Exception as e:
        logger.error(f"Error monitoring bots: {str(e)}")
        return False