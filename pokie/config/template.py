import uuid

from rick.resource.config import StrOrFile


class BaseConfigTemplate:
    # list of enabled module names
    MODULES = []
    # if true, all endpoints are authenticated by default
    USE_AUTH = True
    # Autentication plugins to use
    AUTH_PLUGINS = ['pokie.contrib.auth.plugin.DbAuthPlugin']

    # Secret key for flask-login hashing
    AUTH_SECRET = uuid.uuid4().hex

    # cache table-related metadata (such as primary key info)
    # development should be false
    DB_CACHE_METADATA = False


class PgConfigTemplate:
    # Postgresql Configuration
    DB_NAME = 'pokie'
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_USER = StrOrFile('postgres')
    DB_PASSWORD = StrOrFile('')
    DB_SSL = 'True'


class RedisConfigTemplate:
    # Redis Configuration
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_PASSWORD = StrOrFile('')
    REDIS_DB = 0
    REDIS_SSL = '1'
