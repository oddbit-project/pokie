from rick_db import fieldmapper


@fieldmapper(tablename="articles", pk="article_id")
class ArticleRecord:
    id = "article_id"
    title = "title"
    slug = "slug"
    body = "body"
    author_name = "author_name"
    status = "status"
    created_at = "created_at"


@fieldmapper(tablename="products", pk="product_id")
class ProductRecord:
    id = "product_id"
    product_name = "product_name"
    supplier_id = "supplier_id"
    category_id = "category_id"
    quantity_per_unit = "quantity_per_unit"
    unit_price = "unit_price"
    units_in_stock = "units_in_stock"
    units_on_order = "units_on_order"
    reorder_level = "reorder_level"
    discontinued = "discontinued"


@fieldmapper(tablename="customers", pk="customer_id")
class CustomerRecord:
    id = "customer_id"
    company_name = "company_name"
    contact_name = "contact_name"
    contact_title = "contact_title"
    address = "address"
    city = "city"
    region = "region"
    postal_code = "postal_code"
    country = "country"
    phone = "phone"
    fax = "fax"


@fieldmapper(tablename="shippers", pk="shipper_id")
class ShipperRecord:
    id = "shipper_id"
    company_name = "company_name"
    phone = "phone"
