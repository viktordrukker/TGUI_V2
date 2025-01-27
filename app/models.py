from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy import JSON
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    bots = db.relationship('TelegramBot', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class TelegramBot(db.Model):
    __tablename__ = 'telegram_bots'
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(120), unique=True)
    bot_username = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bot_type = db.Column(db.String(50), nullable=False)  # e.g., 'number_converter', 'dice_mmo'
    config = db.Column(JSON)
    status = db.Column(db.String(20), default='stopped')  # stopped, running, error
    last_activity = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    webhook_url = db.Column(db.String(255))  # Full webhook URL
    container_name = db.Column(db.String(50))  # Docker container name
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def update_stats(self, new_stats):
        """Update bot statistics."""
        current_stats = self.stats or {}
        current_stats.update(new_stats)
        self.stats = current_stats
        self.last_activity = db.func.now()

    def get_controller_class(self):
        """Get the appropriate bot controller class based on bot_type."""
        from app.bots.number_converter_bot import NumberConverterBot
        from app.bots.dice_mmo_bot import DiceMMOBot
        
        bot_types = {
            'number_converter': NumberConverterBot,
            'dice_mmo': DiceMMOBot
        }
        return bot_types.get(self.bot_type)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))