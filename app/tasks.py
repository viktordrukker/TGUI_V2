from app import celery, db
from app.models import TelegramBot
from datetime import datetime
import requests

@celery.task
def setup_webhook(bot_id):
    """Set up webhook for a Telegram bot"""
    bot = TelegramBot.query.get(bot_id)
    if not bot:
        return False
        
    webhook_url = f"{app.config['WEBHOOK_URL_BASE']}/bot/{bot.id}/webhook"
    api_url = f"{app.config['TELEGRAM_API_URL']}/bot{bot.bot_token}/setWebhook"
    
    try:
        response = requests.post(api_url, json={'url': webhook_url})
        if response.status_code == 200 and response.json().get('ok'):
            bot.is_active = True
            bot.last_activity = datetime.utcnow()
            db.session.commit()
            return True
    except Exception as e:
        print(f"Error setting webhook for bot {bot.id}: {str(e)}")
    return False

@celery.task
def check_bot_status(bot_id):
    """Check if a bot is still active and responding"""
    bot = TelegramBot.query.get(bot_id)
    if not bot:
        return False
        
    api_url = f"{app.config['TELEGRAM_API_URL']}/bot{bot.bot_token}/getMe"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200 and response.json().get('ok'):
            bot.last_activity = datetime.utcnow()
            db.session.commit()
            return True
    except Exception as e:
        print(f"Error checking status for bot {bot.id}: {str(e)}")
        bot.is_active = False
        db.session.commit()
    return False

@celery.task
def send_message(bot_id, chat_id, text, parse_mode='HTML'):
    """Send a message using the bot"""
    bot = TelegramBot.query.get(bot_id)
    if not bot:
        return False
        
    api_url = f"{app.config['TELEGRAM_API_URL']}/bot{bot.bot_token}/sendMessage"
    
    try:
        response = requests.post(api_url, json={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        })
        return response.status_code == 200 and response.json().get('ok', False)
    except Exception as e:
        print(f"Error sending message for bot {bot.id}: {str(e)}")
    return False