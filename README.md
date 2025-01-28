# Telegram Bot Management System

A web-based management interface for Telegram bots with separate bot containers.

## Project Structure

```
TGUI_V2/                  # Management UI
├── app/                  # Flask application
├── docker/              # Docker configurations
└── docs/               # Documentation

telegram-bot-base/        # Base bot project
├── bots/               # Bot implementations
├── Dockerfile          # Bot container build
└── main.py            # Bot runner script
```

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Redis server
- PostgreSQL database

## Quick Start

1. **Clone the repositories:**
```bash
git clone https://github.com/your-username/TGUI_V2.git
git clone https://github.com/your-username/telegram-bot-base.git
```

2. **Set up environment variables:**

For Management UI (.env):
```bash
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://app:apppass@db/appdb
REDIS_URL=redis://redis:6379/0
```

For Bot Container (.env):
```bash
BOT_TOKEN=your-bot-token
BOT_TYPE=number_converter  # or dice_mmo
REDIS_URL=redis://redis:6379/0
```

3. **Start Management UI:**
```bash
cd TGUI_V2
docker-compose up -d
```

4. **Build and start bot container:**
```bash
cd telegram-bot-base
docker build -t telegram-bot .
docker run -d \
  --name bot_instance \
  --env-file .env \
  --network tgui_v2_default \
  telegram-bot
```

5. **Access Management UI:**
- Open http://localhost:5000
- Login/Register
- Add your bot using its token

## Development Setup

1. **Set up Management UI:**
```bash
cd TGUI_V2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Run development server
flask run
```

2. **Set up Bot Development:**
```bash
cd telegram-bot-base

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run bot
python main.py
```

## Testing

1. **Test Management UI:**
```bash
cd TGUI_V2

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

2. **Test Bot Implementation:**
```bash
cd telegram-bot-base

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## Bot Development

1. Create new bot class in `telegram-bot-base/bots/`:
```python
from main import BotBase

class MyBot(BotBase):
    async def start(self):
        # Initialize bot
        pass

    async def stop(self):
        # Cleanup
        pass
```

2. Update bot type in environment:
```bash
BOT_TYPE=my_bot
```

3. Build and run container:
```bash
docker build -t telegram-bot .
docker run -d --env-file .env telegram-bot
```

## Monitoring

1. **View Bot Status:**
- Management UI dashboard
- Redis monitoring:
```bash
redis-cli
> HGETALL "bot:YOUR_BOT_TOKEN"
```

2. **View Logs:**
```bash
# Management UI logs
docker-compose logs -f web

# Bot container logs
docker logs -f bot_instance
```

3. **Check Bot State:**
```bash
redis-cli
> GET "bot_state:YOUR_BOT_TOKEN"
```

## Troubleshooting

1. **Management UI Issues:**
- Check database connection
- Verify Redis connection
- Check application logs

2. **Bot Issues:**
- Verify bot token
- Check Redis connection
- Inspect container logs
- Verify network connectivity

3. **Common Problems:**
- Redis connection: Check network and URL
- Database migrations: Run `flask db upgrade`
- Container networking: Check Docker network

## Security Notes

1. **Environment Variables:**
- Never commit .env files
- Use secure secrets
- Rotate sensitive data

2. **Bot Tokens:**
- Store securely
- Use separate tokens for development
- Rotate compromised tokens

3. **Access Control:**
- Use strong passwords
- Enable 2FA where possible
- Restrict network access

## Maintenance

1. **Database:**
```bash
# Backup
docker exec -t db pg_dump -U app appdb > backup.sql

# Restore
cat backup.sql | docker exec -i db psql -U app appdb
```

2. **Redis:**
```bash
# Backup
docker exec -t redis redis-cli SAVE

# Monitor
docker exec -t redis redis-cli MONITOR
```

3. **Containers:**
```bash
# Update images
docker-compose pull
docker pull telegram-bot

# Cleanup
docker system prune
```

## Support

For issues and questions:
1. Check documentation
2. Review logs
3. Open GitHub issue
4. Contact support team
