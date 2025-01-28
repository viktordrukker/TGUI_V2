"""
Test script for bot framework and implementations.
"""

import os
import pytest
import asyncio
from app.bot_framework.manager import BotManager
from app.bots.numbers_bot import NumbersBot
from app.bots.dice_bot import DiceRollerBot

# Bot tokens from environment variables
NUMBERS_BOT_TOKEN = "7710675546:AAHlgaVgGzkI7hrQsf7fjswLFCswWeaWtwE"
DICE_BOT_TOKEN = "8099008651:AAGPPPhufgt8CL04urcPXwPLCdsdFF5TRnk"

@pytest.fixture
async def bot_manager():
    """Create and configure bot manager for testing."""
    manager = BotManager()
    yield manager
    await manager.stop_all()

@pytest.mark.asyncio
async def test_numbers_bot():
    """Test NumbersBot initialization and basic functionality."""
    bot = NumbersBot(
        token=NUMBERS_BOT_TOKEN,
        config={'admin_ids': [123456789]}
    )
    
    # Check initialization
    assert bot.name == "MyFirstNumbersBot"
    assert len(bot.commands) > 0
    
    # Check command registration
    assert "start" in bot.commands
    assert "random" in bot.commands
    assert "range" in bot.commands

@pytest.mark.asyncio
async def test_dice_bot():
    """Test DiceRollerBot initialization and basic functionality."""
    bot = DiceRollerBot(
        token=DICE_BOT_TOKEN,
        config={'admin_ids': [123456789]}
    )
    
    # Check initialization
    assert bot.name == "DiceRoller"
    assert len(bot.commands) > 0
    
    # Check command registration
    assert "start" in bot.commands
    assert "roll" in bot.commands
    assert "help" in bot.commands

@pytest.mark.asyncio
async def test_bot_manager(bot_manager):
    """Test BotManager functionality."""
    # Add bots
    numbers_bot = await bot_manager.add_bot(
        NumbersBot,
        NUMBERS_BOT_TOKEN,
        {'admin_ids': [123456789]}
    )
    dice_bot = await bot_manager.add_bot(
        DiceRollerBot,
        DICE_BOT_TOKEN,
        {'admin_ids': [123456789]}
    )
    
    # Check bot registration
    assert len(bot_manager.get_all_bots()) == 2
    assert bot_manager.get_bot(NUMBERS_BOT_TOKEN) == numbers_bot
    assert bot_manager.get_bot(DICE_BOT_TOKEN) == dice_bot
    
    # Check stats
    stats = bot_manager.get_stats()
    assert stats['total_bots'] == 2
    assert len(stats['bots']) == 2

@pytest.mark.asyncio
async def test_bot_lifecycle(bot_manager):
    """Test bot lifecycle management."""
    # Add bot
    bot = await bot_manager.add_bot(
        NumbersBot,
        NUMBERS_BOT_TOKEN,
        {'admin_ids': [123456789]}
    )
    assert len(bot_manager.get_all_bots()) == 1
    
    # Remove bot
    await bot_manager.remove_bot(NUMBERS_BOT_TOKEN)
    assert len(bot_manager.get_all_bots()) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])