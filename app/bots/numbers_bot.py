"""
Numbers Bot Implementation
A bot that handles number-related operations.
"""

import random
from app.bot_framework import BaseTelegramBot, bot_command, bot_handler

class NumbersBot(BaseTelegramBot):
    """
    A bot that handles number-related operations.
    Features:
    - Number validation
    - Random number generation
    - Basic calculations
    """
    
    def __init__(self, token: str, config: dict = None):
        super().__init__(
            token=token,
            name="MyFirstNumbersBot",
            description="A bot for number-related operations",
            config=config or {}
        )
    
    @bot_command("start", "Start the bot")
    async def cmd_start(self, update, context):
        """Handle the /start command."""
        await update.message.reply_text(
            "👋 Welcome to Numbers Bot!\n\n"
            "I can help you with numbers. Try these commands:\n"
            "/random - Generate a random number\n"
            "/range - Generate a number in a specific range\n"
            "Or just send me any number to validate it!"
        )
    
    @bot_command("random", "Generate a random number")
    async def cmd_random(self, update, context):
        """Generate a random number between 1 and 100."""
        number = random.randint(1, 100)
        await update.message.reply_text(f"🎲 Your random number is: {number}")
    
    @bot_command("range", "Generate a number in a specific range")
    async def cmd_range(self, update, context):
        """Generate a random number in a specified range."""
        args = context.args
        try:
            if len(args) != 2:
                raise ValueError
            start, end = map(int, args)
            if start >= end:
                raise ValueError
            number = random.randint(start, end)
            await update.message.reply_text(
                f"🎯 Your random number between {start} and {end} is: {number}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Please provide two numbers: minimum and maximum\n"
                "Example: /range 1 10"
            )
    
    @bot_handler("message", pattern=r"^-?\d+(\.\d+)?$")
    async def handle_number(self, update, context):
        """Handle when user sends a number."""
        number = float(update.message.text)
        response = [f"📊 Analysis of number {number}:"]
        
        # Integer or float
        if number.is_integer():
            response.append("• This is an integer")
        else:
            response.append("• This is a decimal number")
        
        # Sign
        if number > 0:
            response.append("• Positive number")
        elif number < 0:
            response.append("• Negative number")
        else:
            response.append("• Zero")
        
        # Even/Odd (for integers)
        if number.is_integer():
            if int(number) % 2 == 0:
                response.append("• Even number")
            else:
                response.append("• Odd number")
        
        await update.message.reply_text("\n".join(response))
    
    @bot_handler("message")
    async def handle_non_number(self, update, context):
        """Handle when user sends a non-number message."""
        if update.message.text.startswith('/'):
            return  # Don't handle commands
        
        await update.message.reply_text(
            "🔢 Please send me a number to analyze it!\n"
            "You can also use these commands:\n"
            "/random - Generate a random number\n"
            "/range - Generate a number in a specific range"
        )