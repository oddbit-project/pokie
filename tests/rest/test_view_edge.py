from pokie.constants import HTTP_OK, HTTP_BADREQ, HTTP_NOT_FOUND
from pokie.test import PokieClient


class TestRestViewEdge:
    base_url = "/customers"

    def test_get_nonexistent_record(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, "NONEXISTENT_KEY_XYZ"))
            assert result.code == HTTP_NOT_FOUND
            assert result.success is False

    def test_delete_nonexistent_record(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.delete("{}/{}".format(self.base_url, "NONEXISTENT_KEY_XYZ"))
            assert result.code == HTTP_NOT_FOUND
            assert result.success is False

    def test_list_with_search(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}?search=france".format(self.base_url))
            assert result.code == HTTP_OK
            assert result.success is True

    def test_list_with_limit_offset(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}?limit=5&offset=2".format(self.base_url))
            assert result.code == HTTP_OK
            assert result.success is True
            assert len(result.data["items"]) <= 5

    def test_list_with_invalid_sort(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}?sort=nonexistent_field".format(self.base_url))
            assert result.code == HTTP_BADREQ
            assert result.success is False

    def test_list_default(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.success is True
            assert "total" in result.data
            assert "items" in result.data
