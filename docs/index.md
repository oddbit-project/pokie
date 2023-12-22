![Pokie](img/pokie_bar.png){style="display: block; margin: 0 auto" }

# Welcome to Pokie

[![Tests](https://github.com/oddbit-project/pokie/workflows/Tests/badge.svg?branch=master)](https://github.com/oddbit-project/pokie/actions)
[![pypi](https://img.shields.io/pypi/v/pokie.svg)](https://pypi.org/project/pokie/)
[![license](https://img.shields.io/pypi/l/pokie.svg)](https://git.oddbit.org/OddBit/pokie/src/branch/master/LICENSE)


Pokie is an REST web framework built on top of [Flask](https://github.com/pallets/flask/),
[Rick](https://git.oddbit.org/OddBit/rick) and [Rick-db](https://git.oddbit.org/OddBit/rick_db) libraries, following three-layer and clean architecture
design principles.

It features an object-oriented design, borrowing from common patterns found in other languages, such as
dependency injection, service location, factories and object composition. It also offers the following functionality:

- Modular design;
- Dependency registry;
- CLI command support;
- Jobs (objects invoked periodically to perform a task);
- Fixtures;
- Unit testing support with pytest;
- Code generation;
- Automatic endpoint generation;
- REST-oriented service design;
- Compatibility with Flask;
- Forward-only SQL migrations;
- PostgreSQL support;

> Note: Pokie is still under heavy development and should not be considered stable or production-ready.

## TL; DR; tutorial

1. Create the application entrypoint, called *main.py*:

```python
from rick.resource.config import EnvironmentConfig
from pokie.config.template import BaseConfigTemplate, PgConfigTemplate, TestConfigTemplate
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory

class Config(EnvironmentConfig, BaseConfigTemplate, PgConfigTemplate, TestConfigTemplate):
    # @todo: add your config options or overrides here
    pass

def build_pokie():
    # load configuration from ENV
    cfg = Config().build()

    # modules to load & initialize
    modules = [
        #@ todo: add your modules here
        
    ]

    # factories to run
    factories = [
        PgSqlFactory, 
        # @todo: add additional factories here
    ]

    # build app
    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)
    return pokie_app, flask_app


main, app = build_pokie()

if __name__ == '__main__':
    main.cli()
```

2. Use our application to scaffold a module:

```shell
$ python3 main.py codegen:module my_module_name .
```

3. Add your newly created module to the module list on *main.py*:

```python
    (...)
    # modules to load & initialize
    modules = [
        'my_module_name',  # our newly created module
        
    ]
    (...)
```

4. Implement the desired logic in the module

