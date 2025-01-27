"""
Container manager for bot instances.
"""

import os
import json
import logging
import docker
import redis
from typing import Dict, Optional, List
from docker.models.containers import Container
from .exceptions import BotFrameworkError

logger = logging.getLogger(__name__)

class ContainerManager:
    """Manages Docker containers for bot instances."""
    
    def __init__(self):
        """Initialize the container manager."""
        self.docker = docker.from_env()
        self.redis = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
        self.base_port = int(os.getenv('BOT_BASE_PORT', '8443'))
        self.webhook_host = os.getenv('WEBHOOK_HOST', 'localhost')
    
    def _get_available_port(self) -> int:
        """Get next available port."""
        used_ports = set()
        containers = self.docker.containers.list(all=True)
        for container in containers:
            ports = container.attrs['NetworkSettings']['Ports']
            if ports:
                for port_map in ports.values():
                    if port_map:
                        used_ports.add(int(port_map[0]['HostPort']))
        
        port = self.base_port
        while port in used_ports:
            port += 1
        return port
    
    def _get_container_name(self, bot_token: str) -> str:
        """Generate container name from bot token."""
        # Use last 8 characters of token to avoid collisions
        return f"bot_{bot_token[-8:]}"
    
    def start_bot(self, bot_token: str, bot_type: str) -> Dict:
        """
        Start a bot in a new container.
        
        Args:
            bot_token: Bot API token
            bot_type: Type of bot to start
            
        Returns:
            Dict with container info and webhook URL
        """
        try:
            # Check if bot is already running
            container_name = self._get_container_name(bot_token)
            try:
                existing = self.docker.containers.get(container_name)
                if existing.status == 'running':
                    logger.info(f"Bot container {container_name} already running")
                    return self.get_bot_status(bot_token)
                else:
                    existing.remove(force=True)
            except docker.errors.NotFound:
                pass
            
            # Get available port
            port = self._get_available_port()
            
            # Prepare environment
            environment = {
                'BOT_TOKEN': bot_token,
                'BOT_TYPE': bot_type,
                'WEBHOOK_HOST': self.webhook_host,
                'WEBHOOK_PORT': str(port),
                'CONTAINER_NAME': container_name,
                'REDIS_URL': os.getenv('REDIS_URL', 'redis://redis:6379/0')
            }
            
            # Start container
            container = self.docker.containers.run(
                image='tgui-bot:latest',
                name=container_name,
                environment=environment,
                ports={f'{port}/tcp': port},
                network='tgui_default',
                restart_policy={'Name': 'unless-stopped'},
                detach=True
            )
            
            logger.info(f"Started bot container {container_name} on port {port}")
            
            # Wait for bot to start and return status
            return self.get_bot_status(bot_token)
            
        except Exception as e:
            error_msg = f"Failed to start bot container: {str(e)}"
            logger.error(error_msg)
            self.redis.hset(
                f"bot:{bot_token}",
                mapping={'status': 'error', 'error': error_msg}
            )
            raise BotFrameworkError(error_msg) from e
    
    def stop_bot(self, bot_token: str) -> None:
        """
        Stop a bot container.
        
        Args:
            bot_token: Bot API token
        """
        try:
            container_name = self._get_container_name(bot_token)
            try:
                container = self.docker.containers.get(container_name)
                container.stop()
                container.remove()
                logger.info(f"Stopped and removed container {container_name}")
            except docker.errors.NotFound:
                logger.warning(f"Container {container_name} not found")
            
            # Update Redis status
            self.redis.hset(
                f"bot:{bot_token}",
                mapping={'status': 'stopped', 'error': ''}
            )
            
        except Exception as e:
            error_msg = f"Failed to stop bot container: {str(e)}"
            logger.error(error_msg)
            raise BotFrameworkError(error_msg) from e
    
    def get_bot_status(self, bot_token: str, timeout: int = 30) -> Dict:
        """
        Get bot status from Redis.
        
        Args:
            bot_token: Bot API token
            timeout: How long to wait for status (seconds)
            
        Returns:
            Dict with bot status information
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.redis.hgetall(f"bot:{bot_token}")
            if status:
                return {
                    'status': status.get(b'status', b'unknown').decode(),
                    'error': status.get(b'error', b'').decode(),
                    'container': status.get(b'container', b'').decode(),
                    'webhook_url': status.get(b'webhook_url', b'').decode()
                }
            time.sleep(1)
        
        return {
            'status': 'unknown',
            'error': 'Timeout waiting for status',
            'container': '',
            'webhook_url': ''
        }
    
    def list_bots(self) -> List[Dict]:
        """
        List all running bot containers.
        
        Returns:
            List of bot container information
        """
        containers = self.docker.containers.list(
            filters={'name': 'bot_*'}
        )
        return [
            {
                'name': container.name,
                'status': container.status,
                'ports': container.ports,
                'created': container.attrs['Created']
            }
            for container in containers
        ]