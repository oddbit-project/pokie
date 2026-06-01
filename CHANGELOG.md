# Changelog

## [1.1.0] - 2026-06-01

### Security
- `Auto.rest()` / `Auto.view()` now require authentication by default (`auth=True`), composing `PokieAuthView` into the generated view; pass `auth=False` for public access and `acl=[...]` to require specific permissions
- `CorsFactory` no longer enables cross-origin access by default: `CORS_ORIGINS` defaults to `""` (was `"*"`); set explicit origins to enable CORS
- `DbGridRequest` now rejects `limit` values above `MAX_LIST_SIZE` (1000) to prevent unbounded result sets
- `RedisFactory` defaults TLS to enabled when `REDIS_SSL` is unset, aligning with `PgSqlFactory`
- `RateLimiterFactory` URL-encodes the Redis password in the storage URI
- `RequestGenerator` validates field and foreign-key identifiers before interpolating them into generated source

### Changed
- **Breaking:** auto-generated REST endpoints are authenticated by default; existing callers that relied on public access must pass `auth=False`
- **Breaking:** `CORS_ORIGINS` default changed from `"*"` to `""` (CORS disabled unless configured)
- Updated dependencies to latest: `rick-db>=2.2.2`, `rick>=0.8.3`, `Werkzeug>=3.1.8`, `Flask-Login>=0.6.3`, `setuptools>=82.0.1`, `tabulate>=0.10.0`, `redis>=8.0.0`, `flask-cors>=6.0.2`, `flask-limiter>=4.1.1`
- Reworked CI pipeline (`ci.yml`): test matrix (py3.10–3.14) with PostgreSQL + Redis service containers, plus lint, build, vulnerability (pip-audit) and SAST (bandit) jobs
- SBOM workflow now generates CycloneDX + SPDX SBOMs, scans with Grype, signs with Cosign, and uploads to Dependency-Track and the GitHub release
- Dropped Python 3.8/3.9 from package classifiers (already required `>=3.10`)

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
- `FieldSpec.has_default` attribute for tracking columns with database DEFAULT values
- Validation: non-auto primary keys (e.g. varchar, uuid) are now marked as `required` in generated RequestRecords
- SBOM generation via CycloneDX in GitHub Actions (on push to master and on release)

### Changed
- Job runner now delegates to `JobRunner` class with per-job state tracking
- Updated dependencies: `rick-db>=2.1.0`, `rick>=0.8.2`

### Fixed
- `PgTableSpec.is_serial()`: `pg_get_serial_sequence` returns `[(None,)]` for non-serial columns, not an empty result set; now checks `result[0][0] is not None`
- `RequestGenerator`: fields with database DEFAULT values are no longer marked as `required`, even if NOT NULL

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
