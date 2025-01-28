"""
Template bot with common patterns and best practices.
"""

import os
import logging
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from main import BotBase

logger = logging.getLogger(__name__)

class TemplateBot(BotBase):
    """
    Template bot implementation with common patterns.
    
    Features:
    - Command handling
    - Message handling
    - State management
    - Error handling
    - Configuration
    - Keyboard support
    """
    
    def __init__(self):
        """Initialize bot."""
        super().__init__()
        
        # Initialize state
        self.state = {
            'users': set(),          # Track users
            'messages': 0,           # Message counter
            'commands': 0,           # Command counter
            'errors': 0,            # Error counter
            'settings': {}          # User settings
        }
        
        # Load configuration
        self.config = {
            'max_messages': int(os.getenv('MAX_MESSAGES', 1000)),
            'admin_ids': list(map(int, os.getenv('ADMIN_IDS', '').split(','))),
            'allowed_commands': os.getenv('ALLOWED_COMMANDS', 'start,help').split(','),
            'maintenance_mode': os.getenv('MAINTENANCE_MODE', '0') == '1'
        }
    
    async def start(self):
        """Initialize and start bot."""
        try:
            # Register command handlers
            self.application.add_handler(
                CommandHandler("start", self.cmd_start)
            )
            self.application.add_handler(
                CommandHandler("help", self.cmd_help)
            )
            self.application.add_handler(
                CommandHandler("stats", self.cmd_stats)
            )
            
            # Register message handlers
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.handle_message
                )
            )
            
            # Register callback handlers
            self.application.add_handler(
                CallbackQueryHandler(self.handle_callback)
            )
            
            # Register error handler
            self.application.add_error_handler(self.error_handler)
            
            # Initialize and start
            await self.application.initialize()
            await self.application.start()
            
            # Update status
            self.update_status('running')
            logger.info("Bot started successfully")
            
        except Exception as e:
            self.update_status('error', str(e))
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """Stop bot and clean up."""
        try:
            # Save state
            self._save_state()
            
            # Stop bot
            await self.application.stop()
            
            # Update status
            self.update_status('stopped')
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            self.update_status('error', str(e))
            logger.error(f"Failed to stop bot: {e}")
            raise
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        try:
            user_id = update.effective_user.id
            self.state['users'].add(user_id)
            self.state['commands'] += 1
            
            # Create keyboard
            keyboard = [
                [
                    InlineKeyboardButton("Help", callback_data='help'),
                    InlineKeyboardButton("Stats", callback_data='stats')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "👋 Welcome to Template Bot!\n\n"
                "This is a template with common patterns.\n"
                "Click a button or send a message.",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await self.error_handler(update, context, e)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        try:
            self.state['commands'] += 1
            
            await update.message.reply_text(
                "📖 Available Commands:\n\n"
                "/start - Start bot\n"
                "/help - Show this message\n"
                "/stats - Show statistics\n\n"
                "You can also send any message!"
            )
            
        except Exception as e:
            await self.error_handler(update, context, e)
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        try:
            self.state['commands'] += 1
            
            stats = (
                "📊 Bot Statistics:\n\n"
                f"Users: {len(self.state['users'])}\n"
                f"Messages: {self.state['messages']}\n"
                f"Commands: {self.state['commands']}\n"
                f"Errors: {self.state['errors']}"
            )
            
            await update.message.reply_text(stats)
            
        except Exception as e:
            await self.error_handler(update, context, e)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        try:
            # Update stats
            self.state['messages'] += 1
            user_id = update.effective_user.id
            self.state['users'].add(user_id)
            
            # Process message
            text = update.message.text
            await update.message.reply_text(
                f"You said: {text}\n"
                f"Message count: {self.state['messages']}"
            )
            
        except Exception as e:
            await self.error_handler(update, context, e)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries."""
        try:
            query = update.callback_query
            await query.answer()
            
            if query.data == 'help':
                await self.cmd_help(update, context)
            elif query.data == 'stats':
                await self.cmd_stats(update, context)
            else:
                await query.edit_message_text(
                    f"Unknown callback: {query.data}"
                )
            
        except Exception as e:
            await self.error_handler(update, context, e)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception = None):
        """Handle errors."""
        # Update error stats
        self.state['errors'] += 1
        
        # Log error
        if error:
            logger.error(f"Error: {error}", exc_info=True)
        else:
            logger.error("Error in update: %s", update, exc_info=context.error)
        
        # Notify user
        try:
            await update.effective_message.reply_text(
                "❌ Sorry, an error occurred while processing your request."
            )
        except:
            pass
        
        # Update status if serious error
        if isinstance(error, (ConnectionError, TimeoutError)):
            self.update_status('error', str(error))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics for monitoring."""
        return {
            'users': len(self.state['users']),
            'messages': self.state['messages'],
            'commands': self.state['commands'],
            'errors': self.state['errors']
        }