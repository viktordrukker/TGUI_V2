from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from celery import Celery

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
celery = Celery(__name__, broker='redis://redis:6379/0')

def create_app():
    app = Flask(__name__, 
                template_folder='templates',  # Explicitly set template folder
                static_folder='static')       # Explicitly set static folder
    app.config.from_object('config.DevelopmentConfig')
    app.logger.setLevel('INFO')  # Set logging level to INFO for debugging
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, directory='migrations')
    celery.conf.update(app.config)
    
    # Register blueprints
    from .routes import main_bp, auth_bp, bots_bp, setup_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(bots_bp)
    app.register_blueprint(setup_bp)
    
    # Initialize database and admin interface
    with app.app_context():
        from .models import User, TelegramBot
        db.create_all()
        
        from .admin import init_admin
        init_admin(app)
    
    return app
