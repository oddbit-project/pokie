from pokie.constants import HTTP_OK, HTTP_NOAUTH, HTTP_NOT_FOUND
from pokie.test import PokieClient


class TestPokieAuthView:
    def test_unauthenticated_gets_401(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("/views/protected")
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


class TestAutoRestAuth:
    def test_auth_true_denies_anonymous(self, pokie_app):
        # Auto.rest(..., auth=True) (the default) requires authentication
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("/secure/category")
            assert result.code == HTTP_NOAUTH

    def test_auth_false_allows_anonymous(self, pokie_app):
        # Auto.rest(..., auth=False) keeps endpoints public
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("/catalog/category")
            assert result.code == HTTP_OK
