# Cache

Pokie provides a cache abstraction layer with multiple backends. All cache implementations follow the
`CacheInterface` from Rick, providing a consistent API regardless of the backend.

## Cache Interface

All cache backends implement the following methods:

| Method | Description |
|--------|-------------|
| `get(key)` | Retrieve a value by key. Returns `None` if not found or expired. |
| `set(key, value, ttl=None)` | Store a value with an optional TTL (in seconds). |
| `has(key)` | Check if a key exists and is not expired. |
| `remove(key)` | Remove a key from the cache. |
| `purge()` | Clear all cached entries. |

## Available Backends

### RedisCache

Production cache backend using Redis. Requires `RedisFactory` and `CacheFactory` to be registered (see
[Factories](factories.md)).

```python
from pokie.cache import RedisCache
```

RedisCache wraps the Rick `RedisCache` class and retrieves the Redis client from the DI container (`DI_REDIS`). If
`DI_REDIS` is not available, a `RuntimeError` is raised.

### MemoryCache

In-memory cache for unit testing. Supports TTL via `time.monotonic()` and uses pickle for value serialization.

```python
from pokie.cache import MemoryCache
```

> Note: MemoryCache is intended for testing only. Do not use it in production environments.

**Additional methods:**

| Method | Description |
|--------|-------------|
| `set_prefix(prefix)` | Set a key prefix for namespacing. |

### DummyCache

No-op cache implementation where all operations do nothing. Useful for development or when caching should be
disabled.

```python
from pokie.cache import DummyCache
```

All `get()` calls return `None`, and all `set()`/`remove()`/`purge()` calls are silently ignored.

## Cache Setup

To use Redis-based caching, include both `RedisFactory` and `CacheFactory` in your factory list:

```python
from pokie.core.factories.redis import RedisFactory
from pokie.core.factories.cache import CacheFactory

factories = [
    PgSqlFactory,
    RedisFactory,
    CacheFactory,
]
```

This registers a `RedisCache` instance as `DI_CACHE` in the DI container.

## Cache in Auth Services

The auth module uses caching for user and ACL lookups. This behavior is controlled by the `AUTH_USE_CACHE`
configuration option (default: `True`). When enabled and `DI_CACHE` is available, the `UserService` and `AclService`
use the registered cache. When disabled, a `DummyCache` is used as a transparent fallback.
