from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie.core.factories.redis import RedisFactory


class Config(EnvironmentConfig, PokieConfig):
    REDIS_SSL = "0"
    REDIS_PORT = 6379
    REDIS_PASSWORD = "myRedisPassword"
    TEST_MANAGE_DB = True
    TEST_DB_SSL = False


def build_pokie():
    # load configuration from ENV
    cfg = Config().build()

    # modules to load & initialize
    modules = [
        'pokie.contrib.auth',
        'pokie_test',  # default test module
    ]

    # factories to run
    factories = [PgSqlFactory, RedisFactory, ]

    # build app
    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)

    return pokie_app, flask_app


main, app = build_pokie()

# =============================================================================

if __name__ == '__main__':
    main.cli()
