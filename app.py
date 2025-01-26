from app import create_app, celery
from app.routes import main

app = create_app()

@celery.task
def process_update(update_data):
    from telegram import Update
    from app.routes.bots import BotController
    update = Update.de_json(update_data, None)
    # Implement proper update routing to respective bot controllers

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)