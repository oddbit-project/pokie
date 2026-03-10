from flask import Flask
from rick.base import Di, Container

from pokie.constants import DI_CONFIG, DI_FLASK
from pokie.core.factories.cors import CorsFactory


class TestCorsFactory:
    def test_cors_headers(self):
        cfg = Container(
            {
                "cors_origins": "*",
                "cors_methods": "GET,POST",
                "cors_allow_headers": "Content-Type,Authorization",
                "cors_expose_headers": "",
                "cors_max_age": "600",
            }
        )
        di = Di()
        app = Flask(__name__)
        di.add(DI_CONFIG, cfg)
        di.add(DI_FLASK, app)

        CorsFactory(di)

        @app.route("/test")
        def test_view():
            return "ok"

        with app.test_client() as client:
            resp = client.get("/test", headers={"Origin": "http://example.com"})
            assert resp.status_code == 200
            assert "Access-Control-Allow-Origin" in resp.headers

    def test_cors_preflight(self):
        cfg = Container(
            {
                "cors_origins": "http://example.com",
                "cors_methods": "GET,POST,PUT",
                "cors_allow_headers": "Content-Type",
                "cors_expose_headers": "X-Custom-Header",
                "cors_max_age": "300",
            }
        )
        di = Di()
        app = Flask(__name__)
        di.add(DI_CONFIG, cfg)
        di.add(DI_FLASK, app)

        CorsFactory(di)

        @app.route("/test", methods=["GET", "POST", "PUT"])
        def test_view():
            return "ok"

        with app.test_client() as client:
            resp = client.options(
                "/test",
                headers={
                    "Origin": "http://example.com",
                    "Access-Control-Request-Method": "POST",
                },
            )
            assert resp.status_code == 200
            assert "Access-Control-Allow-Methods" in resp.headers

    def test_cors_defaults(self):
        cfg = Container({})
        di = Di()
        app = Flask(__name__)
        di.add(DI_CONFIG, cfg)
        di.add(DI_FLASK, app)

        CorsFactory(di)

        @app.route("/test")
        def test_view():
            return "ok"

        with app.test_client() as client:
            resp = client.get("/test", headers={"Origin": "http://example.com"})
            assert resp.status_code == 200
            assert "Access-Control-Allow-Origin" in resp.headers
