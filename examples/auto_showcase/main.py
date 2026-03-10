from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory


class Config(EnvironmentConfig, PokieConfig):
    TEST_MANAGE_DB = True
    TEST_DB_SSL = False


def build_pokie():
    cfg = Config().build()

    modules = [
        "showcase",
    ]

    factories = [PgSqlFactory]

    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)

    return pokie_app, flask_app


main, app = build_pokie()

if __name__ == "__main__":
    main.cli()
