from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import TelegramBot
from app.forms import BotRegistrationForm
from app import db, celery
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
import json
import logging

bp = Blueprint('bots', __name__, url_prefix='/bots')
logger = logging.getLogger(__name__)

class BotController:
    def __init__(self, bot_token):
        self.application = ApplicationBuilder().token(bot_token).build()
        self._register_handlers()
        
    def _register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT, self.handle_message))
        
    async def start(self, update: Update, context) -> None:
        await update.message.reply_text("Bot is online and managed by BotManager system!")
        
    async def handle_message(self, update: Update, context) -> None:
        logger.info(f"Message received: {update.message.text}")
        # Implement message handling logic here

@bp.route('/')
@login_required
def list():
    bots = TelegramBot.query.filter_by(user_id=current_user.id).all()
    return render_template('bots/list.html', bots=bots)

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = BotRegistrationForm()
    if form.validate_on_submit():
        bot = TelegramBot(
            bot_token=form.bot_token.data,
            user_id=current_user.id,
            config=json.dumps({'webhook_url': form.webhook_url.data})
        )
        db.session.add(bot)
        db.session.commit()
        
        # Start bot process as Celery task
        start_bot_process.delay(bot.id)
        flash('Bot registered successfully!', 'success')
        return redirect(url_for('bots.list'))
    return render_template('bots/register.html', form=form)

@celery.task(name='start_bot_process')
def start_bot_process(bot_id):
    bot = TelegramBot.query.get(bot_id)
    controller = BotController(bot.bot_token)
    controller.application.run_webhook(
        listen='0.0.0.0',
        port=5001,
        webhook_url=json.loads(bot.config)['webhook_url']
    )