# Changelog

## [1.0.0] - 2026-03-10

### Added
- `FlaskLoginFactory` for Flask-Login initialization (`pokie.core.factories.login`)
- `CorsFactory` for Flask-CORS initialization (`pokie.core.factories.cors`)
- `RateLimiterFactory` for Flask-Limiter initialization (`pokie.core.factories.rate_limiter`)
- CORS configuration options: `CORS_ORIGINS`, `CORS_METHODS`, `CORS_ALLOW_HEADERS`, `CORS_EXPOSE_HEADERS`, `CORS_MAX_AGE`
- Rate limiting configuration options: `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_STORAGE`
- `JobRunner` class with per-job intervals, retry with exponential backoff, and timeout support (`pokie.core.job_runner`)
- Job attributes: `job_interval`, `job_max_retries`, `job_timeout` for fine-grained job control
- `openapi:generate` CLI command for generating OpenAPI 3.0 specifications from registered routes
- `OpenApiBuilder` class for programmatic OpenAPI spec generation (`pokie.contrib.base.cli.openapi_builder`)
- `flask-cors` and `flask-limiter` as dependencies
- Documentation for CORS, rate limiting, job runner, and OpenAPI CLI

### Changed
- Job runner now delegates to `JobRunner` class with per-job state tracking

### Removed
- Extracted `pokie.contrib.auth` module from core (now available as a separate package)
- Removed `AUTH_USE_CACHE` configuration option (was only used by auth services)

## [0.9.7] - 2026-03-10

### Added
- Flask 3.x compatibility
- Python 3.12, 3.13, 3.14 support
- `pokie` CLI entry point via `console_scripts`
- pytest integration (`python main.py pytest`)
- `SignalManager` for OS signal handling with multi-handler support
- `MemoryCache` TTL support via `time.monotonic()` expiry tracking
- `MemoryCache.set_prefix()` for cache key isolation
- `PokieView` application hooks (`pre_http_hooks`, `dispatch_hooks`)
- `RestView` with auto-generated CRUD endpoints (`Auto.rest()`, `Auto.view()`)
- `AutoRouter` with resource, controller, and named view routing
- `DbGridRequest` for paginated/sorted/filtered list queries
- `PokieClient` and `PokieResponse` test helpers
- `AuthInterface` for pluggable test client authentication
- Comprehensive unit tests for REST views, HTTP responses, codegen

### Changed
- Adopted rick_db 2.0.0
- Updated all dependencies to current versions (Flask >=3.1.3, rick >=0.8.1, rick_db >=2.0.2)
- Relaxed dependency pinning (exact versions replaced with minimum versions)
- Redis is now a direct dependency (not optional extra)
- `CacheFactory` imports `RedisCache` from `pokie.cache.redis` (was `rick.resource.redis`)
- `SignalManager` uses `TypeError` instead of `assert` for input validation; logs handler exceptions
- `PokieView.exception_handler()` returns HTTP 500 (was 400) for unhandled exceptions
- `RestView.exception_handler()` returns HTTP 400 for client-caused DB constraint errors
- SSL config in `PgSqlFactory`, `RedisFactory`, and test plugin accepts `"1"`, `"true"`, `"yes"` (case-insensitive)
- Unified SSL config logic between production (`pgsql.py`) and test (`plugin.py`)
- `DbGridRequest.validator_sort()` normalizes sort order to lowercase, strips whitespace, handles empty strings

### Fixed
- `RestServiceMixin.list()`: removed duplicate `search_fields` parameter in `grid.run()` call
- `RestView`: added guard for `record_class is None`
- `MemoryCache`: was ignoring TTL parameter entirely
- `MemoryCache.keys()` usage replaced with proper key-based lookups
- `PokieResponse`: guarded `json.loads()` against non-JSON responses
- `PokieResponse`: guarded error dict access with `isinstance` check
- Test plugin: closed DB connection after dropping test database (resource leak)
- Test plugin: added `None` defaults to `getattr()` calls
- Test plugin: added factory `None` guard when `CFG_TEST_SHARE_CTX` is False
- `codegen/template.py`: `mkdir()` now uses `parents=True, exist_ok=True`
- `db:init` CLI: error message now colored red (was green)
- `tpl:gen` CLI: fixed typo "sucessfully" -> "successfully"
- `cli/pokie.py`: removed unused `args` parameter from `main()`
- `cache/redis.py`: removed unused `pickle` import
