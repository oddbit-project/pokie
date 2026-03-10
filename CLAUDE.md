# Pokie Development Guide

## Project Overview

Pokie is a modular REST web framework built on Flask, Rick, and RickDb. It follows three-layer
and clean architecture design principles with dependency injection, service location, and factories.

## Build & Test

```bash
# activate environment
source .venv/bin/activate && source env.sh

# run all tests (requires PostgreSQL)
python main.py pytest

# run specific test file
python main.py pytest tests/core/test_job_runner.py -v

# run tests matching a pattern
python main.py pytest -k "test_cors"
```

Tests require a running PostgreSQL instance. The test plugin automatically creates/drops the
`pokie_test` database. Configuration comes from environment variables (see `env.sh`).

Do NOT run tests with bare `pytest` - always use `python main.py pytest` which loads the
Pokie test plugin that provides fixtures (`pokie_app`, `pokie_di`, `pokie_db`,
`pokie_service_manager`, `pokie_client`).

## Project Structure

```
pokie/                  # framework source
  config.py             # PokieConfig defaults
  constants.py          # DI keys, CFG keys, HTTP codes
  core/
    application.py      # FlaskApplication (main entry point)
    command.py          # CliCommand base class
    module.py           # BaseModule
    job_runner.py       # JobRunner with intervals/retry/timeout
    factories/          # PgSqlFactory, RedisFactory, CorsFactory, etc.
  contrib/base/         # base module (CLI commands, services, validators)
    cli/                # CLI command implementations
    job/                # IdleJob
  http/
    view.py             # PokieView, PokieAuthView
    routes.py           # AutoRouter
    dbgrid.py           # DbGridRequest
  rest/
    view.py             # RestView
    auto.py             # Auto.rest(), Auto.view()
pokie_test/             # test module (northwind DB fixtures)
tests/                  # test suite
```

## Key Patterns

### Factories
Callable `(Di) -> None` functions passed to `FlaskApplication.build()`. They initialize
resources in the DI container before modules load.

### Modules
Each module has a `module.py` with a `Module(BaseModule)` class defining `services`, `cmd`,
`events`, `jobs`, and `fixtures`. The `build()` method registers Flask routes.

### Views
`PokieView` extends Flask's `MethodView`. Uses dispatch hooks, automatic request body
deserialization via `RequestRecord`, and `JsonResponse` for consistent API responses.

### CLI Commands
Extend `CliCommand`. Register in module's `cmd` dict as `"command:name": "path.to.Class"`.

### Tests
- Test classes: `class TestXxx:` with `def test_xxx(self, fixture):` methods
- CLI testing: use `ConsoleWriter(stdout=io.StringIO(), stderr=io.StringIO())`
- HTTP testing: `PokieClient(client)` wraps Flask test client
- `conftest.py` just has `pytest_plugins = ["tests.unit.fixtures"]`

## Configuration

Config values are class attributes on `PokieConfig`, read from environment variables when
using `EnvironmentConfig`. Keys are lowercased in the built container. Use `cfg.get("key")`
or `cfg.has("key")` to access values.

## Dependencies

Managed in both `setup.cfg` (for pip/PyPI) and `requirements.txt`. Keep them in sync.
Key deps: Flask, rick, rick-db, flask-cors, flask-limiter, redis, tabulate.
