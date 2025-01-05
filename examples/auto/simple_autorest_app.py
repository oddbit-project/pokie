from rick_db import fieldmapper
from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie.rest.auto import Auto


@fieldmapper(tablename="customers", pk="customer_id")
class CustomerRecord:
    id = "customer_id"  # this field is actually a varchar
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


# config parameters, injectable from ENV vars
class Config(EnvironmentConfig, PokieConfig):
    pass


# Our custom route initialization to skip usage of modules
# because Auto.rest() will require database access to the table customers, we need to postpone route registration
# to the actual web initialization routines, as it is done with modules
def router(p: FlaskApplication):
    # Auto.rest() will generate all required classes and register the following routes:
    # /customer                     OPTIONS,HEAD,GET
    # /customer/<string:id_record>  OPTIONS,HEAD,GET
    # /customer                     POST,OPTIONS
    # /customer/<string:id_record>  OPTIONS,PUT,PATCH
    # /customer/<string:id_record>  OPTIONS,DELETE
    Auto.rest(p.app,  # our Flask app
              "customer",  # the base slug
              CustomerRecord,  # the DTO to use
              search_fields=[CustomerRecord.company_name, CustomerRecord.contact_name],  # fields to allow text search
              id_type="string"  # type of id_record to use
              )


def build_pokie():
    # load configuration from ENV
    cfg = Config().build()

    # modules to load & initialize
    modules = []

    # factories to run
    factories = [PgSqlFactory, ]

    # build app
    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)
    # register our route initializer to be used only on web context
    pokie_app.register_pre_http_hook(router)

    return pokie_app, flask_app


main, app = build_pokie()

# =============================================================================

if __name__ == '__main__':
    main.cli()
