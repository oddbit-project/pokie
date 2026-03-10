from pokie.constants import HTTP_OK, HTTP_BADREQ, HTTP_NOAUTH, HTTP_NOT_FOUND
from pokie.test import PokieClient


class TestPokieAuthView:
    def test_unauthenticated_gets_401(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("/auth/logout")
            assert result.code == HTTP_NOAUTH

    def test_success_response_via_hook(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("/views/hooks")
            assert result.code == HTTP_OK
            assert result.success is True

    def test_404_on_missing_route(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("/nonexistent/route")
            assert result.code == HTTP_NOT_FOUND

    def test_wrong_http_method(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            # /auth/login only accepts POST
            result = client.get("/auth/login")
            assert result.success is False
