# Configuration

Pokie uses a class-based configuration system, where configuration values are defined as class attributes that are
automatically mapped to environment variables or JSON files.

## Configuration Classes

Configuration is managed by extending **PokieConfig** together with a config loader class from Rick. The two main
approaches are environment-based and file-based configuration.

### Environment-Based Configuration

**EnvironmentConfig** reads configuration values from environment variables. Attribute names are uppercased to match
environment variable naming conventions:

```python
from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig


class Config(EnvironmentConfig, PokieConfig):
    # custom options
    MY_CUSTOM_OPTION = "default_value"


# build and load from environment
cfg = Config().build()
```

With this setup, each class attribute is read from the corresponding environment variable. For example, `DB_HOST` is
read from the `DB_HOST` environment variable; if not set, the default value from **PokieConfig** is used.

### File-Based Configuration

JSON file configuration can be loaded using the `json_file()` helper:

```python
from rick.resource.config import json_file
from pokie.config import PokieConfig


class Config(PokieConfig):
    pass


cfg = json_file("config.json", Config)
```

## StrOrFile

Some configuration values (passwords, secrets) support the **StrOrFile** mechanism from Rick. When a value is wrapped
with `StrOrFile`, it can be provided either as a plain string or as a file path. If the value is a file path that
exists, the file contents are read as the actual value:

```python
from rick.resource.config import StrOrFile

# can be a literal value or a path to a file containing the value
DB_PASSWORD = StrOrFile("")
```

This is useful for Docker secrets or other systems that mount credentials as files.

## PokieConfig Defaults

### HTTP Settings

| Attribute | Default | Description |
|-----------|---------|-------------|
| `HTTP_ERROR_HANDLER` | `"pokie.http.HttpErrorHandler"` | Default HTTP exception handler class |
| `AUTH_SECRET` | `""` | Secret key for Flask-Login session hashing |

### Database Settings (PostgreSQL)

| Attribute | Default | Description |
|-----------|---------|-------------|
| `DB_CACHE_METADATA` | `False` | Cache table metadata (disable for development) |
| `DB_NAME` | `"pokie"` | Database name |
| `DB_HOST` | `"localhost"` | Database host |
| `DB_PORT` | `5432` | Database port |
| `DB_USER` | `StrOrFile("postgres")` | Database user |
| `DB_PASSWORD` | `StrOrFile("")` | Database password |
| `DB_SSL` | `True` | Enforce SSL connection |
| `DB_MINPROCS` | `5` | Minimum connection pool size |
| `DB_MAXPROCS` | `15` | Maximum connection pool size |

### Redis Settings

| Attribute | Default | Description |
|-----------|---------|-------------|
| `REDIS_HOST` | `"localhost"` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_PASSWORD` | `StrOrFile("")` | Redis password |
| `REDIS_DB` | `0` | Redis database number |
| `REDIS_SSL` | `True` | Enforce SSL connection |

### CORS Settings

| Attribute | Default | Description |
|-----------|---------|-------------|
| `CORS_ORIGINS` | `"*"` | Allowed origins (comma-separated or `*` for all) |
| `CORS_METHODS` | `"GET,POST,PUT,PATCH,DELETE,OPTIONS"` | Allowed HTTP methods |
| `CORS_ALLOW_HEADERS` | `"Content-Type,Authorization"` | Allowed request headers |
| `CORS_EXPOSE_HEADERS` | `""` | Response headers to expose to the browser |
| `CORS_MAX_AGE` | `600` | Preflight cache duration in seconds |

### Rate Limiting Settings

| Attribute | Default | Description |
|-----------|---------|-------------|
| `RATE_LIMIT_DEFAULT` | `""` | Default rate limit (e.g. `"100/hour"`). Empty disables limiting. |
| `RATE_LIMIT_STORAGE` | `"memory"` | Storage backend: `"memory"` or `"redis"` |

### Test Settings

| Attribute | Default | Description |
|-----------|---------|-------------|
| `TEST_DB_NAME` | `"pokie_test"` | Test database name |
| `TEST_DB_HOST` | `"localhost"` | Test database host |
| `TEST_DB_PORT` | `5432` | Test database port |
| `TEST_DB_USER` | `StrOrFile("postgres")` | Test database user |
| `TEST_DB_PASSWORD` | `StrOrFile("")` | Test database password |
| `TEST_DB_SSL` | `False` | Enforce SSL for test database |
| `TEST_MANAGE_DB` | `False` | Manage test database creation/drop |
| `TEST_SHARE_CTX` | `False` | Share application context across tests |
| `TEST_DB_REUSE` | `False` | Reuse existing test database |
| `TEST_SKIP_MIGRATIONS` | `False` | Skip migrations when recreating test database |
| `TEST_SKIP_FIXTURES` | `False` | Skip fixtures when recreating test database |

## CFG Constants Reference

All configuration keys used internally are defined in `pokie.constants`:

| Constant | Config Key | Description |
|----------|-----------|-------------|
| `CFG_HTTP_ERROR_HANDLER` | `http_error_handler` | HTTP error handler class |
| `CFG_DB_NAME` | `db_name` | Database name |
| `CFG_DB_HOST` | `db_host` | Database host |
| `CFG_DB_PORT` | `db_port` | Database port |
| `CFG_DB_USER` | `db_user` | Database user |
| `CFG_DB_PASSWORD` | `db_password` | Database password |
| `CFG_DB_SSL` | `db_ssl` | Database SSL |
| `CFG_DB_MINPROCS` | `db_minprocs` | Min pool size |
| `CFG_DB_MAXPROCS` | `db_maxprocs` | Max pool size |
| `CFG_REDIS_HOST` | `redis_host` | Redis host |
| `CFG_REDIS_PORT` | `redis_port` | Redis port |
| `CFG_REDIS_PASSWORD` | `redis_password` | Redis password |
| `CFG_REDIS_DB` | `redis_db` | Redis database |
| `CFG_REDIS_SSL` | `redis_ssl` | Redis SSL |
| `CFG_AUTH_SECRET` | `auth_secret` | Auth secret key |
| `CFG_CORS_ORIGINS` | `cors_origins` | CORS allowed origins |
| `CFG_CORS_METHODS` | `cors_methods` | CORS allowed methods |
| `CFG_CORS_ALLOW_HEADERS` | `cors_allow_headers` | CORS allowed headers |
| `CFG_CORS_EXPOSE_HEADERS` | `cors_expose_headers` | CORS exposed headers |
| `CFG_CORS_MAX_AGE` | `cors_max_age` | CORS preflight cache (seconds) |
| `CFG_RATE_LIMIT_DEFAULT` | `rate_limit_default` | Default rate limit |
| `CFG_RATE_LIMIT_STORAGE` | `rate_limit_storage` | Rate limit storage backend |

## DI Container Keys

All DI container keys are defined in `pokie.constants`:

| Constant | DI Key | Description |
|----------|--------|-------------|
| `DI_CONFIG` | `config` | Configuration container |
| `DI_FLASK` | `app` | Flask application instance |
| `DI_APP` | `main` | Pokie FlaskApplication instance |
| `DI_MODULES` | `modules` | Loaded module list |
| `DI_SERVICES` | `svc_manager` | Service manager (MapLoader) |
| `DI_DB` | `db` | Database connection pool |
| `DI_REDIS` | `redis` | Redis client |
| `DI_CACHE` | `cache` | Cache client (CacheInterface) |
| `DI_EVENTS` | `event_manager` | Event manager |
| `DI_TTY` | `tty` | Console writer |
| `DI_SIGNAL` | `signal` | Signal manager |
| `DI_HTTP_ERROR_HANDLER` | `http_error_handler` | HTTP exception handler |
| `DI_RATE_LIMITER` | `rate_limiter` | Flask-Limiter instance |

## Other Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `DEFAULT_LIST_SIZE` | `100` | Default list size for DbGrid operations |
| `TTL_1H` | `3600` | 1-hour TTL in seconds |
| `TTL_1D` | `86400` | 1-day TTL in seconds |
