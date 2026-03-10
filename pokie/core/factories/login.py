import logging

from flask_login import LoginManager
from rick.base import Di

from pokie.constants import DI_CONFIG, DI_FLASK, CFG_AUTH_SECRET

logger = logging.getLogger(__name__)


def FlaskLoginFactory(_di: Di):
    """
    Flask-Login initialization factory
    Initializes LoginManager on the Flask application
    """
    cfg = _di.get(DI_CONFIG)
    app = _di.get(DI_FLASK)
    secret = cfg.get(CFG_AUTH_SECRET, "")
    if not secret:
        logger.warning("AUTH_SECRET is empty; sessions are insecure")
    app.secret_key = secret
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return None
