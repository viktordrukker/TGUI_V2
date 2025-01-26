# Telegram Bot Manager (TGUI V2)

A web-based management interface for Telegram bots built with Flask.

## Features

- User Authentication & Authorization
- Bot Management Interface
- Admin Dashboard
- Real-time Bot Status Monitoring
- Celery Task Queue Integration
- PostgreSQL Database
- Redis Cache
- Docker Deployment

## Prerequisites

- Docker
- Docker Compose
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/TGUI_V2.git
cd TGUI_V2
```

2. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

4. Access the application at http://localhost:5000

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
flask db upgrade
```

4. Run the development server:
```bash
flask run
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── tasks.py
│   ├── admin.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── bots.py
│   │   ├── main.py
│   │   └── setup.py
│   └── templates/
├── migrations/
├── tests/
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── entrypoint.sh
```

## Configuration

Configuration is handled through environment variables and the config.py file:

- `FLASK_ENV`: Set to 'development' or 'production'
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: PostgreSQL database URL
- `REDIS_URL`: Redis URL
- Other settings in config.py

## Docker Deployment

The application is containerized with Docker and includes:

- Web application container
- PostgreSQL database
- Redis cache
- Celery worker

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
