# Automatic REST generation

Common REST scenarios include CRUD interaction with a database object (a view, a table or a predefined query); these
often involve a *RequestRecord* with request validation rules, a [DTO Record](https://oddbit-project.github.io/rick_db/object_mapper/) representing the database object, a
*Service* that implements domain logic, and obviously a *RestView* to implement the different endpoints.

Pokie's *rest.Auto* helpers leverage the existing [Code Generation](../codegen/codegen.md) mechanisms to generate in
runtime the required classes for a barebones REST implementation. These classes can be incrementally overridden later,
making them ideal in PoC and simple use cases. They can also be used to perform rapid prototyping - implementations can be done incrementally, starting with automatic helpers and gradually
implementing the specific business logic.

> **Note:** The *rest.Auto* database functionality is only available for PostgreSQL databases. Some data types may not
> work well, and complex schemas may not be fully supported. 

> **Note:** Code generated classes always use **id** as the name representing the primary key field on the database - e.g.
> a table with a field *id_foo* will be referenced on the DTO Record and the RequestRecord as **id**, and not *id_foo*

## Automatic REST from DTO

This mechanism enables the automatic creation of a [RestView](../http/rest.md) object based on a [DTO Record](https://oddbit-project.github.io/rick_db/object_mapper/) representing
a database object. It will automatically generate a *Request* object if none is specified, based on the existing database
table referenced by the DTO Record. The generated View class can also extend either a custom base class or a set of mixins.

### Method signature

*Auto.rest(app: object, slug: str, dto_record: object, request_class: RequestRecord = None, service: str = None,
        id_type: str = None, search_fields: list = None, allow_methods: list = None, base_cls: tuple = None,
        mixins: tuple = None,  \*\*kwargs)*

| Parameter     | Type                                                                         | Description                                                                                  |
|---------------|------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| app           | Flask                                                                        | Flask object                                                                                 |
| slug          | str                                                                          | A endpoint url slug                                                                          |
| dto_record    | RickDB [DTO Record](https://oddbit-project.github.io/rick_db/object_mapper/) | A DTO Record to use                                                                          |
| request_class | Rick [RequestRecord](https://oddbit-project.github.io/rick/forms/requests/)  | An optional RequestRecord to use for input values                                            |
| service       | str                                                                          | An optional service to use instead of the automatically generated one                        |
| id_type       | str                                                                          | The type of the record id for the urls, supported by Flask; defaults to "int"                |
| search_fields | list                                                                         | Optional list of fields to perform text search; if omitted, all varchar/text fields are used |
| allow_methods | list                                                                         | If specified, will only allow the specified http methods                                     |
| base_cls      | class                                                                        | Optional base class to use instead of *pokie.rest.RestView*                                  |
| mixins        | tuple                                                                        | Optional tuple with additional mixins                                                        |


### Usage example

A complete minimal application to expose a database table called *customers* as a REST endpoint:
```python
from rick_db import fieldmapper
from rick.resource.config import EnvironmentConfig
from pokie.config.template import BaseConfigTemplate, PgConfigTemplate
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie.rest.auto import Auto


@fieldmapper(tablename="customers", pk="customer_id")
class CustomerRecord:
    id = "customer_id" # this field is actually a varchar
    company_name = "company_name"
    contact_name = "contact_name"
    contact_title = "contact_title"
    address = "address"
    city = "city"
    region = "region"
    postal_code = "postal_code"
    country = "country"
    phone = "phone"
    fax = "fax"


# config parameters, injectable from ENV vars
class Config(EnvironmentConfig, BaseConfigTemplate, PgConfigTemplate):
    pass


# Our custom route initialization to skip usage of modules
# because Auto.rest() will require database access to the table customers, we need to postpone route registration
# to the actual web initialization routines, as it is done with modules
def router(p: FlaskApplication):
    # Auto.rest() will generate all required classes and register the following routes:
    # /customer                     OPTIONS,HEAD,GET
    # /customer/<string:id_record>  OPTIONS,HEAD,GET
    # /customer                     POST,OPTIONS
    # /customer/<string:id_record>  OPTIONS,PUT,PATCH
    # /customer/<string:id_record>  OPTIONS,DELETE
    Auto.rest(p.app,  # our Flask app
              "customer",  # the base slug
              CustomerRecord,  # the DTO to use
              search_fields=[CustomerRecord.company_name, CustomerRecord.contact_name],  # fields to allow text search
              id_type="string" # type of id_record to use
              )


def build_pokie():
    # load configuration from ENV
    cfg = Config().build()

    # modules to load & initialize
    modules = []

    # factories to run
    factories = [PgSqlFactory, ]

    # build app
    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)
    # register our route initializer to be used only on web context
    pokie_app.register_pre_http_hook(router)

    return pokie_app, flask_app


main, app = build_pokie()

# =============================================================================

if __name__ == '__main__':
    main.cli()
```

While it is possible to build single-file applications with Pokie, the most common scenario is to build modular applications.
When using modules, *Auto.rest* is commonly used in the *build()* section of your *module.py*:

```python
from pokie.core import BaseModule
from pokie.rest.auto import Auto
from pokie_test.dto.records import CustomerRecord


class Module(BaseModule):
    # internal module name
    name = "my_module"

    (...)

    def build(self, parent=None):
        app = parent.app

        # Auto.rest() will generate all required classes and register the following routes:
        # /customer                     OPTIONS,HEAD,GET
        # /customer/<string:id_record>  OPTIONS,HEAD,GET
        # /customer                     POST,OPTIONS
        # /customer/<string:id_record>  OPTIONS,PUT,PATCH
        # /customer/<string:id_record>  OPTIONS,DELETE
        Auto.rest(app,  # our Flask app
                  "customer",  # the base slug
                  CustomerRecord,  # the DTO to use
                  # fields to allow text search
                  search_fields=[CustomerRecord.company_name, CustomerRecord.contact_name],
                  id_type="string"  # type of id_record to use
                  )
        (...)
```

## Automatic REST from Database Table

It is possible to just skip the usage of a [DTO Record](https://oddbit-project.github.io/rick_db/object_mapper/) and
have the framework build one instead in runtime, from an existing database table; *Auto.view()* will generate a RestView
class for the specified table, that can be registered using the [AutoRouter](../http/rest.md#registering-routes) or 
traditional Flask route registration mechanisms.

### Method signature

*Auto.view(app: object, table_name: str, schema: str = None, search_fields: List = None, camel_case: bool = False,
        allow_methods: list = None, base_cls: tuple = None, mixins: tuple = None, \*\*kwargs) -> PokieView:*


| Parameter     | Type  | Description                                                                                  |
|---------------|-------|----------------------------------------------------------------------------------------------|
| app           | Flask | Flask object                                                                                 |
| table_name    | str   | Database table name to use                                                                   |
| schema        | str   | Optional database  schema                                                                    |
| search_fields | list  | Optional list of fields to perform text search; if omitted, all varchar/text fields are used |
| camel_case    | bool  | If true, dict keys are camelCased                                                            |
| allow_methods | list  | If specified, will only allow the specified http methods                                     |
| base_cls      | class | Optional base class to use instead of *pokie.rest.RestView*                                  |
| mixins        | tuple | Optional tuple with additional mixins                                                        |

### Usage example

A complete minimal application to expose a database table called *customers* as a REST endpoint:

```python
from rick.resource.config import EnvironmentConfig
from pokie.config.template import BaseConfigTemplate, PgConfigTemplate
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie.http import AutoRouter
from pokie.rest.auto import Auto


# config parameters, injectable from ENV vars
class Config(EnvironmentConfig, BaseConfigTemplate, PgConfigTemplate):
    pass


# Our custom route initialization to skip usage of modules
# because Auto.rest() will require database access to the table customers, we need to postpone route registration
# to the actual web initialization routines, as it is done with modules
def router(p: FlaskApplication):
    # Auto.view() will generate a view for the customers table
    view = Auto.view(app, "customers", search_fields=["company_name", "contact_name"])
    # and AutoRouter.resouce() registers the following endpoints:
    # /customer                     HEAD,GET,OPTIONS
    # /customer/<string:id_record>  HEAD,GET,OPTIONS
    # /customer                     OPTIONS,POST
    # /customer/<string:id_record>  PATCH,PUT,OPTIONS
    # /customer/<string:id_record>  DELETE,OPTIONS
    AutoRouter.resource(p.app, "customer", view, id_type="string")


def build_pokie():
    # load configuration from ENV
    cfg = Config().build()

    # modules to load & initialize
    modules = []

    # factories to run
    factories = [PgSqlFactory, ]

    # build app
    pokie_app = FlaskApplication(cfg)
    flask_app = pokie_app.build(modules, factories)
    pokie_app.register_pre_http_hook(router)

    return pokie_app, flask_app


main, app = build_pokie()

# =============================================================================

if __name__ == '__main__':
    main.cli()
```


While it is possible to build single-file applications with Pokie, the most common scenario is to build modular applications.
As it happens with *Auto.rest()*, *Auto.view* is commonly used in the *build()* section of your *module.py*:

```python
from pokie.core import BaseModule
from pokie.rest import Auto
from pokie.http import AutoRouter


class Module(BaseModule):
    # internal module name
    name = "my_module"

    (...)

    def build(self, parent=None):
        app = parent.app

        # Auto.view() will generate a view for the customers table
        view = Auto.view(app, "customers", search_fields=["company_name", "contact_name"])
        # and AutoRouter.resouce() registers the following endpoints:
        # /customer                     HEAD,GET,OPTIONS
        # /customer/<string:id_record>  HEAD,GET,OPTIONS
        # /customer                     OPTIONS,POST
        # /customer/<string:id_record>  PATCH,PUT,OPTIONS
        # /customer/<string:id_record>  DELETE,OPTIONS
        AutoRouter.resource(p.app, "customer", view, id_type="string")
        (...)
```