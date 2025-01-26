from .main import bp as main_bp
from .auth import bp as auth_bp
from .bots import bp as bots_bp
from .setup import bp as setup_bp

__all__ = ['main_bp', 'auth_bp', 'bots_bp', 'setup_bp']