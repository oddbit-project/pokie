from rick.resource.config import StrOrFile


class PokieConfig:
    # default HTTP Exception Handler - 404 and 500 exceptions
    HTTP_ERROR_HANDLER = "pokie.http.HttpErrorHandler"

    # Secret key for flask-login hashing
    AUTH_SECRET = ""

    # cache table-related metadata (such as primary key info)
    # development should be false
    DB_CACHE_METADATA = False

    # Postgresql Configuration
    DB_NAME = "pokie"
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_USER = StrOrFile("postgres")
    DB_PASSWORD = StrOrFile("")
    DB_SSL = True
    DB_MINPROCS = 5
    DB_MAXPROCS = 15

    # Redis Configuration
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_PASSWORD = StrOrFile("")
    REDIS_DB = 0
    REDIS_SSL = True

    # Pytest Configuration
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

    # CORS Configuration
    CORS_ORIGINS = "*"
    CORS_METHODS = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    CORS_ALLOW_HEADERS = "Content-Type,Authorization"
    CORS_EXPOSE_HEADERS = ""
    CORS_MAX_AGE = 600

    # Rate Limiting Configuration
    RATE_LIMIT_DEFAULT = ""  # empty = disabled. e.g. "100/hour"
    RATE_LIMIT_STORAGE = "memory"  # "memory" or "redis"
