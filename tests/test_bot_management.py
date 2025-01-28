"""
Test suite for bot management functionality.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app import create_app, db
from app.models import User, TelegramBot
from app.bot_framework.bot_monitor import BotMonitor

@pytest.fixture
def app():
    """Create test application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def auth_client(app, client):
    """Create authenticated test client."""
    user = User(username='testuser')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    return client

@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    with patch('redis.from_url') as mock:
        mock.return_value = MagicMock()
        yield mock.return_value

@pytest.fixture
def bot_monitor(mock_redis):
    """Create bot monitor instance."""
    return BotMonitor()

def test_bot_registration(auth_client):
    """Test bot registration."""
    response = auth_client.post('/bots/register', data={
        'bot_token': 'test_token',
        'bot_type': 'number_converter',
        'webhook_url': 'https://example.com/webhook'
    })
    
    assert response.status_code == 302  # Redirect after success
    
    bot = TelegramBot.query.first()
    assert bot is not None
    assert bot.bot_token == 'test_token'
    assert bot.bot_type == 'number_converter'

def test_bot_status_update(app, auth_client, mock_redis):
    """Test bot status update."""
    # Create test bot
    bot = TelegramBot(
        bot_token='test_token',
        bot_type='number_converter',
        user_id=1
    )
    db.session.add(bot)
    db.session.commit()
    
    # Mock Redis response
    mock_redis.hgetall.return_value = {
        b'status': b'running',
        b'webhook_url': b'https://example.com/webhook',
        b'last_update': datetime.utcnow().isoformat().encode()
    }
    
    response = auth_client.get(f'/bots/status/{bot.id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'running'
    assert data['webhook_url'] == 'https://example.com/webhook'

def test_bot_list(auth_client):
    """Test bot listing."""
    # Create test bots
    bot1 = TelegramBot(
        bot_token='token1',
        bot_type='number_converter',
        user_id=1
    )
    bot2 = TelegramBot(
        bot_token='token2',
        bot_type='dice_mmo',
        user_id=1
    )
    db.session.add_all([bot1, bot2])
    db.session.commit()
    
    response = auth_client.get('/bots/')
    assert response.status_code == 200
    assert b'token1' in response.data
    assert b'token2' in response.data

def test_bot_monitor(bot_monitor, mock_redis):
    """Test bot monitoring."""
    test_token = 'test_token'
    test_status = {
        b'status': b'running',
        b'error': b'',
        b'webhook_url': b'https://example.com/webhook',
        b'last_update': datetime.utcnow().isoformat().encode(),
        b'type': b'number_converter'
    }
    
    mock_redis.hgetall.return_value = test_status
    status = bot_monitor.get_bot_status(test_token)
    
    assert status['status'] == 'running'
    assert status['webhook_url'] == 'https://example.com/webhook'
    assert status['type'] == 'number_converter'

def test_error_handling(auth_client):
    """Test error handling."""
    # Test invalid bot token
    response = auth_client.post('/bots/register', data={
        'bot_token': 'invalid',
        'bot_type': 'unknown',
        'webhook_url': 'not-a-url'
    })
    assert response.status_code == 200
    assert b'error' in response.data.lower()
    
    # Test accessing non-existent bot
    response = auth_client.get('/bots/status/999')
    assert response.status_code == 404

def test_unauthorized_access(client):
    """Test unauthorized access."""
    # Try to access protected routes without authentication
    routes = [
        '/bots/',
        '/bots/register',
        '/bots/status/1'
    ]
    
    for route in routes:
        response = client.get(route)
        assert response.status_code == 302  # Redirect to login
        assert b'/auth/login' in response.data