from flask_cors import CORS
from rick.base import Di

from pokie.constants import (
    DI_CONFIG,
    DI_FLASK,
    CFG_CORS_ORIGINS,
    CFG_CORS_METHODS,
    CFG_CORS_ALLOW_HEADERS,
    CFG_CORS_EXPOSE_HEADERS,
    CFG_CORS_MAX_AGE,
)


def CorsFactory(_di: Di):
    """
    Flask-CORS initialization factory
    Initializes CORS on the Flask application
    """
    cfg = _di.get(DI_CONFIG)
    app = _di.get(DI_FLASK)

    origins = cfg.get(CFG_CORS_ORIGINS, "*")
    methods_str = cfg.get(CFG_CORS_METHODS, "GET,POST,PUT,PATCH,DELETE,OPTIONS")
    methods = [m.strip() for m in methods_str.split(",")]
    allow_headers_str = cfg.get(CFG_CORS_ALLOW_HEADERS, "Content-Type,Authorization")
    allow_headers = [h.strip() for h in allow_headers_str.split(",")]
    expose_headers_str = cfg.get(CFG_CORS_EXPOSE_HEADERS, "")
    expose_headers = [h.strip() for h in expose_headers_str.split(",") if h.strip()]
    max_age = int(cfg.get(CFG_CORS_MAX_AGE, 600))

    CORS(
        app,
        origins=origins,
        methods=methods,
        allow_headers=allow_headers,
        expose_headers=expose_headers if expose_headers else None,
        max_age=max_age,
    )
