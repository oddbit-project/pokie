from pokie.constants import HTTP_OK, HTTP_BADREQ, HTTP_NOT_FOUND
from pokie.test import PokieClient


class TestArticleBasicRest:
    """Feature 1: Basic Auto.rest() with auto-generated RequestRecord and search"""

    base_url = "/article"

    def test_list_empty(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data["total"] == 0
            assert result.data["items"] == []

    def test_crud(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create
            record = {
                "title": "Test Article",
                "slug": "test-article",
                "body": "Hello world",
                "author_name": "Alice",
                "status": "draft",
            }
            result = client.post(self.base_url, data=record)
            assert result.code == HTTP_OK
            assert result.success is True
            article_id = result.data["id"]
            assert isinstance(article_id, int)

            # read
            result = client.get("{}/{}".format(self.base_url, article_id))
            assert result.code == HTTP_OK
            assert result.data["title"] == "Test Article"
            assert result.data["author_name"] == "Alice"
            assert result.data["status"] == "draft"

            # update
            record["title"] = "Updated Title"
            result = client.put(
                "{}/{}".format(self.base_url, article_id), data=record
            )
            assert result.code == HTTP_OK
            assert result.success is True

            # verify update
            result = client.get("{}/{}".format(self.base_url, article_id))
            assert result.data["title"] == "Updated Title"

            # delete
            result = client.delete("{}/{}".format(self.base_url, article_id))
            assert result.code == HTTP_OK
            assert result.success is True

            # verify deletion
            result = client.get("{}/{}".format(self.base_url, article_id))
            assert result.code == HTTP_NOT_FOUND

    def test_search(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create two articles with different authors
            client.post(
                self.base_url,
                data={
                    "title": "Alpha Post",
                    "slug": "alpha",
                    "body": "content",
                    "author_name": "Alice",
                    "status": "published",
                },
            )
            client.post(
                self.base_url,
                data={
                    "title": "Beta Post",
                    "slug": "beta",
                    "body": "content",
                    "author_name": "Bob",
                    "status": "draft",
                },
            )

            # search by author
            result = client.get("{}?search=Alice".format(self.base_url))
            assert result.code == HTTP_OK
            assert result.data["total"] >= 1
            for item in result.data["items"]:
                assert (
                    "Alice" in item.get("author_name", "")
                    or "Alice" in item.get("title", "")
                )

            # search by title
            result = client.get("{}?search=Beta".format(self.base_url))
            assert result.code == HTTP_OK
            assert result.data["total"] >= 1

    def test_list_with_limit_offset(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create a few articles
            for i in range(3):
                client.post(
                    self.base_url,
                    data={
                        "title": "Paginated {}".format(i),
                        "slug": "page-{}".format(i),
                        "body": "body",
                        "author_name": "Author",
                        "status": "draft",
                    },
                )

            result = client.get("{}?limit=2&offset=0".format(self.base_url))
            assert result.code == HTTP_OK
            assert len(result.data["items"]) <= 2

    def test_get_nonexistent(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, 999999))
            assert result.code == HTTP_NOT_FOUND
            assert result.success is False

    def test_delete_nonexistent(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.delete("{}/{}".format(self.base_url, 999999))
            assert result.code == HTTP_NOT_FOUND
            assert result.success is False

    def test_put_nonexistent(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.put(
                "{}/{}".format(self.base_url, 999999),
                data={"title": "x", "slug": "x", "body": "x", "author_name": "x"},
            )
            assert result.code == HTTP_NOT_FOUND
            assert result.success is False


class TestShipperCustomRequest:
    """Feature 2: Auto.rest() with custom RequestRecord for validation"""

    base_url = "/shipper"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] == 6
            assert len(result.data["items"]) == 6

    def test_get_single(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            first = result.data["items"][0]

            result = client.get("{}/{}".format(self.base_url, first["id"]))
            assert result.code == HTTP_OK
            assert "company_name" in result.data
            assert "phone" in result.data

    def test_post_validation_missing_name(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # missing required company_name
            result = client.post(self.base_url, data={"phone": "555-0000"})
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert "company_name" in result.form_error

    def test_post_validation_name_too_long(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            result = client.post(
                self.base_url,
                data={"company_name": "x" * 50, "phone": "555-0000"},
            )
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert "company_name" in result.form_error

    def test_crud(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create
            result = client.post(
                self.base_url,
                data={"company_name": "Test Shipper", "phone": "555-1234"},
            )
            assert result.code == HTTP_OK
            shipper_id = result.data["id"]

            # read
            result = client.get("{}/{}".format(self.base_url, shipper_id))
            assert result.code == HTTP_OK
            assert result.data["company_name"] == "Test Shipper"

            # update
            result = client.put(
                "{}/{}".format(self.base_url, shipper_id),
                data={"company_name": "Updated Shipper", "phone": "555-5678"},
            )
            assert result.code == HTTP_OK

            # verify update
            result = client.get("{}/{}".format(self.base_url, shipper_id))
            assert result.data["company_name"] == "Updated Shipper"

            # delete
            result = client.delete("{}/{}".format(self.base_url, shipper_id))
            assert result.code == HTTP_OK

            result = client.get("{}/{}".format(self.base_url, shipper_id))
            assert result.code == HTTP_NOT_FOUND

    def test_search(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}?search=Express".format(self.base_url))
            assert result.code == HTTP_OK
            assert result.data["total"] >= 1


class TestProductCustomService:
    """Feature 3: Auto.rest() with custom service (RestServiceMixin)"""

    base_url = "/product"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] == 77
            assert len(result.data["items"]) == 77

    def test_get_single(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, 1))
            assert result.code == HTTP_OK
            assert result.data["product_name"] == "Chai"

    def test_crud(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create
            record = {
                "product_name": "Test Widget",
                "supplier_id": 1,
                "category_id": 1,
                "quantity_per_unit": "10 boxes",
                "unit_price": 9.99,
                "units_in_stock": 50,
                "units_on_order": 0,
                "reorder_level": 5,
                "discontinued": 0,
            }
            result = client.post(self.base_url, data=record)
            assert result.code == HTTP_OK
            product_id = result.data["id"]

            # read
            result = client.get("{}/{}".format(self.base_url, product_id))
            assert result.code == HTTP_OK
            assert result.data["product_name"] == "Test Widget"
            assert result.data["unit_price"] == 9.99

            # update
            record["product_name"] = "Updated Widget"
            record["unit_price"] = 12.99
            result = client.put(
                "{}/{}".format(self.base_url, product_id), data=record
            )
            assert result.code == HTTP_OK

            # verify update
            result = client.get("{}/{}".format(self.base_url, product_id))
            assert result.data["product_name"] == "Updated Widget"
            assert result.data["unit_price"] == 12.99

            # delete
            result = client.delete("{}/{}".format(self.base_url, product_id))
            assert result.code == HTTP_OK

            result = client.get("{}/{}".format(self.base_url, product_id))
            assert result.code == HTTP_NOT_FOUND

    def test_search(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}?search=Chai".format(self.base_url))
            assert result.code == HTTP_OK
            assert result.data["total"] == 1
            assert result.data["items"][0]["product_name"] == "Chai"


class TestCustomerReadOnly:
    """Feature 4: Auto.rest() with custom base_cls (read-only) + string ID"""

    base_url = "/customer"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] == 91

    def test_get_single(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, "ALFKI"))
            assert result.code == HTTP_OK
            assert result.data["company_name"] == "Alfreds Futterkiste"

    def test_post_blocked(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.post(
                self.base_url,
                data={"id": "ZZZZZ", "company_name": "Test"},
            )
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert "method not allowed" in result.error_message

    def test_put_blocked(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.put(
                "{}/{}".format(self.base_url, "ALFKI"),
                data={"company_name": "Nope"},
            )
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert "method not allowed" in result.error_message

    def test_delete_blocked(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.delete("{}/{}".format(self.base_url, "ALFKI"))
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert "method not allowed" in result.error_message

    def test_search(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}?search=Alfreds".format(self.base_url))
            assert result.code == HTTP_OK
            assert result.data["total"] >= 1

    def test_get_nonexistent(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, "ZZZZZ"))
            assert result.code == HTTP_NOT_FOUND


class TestPrefixedRoute:
    """Feature 5: Auto.rest() with prefix for API versioning"""

    base_url = "/api/v1/article"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert "total" in result.data
            assert "items" in result.data

    def test_crud(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create via prefixed route
            result = client.post(
                self.base_url,
                data={
                    "title": "Prefixed Article",
                    "slug": "prefixed",
                    "body": "body",
                    "author_name": "Author",
                    "status": "draft",
                },
            )
            assert result.code == HTTP_OK
            article_id = result.data["id"]

            # read via prefixed route
            result = client.get("{}/{}".format(self.base_url, article_id))
            assert result.code == HTTP_OK
            assert result.data["title"] == "Prefixed Article"

            # same article accessible via unprefixed route
            result = client.get("/article/{}".format(article_id))
            assert result.code == HTTP_OK
            assert result.data["title"] == "Prefixed Article"

            # cleanup
            client.delete("{}/{}".format(self.base_url, article_id))


class TestCamelCaseResponse:
    """Feature 6: Auto.rest() with camel_case=True"""

    base_url = "/camel/article"

    def test_list_camelcase_keys(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create an article (via regular endpoint to populate data)
            result = client.post(
                "/article",
                data={
                    "title": "CamelCase Test",
                    "slug": "camel-test",
                    "body": "body",
                    "author_name": "Alice",
                    "status": "published",
                },
            )
            assert result.code == HTTP_OK

            # read via camelCase endpoint
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] >= 1

            item = result.data["items"][0]
            # camelCase keys should be present
            assert "authorName" in item
            assert "createdAt" in item
            # snake_case keys should NOT be present
            assert "author_name" not in item
            assert "created_at" not in item

    def test_get_single_camelcase(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create and read back
            result = client.post(
                "/article",
                data={
                    "title": "Single CamelCase",
                    "slug": "single-camel",
                    "body": "body",
                    "author_name": "Bob",
                    "status": "draft",
                },
            )
            article_id = result.data["id"]

            result = client.get("{}/{}".format(self.base_url, article_id))
            assert result.code == HTTP_OK
            assert "authorName" in result.data
            assert result.data["authorName"] == "Bob"

            # cleanup
            client.delete("/article/{}".format(article_id))


class TestAuditMixin:
    """Feature 7: Auto.rest() with mixin composition (audit hook)"""

    base_url = "/audited/article"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert "total" in result.data

    def test_crud_through_mixin(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create
            result = client.post(
                self.base_url,
                data={
                    "title": "Audited Article",
                    "slug": "audited",
                    "body": "body",
                    "author_name": "Auditor",
                    "status": "draft",
                },
            )
            assert result.code == HTTP_OK
            article_id = result.data["id"]

            # read — mixin hook runs but allows through
            result = client.get("{}/{}".format(self.base_url, article_id))
            assert result.code == HTTP_OK
            assert result.data["title"] == "Audited Article"

            # update through mixin
            result = client.put(
                "{}/{}".format(self.base_url, article_id),
                data={
                    "title": "Audited Updated",
                    "slug": "audited",
                    "body": "body",
                    "author_name": "Auditor",
                    "status": "published",
                },
            )
            assert result.code == HTTP_OK

            # delete through mixin
            result = client.delete("{}/{}".format(self.base_url, article_id))
            assert result.code == HTTP_OK


class TestListLimit:
    """Feature 8: Auto.rest() with list_limit kwarg"""

    base_url = "/limited/article"

    def test_list_respects_limit(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create more than 10 articles
            for i in range(12):
                client.post(
                    self.base_url,
                    data={
                        "title": "Limited {}".format(i),
                        "slug": "limited-{}".format(i),
                        "body": "body",
                        "author_name": "Author",
                        "status": "draft",
                    },
                )

            # list should respect the limit=10
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] >= 12
            assert len(result.data["items"]) <= 10


class TestSupplierAutoView:
    """Feature 9: Auto.view() from DB table + manual AutoRouter.resource() registration"""

    base_url = "/supplier"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] == 29

    def test_get_single(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, 1))
            assert result.code == HTTP_OK
            assert result.data["company_name"] == "Exotic Liquids"

    def test_crud(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create
            record = {
                "company_name": "Test Supplier Co",
                "contact_name": "Jane Doe",
                "contact_title": "Director",
                "address": "123 Main St",
                "city": "Portland",
                "region": "OR",
                "postal_code": "97201",
                "country": "USA",
                "phone": "555-0100",
            }
            result = client.post(self.base_url, data=record)
            assert result.code == HTTP_OK
            supplier_id = result.data["id"]

            # read
            result = client.get("{}/{}".format(self.base_url, supplier_id))
            assert result.code == HTTP_OK
            assert result.data["company_name"] == "Test Supplier Co"

            # update
            record["company_name"] = "Updated Supplier"
            result = client.put(
                "{}/{}".format(self.base_url, supplier_id), data=record
            )
            assert result.code == HTTP_OK

            # verify update
            result = client.get("{}/{}".format(self.base_url, supplier_id))
            assert result.data["company_name"] == "Updated Supplier"

            # delete
            result = client.delete("{}/{}".format(self.base_url, supplier_id))
            assert result.code == HTTP_OK

            result = client.get("{}/{}".format(self.base_url, supplier_id))
            assert result.code == HTTP_NOT_FOUND


class TestCategoryAutoViewSlug:
    """Feature 10: Auto.view() with slug for auto-registration"""

    base_url = "/category"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] == 8

    def test_get_single(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, 1))
            assert result.code == HTTP_OK
            assert result.data["category_name"] == "Beverages"

    def test_crud(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # create
            result = client.post(
                self.base_url,
                data={"category_name": "Test Cat", "description": "A test category"},
            )
            assert result.code == HTTP_OK
            cat_id = result.data["id"]

            # read
            result = client.get("{}/{}".format(self.base_url, cat_id))
            assert result.code == HTTP_OK
            assert result.data["category_name"] == "Test Cat"

            # update
            result = client.put(
                "{}/{}".format(self.base_url, cat_id),
                data={
                    "category_name": "Updated Cat",
                    "description": "Updated desc",
                },
            )
            assert result.code == HTTP_OK

            # verify update
            result = client.get("{}/{}".format(self.base_url, cat_id))
            assert result.data["category_name"] == "Updated Cat"

            # delete
            result = client.delete("{}/{}".format(self.base_url, cat_id))
            assert result.code == HTTP_OK

            result = client.get("{}/{}".format(self.base_url, cat_id))
            assert result.code == HTTP_NOT_FOUND


class TestCustomerController:
    """Feature 11: AutoRouter.controller() with named methods"""

    base_url = "/customer-ctrl"

    def test_list(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.data["total"] == 91
            assert isinstance(result.data["items"], list)

    def test_show(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, "ALFKI"))
            assert result.code == HTTP_OK
            assert result.data["company_name"] == "Alfreds Futterkiste"
            assert result.data["id"] == "ALFKI"

    def test_show_nonexistent(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("{}/{}".format(self.base_url, "ZZZZZ"))
            assert result.code == HTTP_NOT_FOUND
            assert result.success is False
