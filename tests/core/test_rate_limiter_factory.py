from flask import Flask
from rick.base import Di, Container

from pokie.constants import DI_CONFIG, DI_FLASK, DI_RATE_LIMITER
from pokie.core.factories.rate_limiter import RateLimiterFactory


class TestRateLimiterFactory:
    def test_disabled_when_empty(self):
        cfg = Container({"rate_limit_default": ""})
        di = Di()
        app = Flask(__name__)
        di.add(DI_CONFIG, cfg)
        di.add(DI_FLASK, app)

        RateLimiterFactory(di)

        assert not di.has(DI_RATE_LIMITER)

    def test_disabled_when_missing(self):
        cfg = Container({})
        di = Di()
        app = Flask(__name__)
        di.add(DI_CONFIG, cfg)
        di.add(DI_FLASK, app)

        RateLimiterFactory(di)

        assert not di.has(DI_RATE_LIMITER)

    def test_memory_storage(self):
        cfg = Container(
            {
                "rate_limit_default": "10/minute",
                "rate_limit_storage": "memory",
            }
        )
        di = Di()
        app = Flask(__name__)
        di.add(DI_CONFIG, cfg)
        di.add(DI_FLASK, app)

        RateLimiterFactory(di)

        assert di.has(DI_RATE_LIMITER)

    def test_rate_limit_enforced(self):
        cfg = Container(
            {
                "rate_limit_default": "2/minute",
                "rate_limit_storage": "memory",
            }
        )
        di = Di()
        app = Flask(__name__)
        di.add(DI_CONFIG, cfg)
        di.add(DI_FLASK, app)

        RateLimiterFactory(di)

        @app.route("/test")
        def test_view():
            return "ok"

        with app.test_client() as client:
            # first 2 requests should succeed
            resp = client.get("/test")
            assert resp.status_code == 200
            resp = client.get("/test")
            assert resp.status_code == 200
            # third request should be rate limited
            resp = client.get("/test")
            assert resp.status_code == 429
