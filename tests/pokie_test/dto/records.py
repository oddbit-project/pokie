from rick_db import fieldmapper


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
