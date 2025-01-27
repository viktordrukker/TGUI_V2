from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import TelegramBot
from app.forms import BotRegistrationForm
from app import db, celery
import json
import logging
from datetime import datetime
from app.bot_framework.manager import BotManager

bp = Blueprint('bots', __name__, url_prefix='/bots')
logger = logging.getLogger(__name__)

# Global bot manager instance
bot_manager = BotManager()

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

@celery.task(name='start_bot_process')
def start_bot_process(bot_id):
    """Start a bot process."""
    try:
        bot = TelegramBot.query.get(bot_id)
        if not bot:
            raise ValueError(f"Bot {bot_id} not found")

        # Get the appropriate bot class
        bot_class = bot.get_controller_class()
        if not bot_class:
            raise ValueError(f"Invalid bot type: {bot.bot_type}")

        # Update status
        bot.status = 'starting'
        bot.error_message = None
        db.session.commit()

        # Initialize and start bot
        config = json.loads(bot.config) if bot.config else {}
        instance = await bot_manager.add_bot(bot_class, bot.bot_token, config)

        # Update bot record
        bot.status = 'running'
        bot.is_active = True
        bot.last_activity = datetime.utcnow()
        db.session.commit()

        logger.info(f"Bot {bot_id} started successfully")

    except Exception as e:
        logger.error(f"Error starting bot {bot_id}: {str(e)}")
        if bot:
            bot.status = 'error'
            bot.error_message = str(e)
            bot.is_active = False
            db.session.commit()

@celery.task(name='stop_bot_process')
async def stop_bot_process(bot_id):
    """Stop a bot process."""
    try:
        bot = TelegramBot.query.get(bot_id)
        if not bot:
            raise ValueError(f"Bot {bot_id} not found")

        # Update status
        bot.status = 'stopping'
        db.session.commit()

        # Stop bot
        await bot_manager.remove_bot(bot.bot_token)

        # Update bot record
        bot.status = 'stopped'
        bot.is_active = False
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
async def restart_bot_process(bot_id):
    """Restart a bot process."""
    try:
        await stop_bot_process(bot_id)
        await start_bot_process(bot_id)
    except Exception as e:
        logger.error(f"Error restarting bot {bot_id}: {str(e)}")

@celery.task(name='update_bot_stats')
def update_bot_stats(bot_id):
    """Update bot statistics."""
    try:
        bot = TelegramBot.query.get(bot_id)
        if not bot or bot.status != 'running':
            return

        instance = bot_manager.get_bot(bot.bot_token)
        if instance:
            stats = instance.get_stats()
            bot.update_stats(stats)
            db.session.commit()

    except Exception as e:
        logger.error(f"Error updating bot stats {bot_id}: {str(e)}")