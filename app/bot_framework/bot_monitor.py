"""
Bot monitoring service.
"""

import logging
import redis
import json
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class BotMonitor:
    """Monitor external bot instances."""
    
    def __init__(self, redis_url: str = 'redis://redis:6379/0'):
        """Initialize bot monitor."""
        self.redis = redis.from_url(redis_url)
    
    def get_bot_status(self, bot_token: str) -> Dict:
        """
        Get bot status from Redis.
        
        Args:
            bot_token: Bot API token
            
        Returns:
            Dict with bot status information
        """
        try:
            status = self.redis.hgetall(f"bot:{bot_token}")
            if status:
                return {
                    'status': status.get(b'status', b'unknown').decode(),
                    'error': status.get(b'error', b'').decode(),
                    'webhook_url': status.get(b'webhook_url', b'').decode(),
                    'last_update': status.get(b'last_update', b'').decode(),
                    'type': status.get(b'type', b'').decode()
                }
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
        
        return {
            'status': 'unknown',
            'error': '',
            'webhook_url': '',
            'last_update': '',
            'type': ''
        }
    
    def get_bot_state(self, bot_token: str) -> Dict:
        """
        Get bot state from Redis.
        
        Args:
            bot_token: Bot API token
            
        Returns:
            Dict with bot state
        """
        try:
            state = self.redis.get(f"bot_state:{bot_token}")
            if state:
                return json.loads(state)
        except Exception as e:
            logger.error(f"Error getting bot state: {e}")
        
        return {}