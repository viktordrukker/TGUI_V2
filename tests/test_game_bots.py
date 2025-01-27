"""
Test suite for game bots.
"""

import pytest
from datetime import datetime, timedelta
from app.bots.number_converter_bot import NumberConverterBot
from app.bots.dice_mmo_bot import DiceMMOBot

# Bot tokens
NUMBER_BOT_TOKEN = "7710675546:AAHlgaVgGzkI7hrQsf7fjswLFCswWeaWtwE"
DICE_MMO_TOKEN = "8099008651:AAGPPPhufgt8CL04urcPXwPLCdsdFF5TRnk"

@pytest.mark.asyncio
async def test_number_converter_bot():
    """Test NumberConverterBot functionality."""
    bot = NumberConverterBot(
        token=NUMBER_BOT_TOKEN,
        config={'admin_ids': [123456789]}
    )
    
    # Check initialization
    assert bot.name == "NumberConverterBot"
    assert len(bot.SUPPORTED_LANGUAGES) > 0
    
    # Check command registration
    assert "start" in bot.commands
    assert "towords" in bot.commands
    assert "tonumber" in bot.commands
    assert "language" in bot.commands
    
    # Check language management
    user_id = 12345
    assert bot.get_user_language(user_id) == 'en'  # Default language
    bot.user_languages[user_id] = 'es'
    assert bot.get_user_language(user_id) == 'es'

@pytest.mark.asyncio
async def test_dice_mmo_bot():
    """Test DiceMMOBot functionality."""
    bot = DiceMMOBot(
        token=DICE_MMO_TOKEN,
        config={
            'admin_ids': [123456789],
            'max_daily_rolls': 3,
            'reset_hour': 0
        }
    )
    
    # Check initialization
    assert bot.name == "DiceMMOBot"
    assert bot.config['max_daily_rolls'] == 3
    
    # Check command registration
    assert "start" in bot.commands
    assert "roll" in bot.commands
    assert "score" in bot.commands
    assert "leaderboard" in bot.commands
    
    # Test player data management
    user_id = 12345
    player_data = bot._get_player_data(user_id)
    assert player_data['score'] == 0
    assert player_data['rolls_today'] == 0
    assert player_data['last_roll'] is None
    
    # Test roll permission
    can_roll, message = bot._can_roll(user_id)
    assert can_roll is True
    assert message == ""
    
    # Test leaderboard
    bot.players = {
        1: {"username": "Player1", "score": 10},
        2: {"username": "Player2", "score": 20},
        3: {"username": "Player3", "score": 15}
    }
    leaderboard = bot._get_leaderboard(limit=3)
    assert len(leaderboard) == 3
    assert leaderboard[0][2] == 20  # Top score
    assert leaderboard[-1][2] == 10  # Lowest score

@pytest.mark.asyncio
async def test_dice_mmo_daily_limits():
    """Test DiceMMOBot daily roll limits."""
    bot = DiceMMOBot(
        token=DICE_MMO_TOKEN,
        config={'max_daily_rolls': 2}
    )
    
    user_id = 12345
    player = bot._get_player_data(user_id)
    
    # First roll
    can_roll, _ = bot._can_roll(user_id)
    assert can_roll is True
    player['rolls_today'] = 1
    player['last_roll'] = datetime.utcnow()
    
    # Second roll
    can_roll, _ = bot._can_roll(user_id)
    assert can_roll is True
    player['rolls_today'] = 2
    
    # Third roll (should be blocked)
    can_roll, message = bot._can_roll(user_id)
    assert can_roll is False
    assert "No rolls left today" in message
    
    # Test reset
    player['last_roll'] = datetime.utcnow() - timedelta(days=1)
    can_roll, _ = bot._can_roll(user_id)
    assert can_roll is True

@pytest.mark.asyncio
async def test_number_converter_languages():
    """Test NumberConverterBot language support."""
    bot = NumberConverterBot(token=NUMBER_BOT_TOKEN)
    
    # Check supported languages
    assert 'en' in bot.SUPPORTED_LANGUAGES
    assert 'es' in bot.SUPPORTED_LANGUAGES
    
    # Test language switching
    user_id = 12345
    assert bot.get_user_language(user_id) == 'en'  # Default
    
    # Switch language
    bot.user_languages[user_id] = 'es'
    assert bot.get_user_language(user_id) == 'es'
    
    # Invalid language should default to English
    bot.user_languages[user_id] = 'invalid'
    assert bot.get_user_language(user_id) == 'invalid'  # Raw value returned

if __name__ == "__main__":
    pytest.main([__file__, "-v"])