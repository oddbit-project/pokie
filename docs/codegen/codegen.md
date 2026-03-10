# Code Generation

Pokie provides code generation mechanisms that can produce either source code files or runtime classes. Source code
generation is available via CLI commands, while runtime generation is used internally by the
[Auto REST](../rest/auto.md) system.

## CLI Code Generation

### Generating DTO Records

The `codegen:dto` command generates RickDb Record classes from database table schemas:

```shell
$ python main.py codegen:dto <table> [options]
```

| Argument | Description |
|----------|-------------|
| `table` | Table name, `schema.table`, or `*` for all tables |
| `-f`, `--file` | Write output to file (prints to stdout if omitted) |
| `-c`, `--camelcase` | Use camelCase attribute names |

Example:

```shell
$ python main.py codegen:dto customers
```

Generated output:

```python
from rick_db import fieldmapper


@fieldmapper(tablename='customers', pk='customer_id', schema='public')
class CustomersRecord:
    id = 'customer_id'
    company_name = 'company_name'
    contact_name = 'contact_name'
    contact_title = 'contact_title'
    address = 'address'
```

To generate all tables in a schema:

```shell
$ python main.py codegen:dto "public.*" -f dto/records.py
```

The primary key field is always mapped to `id` in the generated class.

### Generating Request Records

The `codegen:request` command generates Rick RequestRecord classes for input validation:

```shell
$ python main.py codegen:request <table> [options]
```

| Argument | Description |
|----------|-------------|
| `table` | Table name, `schema.table`, or `*` for all tables |
| `-f`, `--file` | Write output to file (prints to stdout if omitted) |
| `-c`, `--camelcase-names` | Use camelCase field names |

Example:

```shell
$ python main.py codegen:request customers
```

Generated output:

```python
from rick.form import RequestRecord, field

class CustomersRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric', bind='id'),
        'company_name': field(validators='required|maxlen:100', bind='company_name'),
        'contact_name': field(validators='maxlen:100', bind='contact_name'),
    }
```

Validators are automatically determined from column data types:

| Column Type | Validators |
|-------------|------------|
| `int2`, `int4`, `int8` | `numeric` |
| `numeric` | `decimal` |
| `bool` | `bool` |
| `timestamp`, `timestamptz`, `date` | `iso8601` |
| Columns with max length | `maxlen:{n}` |
| Non-nullable, non-auto columns | `required` |
| Foreign key columns | `pk:{schema}.{table},{column}` |

### Generating Module Structure

The `codegen:module` command creates a module directory from a built-in template:

```shell
$ python main.py codegen:module my_module .
```

This creates a directory `my_module/` with the standard Pokie module layout including `module.py`, `__init__.py`, and
subdirectories for cli, dto, service, view, etc.

### Generating Application

The `codegen:app` command creates a complete Pokie application with a module and entry point:

```shell
$ python main.py codegen:app my_app .
```

This generates both a module structure and a `main.py` entry point.

## Runtime Code Generation

The code generation system is also used at runtime by `Auto.rest()` and `Auto.view()` to dynamically create Record
and RequestRecord classes from database table schemas. This is handled by two generator classes:

### RecordGenerator

Generates RickDb Record classes from a `TableSpec`:

- `generate_source(spec, camelcase=False)` - Returns Python source code as a string
- `generate_class(spec, camelcase=False)` - Returns a dynamically created Record class

### RequestGenerator

Generates Rick RequestRecord classes from a `TableSpec`:

- `generate_source(spec, camelcase=False)` - Returns Python source code as a string
- `generate_class(spec, camelcase=False)` - Returns a dynamically created RequestRecord class

These generators are used internally and typically do not need to be called directly. See
[Auto REST](../rest/auto.md) for the high-level API.

> Note: Database code generation is only supported with PostgreSQL.
