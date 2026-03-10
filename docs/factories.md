# Factories

Factories are callable functions that initialize and register resources in the Dependency Injection (DI) container.
They are executed during application build, before modules are loaded.

## Built-in Factories

### PgSqlFactory

Registers a PostgreSQL connection pool as `DI_DB`. The connection is lazily created on first access.

```python
from pokie.core.factories.pgsql import PgSqlFactory
```

**Configuration keys used:**

| Key | Default | Description |
|-----|---------|-------------|
| `CFG_DB_NAME` | `"postgres"` | Database name |
| `CFG_DB_HOST` | `"localhost"` | Database host |
| `CFG_DB_PORT` | `5432` | Database port |
| `CFG_DB_USER` | `"postgres"` | Database user |
| `CFG_DB_PASSWORD` | `""` | Database password |
| `CFG_DB_SSL` | `True` | If true, uses `sslmode=require` |
| `CFG_DB_MINPROCS` | `5` | Minimum connection pool size |
| `CFG_DB_MAXPROCS` | `15` | Maximum connection pool size |

**Registers:** `DI_DB` as a `PgConnectionPool` instance (from RickDb).

### RedisFactory

Registers a Redis client as `DI_REDIS`. The connection is lazily created on first access.

```python
from pokie.core.factories.redis import RedisFactory
```

**Configuration keys used:**

| Key | Default | Description |
|-----|---------|-------------|
| `CFG_REDIS_HOST` | `"localhost"` | Redis host |
| `CFG_REDIS_PORT` | `6379` | Redis port |
| `CFG_REDIS_PASSWORD` | `None` | Redis password |
| `CFG_REDIS_DB` | `0` | Redis database number |
| `CFG_REDIS_SSL` | `False` | Enable SSL |

**Registers:** `DI_REDIS` as a `redis.Redis` instance.

### CacheFactory

Registers a Redis-based cache as `DI_CACHE`. Requires `RedisFactory` to be loaded first.

```python
from pokie.core.factories.cache import CacheFactory
```

**Registers:** `DI_CACHE` as a `RedisCache` instance.

> Note: CacheFactory currently only supports Redis as the cache backend.

### FlaskLoginFactory

Initializes Flask-Login on the Flask application. Sets the application secret key from configuration and registers
a default user loader that returns `None`. Applications using authentication should override the user loader with
their own implementation.

```python
from pokie.core.factories.login import FlaskLoginFactory
```

**Configuration keys used:**

| Key | Default | Description |
|-----|---------|-------------|
| `CFG_AUTH_SECRET` | `""` | Secret key for Flask-Login session hashing |

**Required by:** `PokieAuthView` (for authentication and ACL checks).

### CorsFactory

Initializes [Flask-CORS](https://flask-cors.readthedocs.io/) on the Flask application, enabling Cross-Origin Resource
Sharing headers on all responses.

```python
from pokie.core.factories.cors import CorsFactory
```

**Configuration keys used:**

| Key | Default | Description |
|-----|---------|-------------|
| `CFG_CORS_ORIGINS` | `"*"` | Allowed origins (comma-separated or `*` for all) |
| `CFG_CORS_METHODS` | `"GET,POST,PUT,PATCH,DELETE,OPTIONS"` | Allowed HTTP methods |
| `CFG_CORS_ALLOW_HEADERS` | `"Content-Type,Authorization"` | Allowed request headers |
| `CFG_CORS_EXPOSE_HEADERS` | `""` | Response headers to expose to the browser |
| `CFG_CORS_MAX_AGE` | `600` | Preflight cache duration in seconds |

### RateLimiterFactory

Initializes [Flask-Limiter](https://flask-limiter.readthedocs.io/) on the Flask application. If `RATE_LIMIT_DEFAULT`
is empty, the factory is a no-op and no rate limiting is applied.

```python
from pokie.core.factories.rate_limiter import RateLimiterFactory
```

**Configuration keys used:**

| Key | Default | Description |
|-----|---------|-------------|
| `CFG_RATE_LIMIT_DEFAULT` | `""` | Default rate limit (e.g. `"100/hour"`, `"10/minute"`). Empty disables limiting. |
| `CFG_RATE_LIMIT_STORAGE` | `"memory"` | Storage backend: `"memory"` or `"redis"` |

When using `"redis"` storage, the factory reads Redis connection settings from the existing Redis configuration keys
(`CFG_REDIS_HOST`, `CFG_REDIS_PORT`, `CFG_REDIS_PASSWORD`, `CFG_REDIS_DB`).

**Registers:** `DI_RATE_LIMITER` as a `Limiter` instance (only when rate limiting is enabled).

The limiter instance can be used for per-route rate limits:

```python
from pokie.constants import DI_RATE_LIMITER

limiter = di.get(DI_RATE_LIMITER)

@limiter.limit("5/minute")
def my_expensive_endpoint():
    ...
```

## Using Factories

Factories are passed to `FlaskApplication.build()` as a list:

```python
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie.core.factories.redis import RedisFactory
from pokie.core.factories.cache import CacheFactory
from pokie.core.factories.login import FlaskLoginFactory
from pokie.core.factories.cors import CorsFactory
from pokie.core.factories.rate_limiter import RateLimiterFactory


cfg = Config().build()
pokie_app = FlaskApplication(cfg)

factories = [
    PgSqlFactory,
    RedisFactory,
    CacheFactory,
    FlaskLoginFactory,
    CorsFactory,
    RateLimiterFactory,
]

flask_app = pokie_app.build(modules, factories)
```

Factories are executed in the order they are listed. If a factory depends on a resource registered by another
factory, the dependency must appear first in the list.

## Writing Custom Factories

A factory is any callable that accepts a `Di` instance. Use `_di.add()` for direct registration or `@_di.register()`
for lazy initialization:

```python
from rick.base import Di


def MyServiceFactory(_di: Di):
    """
    Example factory with lazy initialization
    """

    @_di.register("my_service")
    def _factory(_di: Di):
        # this code runs only when di.get("my_service") is first called
        return MyService(config=_di.get("config"))
```

For simple resources that don't need lazy initialization:

```python
from rick.base import Di


def MySimpleFactory(_di: Di):
    _di.add("my_resource", MyResource())
```
