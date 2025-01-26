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
    config = db.Column(JSON)
    is_active = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))