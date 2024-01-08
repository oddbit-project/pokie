from rick.mixin import Injectable
import uuid

from flask_login import LoginManager
from rick.base import Di

from pokie.constants import DI_CONFIG, DI_SERVICES, CFG_AUTH_SECRET, DI_FLASK
from pokie.contrib.auth.constants import SVC_USER


class SessionProvider(Injectable):
    def __init__(self, di: Di):
        super().__init__(di)

        cfg = di.get(DI_CONFIG)
        app = di.get(DI_FLASK)
        app.secret_key = cfg.get(CFG_AUTH_SECRET, uuid.uuid4().hex)
        login_manager = LoginManager()
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(user_id):
            # restores user profile from user service
            return di.get(DI_SERVICES).get(SVC_USER).load_id(user_id)

        # @todo: finish provider
