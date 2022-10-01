# Version
POKIE_VERSION = ["0", "1", "0"]

def get_version():
    return ".".join(POKIE_VERSION)


# DI Keys
DI_CONFIG = 'config'
DI_APP = 'app'
DI_MODULES = 'modules'
DI_SERVICE_MANAGER = 'svc_manager'
DI_DB = 'db'
DI_REDIS = 'redis'

# DB Configuration
CFG_DB_NAME = 'db_name'
CFG_DB_HOST = 'db_host'
CFG_DB_PORT = 'db_port'
CFG_DB_USER = 'db_user'
CFG_DB_PASSWORD = 'db_password'
CFG_DB_SSL = 'db_ssl'

# Redis Configuration
CFG_REDIS_HOST = 'redis_host'
CFG_REDIS_PORT = 'redis_port'
CFG_REDIS_PASSWORD = 'redis_password'
CFG_REDIS_DB = 'redis_db'
CFG_REDIS_SSL = 'redis_ssl'
