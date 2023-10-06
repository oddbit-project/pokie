import uuid

from rick.resource.config import StrOrFile


class BaseConfigTemplate:
    # default HTTP Exception Handler - 404 and 500 exceptions
    HTTP_ERROR_HANDLER = 'pokie.http.HttpErrorHandler'

    # list of enabled module names
    MODULES = []
    # if true, all endpoints are authenticated by default
    USE_AUTH = True
    # Autentication plugins to use
    AUTH_PLUGINS = ["pokie.contrib.auth.plugin.DbAuthPlugin"]

    # Secret key for flask-login hashing
    AUTH_SECRET = uuid.uuid4().hex

    # cache table-related metadata (such as primary key info)
    # development should be false
    DB_CACHE_METADATA = False


class PgConfigTemplate:
    # Postgresql Configuration
    DB_NAME = "pokie"
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_USER = StrOrFile("postgres")
    DB_PASSWORD = StrOrFile("")
    DB_SSL = "True"


class RedisConfigTemplate:
    # Redis Configuration
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_PASSWORD = StrOrFile("")
    REDIS_DB = 0
    REDIS_SSL = "1"


class TestConfigTemplate:
    TEST_DB_NAME = "pokie_test"  # test database parameters
    TEST_DB_HOST = "localhost"
    TEST_DB_PORT = 5432
    TEST_DB_USER = StrOrFile("postgres")
    TEST_DB_PASSWORD = StrOrFile("")
    TEST_DB_SSL = False

    TEST_MANAGE_DB = (
        False  # if false, unit testing does not manage db creation/migration
    )
    TEST_SHARE_CTX = False  # if false, each test has a separate context
    TEST_DB_REUSE = False  # if true, database is not dropped/recreated
    TEST_SKIP_MIGRATIONS = False  # if true, migrations are not run when recreating db
    TEST_SKIP_FIXTURES = False  # if true, fixtures are not run when recreating db
