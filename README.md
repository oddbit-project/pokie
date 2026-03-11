# Welcome to Pokie


[![Tests](https://github.com/oddbit-project/pokie/workflows/Tests/badge.svg)](https://github.com/oddbit-project/pokie/actions)
[![pypi](https://img.shields.io/pypi/v/pokie.svg)](https://pypi.org/project/pokie/)
[![license](https://img.shields.io/pypi/l/pokie.svg)](https://git.oddbit.org/OddBit/pokie/src/branch/master/LICENSE)


Pokie is an REST web framework built on top of [Flask](https://github.com/pallets/flask/),
[Rick](https://git.oddbit.org/OddBit/rick) and [Rick-db](https://git.oddbit.org/OddBit/rick_db) libraries, following three-layer and clean architecture
design principles.

It features an object-oriented design, borrowing from common patterns found in other languages, such as
dependency injection, service location, factories and object composition. It also offers the following functionality:

- Modular design;
- Dependency registry and factories;
- Configuration via environment variables or JSON files;
- CLI command support;
- Events and signal handlers;
- Caching (Redis, in-memory, dummy);
- Jobs with per-job intervals, retry/backoff, and timeouts;
- CORS and rate limiting via built-in factories;
- OpenAPI 3.0 spec generation from registered routes;
- Fixtures;
- Unit testing support with pytest;
- Code generation;
- Automatic REST endpoint generation;
- REST-oriented service design;
- Compatibility with Flask;
- Forward-only SQL migrations;
- PostgreSQL support;



For detailed information, please check the [Documentation](https://oddbit-project.github.io/pokie/)

## Automatic REST from Database Tables

Generate full CRUD endpoints directly from a database table — no DTO, no RequestRecord, no service class needed:

```python
from pokie.core import BaseModule
from pokie.http import AutoRouter
from pokie.rest.auto import Auto


class Module(BaseModule):
    name = "my_module"

    def build(self, parent=None):
        app = parent.app

        # generate a full REST view from the "customers" table
        view = Auto.view(app, "customers")
        AutoRouter.resource(app, "customer", view, id_type="string")
```

This introspects the `customers` table at startup and registers:

| URL                             | Method       | Operation     |
|---------------------------------|--------------|---------------|
| `/customer`                     | GET          | List records  |
| `/customer/<string:id_record>`  | GET          | Get by id     |
| `/customer`                     | POST         | Create        |
| `/customer/<string:id_record>`  | PUT, PATCH   | Update        |
| `/customer/<string:id_record>`  | DELETE        | Delete        |

Listing supports server-side pagination, sorting, filtering and free-text search out of the box via
query parameters (`offset`, `limit`, `sort`, `match`, `search`).

## Automatic REST from DTO Records

For more control, use `Auto.rest()` with a DTO Record — Pokie generates the RequestRecord and service automatically:

```python
from rick_db import fieldmapper
from pokie.core import BaseModule
from pokie.rest.auto import Auto


@fieldmapper(tablename="customers", pk="customer_id")
class CustomerRecord:
    id = "customer_id"
    company_name = "company_name"
    contact_name = "contact_name"


class Module(BaseModule):
    name = "my_module"

    def build(self, parent=None):
        Auto.rest(
            parent.app,
            "customer",
            CustomerRecord,
            search_fields=[CustomerRecord.company_name, CustomerRecord.contact_name],
            id_type="string",
        )
```

Both approaches can be incrementally customized — add a custom RequestRecord for input validation, a custom
service for business logic, or a custom base class for authentication.

## Getting Started

1. Create the application entrypoint, called *main.py*:

```python
from rick.resource.config import EnvironmentConfig
from pokie.config import PokieConfig
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory


class Config(EnvironmentConfig, PokieConfig):
    pass


def build_pokie():
    cfg = Config().build()

    modules = [
        # add your modules here
    ]

    factories = [
        PgSqlFactory,
    ]

    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)
    return pokie_app, flask_app


main, app = build_pokie()

if __name__ == '__main__':
    main.cli()
```

2. Scaffold a module:

```shell
$ python3 main.py codegen:module my_module_name .
```

3. Add the module to the module list on *main.py*:

```python
    modules = [
        'my_module_name',
    ]
```

4. Implement the desired logic in the module


## Running tests with tox

1. Install tox & tox-docker:
```shell
$ pip install -r requirements-test.txt
```

2. Run tests:
```shell
$ tox [-e py<XX>]
```
