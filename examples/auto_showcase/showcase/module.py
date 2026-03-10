from pokie.core import BaseModule
from pokie.http import AutoRouter
from pokie.rest.auto import Auto

from showcase.constants import SVC_PRODUCT
from showcase.dto import ArticleRecord, ProductRecord, CustomerRecord, ShipperRecord
from showcase.request import ShipperRequest
from showcase.view import ReadOnlyView, CustomerController, AuditMixin


class Module(BaseModule):
    name = "showcase"
    description = "AutoRouter comprehensive showcase"

    services = {
        SVC_PRODUCT: "showcase.service.ProductService",
    }

    def build(self, parent=None):
        app = parent.app

        # 1. Basic Auto.rest() — auto-generated RequestRecord, search
        Auto.rest(
            app,
            "article",
            ArticleRecord,
            search_fields=[ArticleRecord.title, ArticleRecord.author_name],
        )

        # 2. Custom RequestRecord
        Auto.rest(
            app,
            "shipper",
            ShipperRecord,
            ShipperRequest,
            search_fields=[ShipperRecord.company_name],
        )

        # 3. Custom service
        Auto.rest(
            app,
            "product",
            ProductRecord,
            service=SVC_PRODUCT,
            search_fields=[ProductRecord.product_name],
        )

        # 4. Read-only with custom base class + string ID
        Auto.rest(
            app,
            "customer",
            CustomerRecord,
            base_cls=ReadOnlyView,
            id_type="string",
            search_fields=[CustomerRecord.company_name, CustomerRecord.contact_name],
        )

        # 5. Prefixed API versioning
        Auto.rest(
            app,
            "article",
            ArticleRecord,
            search_fields=[ArticleRecord.title],
            prefix="/api/v1",
        )

        # 6. CamelCase responses
        Auto.rest(
            app,
            "camel/article",
            ArticleRecord,
            search_fields=[ArticleRecord.title, ArticleRecord.author_name],
            camel_case=True,
        )

        # 7. Mixin composition (audit logging)
        Auto.rest(
            app,
            "audited/article",
            ArticleRecord,
            search_fields=[ArticleRecord.title],
            mixins=(AuditMixin,),
        )

        # 8. List limit via kwargs
        Auto.rest(
            app,
            "limited/article",
            ArticleRecord,
            search_fields=[ArticleRecord.title],
            list_limit=10,
        )

        # 9. Auto.view() from DB table + manual registration
        view = Auto.view(app, "suppliers")
        AutoRouter.resource(app, "supplier", view)

        # 10. Auto.view() with slug (auto-registration)
        Auto.view(app, "categories", slug="category")

        # 11. Controller-style routing
        AutoRouter.controller(
            app, "customer-ctrl", CustomerController, id_type="string"
        )
