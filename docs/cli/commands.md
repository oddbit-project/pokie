# CLI Commands

Pokie includes a CLI system for common development and administration tasks. Commands are invoked via the application
entry point:

```shell
$ python main.py <command> [arguments]
```

If no command is specified, the `list` command is executed by default.

## Basic Commands

### list

List all available commands.

```shell
$ python main.py list
```

### help

Display usage information for a specific command.

```shell
$ python main.py help <command>
```

### version

Display the Pokie framework version.

```shell
$ python main.py version
```

### runserver

Run the Flask development server.

```shell
$ python main.py runserver [options]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `-h`, `--host` | `127.0.0.1` | Interface to bind to |
| `-p`, `--port` | `5000` | Port to bind to |
| `-d`, `--debug` | `false` | Enable debug mode |
| `-r`, `--reload` | `false` | Enable automatic reload |

## Database Commands

### db:init

Initialize the database migration tracking table.

```shell
$ python main.py db:init
```

This creates the internal migration manager table used to track which SQL migrations have been applied.

### db:check

Show the status of all database migrations.

```shell
$ python main.py db:check
```

Displays each migration file and its status: **new** (not yet applied), **applied**, or **empty** (no SQL content).

### db:update

Apply pending database migrations.

```shell
$ python main.py db:update [options]
```

| Argument | Description |
|----------|-------------|
| `--dry` | Preview migrations without executing them |

Migrations are loaded from the `sql/` folder of each module and executed in order.

## Code Generation Commands

### codegen:dto

Generate a RickDb Record (DTO) class from a database table.

```shell
$ python main.py codegen:dto <table> [options]
```

| Argument | Description |
|----------|-------------|
| `table` | Source table name. Use `schema.table` for non-default schemas, or `*` for all tables. |
| `-f`, `--file` | Destination file (prints to stdout if omitted) |
| `-c`, `--camelcase` | Use camelCase attribute names |

### codegen:request

Generate a Rick RequestRecord class from a database table.

```shell
$ python main.py codegen:request <table> [options]
```

| Argument | Description |
|----------|-------------|
| `table` | Source table name. Use `schema.table` for non-default schemas, or `*` for all tables. |
| `-f`, `--file` | Destination file (prints to stdout if omitted) |
| `-c`, `--camelcase-names` | Use camelCase field names |

### codegen:module

Generate a module directory structure from a template.

```shell
$ python main.py codegen:module <name> <path>
```

| Argument | Description |
|----------|-------------|
| `name` | Module name |
| `path` | Destination directory |

### codegen:app

Generate a complete Pokie application with a module and `main.py`.

```shell
$ python main.py codegen:app <name> <path>
```

| Argument | Description |
|----------|-------------|
| `name` | Application/module name |
| `path` | Destination directory |

See [Code Generation](../codegen/codegen.md) for more details.

## Fixture Commands

### fixture:run

Execute registered fixtures.

```shell
$ python main.py fixture:run [name ...]
```

| Argument | Description |
|----------|-------------|
| `name` | Optional fixture name(s) to run. If omitted, all fixtures are executed. |

Fixtures that have already been executed are skipped. Fixture names must be dotted paths
(e.g. `mymodule.fixtures.SeedData`).

### fixture:check

Show the status of all registered fixtures.

```shell
$ python main.py fixture:check
```

Displays each fixture and its status: **new fixture** or **already executed**. Also detects and reports duplicate
fixture registrations.

See [Fixtures](../fixtures.md) for more details.

## Job Commands

### job:list

List all registered job workers across all modules.

```shell
$ python main.py job:list
```

### job:run

Start all registered job workers in continuous mode.

```shell
$ python main.py job:run
```

Jobs run in an infinite loop until interrupted with SIGINT.

## OpenAPI Commands

### openapi:generate

Generate an [OpenAPI 3.0](https://spec.openapis.org/oas/v3.0.0) specification from the registered routes.

```shell
$ python main.py openapi:generate [options]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `-f` | *(stdout)* | Output file path. If omitted, the spec is printed to stdout. |
| `--title` | `"Pokie API"` | API title in the spec |
| `--version` | `"1.0.0"` | API version in the spec |
| `--prefix` | `""` | Filter routes by URL prefix (e.g. `/api/v1`) |

The command introspects the Flask URL map and view class metadata to generate paths, parameters, request bodies,
and response schemas. It maps `RequestRecord` field validators to OpenAPI types:

| Validator | OpenAPI type | OpenAPI format |
|-----------|-------------|----------------|
| `numeric` | `integer` | - |
| `decimal` | `number` | - |
| `bool` | `boolean` | - |
| `iso8601` | `string` | `date-time` |
| `maxlen:N` | `string` | *(maxLength: N)* |
| *(default)* | `string` | - |

List endpoints (GET without path parameters) automatically include the standard DbGrid query parameters
(`offset`, `limit`, `sort`, `match`, `search`).

**Examples:**

```shell
# print to stdout
$ python main.py openapi:generate

# save to file
$ python main.py openapi:generate -f openapi.json

# filter to a specific prefix
$ python main.py openapi:generate --prefix /api/v1 -f api_v1.json

# custom title and version
$ python main.py openapi:generate --title "My API" --version "2.0.0"
```

## Utility Commands

### module:list

List all loaded modules.

```shell
$ python main.py module:list [options]
```

| Argument | Description |
|----------|-------------|
| `--json` | Output in JSON format |

Displays: module name, class path, and description.

### route:list

List all registered Flask routes.

```shell
$ python main.py route:list
```

### pytest

Run pytest with the Pokie test plugin.

```shell
$ python main.py pytest [pytest-arguments]
```

All arguments after `pytest` are forwarded to pytest. See [Writing Tests](../test/pytest.md) for details.
