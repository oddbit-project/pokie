import logging

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from rick.base import Di

from pokie.constants import (
    DI_CONFIG,
    DI_FLASK,
    DI_RATE_LIMITER,
    CFG_RATE_LIMIT_DEFAULT,
    CFG_RATE_LIMIT_STORAGE,
    CFG_REDIS_HOST,
    CFG_REDIS_PORT,
    CFG_REDIS_PASSWORD,
    CFG_REDIS_DB,
)

logger = logging.getLogger(__name__)


def RateLimiterFactory(_di: Di):
    """
    Flask-Limiter initialization factory
    Initializes rate limiting on the Flask application

    If RATE_LIMIT_DEFAULT is empty, the factory is a no-op.
    """
    cfg = _di.get(DI_CONFIG)
    app = _di.get(DI_FLASK)

    default_limit = cfg.get(CFG_RATE_LIMIT_DEFAULT, "")
    if not default_limit:
        return

    storage_backend = cfg.get(CFG_RATE_LIMIT_STORAGE, "memory")

    if storage_backend == "redis":
        host = cfg.get(CFG_REDIS_HOST, "localhost")
        port = int(cfg.get(CFG_REDIS_PORT, 6379))
        password = cfg.get(CFG_REDIS_PASSWORD, "")
        db = int(cfg.get(CFG_REDIS_DB, 0))
        if password:
            storage_uri = "redis://:{}@{}:{}/{}".format(password, host, port, db)
        else:
            storage_uri = "redis://{}:{}/{}".format(host, port, db)
    else:
        storage_uri = "memory://"

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[default_limit],
        storage_uri=storage_uri,
    )

    _di.add(DI_RATE_LIMITER, limiter)
