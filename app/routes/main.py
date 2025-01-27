import os
from flask import Blueprint, render_template, current_app
from flask_login import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Debug information
    template_path = os.path.join(current_app.root_path, 'templates', 'main', 'index.html')
    current_app.logger.info(f"Template path: {template_path}")
    current_app.logger.info(f"Template exists: {os.path.exists(template_path)}")
    current_app.logger.info(f"Template folder contents: {os.listdir(os.path.dirname(template_path))}")
    
    try:
        return render_template('main/index.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering template: {str(e)}")
        # Fallback to a simple response
        return """
        <html>
            <head><title>Welcome</title></head>
            <body>
                <h1>Welcome to Telegram Bot Manager</h1>
                <p><a href="/auth/login">Login</a> | <a href="/auth/register">Register</a></p>
            </body>
        </html>
        """

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html')