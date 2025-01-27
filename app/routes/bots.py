from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import TelegramBot
from app.forms import BotRegistrationForm
from app import db, celery
import json
import logging
import asyncio
from datetime import datetime
from telegram import Update
from app.bot_framework.container_manager import ContainerManager

bp = Blueprint('bots', __name__, url_prefix='/bots')
logger = logging.getLogger(__name__)

# Global container manager instance
container_manager = ContainerManager()

@bp.route('/')
@login_required
def list():
    """List all bots for the current user."""
    bots = TelegramBot.query.filter_by(user_id=current_user.id).all()
    return render_template('bots/list.html', bots=bots)

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Register a new bot."""
    form = BotRegistrationForm()
    if form.validate_on_submit():
        try:
            # Create bot record
            config = {
                'webhook_url': form.webhook_url.data
            }
            if form.config.data:
                config.update(json.loads(form.config.data))

            bot = TelegramBot(
                bot_token=form.bot_token.data,
                user_id=current_user.id,
                bot_type=form.bot_type.data,
                config=json.dumps(config),
                status='stopped'
            )
            db.session.add(bot)
            db.session.commit()
            
            # Start bot process
            start_bot_process.delay(bot.id)
            flash('Bot registered successfully!', 'success')
            return redirect(url_for('bots.list'))
            
        except json.JSONDecodeError:
            flash('Invalid JSON configuration', 'error')
        except Exception as e:
            flash(f'Error registering bot: {str(e)}', 'error')
            logger.error(f'Bot registration error: {str(e)}')
    
    return render_template('bots/register.html', form=form)

@bp.route('/<int:bot_id>/control/<action>')
@login_required
def control_bot(bot_id, action):
    """Control bot (start/stop/restart)."""
    bot = TelegramBot.query.filter_by(id=bot_id, user_id=current_user.id).first_or_404()
    
    try:
        if action == 'start':
            if bot.status != 'running':
                start_bot_process.delay(bot.id)
                flash('Bot starting...', 'success')
        elif action == 'stop':
            if bot.status == 'running':
                stop_bot_process.delay(bot.id)
                flash('Bot stopping...', 'success')
        elif action == 'restart':
            restart_bot_process.delay(bot.id)
            flash('Bot restarting...', 'success')
        else:
            flash('Invalid action', 'error')
    except Exception as e:
        flash(f'Error controlling bot: {str(e)}', 'error')
        logger.error(f'Bot control error: {str(e)}')
    
    return redirect(url_for('bots.list'))

@bp.route('/<int:bot_id>/stats')
@login_required
def bot_stats(bot_id):
    """Get bot statistics."""
    bot = TelegramBot.query.filter_by(id=bot_id, user_id=current_user.id).first_or_404()
    return jsonify(bot.stats or {})

def run_async(coro):
    """Run an async function in a synchronous context."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@celery.task(name='start_bot_process')
def start_bot_process(bot_id):
    """Start a bot process."""
    try:
        bot = TelegramBot.query.get(bot_id)
        if not bot:
            raise ValueError(f"Bot {bot_id} not found")

        # Start bot container
        status = container_manager.start_bot(bot.bot_token, bot.bot_type)
        
        # Update bot record
        bot.status = status['status']
        bot.error_message = status['error']
        bot.webhook_url = status['webhook_url']
        bot.container_name = status['container']
        bot.last_activity = datetime.utcnow()
        db.session.commit()

        logger.info(f"Bot {bot_id} started successfully")

    except Exception as e:
        logger.error(f"Error starting bot {bot_id}: {str(e)}")
        if bot:
            bot.status = 'error'
            bot.error_message = str(e)
            db.session.commit()

@celery.task(name='stop_bot_process')
def stop_bot_process(bot_id):
    """Stop a bot process."""
    try:
        bot = TelegramBot.query.get(bot_id)
        if not bot:
            raise ValueError(f"Bot {bot_id} not found")

        # Stop bot container
        container_manager.stop_bot(bot.bot_token)
        
        # Update bot record
        bot.status = 'stopped'
        bot.error_message = ''
        bot.webhook_url = ''
        bot.container_name = ''
        bot.last_activity = datetime.utcnow()
        db.session.commit()

        logger.info(f"Bot {bot_id} stopped successfully")

    except Exception as e:
        logger.error(f"Error stopping bot {bot_id}: {str(e)}")
        if bot:
            bot.status = 'error'
            bot.error_message = str(e)
            db.session.commit()

@celery.task(name='restart_bot_process')
def restart_bot_process(bot_id):
    """Restart a bot process."""
    try:
        stop_bot_process(bot_id)
        start_bot_process(bot_id)
    except Exception as e:
        logger.error(f"Error restarting bot {bot_id}: {str(e)}")

@celery.task(name='update_bot_status')
def update_bot_status(bot_id):
    """Update bot status from container."""
    try:
        bot = TelegramBot.query.get(bot_id)
        if not bot:
            return

        # Get status from container manager
        status = container_manager.get_bot_status(bot.bot_token)
        
        # Update bot record
        bot.status = status['status']
        bot.error_message = status['error']
        bot.webhook_url = status['webhook_url']
        bot.container_name = status['container']
        bot.last_activity = datetime.utcnow()
        db.session.commit()

    except Exception as e:
        logger.error(f"Error updating bot status {bot_id}: {str(e)}")

@bp.route('/status/<int:bot_id>')
@login_required
def get_bot_status(bot_id):
    """Get bot status."""
    bot = TelegramBot.query.filter_by(id=bot_id, user_id=current_user.id).first_or_404()
    
    # Get status from container
    status = container_manager.get_bot_status(bot.bot_token)
    
    return jsonify({
        'status': status['status'],
        'error': status['error'],
        'webhook_url': status['webhook_url'],
        'container': status['container'],
        'last_activity': bot.last_activity.isoformat() if bot.last_activity else None
    })

@bp.route('/webhook-url/<int:bot_id>')
@login_required
def get_webhook_url(bot_id):
    """Get the webhook URL for a bot."""
    bot = TelegramBot.query.filter_by(id=bot_id, user_id=current_user.id).first_or_404()
    
    # Get the base URL from request
    base_url = request.url_root.rstrip('/')
    if request.headers.get('X-Forwarded-Proto') == 'https':
        base_url = base_url.replace('http://', 'https://')
    
    webhook_url = f"{base_url}/bots/webhook/{bot.bot_token}"
    
    return jsonify({
        'webhook_url': webhook_url,
        'test_command': f'curl -F "url={webhook_url}" https://api.telegram.org/bot{bot.bot_token}/setWebhook'
    })