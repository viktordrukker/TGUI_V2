"""
Number Converter Bot
Converts numbers to words and vice versa in multiple languages.
"""

from num2words import num2words
from word2number import w2n
from typing import Dict, Optional
from app.bot_framework import BaseTelegramBot, bot_command, bot_handler

class NumberConverterBot(BaseTelegramBot):
    """
    A bot that converts numbers to words and vice versa in multiple languages.
    Features:
    - Convert numbers to words
    - Convert words to numbers
    - Support multiple languages
    - Language selection
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'ru': 'Russian'
    }
    
    def __init__(self, token: str, config: dict = None):
        super().__init__(
            token=token,
            name="NumberConverterBot",
            description="Convert numbers to words and vice versa in multiple languages",
            config=config or {}
        )
        # User language preferences: {user_id: language_code}
        self.user_languages: Dict[int, str] = {}
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language or default to English."""
        return self.user_languages.get(user_id, 'en')
    
    @bot_command("start", "Start the bot")
    async def cmd_start(self, update, context):
        """Handle the /start command."""
        await update.message.reply_text(
            "👋 Welcome to Number Converter Bot!\n\n"
            "I can help you convert numbers to words and vice versa.\n\n"
            "Commands:\n"
            "/towords <number> - Convert number to words\n"
            "/tonumber <text> - Convert words to number\n"
            "/language - Set your preferred language\n"
            "/help - Show help message"
        )
    
    @bot_command("help", "Show help information")
    async def cmd_help(self, update, context):
        """Show help information."""
        help_text = (
            "🔢 *Number Converter Bot Help*\n\n"
            "*Commands:*\n"
            "• `/towords <number>` - Convert number to words\n"
            "• `/tonumber <text>` - Convert words to number\n"
            "• `/language` - Set your preferred language\n\n"
            "*Supported Languages:*\n"
            + "\n".join([f"• {name}" for code, name in self.SUPPORTED_LANGUAGES.items()])
            + "\n\n"
            "*Examples:*\n"
            "• `/towords 42`\n"
            "• `/tonumber forty two`\n"
            "• Send any number to convert it to words"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    @bot_command("language", "Set your preferred language")
    async def cmd_language(self, update, context):
        """Handle language selection."""
        # Create keyboard with language options
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"lang_{code}")]
            for code, name in self.SUPPORTED_LANGUAGES.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Select your preferred language:",
            reply_markup=reply_markup
        )
    
    @bot_handler("callback_query", pattern=r"^lang_\w+$")
    async def handle_language_selection(self, update, context):
        """Handle language selection callback."""
        query = update.callback_query
        lang_code = query.data.split('_')[1]
        
        if lang_code in self.SUPPORTED_LANGUAGES:
            self.user_languages[query.from_user.id] = lang_code
            await query.answer(f"Language set to {self.SUPPORTED_LANGUAGES[lang_code]}")
            await query.edit_message_text(
                f"✅ Your language has been set to {self.SUPPORTED_LANGUAGES[lang_code]}"
            )
        else:
            await query.answer("Invalid language selection", show_alert=True)
    
    @bot_command("towords", "Convert number to words")
    async def cmd_towords(self, update, context):
        """Convert number to words."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a number to convert\n"
                "Example: /towords 42"
            )
            return
        
        try:
            number = float(context.args[0])
            lang = self.get_user_language(update.effective_user.id)
            words = num2words(number, lang=lang)
            await update.message.reply_text(
                f"🔢 {number}\n"
                f"✍️ {words.capitalize()}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid number format\n"
                "Please provide a valid number"
            )
        except NotImplementedError:
            await update.message.reply_text(
                "❌ Number conversion not supported for your language\n"
                "Please try another language or number"
            )
    
    @bot_command("tonumber", "Convert words to number")
    async def cmd_tonumber(self, update, context):
        """Convert words to number."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide words to convert\n"
                "Example: /tonumber forty two"
            )
            return
        
        text = ' '.join(context.args)
        try:
            # Note: word2number currently only supports English
            number = w2n.word_to_num(text)
            await update.message.reply_text(
                f"✍️ {text}\n"
                f"🔢 {number}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Could not convert text to number\n"
                "Please check the format and try again"
            )
    
    @bot_handler("message", pattern=r"^-?\d+(\.\d+)?$")
    async def handle_number(self, update, context):
        """Handle when user sends a number."""
        try:
            number = float(update.message.text)
            lang = self.get_user_language(update.effective_user.id)
            words = num2words(number, lang=lang)
            await update.message.reply_text(
                f"🔢 {number}\n"
                f"✍️ {words.capitalize()}"
            )
        except Exception as e:
            await update.message.reply_text(
                "❌ Error converting number\n"
                "Please try another number or language"
            )