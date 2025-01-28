"""
Dice Roller Bot Implementation
A bot for rolling dice and generating random numbers.
"""

import random
import re
from typing import Tuple, List
from app.bot_framework import BaseTelegramBot, bot_command, bot_handler

class DiceRollerBot(BaseTelegramBot):
    """
    A bot for rolling dice and generating random numbers.
    Features:
    - Roll different types of dice (d4, d6, d8, d10, d12, d20, d100)
    - Roll multiple dice at once
    - Add modifiers to rolls
    - Keep track of roll history
    """
    
    DICE_PATTERN = re.compile(r'^(\d+)?d(\d+)([+-]\d+)?$')
    
    def __init__(self, token: str, config: dict = None):
        super().__init__(
            token=token,
            name="DiceRoller",
            description="A bot for rolling dice and generating random numbers",
            config=config or {}
        )
        self.valid_dice = [4, 6, 8, 10, 12, 20, 100]
    
    @bot_command("start", "Start the bot")
    async def cmd_start(self, update, context):
        """Handle the /start command."""
        await update.message.reply_text(
            "🎲 Welcome to Dice Roller!\n\n"
            "I can help you roll dice. Try these formats:\n"
            "• d20 - Roll a 20-sided die\n"
            "• 2d6 - Roll two 6-sided dice\n"
            "• d8+3 - Roll an 8-sided die and add 3\n\n"
            "Available commands:\n"
            "/roll <dice> - Roll specific dice\n"
            "/help - Show detailed help"
        )
    
    @bot_command("help", "Show help information")
    async def cmd_help(self, update, context):
        """Show detailed help information."""
        help_text = (
            "🎲 *Dice Roller Help*\n\n"
            "*Available Dice:*\n"
            "d4, d6, d8, d10, d12, d20, d100\n\n"
            "*Roll Formats:*\n"
            "• `d20` - Roll one 20-sided die\n"
            "• `2d6` - Roll two 6-sided dice\n"
            "• `d8+3` - Roll d8 and add 3\n"
            "• `3d6-2` - Roll 3d6 and subtract 2\n\n"
            "*Commands:*\n"
            "/roll <dice> - Roll specific dice\n"
            "/stats - View your rolling statistics"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    def _parse_roll(self, roll_str: str) -> Tuple[int, int, int]:
        """
        Parse a roll string into its components.
        
        Args:
            roll_str (str): The roll string (e.g., "2d6+3")
            
        Returns:
            Tuple[int, int, int]: (number of dice, dice type, modifier)
            
        Raises:
            ValueError: If the roll string is invalid
        """
        match = self.DICE_PATTERN.match(roll_str.lower().replace(' ', ''))
        if not match:
            raise ValueError("Invalid roll format")
        
        count = int(match.group(1)) if match.group(1) else 1
        dice = int(match.group(2))
        mod = int(match.group(3)) if match.group(3) else 0
        
        if dice not in self.valid_dice:
            raise ValueError(f"Invalid die type. Valid dice are: {', '.join(map(str, self.valid_dice))}")
        if count < 1 or count > 100:
            raise ValueError("You can roll between 1 and 100 dice")
            
        return count, dice, mod
    
    def _format_roll_result(self, rolls: List[int], mod: int = 0) -> str:
        """Format roll results into a readable string."""
        total = sum(rolls) + mod
        roll_str = ' + '.join(map(str, rolls))
        
        if mod > 0:
            return f"🎲 Rolls: [{roll_str}] + {mod} = {total}"
        elif mod < 0:
            return f"🎲 Rolls: [{roll_str}] - {abs(mod)} = {total}"
        else:
            return f"🎲 Rolls: [{roll_str}] = {total}"
    
    @bot_command("roll", "Roll specific dice")
    async def cmd_roll(self, update, context):
        """Handle the /roll command."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please specify what dice to roll\n"
                "Example: /roll 2d6+3"
            )
            return
        
        roll_str = ''.join(context.args)
        try:
            count, dice, mod = self._parse_roll(roll_str)
            rolls = [random.randint(1, dice) for _ in range(count)]
            result = self._format_roll_result(rolls, mod)
            await update.message.reply_text(result)
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
    
    @bot_handler("message", pattern=r'^(\d+)?d\d+([+-]\d+)?$')
    async def handle_roll(self, update, context):
        """Handle direct roll messages."""
        roll_str = update.message.text
        try:
            count, dice, mod = self._parse_roll(roll_str)
            rolls = [random.randint(1, dice) for _ in range(count)]
            result = self._format_roll_result(rolls, mod)
            await update.message.reply_text(result)
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
    
    @bot_command("stats", "View your rolling statistics", admin_only=True)
    async def cmd_stats(self, update, context):
        """Show rolling statistics (admin only)."""
        # This would normally pull from a database
        await update.message.reply_text(
            "📊 *Rolling Statistics*\n"
            "Feature coming soon!\n"
            "This will show statistics about dice rolls.",
            parse_mode='Markdown'
        )