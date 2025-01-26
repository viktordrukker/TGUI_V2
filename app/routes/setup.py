from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from app.models import User, TelegramBot
from app.forms import RegistrationForm
from app import db
from sqlalchemy import text
import redis
import psycopg2
from urllib.parse import urlparse
import os

bp = Blueprint('setup', __name__)

@bp.route('/initial-setup', methods=['GET', 'POST'])
def initial_setup():
    # Redirect if admin already exists
    if User.query.filter_by(is_admin=True).first():
        flash('Setup has already been completed.', 'info')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        admin = User(
            username=form.username.data,
            is_admin=True
        )
        admin.set_password(form.password.data)
        
        try:
            db.session.add(admin)
            db.session.commit()
            flash('Admin account created successfully!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating admin account. Please try again.', 'error')
            print(f"Error creating admin: {str(e)}")
    
    return render_template('setup/initial.html', form=form)

@bp.before_app_request
def check_setup():
    # Skip check for static files and the setup page itself
    if request.endpoint and (
        request.endpoint.startswith('static') or 
        request.endpoint == 'setup.initial_setup'
    ):
        return

    # Check if admin exists
    if not User.query.filter_by(is_admin=True).first():
        if request.endpoint != 'setup.initial_setup':
            flash('Please complete the initial setup.', 'warning')
            return redirect(url_for('setup.initial_setup'))

@bp.route('/system-check')
@login_required
def system_check():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'users': check_users(),
        'bots': check_bots()
    }
    
    return render_template('setup/system_check.html', checks=checks)

def check_database():
    try:
        # Get database info first
        engine = db.engine
        db_type = engine.dialect.name
        db_url = str(engine.url)
        # Mask password in URL if present
        if '@' in db_url:
            db_url = db_url.replace(db_url.split('@')[0].split(':')[-1], '****')
        
        # Test connection
        result = db.session.execute(text('SELECT 1')).scalar()
        if result != 1:
            return {
                'status': 'error',
                'message': f'Database connection test failed\nType: {db_type}\nURL: {db_url}'
            }
        
        try:
            # Get table information
            inspector = db.inspect(engine)
            tables = inspector.get_table_names()
            
            # Get table statistics
            table_stats = []
            for table in tables:
                try:
                    count = db.session.execute(
                        text(f'SELECT COUNT(*) FROM {table}')
                    ).scalar()
                    table_stats.append(f"{table} ({count} rows)")
                except Exception as table_err:
                    table_stats.append(f"{table} (error: {str(table_err)})")
            
            message = (
                f"Database type: {db_type}\n"
                f"URL: {db_url}\n"
                f"Connection: OK\n"
                f"Tables found: {len(tables)}\n"
                f"Details:\n - " + "\n - ".join(table_stats)
            )
            
            return {
                'status': 'ok',
                'message': message
            }
            
        except Exception as inspect_err:
            return {
                'status': 'error',
                'message': f'Error inspecting database: {str(inspect_err)}\nType: {db_type}\nURL: {db_url}'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database connection error: {str(e)}'
        }

def check_redis():
    try:
        # Get Redis URL from environment or config
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        r = redis.from_url(redis_url)
        
        # Test connection and get info
        r.ping()
        info = r.info()
        
        # Extract relevant information
        version = info.get('redis_version', 'Unknown')
        memory = info.get('used_memory_human', 'Unknown')
        clients = info.get('connected_clients', 0)
        
        message = (
            f'Redis v{version} connected successfully. '
            f'Memory used: {memory}, '
            f'Connected clients: {clients}'
        )
        
        return {'status': 'ok', 'message': message}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_users():
    try:
        total_users = User.query.count()
        admin_users = User.query.filter_by(is_admin=True).count()
        regular_users = total_users - admin_users
        
        # Get latest user if any exist
        latest_user = User.query.order_by(User.id.desc()).first()
        latest_info = f", Latest user: {latest_user.username}" if latest_user else ""
        
        message = (
            f"Total users: {total_users}\n"
            f"Admin users: {admin_users}\n"
            f"Regular users: {regular_users}"
            f"{latest_info}"
        )
        
        return {
            'status': 'ok',
            'message': message
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_bots():
    try:
        total_bots = TelegramBot.query.count()
        active_bots = TelegramBot.query.filter_by(is_active=True).count()
        inactive_bots = total_bots - active_bots
        
        # Get latest bot if any exist
        latest_bot = TelegramBot.query.order_by(TelegramBot.id.desc()).first()
        latest_info = (
            f", Latest bot: {latest_bot.bot_username} "
            f"({'active' if latest_bot.is_active else 'inactive'})"
        ) if latest_bot else ""
        
        message = (
            f"Total bots: {total_bots}\n"
            f"Active bots: {active_bots}\n"
            f"Inactive bots: {inactive_bots}"
            f"{latest_info}"
        )
        
        return {
            'status': 'ok',
            'message': message
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}