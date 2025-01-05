from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie.http import AutoRouter
from pokie.rest.auto import Auto


# config parameters, injectable from ENV vars
class Config(EnvironmentConfig, PokieConfig):
    pass


# Our custom route initialization to skip usage of modules
# because Auto.rest() will require database access to the table customers, we need to postpone route registration
# to the actual web initialization routines, as it is done with modules
def router(p: FlaskApplication):
    # Auto.view() will generate a view for the customers table
    view = Auto.view(app, "customers", search_fields=["company_name", "contact_name"])
    # and AutoRouter.resouce() registers the following endpoints:
    # /customer                     HEAD,GET,OPTIONS
    # /customer/<string:id_record>  HEAD,GET,OPTIONS
    # /customer                     OPTIONS,POST
    # /customer/<string:id_record>  PATCH,PUT,OPTIONS
    # /customer/<string:id_record>  DELETE,OPTIONS
    AutoRouter.resource(p.app, "customer", view, id_type="string")


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
    pokie_app.register_pre_http_hook(router)

    return pokie_app, flask_app


main, app = build_pokie()

# =============================================================================

if __name__ == '__main__':
    main.cli()
