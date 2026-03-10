import logging

logger = logging.getLogger(__name__)


class ModuleRunnerMiddleware:
    def __init__(self, app, pokie_app):
        self.app = app
        self.pokie_app = pokie_app

    def __call__(self, environ, start_response):
        try:
            self.pokie_app.init()
        except Exception as e:
            logger.exception("Application initialization failed: %s", e)
            raise
        return self.app(environ, start_response)
