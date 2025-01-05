from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory


# config parameters, injectable from ENV vars
class Config(EnvironmentConfig, PokieConfig):
    pass


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

    return pokie_app, flask_app


main, app = build_pokie()

if __name__ == '__main__':
    main.cli()
