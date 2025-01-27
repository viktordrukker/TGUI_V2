"""
Dice MMO Game Bot
A multiplayer dice rolling game with daily limits and scoreboards.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.bot_framework import BaseTelegramBot, bot_command, bot_handler

class DiceMMOBot(BaseTelegramBot):
    """
    A multiplayer dice rolling game bot.
    Features:
    - Daily dice rolls
    - Score tracking
    - Leaderboards
    - Roll history
    """
    
    def __init__(self, token: str, config: dict = None):
        super().__init__(
            token=token,
            name="DiceMMOBot",
            description="Multiplayer dice rolling game with scoreboards",
            config=config or {}
        )
        # Player data: {user_id: {"score": int, "rolls_today": int, "last_roll": datetime}}
        self.players: Dict[int, Dict] = {}
        # Default configuration
        self.config.update({
            "max_daily_rolls": 5,
            "reset_hour": 0,  # Hour when daily rolls reset (UTC)
            "min_players_for_ranking": 3
        })
    
    def _get_player_data(self, user_id: int) -> Dict:
        """Get or create player data."""
        if user_id not in self.players:
            self.players[user_id] = {
                "score": 0,
                "rolls_today": 0,
                "last_roll": None,
                "username": None
            }
        return self.players[user_id]
    
    def _can_roll(self, user_id: int) -> Tuple[bool, str]:
        """Check if user can roll dice."""
        player = self._get_player_data(user_id)
        
        # Check if it's a new day
        if player["last_roll"]:
            now = datetime.utcnow()
            reset_time = now.replace(
                hour=self.config["reset_hour"],
                minute=0,
                second=0,
                microsecond=0
            )
            if now < reset_time:
                reset_time -= timedelta(days=1)
            
            if player["last_roll"] < reset_time:
                player["rolls_today"] = 0
        
        if player["rolls_today"] >= self.config["max_daily_rolls"]:
            next_reset = datetime.utcnow().replace(
                hour=self.config["reset_hour"],
                minute=0,
                second=0,
                microsecond=0
            )
            if next_reset < datetime.utcnow():
                next_reset += timedelta(days=1)
            
            time_left = next_reset - datetime.utcnow()
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            
            return False, f"No rolls left today. Next reset in {hours}h {minutes}m"
        
        return True, ""
    
    def _get_leaderboard(self, limit: int = 10) -> List[Tuple[int, str, int]]:
        """Get sorted leaderboard data."""
        leaderboard = [
            (user_id, data["username"] or f"Player{user_id}", data["score"])
            for user_id, data in self.players.items()
        ]
        return sorted(leaderboard, key=lambda x: x[2], reverse=True)[:limit]
    
    @bot_command("start", "Start the game")
    async def cmd_start(self, update, context):
        """Handle the /start command."""
        await update.message.reply_text(
            "🎲 Welcome to Dice MMO Game!\n\n"
            "Roll dice and compete with other players.\n\n"
            "Commands:\n"
            "/roll - Roll the dice\n"
            "/score - Check your score\n"
            "/leaderboard - View top players\n"
            "/help - Show help message"
        )
    
    @bot_command("help", "Show help information")
    async def cmd_help(self, update, context):
        """Show help information."""
        help_text = (
            "🎲 *Dice MMO Game Help*\n\n"
            "*Game Rules:*\n"
            f"• You have {self.config['max_daily_rolls']} dice rolls per day\n"
            f"• Rolls reset at {self.config['reset_hour']:02d}:00 UTC\n"
            "• Your score accumulates over time\n"
            "• Compete for the highest score!\n\n"
            "*Commands:*\n"
            "• `/roll` - Roll the dice\n"
            "• `/score` - Check your score\n"
            "• `/leaderboard` - View top players\n"
            "• `/history` - View your roll history"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    @bot_command("roll", "Roll the dice")
    async def cmd_roll(self, update, context):
        """Handle dice rolling."""
        user_id = update.effective_user.id
        username = update.effective_user.username or f"Player{user_id}"
        
        # Update username
        player = self._get_player_data(user_id)
        player["username"] = username
        
        # Check if user can roll
        can_roll, message = self._can_roll(user_id)
        if not can_roll:
            await update.message.reply_text(f"❌ {message}")
            return
        
        # Send dice and wait for result
        dice_message = await update.message.reply_dice(emoji='🎲')
        value = dice_message.dice.value
        
        # Update player data
        player["score"] += value
        player["rolls_today"] += 1
        player["last_roll"] = datetime.utcnow()
        
        # Send result message
        rolls_left = self.config["max_daily_rolls"] - player["rolls_today"]
        await asyncio.sleep(4)  # Wait for dice animation
        await update.message.reply_text(
            f"🎯 You rolled a {value}!\n"
            f"📊 Your total score: {player['score']}\n"
            f"🎲 Rolls left today: {rolls_left}"
        )
    
    @bot_command("score", "Check your score")
    async def cmd_score(self, update, context):
        """Show player's score."""
        user_id = update.effective_user.id
        player = self._get_player_data(user_id)
        
        await update.message.reply_text(
            f"📊 *Your Stats*\n"
            f"Score: {player['score']}\n"
            f"Rolls today: {player['rolls_today']}/{self.config['max_daily_rolls']}",
            parse_mode='Markdown'
        )
    
    @bot_command("leaderboard", "View top players")
    async def cmd_leaderboard(self, update, context):
        """Show leaderboard."""
        leaderboard = self._get_leaderboard()
        
        if len(leaderboard) < self.config["min_players_for_ranking"]:
            await update.message.reply_text(
                f"❌ Not enough players yet! Need at least "
                f"{self.config['min_players_for_ranking']} players."
            )
            return
        
        text = ["🏆 *Leaderboard*\n"]
        for i, (user_id, username, score) in enumerate(leaderboard, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "•")
            text.append(f"{medal} {username}: {score}")
        
        await update.message.reply_text(
            "\n".join(text),
            parse_mode='Markdown'
        )
    
    @bot_command("stats", "View game statistics", admin_only=True)
    async def cmd_stats(self, update, context):
        """Show game statistics (admin only)."""
        total_players = len(self.players)
        total_score = sum(p["score"] for p in self.players.values())
        active_today = sum(
            1 for p in self.players.values()
            if p["last_roll"] and p["last_roll"].date() == datetime.utcnow().date()
        )
        
        stats = (
            "📈 *Game Statistics*\n"
            f"Total Players: {total_players}\n"
            f"Active Today: {active_today}\n"
            f"Total Score: {total_score}\n"
            f"Average Score: {total_score/total_players if total_players else 0:.1f}"
        )
        
        await update.message.reply_text(stats, parse_mode='Markdown')