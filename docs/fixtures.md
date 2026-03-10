# Fixtures

Fixtures are one-time initialization tasks used to seed databases with default data, perform data migrations, or
execute non-trivial setup operations. Each fixture is tracked in the database and will only run once.

## Writing a Fixture

A fixture class must implement both `Injectable` and `Runnable` from Rick:

```python
from rick.base import Di
from rick.mixin import Injectable, Runnable


class SeedCustomers(Injectable, Runnable):

    def run(self, di: Di):
        db = di.get("db")
        # insert default records, perform migrations, etc.
        pass
```

The `run()` method receives the DI container and can access any registered resource.

## Registering Fixtures

Fixtures are registered in the module's `fixtures` list using dotted class paths:

```python
from pokie.core import BaseModule


class Module(BaseModule):
    name = "my_module"
    description = "My module"

    fixtures = [
        "my_module.fixtures.SeedCustomers",
        "my_module.fixtures.SeedProducts",
    ]
```

## Running Fixtures

### Via CLI

Run all pending fixtures:

```shell
$ python main.py fixture:run
```

Run specific fixtures by name:

```shell
$ python main.py fixture:run my_module.fixtures.SeedCustomers
```

Fixture names must be fully qualified dotted paths. Fixtures that have already been executed are automatically skipped.

### Checking Status

View which fixtures are pending or already executed:

```shell
$ python main.py fixture:check
```

This also detects and reports duplicate fixture registrations across modules.

## Fixture Tracking

Executed fixtures are tracked in the `_fixture` database table. Each entry records the fixture name and when it was
applied. This prevents fixtures from running more than once, even across application restarts.

The `FixtureService` manages fixture scanning, execution, and tracking:

- `scan()` - Scans all loaded modules for fixture definitions
- `execute(fixture_name)` - Loads and runs a fixture by its dotted class path
- `list()` - Returns all tracked fixture records
- `add(record)` - Records a fixture as executed

## Fixtures in Testing

When using Pokie's pytest integration with `TEST_MANAGE_DB = True`, fixtures can be automatically executed when the
test database is created. This behavior is controlled by the `TEST_SKIP_FIXTURES` configuration option. See
[Writing Tests](test/pytest.md) for details.
